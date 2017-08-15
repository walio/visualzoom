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


def compose_url(ip_addr, protocol, url=None):
    if not url:
        return "%s://%s/" % (protocol, ip_addr)
    elif url.startswith("http") or url.startswith("https"):
        return url
    elif url.startswith("/"):
        return "%s://%s%s" % (protocol, ip_addr, url)


def check_login(dev, url, resp):
    """
    :param url: string(login page)
    :param resp: <class 'requests.models.Response'> (used to extract data if needed)
    :param type_name: string(type of device)
    :return: bool
    """
    auth = device_patterns[dev["device_type"]]["auth"]
    logger.debug("在%s页面检查登录" % url)
    if auth[0] == "basic":
        if not auth[1]:
            if requests.get(url, verify=False).status_code == 200:
                logger.info("设备%s，类型为%s，使用了默认用户名密码\n" % (dev["ip"], dev["device_type"]))
                dev["admin"] = device_patterns[dev["device_type"]]["pass"][0]
                dev["pass"] = device_patterns[dev["device_type"]]["pass"][1]
                dev["login_url"] = url
                return True
            else:
                logger.info("设备%s, 类型为%s，已经更改了默认用户名密码\n" % (dev["ip"], dev["device_type"]))
                return False
        else:
            try:
                if requests.get(url, headers={
                    "Authorization": "Basic %s" % base64.b64encode(auth[1].encode(encoding='gb2312')).decode('utf-8')
                }, verify=False, timeout=60).status_code == 200:
                    logger.info("设备%s，类型为%s，使用了默认用户名密码\n" % (dev["ip"], dev["device_type"]))
                    dev["admin"] = device_patterns[dev["device_type"]]["pass"][0]
                    dev["pass"] = device_patterns[dev["device_type"]]["pass"][1]
                    dev["login_url"] = url
                    return True
                else:
                    logger.warning("设备%s, 类型为%s，已经更改了默认用户名密码\n" % (dev["ip"], dev["device_type"]))
                    return False
            except requests.exceptions.ConnectionError:
                logger.warning("设备%s, 类型为%s，已经更改了默认用户名密码\n" % (dev["ip"], dev["device_type"]))
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
            logger.error("无法连接\n")
            return False
        if auth[3] == "body":
            if auth[4] == "regex":
                if re.search(auth[5], resp_.text):
                    logger.info("设备%s，类型为%s，使用了默认用户名密码\n" % (dev["ip"], dev["device_type"]))
                    dev["admin"] = device_patterns[dev["device_type"]]["pass"][0]
                    dev["pass"] = device_patterns[dev["device_type"]]["pass"][1]
                    dev["login_url"] = url
                    return True
                else:
                    logger.warning("设备%s, 类型为%s，已经更改了默认用户名密码\n" % (dev["ip"], dev["device_type"]))
                    return False
            elif auth[4] == "substr":
                if auth[5] in resp_.text:
                    logger.info("设备%s，类型为%s，使用了默认用户名密码\n" % (dev["ip"], dev["device_type"]))
                    dev["admin"] = device_patterns[dev["device_type"]]["pass"][0]
                    dev["pass"] = device_patterns[dev["device_type"]]["pass"][1]
                    dev["login_url"] = url
                    return True
                else:
                    logger.warning("设备%s, 类型为%s，已经更改了默认用户名密码\n" % (dev["ip"], dev["device_type"]))
                    return False
            elif auth[4] == "!substr":
                if not auth[5] in resp_.text and resp_.status_code == 200:
                    logger.info("设备%s，类型为%s，使用了默认用户名密码\n" % (dev["ip"], dev["device_type"]))
                    dev["admin"] = device_patterns[dev["device_type"]]["pass"][0]
                    dev["pass"] = device_patterns[dev["device_type"]]["pass"][1]
                    dev["login_url"] = url
                    return True
                else:
                    logger.info("设备%s, 类型为%s，已经更改了默认用户名密码\n" % (dev["ip"], dev["device_type"]))
                    return False
        raise Exception("auth[1] of type form auth has another type")
    elif auth[0] == "expect200":
        if requests.get(url, verify=False).status_code == 200:
            logger.info("设备%s，类型为%s无需任何用户名密码\n" % (dev["ip"], dev["device_type"]))
            dev["admin"] = device_patterns[dev["device_type"]]["pass"][0]
            dev["pass"] = device_patterns[dev["device_type"]]["pass"][1]
            dev["login_url"] = url
            return True
        else:
            logger.debug("设备%s, 类型为%s，已经更改了默认用户名密码\n" % (dev["ip"], dev["device_type"]))
    else:
        resp_ = requests.get(url, verify=False)
        if resp_.status_code == 301 or resp_.status_code == 302:
            logger.debug("301 and 302 should be automatically handled by requests but not")
        else:
            logger.warning("设备%s: 未处理HTTP状态码%d\n" % (url, resp_.status_code))
        raise Exception("unknown auth type: %s" % auth[0])


def check_init_login():
    pass


# todo: use beautiful soup to handle all redirect
def verify(dev, stage="", uri=None, device_type=""):
    logger.info("开始检测设备%s:%s是否存在默认密码" % (dev["ip"], dev["port"]))
    if device_type not in device_patterns.keys():
        logger.error("设备类型未指定，自定识别设备类型")
        type_name = ""
    else:
        type_name = device_type
    url = compose_url("%s:%s" % (dev["ip"], dev["port"]), dev["protocol"], uri)
    if stage == "initialClickLoginPage":
        return check_init_login()
    try:
        resp = requests.get(url, stream=True, verify=False)
        if resp.headers.get('Content-Type') and ("audio" in resp.headers["Content-Type"] or "video" in resp.headers["Content-Type"]):
            logger.error('无法识别设备%s的类型由于返回了视频流\n' % url)
            return False
        resp = requests.get(url, verify=False, timeout=60)
    except requests.exceptions.ConnectionError:
        logger.error("无法连接到%s\n" % url)
        return False
    except urllib3.exceptions.LocationValueError:
        logger.error("无法连接到%s\n" % url)
        return False
    except requests.exceptions.ReadTimeout:
        logger.error("无法连接到%s\n" % url)
        return False
    soup = BeautifulSoup(resp.text.lower(),  "html5lib")
    logger.debug("got status=%d for %s" % (resp.status_code, resp.url))
    if (resp.status_code == 401) or (resp.status_code == 403):
        type_name = type_name or search4type(resp)
        if not type_name:
            logger.info("无法识别设备类型或设备类型未收录\n")
            return False
        logger.debug("设备类型为%s" % type_name)
        dev["device_type"] = type_name
        return True if check_login(url=compose_url("%s:%s" % (dev["ip"], dev["port"]), dev["protocol"], resp.url), resp=resp, dev=dev) else False
    elif resp.status_code == 200:
        type_name = type_name or search4type(resp)
        if type_name:
            logger.debug("设备类型为%s\n" % type_name)
            dev["device_type"] = type_name
            if "loginUrlPattern" in device_patterns[type_name]:
                _ = re.search(device_patterns[type_name]["loginUrlPattern"], resp.text)
                return check_login(url=compose_url("%s:%s" % (dev["ip"], dev["port"]), dev["protocol"], _.group()), resp=resp, dev=dev) if _ else False
            else:
                _ = device_patterns[type_name]["nextUrl"]
                if _[0] == "string":
                    for _url in _[1:]:
                        if not _url:
                            if check_login(url=compose_url("%s:%s" % (dev["ip"], dev["port"]), dev["protocol"]), resp=resp, dev=dev):
                                return True
                        else:
                            if check_login(url=compose_url("%s:%s" % (dev["ip"], dev["port"]), dev["protocol"], _url), resp=resp, dev=dev):
                                return True
                    return False
        elif stage == "look4LoginPage":
            pass
        elif not stage:
            if soup.find('meta', attrs={'http-equiv': 'refresh'}):
                return verify(dev, "look4LoginPage", soup.find('meta', attrs={'http-equiv': 'refresh'})['content'].partition('=')[2].strip())
            else:
                logger.info("无法识别设备类型或设备类型未收录")
    elif resp.status_code == 404:
        logger.warning("无法识别设备类型%s由于返回了404响应\n" % url)
        return False
    elif resp.status_code == 595:
        logger.warning("设备%s无法建立TCP连接\n" % url)
        return False
    elif resp.status_code == 301 or resp.status_code == 302:
        raise Exception("redirect should be automatically handled but not. source:%s, destiny:%s\n" % (dev["ip"], resp.url))
    else:
        logger.warning("未处理的HTTP状态码%s\n" % url)
        return False
    if not search4type(resp):
        logger.warning("无法识别设备%s的类型\n" % url)
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
