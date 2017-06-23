import logging
from flask_socketio import emit

fmt_str = '%(asctime)s - %(message)s'
formatter = logging.Formatter(fmt_str)
logging.basicConfig(level=logging.INFO, format=fmt_str)

logger = logging.getLogger("scantools")

class SocketIOHandler(logging.Handler):
    def emit(self, record):
        emit("logInfo", record.getMessage())

sio = SocketIOHandler()
logger.addHandler(sio)
