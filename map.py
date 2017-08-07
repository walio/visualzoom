# -*- coding:utf-8 -*-
import optparse
import logging
from core.utils import zoom_iter, get_ip_from_file
from core.request_handler import serve_forever


def main():
    apiparser = optparse.OptionParser()
    apiparser.add_option("-s", "--server", help="start server at http://localhost:80/", default=False, action="store_true")
    apiparser.add_option("-c", "--cmd", help="start scan in command", default=False, action="store_true")
    apiparser.add_option("-f", "--file", help="load ip from files", action="store")
    apiparser.add_option("-z", "--zoomeye", help="load ip by searching ZoomEye with query string", action="store")
    apiparser.add_option("-t", "--type", help="specify check type", action="store")
    (args, _) = apiparser.parse_args()

    if args.server is True:
        serve_forever(80)
    elif args.cmd is True:
        if args.file:
            ip_source = get_ip_from_file(args.file)
        elif args.zoomeye:
            ip_source = zoom_iter(args.zoomeye)
        else:
            print("please confirm ip source")
            return

        if args.type == "memory leak":
            verify_iter = filter(_verify, ip_source)
            target_iter = filter(_attack, verify_iter)
        elif args.type == "default password":
            target_iter = filter(check, ip_source)
        else:
            print("please confirm penetration type ")
            return

        logger = logging.getLogger("root")
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        while True:
            try:
                logger.info(u"设备信息如下：")
                logger.info(str(next(target_iter)))
            except:
                logger.warning("exception happened, skip\n")
    else:
        apiparser.print_help()


if __name__ == '__main__':
    main()
