import tkinter as tk
import tkinter.messagebox
import sqlite3
import bcrypt


def unlock():
    global master
    global tb_ss

    master = tb_ss.get()
    master = bytes(master, 'utf-8')

    ss_conn = sqlite3.connect('db/unlock.db')
    ss_c = ss_conn.cursor()

    ss_c.execute("SELECT * FROM master")
    fetch = ss_c.fetchone()
    ss_key = fetch[0]

    if bcrypt.checkpw(master, ss_key):
        splashscreen.destroy()
        import main
    else:
        tk.messagebox.showerror(title="Incorrect password...", message="Incorrect master key.")


splashscreen = tk.Tk()
splashscreen.title('RandPyPwGen login')
splashscreen.geometry('200x50')


key = b''
master = b''
lbl_ss = tk.Label(splashscreen, text='master key:')
tb_ss = tk.Entry(splashscreen, textvariable=master)
btn_ss = tk.Button(splashscreen, text='Unlock', command=unlock)
lbl_ss.grid(row=0, column=0)
tb_ss.grid(row=0, column=1)
btn_ss.grid(column=0, row=1, columnspan=2)


splashscreen.mainloop()
