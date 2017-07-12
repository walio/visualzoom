# -*- coding:utf-8 -*-
import optparse
from tornado import ioloop
import logging
from core.poc import mode_verify, mode_attack
from core.utils import get_dev_list, insert_device, get_dev_from_file
from core.request_handler import application
from core import init_db

global log
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


def main():
    init_db()
    apiparser = optparse.OptionParser()
    apiparser.add_option("-s", "--server", help="start server at http://localhost:80/", default=False, action="store_true")
    apiparser.add_option("-c", "--cmd", help="start scan in command", default=False, action="store_true")
    apiparser.add_option("-f", "--file", help="load host from files" , action="store")
    (args, _) = apiparser.parse_args()
    if args.server is True:
        application.listen(80)
        logger.info('Server listening at http://localhost:80/')
        ioloop.IOLoop.instance().start()
    elif args.cmd is True:
        if args.file:
            verify_iter = filter(mode_verify(log), get_dev_from_file(args.file))
        else:
            verify_iter = filter(mode_verify(log), get_dev_list(log))
        target_iter = filter(mode_attack(log), verify_iter)
        for dev in target_iter:
            log.info(u"设备信息如下：")
            log.info(str(dev))
            insert_device(dev)
    else:
        apiparser.print_help()


if __name__ == '__main__':
    main()
