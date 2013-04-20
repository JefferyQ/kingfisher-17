import socket
import struct
import threading
import logging
import dns
import worker
import multiprocessing


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

    def __init__(self, sock, handler, num_workers=4):
        threading.Thread.__init__(self)
        self.sock = sock
        self.input_queue = multiprocessing.Queue(512)
        self.output_queue = multiprocessing.Queue(512)
        def work(input_queue=self.input_queue, output_queue=self.output_queue):
            while True:
                try:
                    data, addr = input_queue.get()
                    request = dns.parse(data)
                    response = handler.handle(request)
                    output = dns.construct_response(request, response)
                    output_queue.put((output, addr))
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logging.error('Got exception: %r', e, exc_info=True)
        self.workers = []
        for i in range(num_workers):
            self.create_worker(work)
        self.output_thread = UdpOutputThread(self.sock, self.output_queue)
        self.output_thread.daemon = True
        self.output_thread.start()

    def create_worker(self, thunk):
        w = multiprocessing.Process(target=thunk)
        w.start()
        self.workers.append(w)

    def run(self):
        recv_sock = self.sock
        input_queue = self.input_queue
        output_queue = self.output_queue
        while True:
            try:
                data, addr = recv_sock.recvfrom(512)
                logging.debug('UDP packet from %r length %d raw = %r',
                    addr, len(data), data)
                input_queue.put((data, addr))
            except KeyboardInterrupt:
                break
            except Exception as e:
                logging.error('Got exception: %r', e, exc_info=True)
        logging.debug('UdpThread exiting')

# TCP
import asyncore

class TcpHandler(asyncore.dispatcher_with_send):

    def __init__(self, handler, sock, **kwargs):
        asyncore.dispatcher_with_send.__init__(self, sock)
        self.handler = handler
        self.buffer = ''
        self.write_buffer = ''
        self.size = None

    def handle_read(self):
        data = self.recv(514)
        if not data:
            return
        # Add to the buffer
        self.buffer += data
        data = self.buffer
        if len(data) < 2:
            return
        if self.size is None:
            self.size, = struct.unpack('!H', data[:2])
        packet = data[2:2 + self.size]
        diff = len(packet) - self.size
        if diff < 0:
            return
        else:
            self.buffer = self.buffer[2 + len(packet):]
        request = dns.parse(packet)
        response = self.handler.handle(request)
        output = dns.construct_response(request, response)
        self.send(struct.pack('!H', len(output)) + output)
        self.close()

class TcpServer(asyncore.dispatcher):

    def __init__(self, address, handler):
        asyncore.dispatcher.__init__(self)
        self.handler = handler
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(address)
        self.listen(15)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            logging.debug('TCP connection from %r', addr)
            handler = TcpHandler(self.handler, sock)

class TcpThread(threading.Thread):

    def __init__(self, address, handler):
        threading.Thread.__init__(self)
        self.address = address
        self.handler = handler
        self.server = TcpServer(self.address, self.handler)

    def run(self):
        asyncore.loop()
