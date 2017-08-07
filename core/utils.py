# -*- coding:utf-8 -*-
import requests
import json
import os
import logging
import redis
import itertools
import ipaddress

config_store = redis.StrictRedis("127.0.0.1", 6379, 0, decode_responses=True)
device_store = redis.StrictRedis("127.0.0.1", 6379, 1, decode_responses=True)
error_store = redis.StrictRedis("127.0.0.1", 6379, 2, decode_responses=True)
extra_store = redis.StrictRedis("127.0.0.1", 6379, 3, decode_responses=True)
logger = logging.getLogger("webLog")


# transform data from ZoomEye to the format we want
def trans(match):
    return {
        "ip": match["ip"],
        "port": match["portinfo"]["port"],
        "lat": match["geoinfo"]["location"]["lat"],
        "lon": match["geoinfo"]["location"]["lon"],
        "city": match["geoinfo"]["city"]["names"]["zh-CN"],
        "country": match["geoinfo"]["country"]["names"]["zh-CN"],
        "continent": match["geoinfo"]["continent"]["names"]["zh-CN"]
    }


def get_access_token():
    data = {
        "username": "907937976@qq.com",
        "password": "bupt1210",
    }
    logger.info(u"获取access_token..")
    resp = json.loads(requests.post(url="https://api.zoomeye.org/user/login", data=json.dumps(data)).text)
    logger.info("已获取access_token")
    return resp["access_token"]


def zoom_iter(query_string):
    page_number = 1005
    headers = {"Authorization": "JWT " + get_access_token()}
    page = int(config_store.get("page") or 1)

    while True:
        resp = json.loads(requests.get(
            url='https://api.zoomeye.org/host/search?query=%s&page=%s' % (query_string, page),
            headers=headers).text)
        if "error" in resp and resp["message"] == "Invalid Token, Signature has expired":
            headers = {"Authorization": "JWT " + get_access_token()}
            continue
        try:
            for dev in resp["matches"]:
                yield trans(dev)
            page = page+1
            config_store.set("page", page)
            logger.info("已扫描%s个ip" % (page * 10 - 10))
            if page > page_number:
                break
        except KeyError as err:
            if err == "matches":
                logger.info(u"超过请求次数上限")  # 有请求次数限制
                break
            else:
                logger.info(u"其余键值错误:%s" % err)
                logger.debug(resp)


def get_ip_from_file(file):
    with open(file, "r") as f:
        for line in f:
            yield {
                "ip": line.replace("\n", "").split(":")[0],
                "port": line.replace("\n", "").split(":")[1],
            }


def ip_iter(start, end, port):
    for _ in range(int(ipaddress.ip_address(start)), int(ipaddress.ip_address(end))+1):
        yield {
            "ip": str(ipaddress.ip_address(_)),
            "port": port
        }


def scan_iter():
    ip_source = iter([])
    for _ in config_store.smembers("zoomeye_queries"):
        ip_source = itertools.chain(ip_source, zoom_iter(_))
    for _ in config_store.smembers("ip_ranges"):
        _ = json.loads(_)
        ip_source = itertools.chain(ip_source, ip_iter(_["start"], _["end"], _["port"]))

    poc = __import__("poc.%s" % os.path.splitext(config_store.get("selected_poc"))[0], fromlist=[""])
    target_iter = filter(poc.verify, ip_source)
    return target_iter


def set_config(config):
    if "selected_poc" in config.keys():
        assert type(config["selected_poc"]) == str, "Poc file name format not correct"
        assert os.path.exists("poc\%s" % config["selected_poc"]), "Poc file not found"
        config_store.set("selected_poc", config["selected_poc"])
    if "zoomeye_queries" in config.keys():
        assert type(config["zoomeye_queries"]) == list, "zoomeye_queries format not corrected"
        for _ in config["zoomeye_queries"]:
            assert type(_) == str, "zoomeye_queries format not corrected"
        config_store.delete("zoomeye_queries")
        for _ in config["zoomeye_queries"]:
            config_store.sadd("zoomeye_queries",_)
    if "ip_ranges" in config.keys():
        assert type(config["ip_ranges"]) == list, "Ip ranges format not correct"
        for _ in config["ip_ranges"]:
            assert type(_) == dict, "Ip range format not correct"
            assert _.get("start") or _.get("end"), "Ip range format not correct"
            assert type(_.get("port")) == int and -1 < _["port"] < 65536, "Port format not correct"
        config_store.delete("ip_ranges")
        for _ in config["ip_ranges"]:
            ip_range = ipaddress.ip_address(_.get("start") or _.get("end")), ipaddress.ip_address(_.get("end") or _.get("start"))
            # todo: remove the same ip:port address
            config_store.sadd("ip_ranges",json.dumps({
                "start": str(min(ip_range)),
                "end": str(max(ip_range)),
                "port": _["port"]
            }))


if __name__ == "__main__":
    pass
