import logging
import telnetlib
import time
import json
logger = logging.getLogger("webLog")
config={
    "device_type":"device_type test",
    "zoomeye_query":"zoomeye_query test"
}
with open("pass.cfg", "r") as f:
    tokens = json.loads(f.read())
def verify(dev):
    tn = telnetlib.Telnet()
    try:
        tn.open(dev["ip"],port=23)
    except:
        logging.warning('%s网络连接失败'%dev["ip"])
        return False
    for token in tokens:
        username = token['user']
        password = token['pass']
        tn.read_until(b'login: ',timeout=10)
        tn.write(username.encode('ascii') + b'\n')
        tn.read_until(b'Password: ',timeout=10)
        tn.write(password.encode('ascii') + b'\n')
        time.sleep(2)
        command_result = tn.read_very_eager().decode('ascii')
        if 'incorrect' not in command_result.lower():
            dev["admin"] = username
            dev["pass"] = password
            logging.warning('地址：%s，用户名：%s，密码：%s登录成功'%(dev["ip"], username,password))
            return True
        else:
            logging.warning('地址：%s，用户名：%s，密码：%s登录失败'%(dev["ip"], username,password))
    logging.warning('%s登录失败，用户名或密码错误'%dev["ip"])
    return False
