# -*- coding:utf-8 -*-
import optparse
from core.request_handler import serve_forever


def main():
    apiparser = optparse.OptionParser()
    apiparser.add_option("-s", "--server", help="start server at 0.0.0.0", default=False, action="store_true")
    apiparser.add_option("-p", "--port", help="specify server port", default=80, action="store", type="int")
    apiparser.add_option("-c", "--cmd", help="start scan in command", default=False, action="store_true")
    apiparser.add_option("-f", "--file", help="load ip from files", action="store")
    apiparser.add_option("-z", "--zoomeye", help="load ip by searching ZoomEye with query string", action="store")
    apiparser.add_option("-t", "--type", help="specify Poc file", action="store")
    (args, _) = apiparser.parse_args()

    if args.server is True:
        serve_forever(args.port)
    elif args.cmd is True:
        print("under development")
    else:
        apiparser.print_help()


if __name__ == '__main__':
    main()
