import sqlite3
store = sqlite3.connect("output/devices.db", check_same_thread=False)
cursor = store.cursor()


def init_db():
    store.execute("CREATE TABLE IF NOT EXISTS devices (ip_addr VARCHAR(20), lat FLOAT, lon FLOAT, addr VARCHAR(10), "
                  "level INT, wpapsk VARCHAR(10), ssid VARCHAR(20), user VARCHAR(20), passwd VARCHAR(20))")
    store.execute("CREATE TABLE IF NOT EXISTS exception (file varchar(20), line int, message varchar(100))")
    store.execute("CREATE TABLE IF NOT EXISTS page (page int)")
    cursor.execute("select * from page where rowid=1")
    if not cursor.fetchone():
        cursor.execute("insert into page values (1)")

column = ["ip_addr", "lat", "lon", "addr", "level", "wpapsk", "ssid", "user", "passwd"]



