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
    p = struct.unpack('>HHHHHH', msg[:12])
    msg_id = p[0]
    question_count = p[2]
    answer_count = p[3]
    ns_count = p[4]
    additional_count = p[5]
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
    if length == 0:
        return (1, None)
    assert length > 0
    part = msg[1:1 + length]
    return (length + 1, part)


def parse_question(msg):
    parts = []
    while True:
        offset, part = get_part(msg)
        if part is None:
            msg = msg[1:]
            break
        parts.append(part)
        logging.debug('%d %r', offset, part)
        msg = msg[offset:]
    qtype, qclass = struct.unpack('>HH', msg[:4])
    return {
        'names': parts,
        'qtype': qtype,
        'qclass': qclass,
        'msg': msg[4:],
    }
