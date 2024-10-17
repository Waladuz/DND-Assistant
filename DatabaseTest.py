import sqlite3


connection = sqlite3.connect('assets.db')
cursor = connection.cursor()

cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS items
    (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    type INTEGER NOT NULL,
    baseValue INTEGER
    )
    '''
)

cursor.execute('''
INSERT INTO items (name, type, baseValue)
VALUES (?, ?, ?)
''', ('Long Sword', 1, 5))

connection.commit()

