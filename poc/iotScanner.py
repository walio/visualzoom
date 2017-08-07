# -*- coding:utf-8 -*-
import json
import requests
import logging
import re
import base64
from bs4 import BeautifulSoup
with open("core/devices.cfg", "r") as f:
    dev_types = json.load(f)
http_port = 80
logger = logging.getLogger("root")
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
    soup = BeautifulSoup(resp.text.lower(), "html.parser")

    for type_name, type_pattern in dev_types.items():
        tomatch_locate = type_pattern["devTypePattern"][0]
        if tomatch_locate[0] == "header":
            tomatch = resp.headers.get(tomatch_locate[1]) or ""
        elif tomatch_locate[0] == "body":
            if tomatch_locate[1] == "":
                tomatch = resp.text
            else:
                tomatch = soup.find(tomatch_locate[1].lower()).get_text()
        tomatch_pattern = type_pattern["devTypePattern"][1]
        if tomatch_pattern[0] == "==":
            if tomatch == tomatch_pattern[1].lower():
                return type_name
        elif tomatch_pattern[0].startswith("regex"):
            has_diff = False
            for _ in type_pattern["devTypePattern"][1][1:]:
                if not re.search(_, tomatch):
                    has_diff = True
                    break
            if not has_diff:
                return type_name
        elif tomatch_pattern[0] == "substr":
            if tomatch_pattern[1] in tomatch:
                return type_name
    return ""


def compose_url(ip_addr, url=None):
    if not url:
        return "http://%s/" % ip_addr
    elif url.startswith("http"):
        return url
    elif url.startswith("/"):
        return "http://%s%s" % (ip_addr, url)


def check_login(url, resp, type_name):
    """
    :param url: string(login page)
    :param resp: <class 'requests.models.Response'>
    :param type_name: string(type of device)
    :return: bool
    """
    auth = dev_types[type_name]["auth"]
    logger.debug("checking login on %s" % url)
    if auth[0] == "basic":
        if not auth[1]:
            if requests.get(url, verify=False).status_code == 200:
                logger.info("device %s is of type %s still has default password\n" % (url, type_name))
                return True
            else:
                logger.info("device %s of type %s has changed password\n" % (url, type_name))
                return False
        elif requests.get(url, headers={"Authorization": "Basic %s" % base64.b64encode(auth[1])}, verify=False).status_code == 200:
            logger.info("device %s is of type %s still has default password\n" % (url, type_name))
            return True
        else:
            logger.warning("device %s of type %s has changed password\n" % (url, type_name))
            return False
    elif auth[0] == "form":
        if auth[1].startswith("sub") != ("extractFormData" in dev_types[type_name]):
            raise Exception("lack one of extractFormData and substitute")
        post_data = auth[2]
        if "extractFormData" in dev_types[type_name]:
            extracted_data = []
            for _ in dev_types[type_name]["extractFormData"]:
                extracted_data.append(re.search(_, resp.text).group())
            # substitude $1,$2,$3 and so on to %, and use dev_info["extractedData"] to assign
            post_data = re.sub("\$(\d+)", "%", post_data) % tuple(extracted_data)
        resp_ = requests.get(url, post_data, verify=False)
        if auth[3] == "body":
            if auth[4] == "regex":
                if re.search(auth[5], resp_.text):
                    logger.info("device %s is of type %s still has default password\n" % (url, type_name))
                    return True
                else:
                    logger.warning("device %s of type %s has changed password\n" % (url, type_name))
                    return False
            elif auth[4] == "!substr":
                if auth[5] in resp_.text:
                    logger.info("device %s is of type %s still has default password\n" % (url, type_name))
                    return True
                else:
                    logger.warning("device %s of type %s has changed password\n" % (url, type_name))
                    return False
        logger.critical("auth[1] another type")
        return False
    elif auth[0] == "expect200":
        if requests.get(url, verify=False).status_code == 200:
            logger.info("device %s is of type %s doesnot have any password\n" % (url, type_name))
            return True
        else:
            logger.debug("device %s is of type %s fail to expect 200\n" % (url, type_name))
    else:
        resp_ = requests.get(url, verify=False)
        if resp_.status_code == 301 or resp_.status_code == 302:
            logger.debug("301 and 302 should be automatically handled by requests but not")
        else:
            logger.warning("device %s: unexpected resp code %d\n" % (url, resp_.status_code))
        return False


def check_init_login():
    pass


def check(dev_info, stage="", uri=None):
    """
    :param ip_addr: string(ip:port)
    :param stage: string
    :return: {ip_addr,type_name}(if success) or False(if fail)
    """
    url = compose_url(dev_info["ip_addr"], uri)
    if stage == "initialClickLoginPage":
        return check_init_login()
    resp = requests.get(url, verify=False)
    soup = BeautifulSoup(resp.text.lower(),  "html.parser")
    logger.debug("got status=%d for %s" % (resp.status_code, resp.url))
    if resp.status_code == 301 or resp.status_code == 302:
        raise Exception("redirect should be automatically handled but not. source ip:%s, destiny:%s\n" % (dev_info["ip_addr"], resp.url))
    elif resp.status_code == 401:
        type_name = search4type(resp)
        if not type_name:
            logger.info("cannot find dev type after trying all patterns\n")
            return False
        logger.debug("device type is %s" % type_name)
        dev_info["type_name"] = type_name
        return dev_info if check_login(compose_url(dev_info["ip_addr"], resp.url), resp, type_name) else False
    elif resp.status_code == 200:
        type_name = search4type(resp)
        if type_name:
            logger.debug("devType=%s\n" % type_name)
            dev_info["devType"] = type_name
            if "loginUrlPattern" in dev_types[type_name]:
                _ = re.search(dev_types[type_name]["loginUrlPattern"], resp.text)
                return check_login(compose_url(dev_info["ip_addr"], _.group()), resp, type_name) if _ else False
            else:
                _ = dev_types[type_name]["nextUrl"]
                if _[0] == "string":
                    if not _[1]:
                        return check_login(compose_url(dev_info["ip_addr"]), resp, type_name)
                    else:
                        return check_login(compose_url(dev_info["ip_addr"], _[1]), resp, type_name)
        elif stage == "look4LoginPage":
            pass
        elif not stage:
            if soup.find('meta', attrs={'http-equiv': 'refresh'}):
                return check(dev_info, "look4LoginPage", soup.find('meta', attrs={'http-equiv': 'refresh'})['content'].partition('=')[2])
            else:
                logger.info("cannot find dev type after trying all patterns")
    elif resp.status_code == 404:
        logger.warning("canot find dev type for %s due to 404 response\n" % url)
        return False
    elif resp.status_code == 595:
        logger.warning("device %s: failed to establish TCP connection\n" % url)
        return False
    else:
        logger.warning("unexpected status code $status for ip %s\n" % url)
        return False
    if not search4type(resp):
        logger.warning("%s: didnot find dev type after trying all devices\n" % url)
        return False

if __name__ == "__main__":
    for ip in ["79.98.40.113"]:
        print(check(ip+":80", ""))

# fixme:
# "axis" "loginUrlPattern" wrong pattern(about backslash)
