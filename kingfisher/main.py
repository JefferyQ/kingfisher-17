import sys
import socket
import net
import threading
import logging


def main(argv):
    FORMAT = '%(asctime)s %(levelname)s %(module)s:%(lineno)d %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    logging.debug('%r', argv)
    u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    u.bind(('127.0.0.1', 1053))
    x = net.UdpThread(u)
    x.start()
    try:
        x.join()
    except KeyboardInterrupt:
        sys.exit(1)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
