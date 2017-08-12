# -*- coding:utf-8 -*-
from tornado import ioloop, web, websocket
import json
import logging
import glob
import os
from core.utils import device_store, config_store, extra_store, set_config, Scan

global scan_thread
dev_logger = logging.getLogger("devReport")
web_logger = logging.getLogger("webLog")


def make_logger(ws, name):
    class LogInfoHandler(logging.Handler):
        def emit(self, record):
            try:
                if name != "devReport":
                    ws.write_message({"level": record.levelname, "message": record.getMessage()})
            except websocket.WebSocketClosedError:
                pass

    logger = logging.getLogger(name)
    logger.addHandler(LogInfoHandler())
    logger.setLevel(logging.DEBUG)
    return logger


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
        page = int(self.get_arguments("page")[0] if self.get_arguments("page") else 1)
        size = int(self.get_arguments("size")[0] if self.get_arguments("size") else 20)
        ret = []
        for _ in glob.glob("poc/*.py")[(page-1)*size:page*size]:
            if _ == "poc\__init__.py":
                continue
            try:
                _config = __import__(os.path.splitext(_)[0].replace("\\", "."), fromlist=[""]).config
                assert type(_config) == dict
            except Exception as err:
                _config = {}
                print("import %s error:%s" % (_, err))
            ret.append(dict({
                "name": os.path.basename(_),
                "content": open(_, "r", encoding="utf-8").read()
            }, **_config))
        self.write({
            "pocs": ret,
            "total": len(glob.glob("poc/*.py"))
        })


class DeviceGetter(BaseRequest):
    def get(self):
        page = int(self.get_arguments("page")[0] if self.get_arguments("page") else 1)
        size = int(self.get_arguments("size")[0] if self.get_arguments("size") else 20)
        devices = [device_store.hgetall(_) for _ in device_store.keys("*")]
        self.write({
            "total": len(devices),
            "devices": devices[(page-1)*size:page*size]
        })


class ConfigHandler(BaseRequest):
    def get(self):
        fields = self.get_argument("fields").split(",")
        _ = {}
        if "selected_poc" in fields:
            _["selected_poc"] = config_store.get("selected_poc")
        if "zoomeye_queries" in fields:
            _["zoomeye_queries"] = list(config_store.smembers("zoomeye_queries"))
        if "ip_ranges" in fields:
            _["ip_ranges"] = [json.loads(_) for _ in config_store.smembers("ip_ranges")]
        self.write(_)

    def post(self):
        try:
            config = json.loads(self.request.body.decode('utf-8'))
        except json.decoder.JSONDecodeError:
            self.set_status(400)
            self.finish("fail to parse json")
            return
        try:
            set_config(config)
        except AssertionError as err:
            self.set_status(400)
            self.finish(str(err))
            return
        except ValueError:
            self.set_status(400)
            self.finish("Ip address not valid")

    def delete(self):
        config_store.flushdb()
        self.write({"code": 200, "message": "success"})


class ExtraHandler(BaseRequest):
    def get(self):
        fields = self.get_argument("fields").split(",")
        self.write({_: json.loads(extra_store.get(_)) for _ in fields if extra_store.get(_)})

    def post(self):
        try:
            extra = json.loads(self.request.body.decode('utf-8'))
        except json.decoder.JSONDecodeError:
            self.set_status(400)
            self.finish("fail to parse json")
            return
        for _ in extra.keys():
            extra_store.set(_, json.dumps(extra[_]))


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
    def get(self, action):
        global scan_thread
        if action == "start":
            if not config_store.get("selected_poc"):
                self.set_status(400)
                self.finish("Poc not selected!")
                return
            if not config_store.smembers("zoomeye_queries") and not config_store.smembers("ip_ranges"):
                self.set_status(400)
                self.finish("Lack ip source")
            scan_thread = Scan()
            scan_thread.start()
        elif action == "pause":
            scan_thread.pause()
            self.write({"code": 200, "message": "success"})
        elif action == "stop":
            scan_thread.pause()
            self.write({"code": 200, "message": "success"})

    
class LogInfo(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("logInfo open")
        make_logger(self, "webLog")

    def on_close(self):
        scan_thread.pause()


class DevReport(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("devReport open")
        make_logger(self, "devReport")

    def on_close(self):
        scan_thread.pause()


def serve_forever(port):
    application = web.Application(
        [
            (r"/", IndexHandler),
            (r"/poc", PocGetter),
            (r"/poc/(?P<name>.*)", PocHandler),
            (r"/devices", DeviceGetter),
            (r"/config", ConfigHandler),
            (r"/style", ExtraHandler),
            (r"/action/(?P<action>.*)", ScanHandler),
            (r"/ws/log", LogInfo),
            (r"/ws/dev", DevReport)
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
