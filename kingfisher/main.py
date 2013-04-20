"""\
Usage:
    kingfisher [options]
    kingfisher -h | --help
    kingfisher --version

Options:
    -h --help          Show help.
    --version          Show version.
    --address=ADDRESS  The address to bind to [default: 127.0.0.1:53]
    --run-as=USER      The user to run as.
    --log-level=LEVEL  The log level [INFO/DEBUG]. [default: INFO]

"""
from docopt import docopt
import os
import sys
import socket
import net
import threading
import logging
import worker

def parse_loglevel(raw_loglevel):
    return {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
    }[raw_loglevel.upper()]

def parse_address(raw_address):
    if raw_address.startswith('['):
        # ipv6
        raise Exception()
    address, port = raw_address.split(':')
    return address, int(port)

def parse_user(raw_user):
    if not raw_user:
        return os.geteuid()
    import pwd
    uid = pwd.getpwnam(raw_user).pw_uid
    del pwd
    return uid

def drop_root(uid):
    if os.geteuid() > 0:
        logging.info('Did not start as root.')
        return
    os.setuid(uid)
    os.seteuid(uid)
    logging.info('UID=%d EUID=%d', os.getuid(), os.geteuid())

def to_daemon(func):
    pid = os.fork()
    if pid == 0:
        # Start a new session
        os.setsid()
        # Fork a second time to create an orphan
        pid = os.fork()
        if pid == 0:
            # Not a session leader, no controlling terminal
            # The init process is responsible for clean up
            return func()
        if pid > 0:
            return 0
        return 1
    if pid > 0:
        # parent
        return 0
    logging.info('Forking failed.')
    return 1

def main(argv):
    arguments = docopt(__doc__, version='Kingfisher 0.1')
    logging.basicConfig(level=parse_loglevel(arguments['--log-level']),
        format=('%(asctime)s %(process)d %(threadName)s '
            '%(levelname)s %(module)s:%(lineno)d '
            '%(message)s'),
        filename='kingfisher.log')
    logging.info('arguments = %r', arguments)
    address = parse_address(arguments['--address'])
    logging.info('address = %r', address)
    desired_uid = parse_user(arguments['--run-as'])
    logging.info('Desired uid = %d', desired_uid)
    handler = worker.Handler()
    # Acquire sockets.
    u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    u.bind(address)
    tcp_thread = net.TcpThread(address, handler)
    # Drop privileges
    drop_root(desired_uid)
    def func():
        # Start the program
        udp_thread = net.UdpThread(u, handler)
        udp_thread.start()
        tcp_thread.start()
        try:
            udp_thread.join()
        except KeyboardInterrupt:
            sys.exit(1)
        return 0
    return to_daemon(func)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
