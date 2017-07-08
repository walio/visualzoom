from core.request_handler import serve_forver
from core import init_db

if __name__ == '__main__':
    init_db()
    serve_forver()
