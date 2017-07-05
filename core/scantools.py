# -*- coding:utf-8 -*-
import requests
import json
from core.const import logger, store, cursor, column, WEAK_LEVEL


# transform data from ZoomEye to the format we want
def trans(match):
    return {
        "ip_addr": "%s:%s" % (match["ip"], match["portinfo"]["port"]),
        "lat": match["geoinfo"]["location"]["lat"],
        "lon": match["geoinfo"]["location"]["lon"],
        "addr": "%s, %s, %s" % (
            match["geoinfo"]["city"]["names"]["zh-CN"] or "unknowncity%s" % (
            repr(match["geoinfo"]["city"]["geoname_id"])),
            match["geoinfo"]["country"]["names"]["zh-CN"], match["geoinfo"]["continent"]["names"]["zh-CN"]),
        "level": WEAK_LEVEL.POSSIBLE
    }


def login():
    data = {
        "username": "907937976@qq.com",
        "password": "bupt1210",
    }
    logger.info("获取access_token..")
    resp = json.loads(requests.post(url="https://api.zoomeye.org/user/login", data=json.dumps(data)).text)
    access_token = resp["access_token"]
    with open("output/access_token.txt", "w") as f:
        f.write(access_token)
    logger.info("access_token已写入文件")


def get_dev_list():
    login()
    with open("output/access_token.txt", "r") as f:
        access_token = f.read()

    page_number = 1005
    headers = {"Authorization": "JWT " + access_token}

    cursor.execute("select * from page where rowid=1")
    page = cursor.fetchone()[0]

    while True:
        resp = json.loads(requests.get(
            url='https://api.zoomeye.org/host/search?query=app:"Netwave IP camera http config" &page=%s' % page,
            headers=headers).text)
        try:
            for dev in resp["matches"]:
                yield trans(dev)
            page += 1
            store.execute("update page set page=? where rowid=1", str(page))
            store.commit()
            logger.info("已扫描%s个ip" % (page * 10 - 10))
            if page > page_number:
                break
        except KeyError as err:
            if err == "matches":
                logger.info("超过请求次数上限")  # 有请求次数限制
                break
            else:
                logger.debug("其余键值错误:%s" % err)
                print(resp)


def restore():
    cursor.execute("select * from devices")
    while True:
        try:
            yield dict(zip(column, list(cursor.fetchone())))
        except TypeError:
            break


if __name__ == "__main__":
    import logging

    logger = logging.getLogger("scantools")
    logger.setLevel(logging.INFO)
    dev = [{
        "ip_addr": "116.110.5.114:81",
        "mac_addr": "00A9C000BF7A"
    }]
    test = filter(_attack, dev)

    # print(next(test))
    print(next(restore()))
