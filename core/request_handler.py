# -*- coding:utf-8 -*-
from tornado import ioloop, web, websocket
from threading import Thread
import json
import logging
import glob
import os
from core.poc import mode_verify, mode_attack
from core.utils import get_dev_list, restore
from core import cursor, store

global logger


def insert_device(device):
    store.execute("INSERT INTO devices VALUES (?,?,?,?,?,?,?,?,?)",
                  (device.get("ip_addr"), device.get("lat"), device.get("lon"), device.get("addr"), device.get("level"),
                   device.get("wpapsk"), device.get("ssid"), device.get("user"), device.get("passwd")))
    store.commit()


def make_logger(ws):
    fmt_str = '%(asctime)s - %(message)s'
    formatter = logging.Formatter(fmt_str)
    logging.basicConfig(level=logging.INFO, format=formatter)
    logger = logging.getLogger("scantools")

    class LogInfoHandler(logging.Handler):
        def emit(self, record):
            ws.write_message(record.getMessage() + "\n")

    lg = LogInfoHandler()
    lg.setLevel(logging.INFO)
    logger.addHandler(lg)

    logger.setLevel(logging.INFO)
    return logger


class TestHandler(web.RequestHandler):
    def get(self):
        self.render('index.html')


class ViewPoc(web.RequestHandler):
    def get(self):
        page = int(self.get_arguments("page")[0])
        pocs = [
            {"name": os.path.basename(_), "content": open(_, "r", encoding="utf-8").read(), "dev_type": "Netwave"}
            for _ in glob.glob("poc/*.py")
        ][(page-1)*20:page*20]
        self.write({
            "pocs": pocs,
            "total": len(pocs)
        })


class PocHandler(web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')


    def options(self, name):
        self.set_header('Access-Control-Allow-Origin', "http://www.xxx.com")
        self.set_header('Access-Control-Allow-Headers', "k1,k2")
        self.set_header('Access-Control-Allow-Methods', "PUT,DELETE")
        self.set_header('Access-Control-Max-Age', 10)    


    def put(self, name):
        req = json.loads(self.request.body.decode('utf-8'))
        with open("poc/%s" % req["name"], "w") as f:
            f.write(req["content"])
        self.write({"code": 200, "message": "success"})

    def delete(self, name):
        os.remove("poc/%s" % name)
        self.write({"code": 200, "message": "success"})

    def post(self, name):
        req = json.loads(self.request.body.decode('utf-8'))
        filename = "poc/%s" % req["name"]
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
        print("%s WebSocket opened" % self.__class__.__name__)

    def on_close(self):
        print("%s WebSocket closed" % self.__class__.__name__)


class ScanDev(BaseWebSocketHandler):
    isStopped = False

    def open(self):
        print("scanDev WebSocket opened")
        self.set_nodelay(True)
        global logger
        self.target_iter = filter(mode_attack(logger), filter(mode_verify(logger), get_dev_list(logger)))

    def on_message(self, message):
        if message == "scanNext":
            def scan():
                try:
                    dev = next(self.target_iter)
                    self.write_message(json.dumps(dev))
                    insert_device(dev)
                except StopIteration:
                    self.write_message("finishScan")
                    # except Exception:
                    #   exc_type, exc_obj, exc_tb = sys.exc_info()
                    #  store.execute("insert into exception values (?,?,?,?)", (
                    #     str(exc_type), str(exc_obj), exc_tb.tb_frame.f_code.co_filename, str(exc_tb.tb_lineno)))
                    # print("扫描时发生异常，信息已存入数据库")
                    self.write_message(None)

            scant = Thread(target=scan)
            scant.start()
        elif message == "stop":
            self.isStopped = True


class GetStat(BaseWebSocketHandler):
    def on_message(self, message):
        cursor.execute("SELECT count(*) FROM devices WHERE level=0")
        poss = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM devices WHERE level=1")
        vulner = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM devices WHERE level=2")
        frag = cursor.fetchone()[0]
        self.write_message(json.dumps({
            "possible": poss,
            "vulnerable": vulner,
            "fragile": frag,
        }))


class Restore(BaseWebSocketHandler):
    def on_message(self, message):
        for dev in restore():
            self.write_message(json.dumps(dev))
        self.write_message("restoreFinish")
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
            (r"/", TestHandler),
            (r"/list", ViewPoc),
            (r"/poc/(?P<name>.*)", PocHandler),
            (r"/scanDev", ScanDev),
            (r"/restore", Restore),
            (r"/logInfo", LogInfo),
            (r"/getStat", GetStat),
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