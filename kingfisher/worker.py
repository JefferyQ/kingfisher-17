import logging
import dns
from data import ObjectNotFoundException

class Handler(object):

    def __init__(self, connection):
        self.conn = connection

    def handle(self, request):
        logging.info('Request = %r', request)
        try:
            result = self.conn.get()
        except ObjectNotFoundException:
            log.error('error')
            raise
        # ''.join([chr(int(x)) for x in '1.2.3.4'.split('.')])
        response = {
            'questions': request['questions'],
            'answers': [
                {
                'name': 'example.com',
                'type': 1,
                'class': 1,
                'ttl': result['ttl'],
                'rdata': ''.join([chr(int(x)) for x in result['answer'].split('.'))
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
        logging.info('Response = %r', response)
        return response
