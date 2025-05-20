import sqlite3
from datetime import datetime

conn = sqlite3.connect('openAiFinal.db', timeout=10.0)
cursor = conn.cursor()

# Used SQLite documentation for setting up foreign keys and other setups, https://sqlite.org/foreignkeys.html
# This file is exclusivly used to retrieve data from sqlite tables and save data to them
# ChatGpt how to do auto increment for ids
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_created TEXT NOT NULL,
        name TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        message TEXT NOT NULL,
        source TEXT NOT NULL,
        date_created TEXT NOT NULL,
        FOREIGN KEY(session_id) REFERENCES Sessions(id)
    )
''')


def get_messages_by_session_id_order_by_date_asc(session_id: int) -> list[str]:
    """
    Gets all of the messages with the session_id provided, returns a list of messages ordered by date created ascending

    :param session_id: used to query the messages table 
    :returns: all messages with the corrisponding session_id
    """
    cursor.execute(
        "SELECT source, message, date_created FROM Messages WHERE session_id = ? ORDER BY date_created ASC", (session_id,))
    return cursor.fetchall()


def save_message(session_id: int, message: str, source: str) -> None:
    """
    Saves a message to the message table, could either be the user's prompt message or the LLM's response.
    It is saved with the current session_id

    :param session_id: used to save identify which session the message is linked to
    :param message: the message that we wish to save to the messages table
    :param source: The creator of this message
    """
    date = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO Messages (session_id, message, date_created, source) VALUES (?, ?, ?, ?)",
        (session_id, message, date, source))
    conn.commit()


def save_new_session() -> int:
    """
    Creates a new session in the session table and return the created session_id
    Returns the auto incremented id back so the UI can use for chat sessions

    : returns: a session_id that was randomly created
    """
    name = "Session"
    # chatgpt how to do iso format dates
    date = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO Sessions (date_created, name) VALUES (?, ?)", (date, name))
    conn.commit()
    # https://www.sqlite.org/c3ref/last_insert_rowid.html
    return cursor.lastrowid


def get_sessions_with_session_id(session_id: str) -> list[str]:
    """
     Used to pull all sessions from the session table with the matching session_id

     :param session_id: used to query whether any sessions exist with the session_id
     :returns: a list of ids from the session table matching the param session_id
     """
    cursor.execute("SELECT id FROM Sessions WHERE id = ?", (session_id,))
    return cursor.fetchall()
