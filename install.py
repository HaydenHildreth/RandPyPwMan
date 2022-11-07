import sqlite3

conn = sqlite3.connect('db/data.db')
c = conn.cursor()

c.execute("CREATE TABLE data(id, site, username, password)")
