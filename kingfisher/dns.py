"""
RFC1035
"""
import struct
import logging


def get_header(msg):
    r"""
    :param msg: The message.
    :returns: A dictionary representing the header.
    ID => msg_id
    QR => is_response
    Opcode => opcode
    AA => is_authorative
    TC => is_truncated
    RD => recursion_desired
    RA => recursion_available
    Z => z
    RCODE => rcode
    QDCOUNT => question_count
    ANCOUNT => answer_count
    NSCOUNT => authority_count
    ARCOUNT => additional_count

    >>> get_header('\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')['msg_id']
    1
    >>> get_header('\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00')['question_count']
    1
    >>> get_header('\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00')['answer_count']
    1
    >>> get_header('\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00')['authority_count']
    1
    >>> get_header('\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01')['additional_count']
    1
    >>> get_header('\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')['msg_id']
    65280
    >>> get_header('\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00')['is_response']
    1
    >>> get_header('\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00')['opcode']
    1
    >>> get_header('\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00')['is_authorative']
    1
    >>> get_header('\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00')['is_truncated']
    1
    >>> get_header('\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00')['recursion_desired']
    1
    >>> get_header('\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00')['recursion_available']
    1
    >>> get_header('\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00')['rcode']
    1
    >>> x = get_header('\x78\x8c\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00')
    >>> x['msg_id']
    30860
    >>> x['question_count']
    1
    >>> x['recursion_desired']
    1
    >>> x['is_response']
    0
    """
    p = struct.unpack('>HHHHHH', msg[:12])
    return {
        'msg_id': p[0],
        'question_count': p[2],
        'answer_count': p[3],
        'authority_count': p[4],
        'additional_count': p[5],
        'is_response':         (p[1] >> 15) % 2,
        'opcode':              (p[1] >> 11) % 16,
        'is_authorative':      (p[1] >> 10) % 2,
        'is_truncated':        (p[1] >> 9)  % 2,
        'recursion_desired':   (p[1] >> 8)  % 2,
        'recursion_available': (p[1] >> 7)  % 2,
        'z':                   (p[1] >> 4)  % 8,
        'rcode':               (p[1]     )  % 16,
    }

def _get_part(msg):
    r"""
    >>> _get_part('\x07example')
    (8, 'example')
    >>> _get_part('\x00')
    (1, None)
    """
    # Read a byte, which indicates length
    # if length is 0, it is the end
    # otherwise read the part, report the part and length used
    length, = struct.unpack('>B', msg[0])
    logging.debug('Part length = %d', length)
    if length == 0:
        return (1, None)
    assert length > 0
    part = msg[1:1 + length]
    logging.debug('Part = %r', part)
    # 1 byte used for the length
    return (length + 1, part)

def get_name(msg):
    r"""
    >>> get_name('\x07example\x03com\x00')
    ('', 'example.com')
    >>> get_name('\x07example\x03com\x00stuffattheend')
    ('stuffattheend', 'example.com')
    """
    parts = []
    while True:
        offset, part = _get_part(msg)
        if part is None:
            msg = msg[1:]
            break
        parts.append(part)
        msg = msg[offset:]
    name = '.'.join(parts)
    return msg, name

def parse_question(msg):
    r"""
    >>> parse_question('\x07example\x03com\x00\x00\xff\x00\xff')
    ('', {'qclass': 255, 'qtype': 255, 'name': 'example.com'})
    """
    msg, name = get_name(msg)
    qtype, qclass = struct.unpack('>HH', msg[:4])
    logging.debug('qtype = %d, qclass = %d', qtype, qclass)
    return (msg[4:], {
        'name': name,
        'qtype': qtype,
        'qclass': qclass,
    })

def parse_resource_record(msg):
    r"""
    >>> parse_resource_record('\x07example\x03com\x00\x00\xff\x00\x01\x00\x00\xf0\x00\xff\x00')
    ('', {'record': '', 'ttl': 61440, 'type': 255, 'name': 'example.com', 'class': 1})
    """
    msg, name = get_name(msg)
    type, klass, ttl, rd_length = struct.unpack('>HHIH', msg[:10])
    msg = msg[10:]
    record_data = msg[:rd_length]
    return (msg[rd_length:], {
        'name': name,
        'type': type,
        'class': klass,
        'ttl': ttl,
        'record': record_data
    })

def parse(msg):
    r"""
    >>> x = parse('\xf7\x91\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01')
    >>> x['header']['question_count']
    1
    >>> x['questions'][0]['name']
    'example.com'
    >>> x['questions'][0]['qtype']
    1
    >>> x['questions'][0]['qclass']
    1
    """
    header = get_header(msg)
    msg = msg[12:]
    # Question
    question_count = header['question_count']
    questions = []
    while question_count > 0:
        msg, question = parse_question(msg)
        questions.append(question)
        question_count -= 1
    # Answer
    answer_count = header['answer_count']
    answers = []
    while answer_count > 0:
        msg, record = parse_resource_record(msg)
        answers.append(record)
        answer_count -= 1
    # Authority
    authority_count = header['authority_count']
    authorities = []
    while authority_count > 0:
        msg, record = parse_resource_record(msg)
        authorities.append(record)
        authority_count -= 1
    # Additional
    additional_count = header['additional_count']
    additionals = []
    while additional_count > 0:
        msg, record = parse_resource_record(msg)
        additionals.append(record)
        additional_count -= 1
    return {
        'header': header,
        'questions': questions,
        'answers': answers,
        'authorities': authorities,
        'additionals': additionals
    }

# Construction

def construct_part(part):
    r"""
    >>> construct_part('name')
    '\x04name'
    """
    return struct.pack('>B', len(part)) + part

def construct_name(name):
    r"""
    >>> construct_name('example.com')
    '\x07example\x03com\x00'
    """
    result = ''
    for part in name.split('.'):
        result += construct_part(part)
    result += construct_part('')
    return result

def construct_record(record):
    r"""
    >>> construct_record({
    ...     'name': 'example.com',
    ...     'type': 1,
    ...     'class': 1,
    ...     'ttl': 300,
    ...     'rdata': '\x01\x02\x03\x04'
    ... })
    '\x07example\x03com\x00\x00\x01\x00\x01\x00\x00\x01,\x00\x04\x01\x02\x03\x04'
    """
    # record is:
    #   name
    #   type
    #   class
    #   ttl
    #   rdlength
    #   rdata
    name = construct_name(record['name'])
    middle = struct.pack('>HHIH', record['type'], record['class'],
        record['ttl'], len(record['rdata']))
    return name + middle + record['rdata']

def construct_question(question):
    r"""
    >>> x = {
    ...     'name': 'example.com',
    ...     'qtype': 255,
    ...     'qclass': 255
    ... }
    >>> construct_question(x)
    '\x07example\x03com\x00\x00\xff\x00\xff'
    >>> x == parse_question(construct_question(x))[1]
    True
    """
    name = construct_name(question['name'])
    return name + struct.pack('>HH', question['qtype'], question['qclass'])

def construct_response(request, response):
    r"""
    >>> request = {
    ...     'header': {
    ...         'msg_id': 123,
    ...         'question_count': 0,
    ...         'answer_count': 0,
    ...         'authority_count': 0,
    ...         'additional_count': 0,
    ...         'is_response':         0,
    ...         'opcode':              0,
    ...         'is_authorative':      0,
    ...         'is_truncated':        0,
    ...         'recursion_desired':   0,
    ...         'recursion_available': 0,
    ...         'z':                   0,
    ...         'rcode':               0,
    ...     },
    ...     'questions': [
    ...         {
    ...             'name': 'example.com',
    ...             'qtype': 255,
    ...             'qclass': 255
    ...         }
    ...     ],
    ...     'answers': [],
    ...     'authorities': [],
    ...     'additionals': [],
    ... }
    >>> response = {
    ...     'questions': request['questions'],
    ...     'answers': [
    ...         {
    ...             'name': 'example.com',
    ...             'type': 1,
    ...             'class': 1,
    ...             'ttl': 300,
    ...             'rdata': '\x01\x02\x03\x04'
    ...         },
    ...     ],
    ...     'authorities': [
    ...         {
    ...             'name': 'ns1.example.com',
    ...             'type': 2,
    ...             'class': 1,
    ...             'ttl': 300,
    ...             'rdata': '\x01\x02\x03\x04'
    ...         },
    ...     ],
    ...     'additionals': [
    ...         {
    ...             'name': 'ns2.example.com',
    ...             'type': 2,
    ...             'class': 1,
    ...             'ttl': 300,
    ...             'rdata': '\x01\x02\x03\x04'
    ...         },
    ...     ],
    ...     'opcode': 0,
    ...     'is_authorative': 0,
    ...     'is_truncated': 0,
    ...     'recursion_available': 0,
    ...     'rcode': 0,
    ... }
    >>> construct_response(request, response)
    '\x00{\x80\x00\x00\x01\x00\x01\x00\x01\x00\x01\x07example\x03com\x00\x00\xff\x00\xff\x07example\x03com\x00\x00\x01\x00\x01\x00\x00\x01,\x00\x04\x01\x02\x03\x04\x03ns1\x07example\x03com\x00\x00\x02\x00\x01\x00\x00\x01,\x00\x04\x01\x02\x03\x04\x03ns2\x07example\x03com\x00\x00\x02\x00\x01\x00\x00\x01,\x00\x04\x01\x02\x03\x04'
    """
    # response is:
    #   opcode
    #   is_authorative
    #   is_truncated
    #   recursion_available
    #   rcode
    #   questions
    #   answers
    #   authorities
    #   additionals
    original_header = request['header']
    question_count    = len(response['questions'])
    answers_count     = len(response['answers'])
    authorities_count = len(response['authorities'])
    additionals_count = len(response['additionals'])
    msg_id = original_header['msg_id']
    # This is a response
    codes = 1 << 15
    codes += response['opcode'] << 11
    codes += response['is_authorative'] << 10
    codes += response['is_truncated'] << 9
    codes += original_header['recursion_desired'] << 8
    codes += response['recursion_available'] << 7
    # Skip Z
    codes += response['rcode']
    result = struct.pack('>HHHHHH', msg_id, codes, question_count,
        answers_count, authorities_count, additionals_count)
    # Question
    for question in response['questions']:
        result += construct_question(question)
    # Answer
    for record in response['answers']:
        result += construct_record(record)
    # Authority
    for record in response['authorities']:
        result += construct_record(record)
    # Additional
    for record in response['additionals']:
        result += construct_record(record)
    return result
