import sqlite3
from datetime import datetime, timedelta

class Session:
    def __init__(self, date, items=None, score=0):
        self.date = date
        self.items = items if items is not None else []
        self._score = score

    def add_item(self, received, sent, speed, duration):
        self.items.append((received, sent, speed, duration))

    def get_score(self):
        return self._score

    def set_score(self, score):
        self._score = score

    score = property(get_score, set_score)

    def __repr__(self):
        return f"Session(date={self.date}, score={self.score}, items={self.items})"


class SessionDB:
    def __init__(self, db_name='sessions.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    date TEXT PRIMARY KEY,
                    score INTEGER
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    received TEXT,
                    sent TEXT,
                    speed INTEGER,
                    duration REAL,
                    FOREIGN KEY(date) REFERENCES sessions(date)
                )
            ''')

    def add_session(self, session):
        with self.conn:
            self.conn.execute('''
                INSERT INTO sessions (date, score)
                VALUES (?, ?)
            ''', (session.date, session.score))
            for received, sent, speed, duration in session.items:
                self.conn.execute('''
                    INSERT INTO items (date, received, sent, speed, duration)
                    VALUES (?, ?, ?, ?, ?)
                ''', (session.date, received, sent, speed, duration))

    def delete_session(self, date):
        with self.conn:
            self.conn.execute('DELETE FROM items WHERE date = ?', (date,))
            self.conn.execute('DELETE FROM sessions WHERE date = ?', (date,))

    def get_sorted_sessions(self, sort_by='score', ascending=False):
        order = 'ASC' if ascending else 'DESC'
        with self.conn:
            cursor = self.conn.execute(f'''
                SELECT * FROM sessions ORDER BY {sort_by} {order}
            ''')
            sessions = cursor.fetchall()
        return [self.get_session(session[0]) for session in sessions]

    def get_session(self, date):
        with self.conn:
            cursor = self.conn.execute('''
                SELECT * FROM sessions WHERE date = ?
            ''', (date,))
            session_data = cursor.fetchone()
            if session_data:
                cursor = self.conn.execute('''
                    SELECT received, sent, speed, duration FROM items WHERE date = ?
                ''', (date,))
                items = [(received, sent, speed, duration) for received, sent, speed, duration in cursor.fetchall()]
                session = Session(date=session_data[0], items=items, score=session_data[1])
                return session
            return None


if __name__ == "__main__":# Example Usage
    session_db = SessionDB()

    # Adding sessions
    current_time_1 = datetime.now().isoformat()
    session1 = Session(
        date=current_time_1,
        received_sent_pairs=[('HELLO', 'HELLO', 0), ('WORLD', 'WORD', 1)],
        score=95
    )
    session_db.add_session(session1)

    current_time_2 = datetime.now().isoformat()
    session2 = Session(
        date=current_time_2,
        received_sent_pairs=[('FOO', 'FOO', 3), ('BAR', 'BR', 1.5)],
        score=80
    )
    session_db.add_session(session2)

    current_time_3 = datetime.now().isoformat()
    session3 = Session(
        date=current_time_3,
        received_sent_pairs=[('PYTHON', 'PYTHON',1.3), ('CODE', 'CODE', 1.4)],
        score=90
    )
    session_db.add_session(session3)

    session_to_delete_date = '2023-07-02T11:00:00'
    session4 = Session(
        date=session_to_delete_date,
        received_sent_pairs=[('MORSE', 'MORSE', 1.3), ('TRAINING', 'TRAINING', 1.34)],
        score=85
    )
    session_db.add_session(session4)

    # Listing sessions
    print("All Sessions:", session_db.list_sessions())

    # Getting a specific session
    print(f"Session for {current_time_1}:", session_db.get_session(current_time_1))

    # Deleting a session
    session_db.delete_session(session_to_delete_date)

    # Listing sorted sessions by date in ascending order
    print("Sorted Sessions by Date Ascending:", session_db.get_sorted_sessions(sort_by='date', ascending=True))

    # Listing sorted sessions by date in descending order
    print("Sorted Sessions by Date Descending:", session_db.get_sorted_sessions(sort_by='date', ascending=False))

    # Listing sorted sessions by score in ascending order
    print("Sorted Sessions by Score Ascending:", session_db.get_sorted_sessions(sort_by='score', ascending=True))

    # Listing sorted sessions by score in descending order
    print("Sorted Sessions by Score Descending:", session_db.get_sorted_sessions(sort_by='score', ascending=False))
