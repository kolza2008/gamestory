import sqlite3

conn = sqlite3.connect('db.db')
cur = conn.cursor()

cur.execute('DELETE *  FROM tokens')
cur.execute()