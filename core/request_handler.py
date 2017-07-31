# -*- coding:utf-8 -*-
from tornado import ioloop, web, websocket
from threading import Thread
import json
import logging
import glob
import os
import itertools
import redis
import pickle
from core.utils import restore, get_dev_list, device_store, info_store
poc_store = redis.StrictRedis("127.0.0.1", 6379, 2, decode_responses=True)
global isStopped
isStopped = False


def make_logger(ws):
    fmt_str = '%(asctime)s - %(message)s'
    formatter = logging.Formatter(fmt_str)
    logging.basicConfig(level=logging.INFO, format=formatter)
    logger = logging.getLogger("root")

    class LogInfoHandler(logging.Handler):
        def emit(self, record):
            ws.write_message(record.getMessage() + "\n")

    lg = LogInfoHandler()
    lg.setLevel(logging.INFO)
    logger.addHandler(lg)

    logger.setLevel(logging.INFO)
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


class BaseHandler(web.RequestHandler):
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


class ConfigHandler(BaseHandler):
    def get(self):
        self.write(pickle.loads(info_store.get("config")))

    def post(self):
        config = json.loads(self.request.body.decode('utf-8'))
        info_store.set("config", pickle.dumps(config))
        global target_iter
        target_iter = make_target_iter(config)
        self.write({"code": 200, "message": "success"})


class PocGetter(BaseHandler):
        
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


class PocHandler(BaseHandler):

    def get(self, name):
        with open("poc/%s" % name, "r", encoding="utf-8") as f:
            self.write({"code": 200, "content": f.read()})

    def put(self, name):
        req = json.loads(self.request.body.decode('utf-8'))
        with open("poc/%s" % name, "w") as f:
            f.write(req["content"])
        self.write({"code": 200, "message": "success"})

    def delete(self, name):
        os.remove("poc/%s" % name)
        self.write({"code": 200, "message": "success"})

    def post(self, name):
        req = json.loads(self.request.body.decode('utf-8'))
        filename = "poc/%s" % name
        if os.path.exists(filename):
            self.set_status(409)
            self.finish("Conflict")
        else:
            with open(filename, "w") as f:
                f.write(req["content"])
            self.write({"code": 200, "message": "success"})


class BaseWebSocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("%s WebSocket connected" % self.__class__.__name__)
        self.set_nodelay(True)

    def on_close(self):
        print("%s WebSocket disconnected" % self.__class__.__name__)


class ScanDev(BaseWebSocketHandler):

    def on_message(self, message):
        if message == "start":
            global target_iter
            global isStopped

            def scan():
                while True:
                    if not isStopped:
                        try:
                            dev = next(target_iter)
                            self.write_message(json.dumps(dev))
                            device_store.hmset(dev["ip_addr"], dev)
                        except StopIteration:
                            self.write_message("Scanfinished")
                        except Exception:
                            print("exception occur during scan")
                    else:
                        self.write_message("stopScanSuccess")
                    # except Exception:
                    #   exc_type, exc_obj, exc_tb = sys.exc_info()
                    #  store.execute("insert into exception values (?,?,?,?)", (
                    #     str(exc_type), str(exc_obj), exc_tb.tb_frame.f_code.co_filename, str(exc_tb.tb_lineno)))
                    # print("扫描时发生异常，信息已存入数据库")
                    # self.write_message(None)

            scant = Thread(target=scan)
            scant.start()
        elif message == "stop" or message == "pause":
            print("stopped")
            global isStopped
            isStopped = True


class Restore(BaseWebSocketHandler):
    def on_message(self, message):
        for dev in restore():
            self.write_message(json.dumps(dev))
        self.write_message("restoreFinished")
        print("restore finish")


class LogInfo(BaseWebSocketHandler):
    def open(self):
        print("logInfo WebSocket opened")
        global logger
        logger = make_logger(self)

    def on_message(self, message):
        pass


def serve_forever():
    application = web.Application(
        [
            (r"/", IndexHandler),
            (r"/list", PocGetter),
            (r"/poc/(?P<name>.*)", PocHandler),
            (r"/config", ConfigHandler),
            (r"/scanDev", ScanDev),
            (r"/restore", Restore),
            (r"/logInfo", LogInfo),
        ],
        static_path="web/static",
        template_path="web/",
        debug=True,
    )
    application.listen(80)
    print('Server listening at http://localhost:80/')
    ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    serve_forever()
