
# A               1 a host address
# NS              2 an authoritative name server
# MD              3 a mail destination (Obsolete - use MX)
# MF              4 a mail forwarder (Obsolete - use MX)
# CNAME           5 the canonical name for an alias
# SOA             6 marks the start of a zone of authority
# MB              7 a mailbox domain name (EXPERIMENTAL)
# MG              8 a mail group member (EXPERIMENTAL)
# MR              9 a mail rename domain name (EXPERIMENTAL)
# NULL            10 a null RR (EXPERIMENTAL)
# WKS             11 a well known service description
# PTR             12 a domain name pointer
# HINFO           13 host information
# MINFO           14 mailbox or mail list information
# MX              15 mail exchange
# TXT             16 text strings
TYPES = {
    'A': 1,
    'NS': 2,
    'MD': 3,
    'MF': 4,
    'CNAME': 5,
    'SOA': 6,
    'MB': 7,
    'MG': 8,
    'MR': 9,
    'NULL': 10,
    'WKS': 11,
    'PTR': 12,
    'HINFO': 13,
    'MINFO': 14,
    'MX': 15,
    'TXT': 16,
    'AAAA': 28, # RFC 3596
    'SRV': 33,  # RFC 2782
}

# AXFR            252 A request for a transfer of an entire zone
# MAILB           253 A request for mailbox-related records (MB, MG or MR)
# MAILA           254 A request for mail agent RRs (Obsolete - see MX)
# *               255 A request for all records
QTYPES = {
    'AXFR': 252,
    'MAILB': 253,
    'MAILA': 254,
    '*': 255
}

# IN              1 the Internet
# CS              2 the CSNET class (Obsolete - used only for examples in
#                 some obsolete RFCs)
# CH              3 the CHAOS class
# HS              4 Hesiod [Dyer 87]
CLASSES = {
    'IN': 1,
    'CS': 2,
    'CH': 3,
    'HS': 4,
}

# *               255 any class
QCLASSES = {
    '*': 255,
}

# CNAME RDATA => a domain name

# HINFO RDATA => two strings (1 byte length, then data) representing cpu, os
