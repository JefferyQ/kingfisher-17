import logging
import dns
from .constants import TYPES, QTYPES, CLASSES, QCLASSES

class Handler(object):

    def __init__(self, connection):
        self.conn = connection

    def handle_question(self, question):
        return list(self.conn.get(question))

    def handle(self, request):
        logging.info('Request = %r', request)
        answers = []
        rcode = 0
        for question in request['questions']:
            qtype = question['qtype']
            if qtype == QTYPES['*']:
                types = TYPES.values()
            else:
                types = [qtype]
            qclass = question['qclass']
            if qclass == QCLASSES['*']:
                classes = CLASSES.values()
            else:
                classes = [qclass]
            for a in self.conn.get(question['name'], types, classes):
                logging.info('Answer = %r', a)
                a['rdata'] = ''.join([chr(int(x)) for x in a['answer'].split('.')])
                a['name'] = a['name'].encode('ascii')
                answers.append(a)
        # ''.join([chr(int(x)) for x in '1.2.3.4'.split('.')])
        response = {
            'questions': request['questions'],
            'answers': answers,
            'authorities': [],
            'additionals': [],
            'opcode': 0,
            'is_authorative': 0,
            'is_truncated': 0,
            'recursion_available': 0,
            'rcode': rcode,
        }
        logging.info('Response = %r', response)
        return response
