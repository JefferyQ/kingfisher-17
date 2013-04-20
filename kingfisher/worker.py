import logging
import dns

class Handler(object):

    def handle(self, request):
        logging.info('Request = %r', request)
        response = {
            'questions': request['questions'],
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
        logging.info('Response = %r', response)
        return response
