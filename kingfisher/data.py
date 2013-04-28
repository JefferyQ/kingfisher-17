import sqlite3
import dns

class Connection(object):
    """
    >>> c = Connection(':memory:')
    >>> c.insert({'type': 1, 'class': 1, 'name': 'EXAMPLE.com', 'answer': 'blah', 'ttl': 300, 'priority': 0})
    >>> foo = c.get('example.com', [1], [1])
    >>> list(foo) is not None
    True
    >>> foo = c.get('EXAMPLE.COM', [1], [1])
    >>> list(foo) is not None
    True
    >>> foo = c.get('NONEXISTENT', [1], [1])
    >>> list(foo)
    []
    """
    DOMAIN_NAMES = """
    CREATE TABLE IF NOT EXISTS domain_names (
        type INTEGER NOT NULL,
        class INTEGER NOT NULL,
        name TEXT NOT NULL COLLATE NOCASE,
        answer TEXT NOT NULL,
        ttl INTEGER NOT NULL,
        priority INTEGER,
        UNIQUE (name, type, class)
    )
    """

    def __init__(self, conn_url):
        self.conn = sqlite3.connect(conn_url)
        c = self.conn.cursor()
        c.execute(self.DOMAIN_NAMES)
        self.conn.commit()
        c.close()

    def insert(self, row):
        c = self.conn.cursor()
        c.execute('''INSERT INTO domain_names
            (type, class, name, answer, ttl, priority) VALUES (?, ?, ?, ?, ?, ?)''',
            [row['type'], row['class'], row['name'], row['answer'], row['ttl'],
            row['priority']])
        self.conn.commit()

    def get(self, name, types, classes):
        if not types:
            return
        if not classes:
            return
        c = self.conn.cursor()
        c.execute('''SELECT name, type, class, answer, ttl, priority
            FROM domain_names
            WHERE name = ? AND type in (%s) AND class in (%s)''' % (
                ','.join('?' * len(types)),
                ','.join('?' * len(classes)),
            ), [name] + types + classes)
        for result in c.fetchall():
            yield {
                'name': result[0],
                'type': result[1],
                'class': result[2],
                'answer': result[3],
                'ttl': result[4],
                'priority': result[5],
            }
