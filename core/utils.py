# -*- coding:utf-8 -*-
import requests
import json
from core import store, cursor, column


class WEAK_LEVEL:
    POSSIBLE = 0
    VULNERABLE = 1
    FRAGILE = 2


def insert_device(device):
    store.execute("INSERT INTO devices VALUES (?,?,?,?,?,?,?,?,?)",
                  (device.get("ip_addr"), device.get("lat"), device.get("lon"), device.get("addr"), device.get("level"),
                   device.get("wpapsk"), device.get("ssid"), device.get("user"), device.get("passwd")))
    store.commit()

# transform data from ZoomEye to the format we want
def trans(match):
    return {
        "ip_addr": "%s:%s" % (match["ip"], match["portinfo"]["port"]),
        "lat": match["geoinfo"]["location"]["lat"],
        "lon": match["geoinfo"]["location"]["lon"],
        "addr": "%s, %s, %s" % (
            match["geoinfo"]["city"]["names"]["zh-CN"] or "unknowncity%s" % (repr(match["geoinfo"]["city"]["geoname_id"])),
            match["geoinfo"]["country"]["names"]["zh-CN"], match["geoinfo"]["continent"]["names"]["zh-CN"]),
        "level": WEAK_LEVEL.POSSIBLE
    }


def login(logger):
    data = {
        "username": "907937976@qq.com",
        "password": "bupt1210",
    }
    logger.info(u"获取access_token..")
    resp = json.loads(requests.post(url="https://api.zoomeye.org/user/login", data=json.dumps(data)).text)
    access_token = resp["access_token"]
    with open("output/access_token.txt", "w") as f:
        f.write(access_token)
    logger.info(u"access_token已写入文件")
    return access_token


def get_dev_list(logger):
    login(logger)
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
        if "error" in resp and resp["message"] == "Invalid Token, Signature has expired":
            access_token = login()
            headers = {"Authorization": "JWT " + access_token}
            continue
        try:
            for dev in resp["matches"]:
                yield trans(dev)
            page += 1
            logger.debug(page)
            store.execute("update page set page=? where rowid=1", (str(page),))
            store.commit()
            logger.info("已扫描%s个ip" % (page * 10 - 10))
            if page > page_number:
                break
        except KeyError as err:
            if err == "matches":
                logger.info(u"超过请求次数上限")  # 有请求次数限制
                break
            else:
                logger.debug(u"其余键值错误:%s" % err)
                logger.debug(resp)

def get_dev_from_file(file):
    with open(file, "r") as f:
        for line in f:
            yield {"ip_addr":line.replace("\n", "")}


def restore():
    cursor.execute("select * from devices")
    while True:
        try:
            yield dict(zip(column, list(cursor.fetchone())))
        except TypeError:
            break


if __name__ == "__main__":
    pass
