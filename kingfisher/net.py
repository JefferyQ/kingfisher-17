import socket
import threading
import logging
import dns


class ListenSocket(object):
    DEFAULT_PORT = 53

    def __init__(self, config=None):
        if config is None:
            self.udp_port = DEFAULT_PORT
            self.tcp_port = DEFAULT_PORT
            return
        self.udp_port = config.get('udp', 53)
        self.tcp_port = config.get('tcp', 53)
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def listen(self):
        self.udp.bind(('127.0.0.1', self.udp_port))
        self.tcp.bind(('127.0.0.1', self.tcp_port))
        self.tcp.listen(5)


class TcpThread(threading.Thread):

    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock

    def run(self):
        accept_sock = self.sock
        while True:
            try:
                sock, addr = accept_sock.accept()
                logging.debug('Connection from %r', addr)
                data = sock.recv(512)
                sock.sendall(data)
                sock.close()
            except Exception as e:
                logging.error('Got exception.', e)

                
class UdpThread(threading.Thread):

    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock

    def run(self):
        recv_sock = self.sock
        while True:
            try:
                data, addr = recv_sock.recvfrom(512)
                logging.debug('Connection from %r', addr)
                logging.debug('Message length %d', len(data))
                request = dns.parse(data)
                logging.debug('Raw = %r', data)
                logging.debug('Message = %r', request)
                response = {
                    'questions': [],
                    'answers': [
                        {
                        'name': 'example.com',
                        'type': 1,
                        'class': 1,
                        'ttl': 300,
                        'rdata': ''.join([chr(int(x)) for x in '1.2.3.4'.split('.')]),
                        }
                    ],
                    'authorities': [],
                    'additionals': [],
                    'opcode': 0,
                    'is_authorative': 0,
                    'is_truncated': 0,
                    'recursion_available': 0,
                    'rcode': 0,
                }
                output = dns.construct_response(request, response)
                recv_sock.sendto(output, addr)
            except Exception as e:
                logging.error('Got exception: %r', e, exc_info=True)
