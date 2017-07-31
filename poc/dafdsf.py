import requests
import time
import logging
logger = logging.getLogger("root")
__query__="query test"
__devtype__="test"
def _verify(dev):
    if requests.get(dev["ip_addr"]).status_code == 200:
        time.sleep(10)
        logger.info("passed verify test")
        return True
    else:
        time.sleep(10)
        logger.info("not pass verify test")
        return False

def _attack(dev):
    if requests.get(dev["ip_addr"]).status_code == 200:
        time.sleep(10)
        logger.info("passed attack test")
        return True
    else:
        time.sleep(10)
        logger.info("not pass attack test")
        return False