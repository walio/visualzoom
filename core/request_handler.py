# -*- coding:utf-8 -*-
from tornado import web, websocket
from threading import Thread
import json
import logging
import sys
from core.poc import mode_verify, mode_attack
from core.utils import get_dev_list, restore, insert_device
from core import cursor, store

global logger

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


class BaseWebSocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        logger.debug("%s WebSocket opened" % self.__class__.__name__)

    def on_close(self):
        logger.debug("%s WebSocket closed" % self.__class__.__name__)


class ScanDev(BaseWebSocketHandler):
    isStopped = False

    def open(self):
        logger.debug("scanDev WebSocket opened")
        self.set_nodelay(True)
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
                except Exception:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    store.execute("insert into exception values (?,?,?,?)", (
                       str(exc_type), str(exc_obj), exc_tb.tb_frame.f_code.co_filename, str(exc_tb.tb_lineno)))
                    logger.debug(u"扫描时发生异常，信息已存入数据库")
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
        logger.debug("restore finish")


class LogInfo(BaseWebSocketHandler):

    def open(self):
        logger.debug("logInfo WebSocket opened")
        logger = make_logger(self)
        
    def on_message(self, message):
        pass


application = web.Application(
    [
        (r"/", TestHandler),
        (r"/scanDev", ScanDev),
        (r"/restore", Restore),
        (r"/logInfo", LogInfo),
        (r"/getStat", GetStat),
    ],
    static_path="web/static",
    template_path="web/",
    debug=True,
)

