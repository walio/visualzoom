from core.const import socketio, app
from core.scantools import get_dev_list, _verify, _attack, store
import sys


@app.route('/')
def index():
    return app.send_static_file('index.html')


@socketio.on("init")
def init(data):
    global pipfilter
    pipfilter = get_dev_list()
    global vipfilter
    vipfilter = filter(_verify, pipfilter)
    global fipfilter
    fipfilter = filter(_attack, vipfilter)
    global target_filter
    target_filter = vipfilter


@socketio.on("scanNext")
def scan_next():
    try:
        next(target_filter)
    except StopIteration:
        socketio.emit("finished")
    # except Exception as err:
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     store.execute("insert into exception values (?,?,?,?)", (str(exc_type), str(exc_obj), exc_tb.tb_frame.f_code.co_filename, str(exc_tb.tb_lineno)))
    #     print("扫描时发生异常，信息已存入数据库")
    #     socketio.emit("reportNext", None)


@socketio.on("clear")
def kill(message):
    # todo
    pass


