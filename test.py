from core.utils import zoom_iter
from poc.iotScanner import verify

if __name__ == "__main__":
    i = 0
    m = []
    n = []
    for dev in zoom_iter("Grandstream"):
        i += 1
        verify(dev)
        if "device_type" not in dev:
            m.append(dev)
        if "admin" not in dev:
            n.append(dev)
        if i == 20:
            break
    print(m)
    if len(n) > 18:
        print(n)
        raise Exception

# 测试：
# 20条数据，只保证能检测出设备类型，
# 已通过测试
# mobotix IQinVision JVC Brickcom GeoVision Grandstream
# fixme:
# 1. zoomeye查询字符串不准确，查到的设备不是这个类型的，能不能根据模式json生成查询字符串？
# 2. 模式json不准确
