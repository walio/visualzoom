# -*- coding:utf-8 -*-
from core.const import socketio, app, store, cursor
from core.scantools import get_dev_list, restore
from core.poc import _verify, _attack
import sys


def insert_device(device):
    store.execute("INSERT INTO devices VALUES (?,?,?,?,?,?,?,?,?)",
                  (device.get("ip_addr"), device.get("lat"), device.get("lon"), device.get("addr"), device.get("level"),
                   device.get("wpapsk"), device.get("ssid"), device.get("user"), device.get("passwd")))
    store.commit()


@app.route('/')
def index():
    return app.send_static_file('index.html')


@socketio.on("init")
def init(data):
    global iter_candi
    iter_candi = get_dev_list()
    global iter_vul
    iter_vul = filter(_verify, iter_candi)
    global iter_fragile
    iter_fragile = filter(_attack, iter_vul)
    global target_filter
    target_filter = iter_vul
    global iter_restore
    iter_restore = restore()


@socketio.on("scanNext")
def scan_next():
    try:
        dev = next(target_filter)
        socketio.emit("reportNext", dev)
        insert_device(dev)
    except StopIteration:
        socketio.emit("finished")
    except Exception as err:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        store.execute("insert into exception values (?,?,?,?)", (str(exc_type), str(exc_obj), exc_tb.tb_frame.f_code.co_filename, str(exc_tb.tb_lineno)))
        print("扫描时发生异常，信息已存入数据库")
        socketio.emit("reportNext", None)


@socketio.on("clear")
def clear():
    # todo
    pass


@socketio.on("getStat")
def get_stat():
    cursor.execute("SELECT count(*) FROM devices WHERE level=0")
    poss = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM devices WHERE level=1")
    vulner = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM devices WHERE level=2")
    frag = cursor.fetchone()[0]
    socketio.emit("reportStat", {
        "possible": poss,
        "vulnerable": vulner,
        "fragile": frag,
    })

@socketio.on("restoreNext")
def restore_next():
    try:
        socketio.emit("reportNextRestore", next(iter_restore))
    except StopIteration:
        socketio.emit("restoreFinish")
