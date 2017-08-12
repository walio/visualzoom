import requests
import time
import logging
logger = logging.getLogger("webLog")
config={
    "device_type":"device_type test",
    "zoomeye_query":"zoomeye_query test"
}
def verify(dev):
    if requests.get("http://%s:%s" % (dev["ip"],dev["port"])).status_code == 200:
        time.sleep(10)
        logger.info("passed verify test")
        return True
    else:
        time.sleep(10)
        logger.info("not pass verify test")
        return False
