from core.utils import zoomeye_generator
from poc.iotScanner import verify
import logging
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    i = 0
    m = []
    n = []
    for dev in zoomeye_generator("SAMSUNG TECHWIN NVR"):
        i += 1
        verify(dev)
        if "device_type" not in dev:
            m.append(dev)
        if "admin" in dev:
            print(dev)
            break
        if i == 100:
            break
    print(m)
    if len(n) > 15:
        print(n)
        raise Exception('too little pass get')

# 测试：
# 每种设备取20条数据，只保证能检测出设备类型，
# 已通过测试
# mobotix IQinVision JVC Brickcom GeoVision Grandstream
# fixme:
# 1. zoomeye查询字符串不准确，查到的设备不是这个类型的，能不能根据模式json生成查询字符串？
# 2. 模式json不准确
# ATCi:
# startdot: identification not correct
# Toshiba eStudio: no result in zoomeye
# Ubiquiti:


# magic words
# app:Ubiquiti EdgeRouter router httpd
# app:ACTi webcam httpd