# -*- coding:utf-8 -*-
import requests
import json
import os
import logging
import redis
import itertools
import ipaddress
import threading

config_store = redis.StrictRedis("127.0.0.1", 6379, 0, decode_responses=True)
device_store = redis.StrictRedis("127.0.0.1", 6379, 1, decode_responses=True)
error_store = redis.StrictRedis("127.0.0.1", 6379, 2, decode_responses=True)
extra_store = redis.StrictRedis("127.0.0.1", 6379, 3, decode_responses=True)

dev_logger = logging.getLogger("devReport")
web_logger = logging.getLogger("webLog")


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
        "username": "1810440817@qq.com",
        "password": "bupt1210",
    }
    web_logger.info(u"获取access_token..")
    resp = json.loads(requests.post(url="https://api.zoomeye.org/user/login", data=json.dumps(data)).text)
    web_logger.info("已获取access_token")
    return resp["access_token"]


def zoomeye_generator(query_string):
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
            web_logger.info("已扫描%s个ip" % (page * 10 - 10))
            if page > page_number:
                break
        except KeyError as err:
            if err == "matches":
                web_logger.info(u"超过请求次数上限")  # 有请求次数限制
                break
            else:
                web_logger.info(u"其余键值错误:%s" % err)
                web_logger.debug(resp)


def ip_file_generator(file):
    with open(file, "r") as f:
        for line in f:
            yield {
                "ip": line.replace("\n", "").split(":")[0],
                "port": line.replace("\n", "").split(":")[1],
            }


def ip_generator(start, end, port):
    for _ in range(int(ipaddress.ip_address(start)), int(ipaddress.ip_address(end))+1):
        yield {
            "ip": str(ipaddress.ip_address(_)),
            "port": port
        }


def scan_generator():
    ip_source = iter([])
    for _ in config_store.smembers("zoomeye_queries"):
        ip_source = itertools.chain(ip_source, zoomeye_generator(_))
    for _ in config_store.smembers("ip_ranges"):
        _ = json.loads(_)
        ip_source = itertools.chain(ip_source, ip_generator(_["start"], _["end"], _["port"]))

    poc = __import__("poc.%s" % os.path.splitext(config_store.get("selected_poc"))[0], fromlist=[""])
    for _ in ip_source:
        yield poc.verify(_), _
    # target_iter = filter(poc.verify, ip_source)
    # return target_iter


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
            config_store.sadd("zoomeye_queries", _)
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


class Scan(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.iterations = 0
        self.daemon = True
        self.paused = True
        self.state = threading.Condition()
        self.target_iter = scan_generator()

    def run(self):
        self.resume()
        while True:
            with self.state:
                if self.paused:
                    print(self.paused)
                    self.state.wait()
            try:
                print("start")
                res = next(self.target_iter)
                if res[0]:
                    dev_logger.info(json.dumps(res[1]))
                    device_store.hmset("%s:%s" % (res[1]["ip"], res[1]["port"]), res[1])
            except StopIteration:
                dev_logger.info("scanFinished")
                break
            # except Exception:
            #     exc_type, exc_obj, exc_tb = sys.exc_info()
            #     web_logger.info("扫描时发生异常：")
            #     for _ in (str(exc_type), exc_tb.tb_frame.f_code.co_filename, str(exc_tb.tb_lineno)):
            #         web_logger.critical(_)
            #         error_store.lpush(time, _)

    def resume(self):
        with self.state:
            self.paused = False
            self.state.notify()

    def pause(self):
        with self.state:
            self.paused = True
            web_logger.info("stopScanSuccess")

if __name__ == "__main__":
    pass
