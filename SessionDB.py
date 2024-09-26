import sqlite3
from helpers import log
from collections import Counter

class Session:
    def __init__(self, date, source_name, volume=0.0, noise=0.0, qrn=0.0, qrm=0.0, mode=0, items=None, score=0):
        self.date = date
        self.source_name = source_name
        self.volume = volume
        self.noise = noise
        self.qrn = qrn
        self.qrm = qrm
        self.items = items if items is not None else []
        self._score = score
        self.mode = mode  # training mode: 0 sequential, 1 pileup

    def add_item(self, received, sent, speed, duration):
        self.items.append((received, sent, speed, duration))

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value

    def __repr__(self):
        return (f"Session(date={self.date}, source_name={self.source_name}, score={self.score}, "
                f"items={self.items}, volume={self.volume}, noise={self.noise}, qrn={self.qrn}, qrm={self.qrm})")


import sqlite3
from helpers import log

class SessionDB:
    def __init__(self, db_name='sessions.db'):
        self.conn = sqlite3.connect(db_name)
        self.conn.execute("PRAGMA foreign_keys = ON")  # Ensure foreign keys are enforced
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS version (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    major INTEGER,
                    minor INTEGER,
                    patch INTEGER,
                    prerelease INTEGER
                )
            ''')

            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS source_names (
                    name TEXT PRIMARY KEY
                )
            ''')

            # sessions now uses 'id' as the primary key
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    score INTEGER,
                    source_name TEXT,
                    volume REAL,
                    noise REAL,
                    qrn REAL,
                    qrm REAL,
                    mode INTEGER,
                    FOREIGN KEY (source_name) REFERENCES source_names(name)
                )
            ''')

            # items references sessions by session_id
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    received TEXT,
                    sent TEXT,
                    speed INTEGER,
                    duration REAL,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
            ''')

            # Index to make session lookups by source name faster
            self.conn.execute('CREATE INDEX IF NOT EXISTS idx_sessions_source_name ON sessions(source_name)')

    def add_session(self, session):
        with self.conn:
            # Insert or ignore the source name
            self.conn.execute('INSERT OR IGNORE INTO source_names (name) VALUES (?)', (session.source_name,))

            # Insert the session data and retrieve the last inserted session_id
            self.conn.execute('''
                INSERT INTO sessions (date, score, source_name, volume, noise, qrn, qrm, mode)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session.date, session.score, session.source_name, session.volume,
                  session.noise, session.qrn, session.qrm, session.mode))

            session_id = self.conn.execute('SELECT last_insert_rowid()').fetchone()[0]

            # Batch insert items associated with this session
            items_data = [(session_id, received, sent, speed, duration) for received, sent, speed, duration in session.items]
            self.conn.executemany('''
                INSERT INTO items (session_id, received, sent, speed, duration)
                VALUES (?, ?, ?, ?, ?)
            ''', items_data)

    def delete_session(self, date):
         session_id = self.get_session_id(date)
         if session_id:
            self.delete_session_by_id(session_id)

    def delete_session_by_id(self, session_id):
        with self.conn:
            self.conn.execute('DELETE FROM sessions WHERE id = ?', (session_id,))

    def get_sorted_sessions(self, sort_by='score', ascending=False):
        order = 'ASC' if ascending else 'DESC'
        with self.conn:
            cursor = self.conn.execute(f'''
                SELECT id, date, score, source_name, volume, noise, qrn, qrm, mode FROM sessions ORDER BY {sort_by} {order}
            ''')
            sessions = cursor.fetchall()
        return [self.get_session_by_id(session[0]) for session in sessions]

    def get_session_id(self, date : str) -> int:
        with self.conn:
            # Get the session_id based on the date
            session_id = self.conn.execute('''
                SELECT id
                FROM sessions
                WHERE date = ?
            ''', (date,)).fetchone()

            return session_id[0]

    def get_session(self, date):
        session_id = self.get_session_id(date)
        if session_id is None:
            return None

        return self.get_session_by_id(session_id)
    
    def get_session_by_id(self, session_id):
        with self.conn:
            # Fetch the session details based on session_id
            session_data = self.conn.execute('''
                SELECT id, date, score, source_name, volume, noise, qrn, qrm, mode
                FROM sessions
                WHERE id = ?
            ''', (session_id,)).fetchone()

            if session_data is None:
                return None

            session_id, date, score, source_name, volume, noise, qrn, qrm, mode = session_data

            # Fetch the related items for the session
            items = self.conn.execute('''
                SELECT received, sent, speed, duration
                FROM items
                WHERE session_id = ?
            ''', (session_id,)).fetchall()

            # Create and return the session object, passing the items list directly
            session = Session(date=date, source_name=source_name, volume=volume, noise=noise,
                            qrn=qrn, qrm=qrm, mode=mode, score=score, items=items)

            return session

    def set_version(self, version_tuple):
        if len(version_tuple) != 4:
            raise ValueError("Version must be a tuple with 4 numeric values (major, minor, patch, prerelease)")

        major, minor, patch, prerelease = map(int, version_tuple)

        with self.conn:
            self.conn.execute('''
                INSERT INTO version (major, minor, patch, prerelease)
                VALUES (?, ?, ?, ?)
            ''', (major, minor, patch, prerelease))

    def get_version(self):
        with self.conn:
            version_data = self.conn.execute('''
                SELECT major, minor, patch, prerelease
                FROM version
                ORDER BY id DESC
                LIMIT 1
            ''').fetchone()

            if version_data is None:
                return (0, 0, 0, 0)

            return version_data

    def get_histogram(self, source_name):
        #Calculate number of items for the source
        query = '''
        SELECT items.received, items.sent, items.speed
        FROM items
        JOIN sessions ON items.session_id = sessions.id
        WHERE sessions.source_name = ?
        '''
        rows = self.conn.execute(query, (source_name,)).fetchall()
        total_count = len(rows)

        # find errors and related speeds
        query = '''
        SELECT items.speed
        FROM items
        JOIN sessions ON items.session_id = sessions.id
        WHERE sessions.source_name = ?
        AND items.received != items.sent
        ORDER BY items.speed;
        '''
        failed_speeds = self.conn.execute(query, (source_name,)).fetchall()
        failed_speeds = [row[0] for row in failed_speeds]  # row[0] = speed

        # Calculate the histogram (frequency of each speed value)
        speed_histogram = Counter(failed_speeds)
        sorted_histogram = sorted(speed_histogram.items())  # Sort by speed (the key)

        # Calculate the cumulative histogram
        cumulative_histogram = []
        cumulative_count = 0
        for speed, count in sorted_histogram:
            cumulative_count += count  # Accumulate the counts
            cumulative_histogram.append((speed, float(cumulative_count) / total_count))  # Scale the cumulative count

        return total_count, cumulative_histogram

def column_exists(conn, table_name, column_name):
    """Check if a column exists in a given table."""
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]  # row[1] contains the column names
    return column_name in columns


def table_exists(conn, table_name):
    """Check if a table exists in the database."""
    cursor = conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    return cursor.fetchone() is not None


def convert_v0950(db_name: str):
    """Converts an older version of the database to the new version with source_names and session references."""
    conn = sqlite3.connect(db_name)
    with conn:
        conn.execute("PRAGMA foreign_keys = ON")

        # Step 1: Create the new `source_names` table if it doesn't exist
        conn.execute('''
            CREATE TABLE IF NOT EXISTS source_names (
                name TEXT PRIMARY KEY
            )
        ''')

        # Step 2: Insert the 'unavailable' source in the source_names table
        conn.execute('''
            INSERT OR IGNORE INTO source_names (name) VALUES ('unavailable')
        ''')

        # Step 3: Create a new sessions table (sessions_new) with `id` as the primary key
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sessions_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                score INTEGER,
                source_name TEXT,
                volume REAL,
                noise REAL,
                qrn REAL,
                qrm REAL,
                mode INTEGER,
                FOREIGN KEY (source_name) REFERENCES source_names(name)
            )
        ''')

        # Step 4: Migrate data from the old sessions table to the new one
        # All old sessions will have 'unavailable' as the source_name
        conn.execute('''
            INSERT INTO sessions_new (date, score, source_name, volume, noise, qrn, qrm, mode)
            SELECT date, score, 'unavailable', 0.5, 0.33, 0.0, 0.0, 0 FROM sessions
        ''')

        # Step 5: Create a new items table (items_new) that refers to session_id
        conn.execute('''
            CREATE TABLE IF NOT EXISTS items_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                received TEXT,
                sent TEXT,
                speed INTEGER,
                duration REAL,
                FOREIGN KEY (session_id) REFERENCES sessions_new(id) ON DELETE CASCADE
            )
        ''')

        # Step 6: Copy items data to the new items table, linking them to the new session ids
        # Use the date to match the correct session_id
        conn.execute('''
            INSERT INTO items_new (session_id, received, sent, speed, duration)
            SELECT s.id, i.received, i.sent, i.speed, i.duration
            FROM items i
            JOIN sessions_new s ON s.date = i.date
        ''')

        # Step 7: Drop the old tables and rename the new tables
        conn.execute("DROP TABLE items")
        conn.execute("ALTER TABLE items_new RENAME TO items")

        conn.execute("DROP TABLE sessions")
        conn.execute("ALTER TABLE sessions_new RENAME TO sessions")

        # Step 8: Create the version table if it doesn't exist
        if not table_exists(conn, 'version'):
            conn.execute('''
                CREATE TABLE version (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    major INTEGER,
                    minor INTEGER,
                    patch INTEGER,
                    prerelease INTEGER
                )
            ''')

        # Step 9: Insert version (0, 9, 5, 0) into the version table
        conn.execute('''
            INSERT INTO version (major, minor, patch, prerelease)
            VALUES (?, ?, ?, ?)
        ''', (0, 9, 5, 0))

    conn.close()
    log('info', f"Database {db_name} conversion completed successfully.")

if __name__ == "__main__":
    import os
    db_name = 'test.db'
    try:
        os.remove(db_name)
    except Exception:
        pass

    session_db = SessionDB(db_name=db_name)

    # Adding sessions
    current_time_1 = "2024-09-16T12:00:00"  # Replace with actual date-time or string value
    session1 = Session(
        date=current_time_1,
        source_name="Source1",
        volume=0.5,
        noise=1.2,
        qrn=0.8,
        qrm=1.1,
        items=[('HELLO', 'HELLO', 0, 5.0), ('WORLD', 'WORD', 1, 10.0)],
        score=95
    )
    session_db.add_session(session1)

    current_time_2 = "2024-09-16T13:00:00"  # Replace with actual date-time or string value
    session2 = Session(
        date=current_time_2,
        source_name="Source2",
        volume=0.7,
        noise=1.5,
        qrn=1.0,
        qrm=0.9,
        items=[('FOO', 'FOO', 3, 8.0), ('BAR', 'BR', 1.5, 12.0)],
        score=80
    )
    session_db.add_session(session2)

    current_time_3 = "2024-09-16T14:00:00"  # Replace with actual date-time or string value
    session3 = Session(
        date=current_time_3,
        source_name="Source3",
        volume=0.6,
        noise=0.9,
        qrn=1.3,
        qrm=1.2,
        items=[('PYTHON', 'PYTHON', 1.3, 7.5), ('CODE', 'CODE', 1.4, 6.0)],
        score=90
    )
    session_db.add_session(session3)

    session_to_delete_date = "2023-07-02T11:00:00"  # Replace with actual date-time or string value
    session4 = Session(
        date=session_to_delete_date,
        source_name="Source1",
        volume=0.9,
        noise=1.1,
        qrn=0.7,
        qrm=1.5,
        items=[('MORSE', 'MORSE', 1.3, 8.0), ('TRAINING', 'TRAINING', 1.34, 9.5)],
        score=85
    )
    session_db.add_session(session4)

    # Listing sorted sessions by date in ascending order
    print("Sorted Sessions by Date Ascending:", *session_db.get_sorted_sessions(sort_by='date', ascending=True), sep='\n')

    # Listing sorted sessions by date in descending order
    print("Sorted Sessions by Date Descending:", *session_db.get_sorted_sessions(sort_by='date', ascending=False), sep='\n')

    # Listing sorted sessions by score in ascending order
    print("Sorted Sessions by Score Ascending:", *session_db.get_sorted_sessions(sort_by='score', ascending=True), sep='\n')

    # Listing sorted sessions by score in descending order
    print("Sorted Sessions by Score Descending:", *session_db.get_sorted_sessions(sort_by='score', ascending=False), sep='\n')

    # Deleting a session
    session_db.delete_session(session_to_delete_date)
    #session_db.get_session(session_to_delete_date)

    version = session_db.get_version()
    assert version == (0, 0, 0, 0)
    session_db.set_version((1, 2, 3, 4))
    version = session_db.get_version()
    assert version == (1, 2, 3, 4)
    #convert_v0950('sessions.db')
    s = SessionDB('sessions.db')
    s.get_histogram('ca_counties.txt')
    