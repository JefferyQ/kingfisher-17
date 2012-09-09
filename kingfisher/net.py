import socket
import threading
import logging
import dns
import worker
import multiprocessing


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


class UdpOutputThread(threading.Thread):

    def __init__(self, sock, queue):
        threading.Thread.__init__(self)
        self.sock = sock
        self.queue = queue

    def run(self):
        recv_sock = self.sock
        queue = self.queue
        while True:
            try:
                output, addr = queue.get()
                recv_sock.sendto(output, addr)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logging.error('Got exception: %r', e, exc_info=True)

                
class UdpThread(threading.Thread):

    def __init__(self, sock, num_workers=4):
        threading.Thread.__init__(self)
        self.sock = sock
        self.input_queue = multiprocessing.Queue(512)
        self.output_queue = multiprocessing.Queue(512)
        self.workers = []
        for i in range(num_workers):
            self.create_worker()
        self.output_thread = UdpOutputThread(self.sock, self.output_queue)
        self.output_thread.daemon = True
        self.output_thread.start()

    def create_worker(self):
        w = multiprocessing.Process(target=worker.work,
            args=(self.input_queue, self.output_queue))
        w.start()
        self.workers.append(w)

    def run(self):
        recv_sock = self.sock
        input_queue = self.input_queue
        output_queue = self.output_queue
        while True:
            try:
                data, addr = recv_sock.recvfrom(512)
                logging.debug('Connection from %r length %d raw = %r',
                    addr, len(data), data)
                input_queue.put((data, addr))
            except KeyboardInterrupt:
                break
            except Exception as e:
                logging.error('Got exception: %r', e, exc_info=True)
        logging.debug('UdpThread exiting')
