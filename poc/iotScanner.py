# -*- coding:utf-8 -*-
import json
import requests
import logging
import re
import base64
import html5lib
import urllib3
from bs4 import BeautifulSoup
config = {
    "device_type": "all",
    "zoomeye_query": "any"
}
with open("poc/devices.cfg", "r") as f:
    device_patterns = json.loads(f.read())
logger = logging.getLogger("webLog")
"""
1. identify device type of a ip_addr according to devTypePattern
2. find login url with nextUrl or loginUrlPattern
3. call check_login to try to login with auth
"""


def search4type(resp):
    """
    :param resp: <class 'requests.models.Response'>
    :return: string
    """
    soup = BeautifulSoup(resp.text.lower(), "html5lib")

    for type_name, type_pattern in device_patterns.items():
        tomatch_locate = type_pattern["devTypePattern"][0]
        if tomatch_locate[0] == "header":
            tomatch = resp.headers.get(tomatch_locate[1], "").lower()
        elif tomatch_locate[0] == "body":
            if tomatch_locate[1] == "":
                tomatch = resp.text.lower()
            else:
                tomatch = soup.find(tomatch_locate[1].lower()).get_text() if soup.find(tomatch_locate[1].lower()) else ""
        tomatch_pattern = type_pattern["devTypePattern"][1]
        if tomatch_pattern[0] == "==":
            if tomatch == tomatch_pattern[1].lower():
                return type_name
        elif tomatch_pattern[0].startswith("regex"):
            has_diff = False
            for _ in type_pattern["devTypePattern"][1][1:]:
                if not re.search(_.lower(), tomatch):
                    has_diff = True
                    break
            if not has_diff:
                return type_name
        elif tomatch_pattern[0] == "substr":
            if tomatch_pattern[1].lower() in tomatch:
                return type_name
    return ""


def compose_url(ip_addr, url=None):
    if not url:
        return "http://%s/" % ip_addr
    elif url.startswith("http"):
        return url
    elif url.startswith("/"):
        return "http://%s%s" % (ip_addr, url)


def check_login(dev, url, resp):
    """
    :param url: string(login page)
    :param resp: <class 'requests.models.Response'> (used to extract data if needed)
    :param type_name: string(type of device)
    :return: bool
    """
    auth = device_patterns[dev["device_type"]]["auth"]
    logger.debug("checking login on url: %s" % url)
    if auth[0] == "basic":
        if not auth[1]:
            if requests.get(url, verify=False).status_code == 200:
                logger.info("device %s of type %s still has default password\n" % (dev["ip"], dev["device_type"]))
                dev["admin"] = device_patterns[dev["device_type"]]["pass"][0]
                dev["pass"] = device_patterns[dev["device_type"]]["pass"][1]
                return True
            else:
                logger.info("device %s of type %s has changed password\n" % (dev["ip"], dev["device_type"]))
                return False
        elif requests.get(url, headers={
            "Authorization": "Basic %s" % base64.b64encode(auth[1].encode(encoding='gb2312')).decode('utf-8')
        }, verify=False).status_code == 200:
            logger.info("device%s of type %s still has default password\n" % (dev["ip"], dev["device_type"]))
            dev["admin"] = device_patterns[dev["device_type"]]["pass"][0]
            dev["pass"] = device_patterns[dev["device_type"]]["pass"][1]
            return True
        else:
            logger.warning("device %s of type %s has changed password\n" % (dev["ip"], dev["device_type"]))
            return False
    elif auth[0] == "form":
        if auth[1].startswith("sub") != ("extractFormData" in device_patterns[dev["device_type"]]):
            raise Exception("lack one of extractFormData and substitute")
        post_data = auth[2]
        if "extractFormData" in device_patterns[dev["device_type"]]:
            extracted_data = []
            for _ in device_patterns[dev["device_type"]]["extractFormData"]:
                extracted_data.append(re.search(_, resp.text).group(1))
            # substitude $1,$2,$3 and so on to %, and use dev_info["extractedData"] to assign
            post_data = re.sub("\$(\d+)", "%s", post_data) % tuple(extracted_data)
        try:
            resp_ = requests.get(url, post_data, verify=False)
        except requests.exceptions.ConnectionError:
            logger.error("connection error\n")
            return False
        if auth[3] == "body":
            if auth[4] == "regex":
                if re.search(auth[5], resp_.text):
                    logger.info("device %s of type %s still has default password\n" % (dev["ip"], dev["device_type"]))
                    dev["admin"] = device_patterns[dev["device_type"]]["pass"][0]
                    dev["pass"] = device_patterns[dev["device_type"]]["pass"][1]
                    return True
                else:
                    logger.warning("device %s of type %s has changed password\n" % (dev["ip"], dev["device_type"]))
                    return False
            elif auth[4] == "substr":
                if auth[5] in resp_.text:
                    logger.info("device %s of type %s still has default password\n" % (dev["ip"], dev["device_type"]))
                    dev["admin"] = device_patterns[dev["device_type"]]["pass"][0]
                    dev["pass"] = device_patterns[dev["device_type"]]["pass"][1]
                    return True
                else:
                    logger.warning("device %s of type %s has changed password\n" % (dev["ip"], dev["device_type"]))
                    return False
            elif auth[4] == "!substr":
                if not auth[5] in resp_.text:
                    logger.info("device %s of type %s still has default password\n" % (dev["ip"], dev["device_type"]))
                    dev["admin"] = device_patterns[dev["device_type"]]["pass"][0]
                    dev["pass"] = device_patterns[dev["device_type"]]["pass"][1]
                    return True
        raise Exception("auth[1] of type form auth has another type")
    elif auth[0] == "expect200":
        if requests.get(url, verify=False).status_code == 200:
            logger.info("device %s of type %s not have any password\n" % (dev["ip"], dev["device_type"]))
            dev["admin"] = device_patterns[dev["device_type"]]["pass"][0]
            dev["pass"] = device_patterns[dev["device_type"]]["pass"][1]
            return True
        else:
            logger.debug("device %s of type %s fail to expect 200\n" % (dev["ip"], dev["device_type"]))
    else:
        resp_ = requests.get(url, verify=False)
        if resp_.status_code == 301 or resp_.status_code == 302:
            logger.debug("301 and 302 should be automatically handled by requests but not")
        else:
            logger.warning("device %s: unexpected resp code %d\n" % (url, resp_.status_code))
        raise Exception("unknown auth type: %s" % auth[0])


def check_init_login():
    pass


def verify(dev, stage="", uri=None, device_type=""):
    if device_type not in device_patterns.keys():
        logger.error("device type not correct, type will be checked automatically")
        type_name = ""
    else:
        type_name = device_type
    url = compose_url("%s:%s" % (dev["ip"], dev["port"]), uri)
    if stage == "initialClickLoginPage":
        return check_init_login()
    try:
        resp = requests.get(url, verify=False)
    except requests.exceptions.ConnectionError:
        logger.error("could not connect")
        return False
    except urllib3.exceptions.LocationValueError:
        logger.error("could not connect")
        return False
    soup = BeautifulSoup(resp.text.lower(),  "html5lib")
    logger.debug("got status=%d for %s" % (resp.status_code, resp.url))
    if (resp.status_code == 401) or (resp.status_code == 403):
        type_name = type_name or search4type(resp)
        if not type_name:
            logger.info("fail to identify device type after trying all patterns\n")
            return False
        logger.debug("device type is %s" % type_name)
        dev["device_type"] = type_name
        return True if check_login(url=compose_url("%s:%s" % (dev["ip"], dev["port"]), resp.url), resp=resp, dev=dev) else False
    elif resp.status_code == 200:
        type_name = type_name or search4type(resp)
        if type_name:
            logger.debug("device type is %s\n" % type_name)
            dev["device_type"] = type_name
            if "loginUrlPattern" in device_patterns[type_name]:
                _ = re.search(device_patterns[type_name]["loginUrlPattern"], resp.text)
                return check_login(url=compose_url("%s:%s" % (dev["ip"], dev["port"]), _.group()), resp=resp, dev=dev) if _ else False
            else:
                _ = device_patterns[type_name]["nextUrl"]
                if _[0] == "string":
                    if not _[1]:
                        return check_login(url=compose_url("%s:%s" % (dev["ip"], dev["port"])), resp=resp, dev=dev)
                    else:
                        return check_login(url=compose_url("%s:%s" % (dev["ip"], dev["port"]), _[1]), resp=resp, dev=dev)
        elif stage == "look4LoginPage":
            pass
        elif not stage:
            if soup.find('meta', attrs={'http-equiv': 'refresh'}):
                return verify(dev, "look4LoginPage", soup.find('meta', attrs={'http-equiv': 'refresh'})['content'].partition('=')[2])
            else:
                logger.info("fail to identify device type after trying all patterns")
    elif resp.status_code == 404:
        logger.warning("fail to identify type for %s due to 404 response\n" % url)
        return False
    elif resp.status_code == 595:
        logger.warning("device %s: failed to establish TCP connection\n" % url)
        return False
    elif resp.status_code == 301 or resp.status_code == 302:
        raise Exception("redirect should be automatically handled but not. source:%s, destiny:%s\n" % (dev["ip"], resp.url))
    else:
        logger.warning("unexpected status code status for ip %s\n" % url)
        dev["test"] = 1
        return False
    if not search4type(resp):
        logger.warning("%s: didnot find dev type after trying all devices\n" % url)
        return False

if __name__ == "__main__":
    a = {"ip": "198.82.172.46", "port": "80"}
    verify(a)
    print(a)

# fixme:
# "axis" "loginUrlPattern" wrong pattern(about backslash)
# pass IQinVision: verify({"ip": "128.112.184.213","port": "80"})
# pass JVC: verify({"ip": "124.219.170.104","port": "81"})
# pass Stardot: verify({"ip": "62.213.36.28", "port": "80"})
# pass basler: verify({"ip": "134.60.38.35", "port": "80"}) not pass: verify({"ip": "198.82.172.46", "port": "80"})
