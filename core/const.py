import logging
from flask import Flask
from flask_socketio import SocketIO
import sqlite3
import os
app = Flask(__name__, static_url_path="")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
store = sqlite3.connect("output/devices.db", check_same_thread=False)
store.execute("CREATE TABLE IF NOT EXISTS devices (ip_addr VARCHAR(20), lat FLOAT, lon FLOAT, addr VARCHAR(10), "
              "level INT, wpapsk VARCHAR(10), ssid VARCHAR(20), user VARCHAR(20), passwd VARCHAR(20))")
store.execute("CREATE TABLE IF NOT EXISTS exception (type varchar(20), message varchar(100),"
              "file varchar(20), line int)")
store.execute("CREATE TABLE IF NOT EXISTS page (page int)")
# debug: system error
# info: info
# warning: information leak
# error: final result
# critical: markpoint
fmt_str = '%(asctime)s - %(message)s'
formatter = logging.Formatter(fmt_str)
logging.basicConfig(level=logging.DEBUG, format=fmt_str)
logger = logging.getLogger("scantools")

class LogInfoHandler(logging.Handler):
    def emit(self, record):
        socketio.emit("logInfo", record.getMessage()+"\n")


class ReportNextHandler(logging.Handler):
    def emit(self, record):
        socketio.emit("reportNext", record.getMessage())


lg = LogInfoHandler()
lg.setLevel(logging.INFO)
rn = ReportNextHandler()
rn.setLevel(logging.CRITICAL)
logger.addHandler(lg)
logger.addHandler(rn)
