from flask import Flask
from flask_socketio import SocketIO, emit
from scantools import get_dev_list, _verify
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@socketio.on("init")
def init(message):
    ip_list = get_dev_list()
    global vfilter
    vfilter = filter(_verify, ip_list)
    emit("nextInClient", "trigger")


@socketio.on("nextInServer")
def handle_message(message):
    try:
        emit("ipVul", next(vfilter))
        emit("nextInClient", "trigger")
        # for test
        # emit("finished", "trigger")
    except StopIteration:
        emit("finished", "trigger")


if __name__ == '__main__':
    socketio.run(app, debug=True)

