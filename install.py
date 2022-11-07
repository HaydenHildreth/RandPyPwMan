import sqlite3

conn = sqlite3.connect('db/data.db')
c = conn.cursor()

c.execute("CREATE TABLE data(id INTEGER PRIMARY KEY,"
          "site varchar(100) NOT NULL,"
          "username varchar(100) NOT NULL,"
          "password varchar(100) NOT NULL)")
