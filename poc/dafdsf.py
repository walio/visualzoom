import requests
import time
import logging
logger = logging.getLogger("webLog")
config={
    "device_type":"device_type test",
    "zoomeye_query":"zoomeye_query test"
}
def _verify(dev):
    if requests.get(dev["ip_addr"]).status_code == 200:
        time.sleep(10)
        logger.info("passed verify test")
        return True
    else:
        time.sleep(10)
        logger.info("not pass verify test")
        return False
