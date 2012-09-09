import logging
import dns


def work(input_queue, output_queue):
    while True:
        try:
            data, addr = input_queue.get()
            request = dns.parse(data)
            logging.debug('Message = %r', request)
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
            output = dns.construct_response(request, response)
            output_queue.put((output, addr))
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error('Got exception: %r', e, exc_info=True)
