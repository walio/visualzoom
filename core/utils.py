# -*- coding:utf-8 -*-
import requests
import json
import logging
import redis

info_store = redis.StrictRedis("127.0.0.1", 6379, 0, decode_responses=True)
device_store = redis.StrictRedis("127.0.0.1", 6379, 1, decode_responses=True)
logger = logging.getLogger("webLog")


# transform data from ZoomEye to the format we want
def trans(match):
    return {
        "ip_addr": "%s:%s" % (match["ip"], match["portinfo"]["port"]),
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


def get_dev_list(query_string):
    page_number = 1005
    headers = {"Authorization": "JWT " + get_access_token()}
    page = int(info_store.get("page"))

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
            info_store.set("page", page)
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
            yield {"ip_addr": line.replace("\n", "")}


def restore():
    for _ in device_store.keys("*"):
        yield device_store.hgetall(_)


def init_db():
    info_store.setnx("page","1")
    info_store.setnx("zoomQueries","[]")
    info_store.setnx("ipList","[]")
    info_store.setnx("selectedPoc","''")
    info_store.setnx("styleJson","[]")
    info_store.setnx("translate","{}")
    


if __name__ == "__main__":
    pass
