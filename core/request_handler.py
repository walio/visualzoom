# -*- coding:utf-8 -*-
from tornado import ioloop, web, websocket
from threading import Thread
import json
import logging
import glob
import os
import itertools
import redis
from core.utils import restore, get_dev_list, device_store, info_store
poc_store = redis.StrictRedis("127.0.0.1", 6379, 2, decode_responses=True)


def make_logger(ws, name):
    fmt_str = '%(asctime)s - %(message)s'
    formatter = logging.Formatter(fmt_str)
    logging.basicConfig(level=logging.INFO, format=formatter)
    logger = logging.getLogger(name)

    class LogInfoHandler(logging.Handler):
        def emit(self, record):
            ws.write_message(record.getMessage())

    lg = LogInfoHandler()
    lg.setLevel(logging.DEBUG)
    logger.addHandler(lg)

    logger.setLevel(logging.DEBUG)
    return logger


def make_ip_iter(start, end):
    # todo
    yield start
    yield end


def make_target_iter(config):
    ip_source = iter([])
    for _ in config["zoomQueries"]:
        ip_source = itertools.chain(ip_source, get_dev_list(_))
    for _ in config["ipList"]:
        ip_source = itertools.chain(ip_source, make_ip_iter(_["start"], _["end"]))

    _poc = __import__("poc.%s" % os.path.splitext(config["selectedPoc"])[0], fromlist=[""])
    target_iter = filter(_poc._verify, ip_source)
    return target_iter


class BaseRequest(web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

    def options(self, *a, **ka):
        self.set_header('Access-Control-Allow-Origin', "*")
        self.set_header('Access-Control-Allow-Headers', "content-type")
        self.set_header('Access-Control-Allow-Methods', "PUT,DELETE")
        self.set_header('Access-Control-Max-Age', 10)


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render('index.html')


class PocGetter(BaseRequest):
    def get(self):
        # todo: page index of config
        page = int(self.get_arguments("page")[0] if self.get_arguments("page") else 1)
        ret = []
        for _ in glob.glob("poc\*.py")[(page-1)*20:page*20]:
            if _ == "poc\__init__.py":
                continue
            try:
                _module = __import__(os.path.splitext(_)[0].replace("\\", "."), fromlist=[""])
            except:
                _module = None
                print("import %s error" % _)
            ret.append({
                "name": os.path.basename(_),
                "author": getattr(_module, "__author__", None),
                "devtype": getattr(_module, "__devtype__", None),
                "zoomQuery": getattr(_module, "__query__", None),
                "content": open(_, "r", encoding="utf-8").read()
            })
        self.write({
            "pocs": ret,
            "total": len(glob.glob("poc/*.py"))
        })


class ConfigHandler(BaseRequest):
    def get(self):
        fields = self.get_argument("fields").split(",")
        self.write({_: eval(info_store.get(_)) for _ in fields if info_store.get(_)})

    def put(self):
        config = json.loads(self.request.body.decode('utf-8'))
        for (k,v) in config.items():
            info_store.set(k, repr(v))
        self.write({"code": 200, "message": "success"})


class PocHandler(BaseRequest):
    def get(self, name):
        try:
            with open("poc/%s" % name, "r", encoding="utf-8") as f:
                self.write(f.read())
        except FileNotFoundError:
            self.set_status(404)
            self.finish("Poc File Not Found")

    def put(self, name):
        try:
            with open("poc/%s" % name, "w", encoding="utf-8") as f:
                f.write(self.request.body.decode('utf-8'))
                self.write({"code": 200, "message": "success"})
        except FileNotFoundError:
            self.set_status(404)
            self.finish("Poc File Not Found")

    def delete(self, name):
        try:
            os.remove("poc/%s" % name)
            self.write({"code": 200, "message": "success"})
        except FileNotFoundError:
            self.set_status(404)
            self.finish("Poc File Not Found")

    def post(self, name):
        if os.path.exists("poc/%s" % name):
            self.set_status(409)
            self.finish("Conflict")
        else:
            with open("poc/%s" % name, "w") as f:
                f.write(self.request.body.decode('utf-8'))
            self.write({"code": 200, "message": "success"})


class ScanHandler(BaseRequest):
    isStopped = False

    def get(self, action):
        logger = logging.getLogger("devReport")
        if action == "start":
            target_iter = make_target_iter({
                "zoomQueries": eval(info_store.get("zoomQueries") or "[]"),
                "ipList": eval(info_store.get("ipList") or "[]"),
                "selectedPoc": eval(info_store.get("selectedPoc") or "''"),
            })

            def scan():
                while True:
                    if not self.isStopped:
                        try:
                            dev = next(target_iter)
                            logger.info(json.dumps(dev))
                            device_store.hmset(dev["ip_addr"], dev)
                        except StopIteration:
                            logger.info("scanFinished")
                        #except Exception:
                         #   print("exception occur during scan")
                    else:
                        logger.info("stopScanSuccess")
                    # except Exception:
                    #   exc_type, exc_obj, exc_tb = sys.exc_info()
                    #  store.execute("insert into exception values (?,?,?,?)", (
                    #     str(exc_type), str(exc_obj), exc_tb.tb_frame.f_code.co_filename, str(exc_tb.tb_lineno)))
                    # print("扫描时发生异常，信息已存入数据库")
                    # self.write_message(None)
            scant = Thread(target=scan)
            self.write({"code": 200, "message": "success"})
            scant.start()
        elif action == "pause":
            self.isStopped = True
            self.write({"code": 200, "message": "success"})
        elif action == "stop":
            self.isStopped = True
            self.write({"code": 200, "message": "success"})
        elif action == "restore":
            fff = logging.getLogger("webLog")
            for dev in restore():
                logger.info(json.dumps(dev))
                fff.info(json.dumps(dev))
            logger.info("restoreFinished")


class DeviceHandler(BaseRequest):
    def get(self):
        page = int(self.get_arguments("page")[0] if self.get_arguments("page") else 1)
        devices = [device_store.hgetall(_) for _ in device_store.keys("*")]
        self.write({
            "total": len(devices),
            "devices": devices[(page-1)*20:page*20]
        })

    
class LogInfo(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("loginfo open")
        make_logger(self, "webLog")


class DevReport(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("devreport open")
        make_logger(self, "devReport")


def serve_forever(port):
    application = web.Application(
        [
            (r"/", IndexHandler),
            (r"/poc", PocGetter),
            (r"/poc/(?P<name>.*)", PocHandler),
            (r"/config", ConfigHandler),
            (r"/action/(?P<action>.*)", ScanHandler),
            (r"/device", DeviceHandler),
            (r"/log", LogInfo),
            (r"/dev", DevReport)
        ],
        static_path="web/static",
        template_path="web/",
        debug=True,
    )
    application.listen(port)
    print('Server listening at http://localhost:%s/' % port)
    ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    serve_forever(80)
