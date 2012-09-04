"""
4.1.1. Header section format

The header contains the following fields:

                                    1  1  1  1  1  1
      0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                      ID                       |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE   |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    QDCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    ANCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    NSCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    ARCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

where:

ID              A 16 bit identifier assigned by the program that
                generates any kind of query.  This identifier is copied
                the corresponding reply and can be used by the requester
                to match up replies to outstanding queries.

QR              A one bit field that specifies whether this message is a
                query (0), or a response (1).

OPCODE          A four bit field that specifies kind of query in this
                message.  This value is set by the originator of a query
                and copied into the response.  The values are:

                0               a standard query (QUERY)

                1               an inverse query (IQUERY)

                2               a server status request (STATUS)

                3-15            reserved for future use

AA              Authoritative Answer - this bit is valid in responses,
                and specifies that the responding name server is an
                authority for the domain name in question section.

                Note that the contents of the answer section may have
                multiple owner names because of aliases.  The AA bit
                corresponds to the name which matches the query name, or
                the first owner name in the answer section.

TC              TrunCation - specifies that this message was truncated
                due to length greater than that permitted on the
                transmission channel.

RD              Recursion Desired - this bit may be set in a query and
                is copied into the response.  If RD is set, it directs
                the name server to pursue the query recursively.
                Recursive query support is optional.

RA              Recursion Available - this be is set or cleared in a
                response, and denotes whether recursive query support is
                available in the name server.

Z               Reserved for future use.  Must be zero in all queries
                and responses.

RCODE           Response code - this 4 bit field is set as part of
                responses.  The values have the following
                interpretation:

                0               No error condition

                1               Format error - The name server was
                                unable to interpret the query.

                2               Server failure - The name server was
                                unable to process this query due to a
                                problem with the name server.

                3               Name Error - Meaningful only for
                                responses from an authoritative name
                                server, this code signifies that the
                                domain name referenced in the query does
                                not exist.

                4               Not Implemented - The name server does
                                not support the requested kind of query.

                5               Refused - The name server refuses to
                                perform the specified operation for
                                policy reasons.  For example, a name
                                server may not wish to provide the
                                information to the particular requester,
                                or a name server may not wish to perform
                                a particular operation (e.g., zone
"""
import struct
import logging


def get_header(msg):
    """
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
    NSCOUNT => ns_count
    ARCOUNT => additional_count
    """
    p = struct.unpack('>HHHHHH', msg[:12])
    return {
        'msg_id': p[0],
        'question_count': p[2],
        'answer_count': p[3],
        'ns_count': p[4],
        'additional_count': p[5],
        'is_response': p[1] % 2,
        'opcode': (p[1] >> 1) % 16,
        'is_authorative': (p[1] >> 5) % 2,
        'is_truncated': (p[1] >> 6) % 2,
        'recursion_desired': (p[1] >> 7) % 2,
        'recursion_available': (p[1] >> 8) % 2,
        'z': (p[1] >> 9) % 8,
        'rcode': (p[1] >> 12) % 16,
    }

def get_part(msg):
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


def parse_question(msg):
    parts = []
    while True:
        offset, part = get_part(msg)
        if part is None:
            msg = msg[1:]
            break
        parts.append(part)
        msg = msg[offset:]
    qtype, qclass = struct.unpack('>HH', msg[:4])
    logging.debug('qtype = %d, qclass = %d', qtype, qclass)
    return (msg[4:], {
        'name': '.'.join(parts),
        'qtype': qtype,
        'qclass': qclass,
    })

def parse_resource_record(msg):
    parts = []
    while True:
        offset, part = get_part(msg)
        if part is None:
            msg = msg[1:]
            break
        parts.append(part)
        msg = msg[offset:]
    name = '.'.join(parts)
    type, klass, ttl, rd_length = struct.unpack('>HHIH')
    record_data = msg[:rd_length]
    return (msg[rd_length:], {
        'type': type,
        'class': klass,
        'ttl': ttl,
        'record': record_data
    })

def parse(msg):
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
    ns_count = header['ns_count']
    authorities = []
    while ns_count > 0:
        msg, record = parse_resource_record(msg)
        authorities.append(record)
        ns_count -= 1
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
