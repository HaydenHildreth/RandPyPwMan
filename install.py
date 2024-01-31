import sqlite3
import bcrypt
from cryptography.fernet import Fernet
import os
import tkinter as tk


def set_master():
    global password
    password = tb_password.get()
    password = bytes(password, 'utf-8')
    hash_master = bcrypt.hashpw(password, bcrypt.gensalt())
    enc_key = Fernet.generate_key()
    c2.execute("INSERT INTO master VALUES (?,?)", (hash_master, enc_key,))
    conn2.commit()
    window.destroy()


os.mkdir('./db/')
conn = sqlite3.connect('db/data.db')
c = conn.cursor()

c.execute("CREATE TABLE data(id INTEGER PRIMARY KEY,"
          "site varchar(100) NOT NULL,"
          "username varchar(100) NOT NULL,"
          "password varchar(100) NOT NULL,"
          "groups varchar(100) NOT NULL)")


conn2 = sqlite3.connect('db/unlock.db')
c2 = conn2.cursor()

c2.execute("CREATE TABLE master(key varchar(255), "
           "enc_key varchar(255))")

window = tk.Tk()
window.title('RandPyPwMan setup')
password = b''

lbl_password = tk.Label(window, text='Enter master password:')
tb_password = tk.Entry(window, textvariable=password)
lbl_password.grid(column=0, row=0)
tb_password.grid(column=1, row=0)
btn_create = tk.Button(window, text='Set master password', command=set_master)
btn_create.grid(column=0, row=1, columnspan=2)


window.mainloop()

import splashscreen
