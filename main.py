import string
import secrets
import tkinter.messagebox
import pyperclip
import sqlite3
import tkinter as tk
from cryptography.fernet import Fernet
from tkinter.ttk import *


window = tk.Tk()
window.title('RandPyPwGen v.0.4.5')
window.geometry('800x600')
alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
password = ""
pw_len = 0
entry_len = tk.StringVar()
columns = ('ID', 'Site name', 'Username', 'Password')
site_name = ''
username = ''
password_str = ''

try:
    conn = sqlite3.connect('db/data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM data")
    records = c.fetchall()
except sqlite3.OperationalError:
    tkinter.messagebox.showerror(title="SQLite not installed", message="Please install SQLite before use.")
    exit()


try:
    conn2 = sqlite3.connect('db/unlock.db')
    c2 = conn2.cursor()
    c2.execute("SELECT enc_key FROM master")
    records2 = c2.fetchall()
    conv = records2[0]
    conv2 = conv[0]
    key = conv2
    f = Fernet(key)
except sqlite3.OperationalError:
    tkinter.messagebox.showerror(title="Encryption key not found", message="Please run install.py again.")
    exit()


# TO DO:
# 1. Add scrollbar functionality
# 2. Add groups (Streaming, random, sports, etc... Groups of PWs)
# 3. Encrypt/Decrypt passwords - Also, display decrypted passwords in Treeview
# 4. Fix UI
# 5. Splashscreen/login page
# 6. Make UI fit screen (grow/shrink with window size)


def click():
    global password
    global pw_len
    try:
        pw_len = int(entry_len.get())
        if pw_len > 100 or pw_len <= 0:
            raise RuntimeError

        password = ''.join(secrets.choice(alphabet) for i in range(pw_len))
        print_pw.configure(text=f"Your password is {password}")
    except ValueError:
        tkinter.messagebox.showerror(title="Invalid input", message="Enter an integer...")
    except RuntimeError:
        tkinter.messagebox.showerror(title="Invalid input", message="Number must be positive and under 101 characters")


def new_window():
    global site_name
    global username
    global password_str
    global ipsn
    global ipun
    global ippw
    global new
    new = tk.Toplevel(window)
    new.title("Add new site...")
    new.geometry("200x200")
    lblsn = Label(new, text="Site name:")
    lblsn.grid()
    ipsn = tk.Entry(new, textvariable=site_name)
    ipsn.grid()
    lblun = Label(new, text="Username:")
    lblun.grid()
    ipun = tk.Entry(new, textvariable=username)
    ipun.grid()
    lblpw = Label(new, text="Password:")
    lblpw.grid()
    ippw = tk.Entry(new, textvariable=password_str)
    ippw.grid()
    btnSubmit = Button(new, text="Add account", command=insert_info)
    btnSubmit.grid()
    btnCancel = Button(new, text="Cancel", command=cancel_button)
    btnCancel.grid()
    btnExit = Button(new, text="Exit", command=exit_button)
    btnExit.grid()
    ippw.insert(0, password)


def insert_info():
    global index
    site_name = ipsn.get()
    username = ipun.get()
    password_str = ippw.get()

    enc_test = password_str
    enc_test = bytes(enc_test, 'utf-8')
    test = f.encrypt(enc_test)
    print(test)

    tvData.insert(parent='', index='end', values=(index, site_name, username, password_str))
    c.execute("INSERT INTO data VALUES (?,?,?,?)", (index, site_name, username, password_str))
    index = index + 1
    conn.commit()
    new.destroy()


def cancel_button():
    ipsn.delete(0, 'end')
    ipun.delete(0, 'end')
    ippw.delete(0, 'end')


def add_button():
    pw_len_verify = int(len(password))
    if pw_len_verify > 100 or pw_len_verify <= 0:
        raise RuntimeError(tkinter.messagebox.showerror(title="Invalid usage", message="Generate a password first..."))
    else:
        new_window()


def copy():
    sel = tvData.selection()[0]
    item = tvData.item(sel)
    v = item['values']
    val = v[3]
    pyperclip.copy(val)


def deleteRecord():
    try:
        sel = tvData.selection()[0]
        v = tvData.item(sel)
        tvData.delete(sel)
        d = v['values']
        iid = d[0]
        c.execute("DELETE FROM data WHERE id = ?", (iid,))
        conn.commit()
    except IndexError:
        tkinter.messagebox.showerror(title="Cannot delete record", message="Please choose a record to delete.")


def editRecord():
    global ipsn
    global ipun
    global ippw
    global new
    try:
        cur = tvData.focus()
        v = tvData.item(cur)
        d = v['values']
        sn = d[1]
        un = d[2]
        pw = d[3]
        new = tk.Toplevel(window)
        new.title("Add new site...")
        new.geometry("200x200")
        lblsn = Label(new, text="Site name:")
        lblsn.grid()
        ipsn = tk.Entry(new, textvariable=site_name)
        ipsn.grid()
        lblun = Label(new, text="Username:")
        lblun.grid()
        ipun = tk.Entry(new, textvariable=username)
        ipun.grid()
        lblpw = Label(new, text="Password:")
        lblpw.grid()
        ippw = tk.Entry(new, textvariable=password_str)
        ippw.grid()
        btnSubmit = Button(new, text="Update", command=update_info)
        btnSubmit.grid()
        btnCancel = Button(new, text="Cancel", command=cancel_edit)
        btnCancel.grid()
        btnExit = Button(new, text="Exit", command=exit_button)
        btnExit.grid()
        ipsn.insert(0, sn)
        ipun.insert(0, un)
        ippw.insert(0, pw)
    except IndexError:
        tkinter.messagebox.showerror(title="Cannot edit record", message="Please choose a record to edit.")


def exit_button():
    new.destroy()


def update_info():
    global ipsn
    global ipun
    global ippw
    global new
    sel = tvData.focus()
    item = tvData.item(sel)
    get_values = item['values']
    selected_index = get_values[0]
    val = tvData.item(sel, values=(selected_index, ipsn.get(), ipun.get(), ippw.get()))
    values = []
    temp_sn = ipsn.get()
    temp_un = ipun.get()
    temp_pw = ippw.get()
    values.append(temp_sn)
    values.append(temp_un)
    values.append(temp_pw)
    c.execute("UPDATE data SET site = (?), username = (?), password = (?) WHERE id = (?)", (values[0], values[1], values[2], selected_index))
    conn.commit()
    new.destroy()


def cancel_edit():
    global ipsn
    global ipun
    global ippw
    cur = tvData.focus()
    v = tvData.item(cur)
    d = v['values']
    sn = d[0]
    un = d[1]
    pw = d[2]
    ipsn.delete(0, 'end')
    ipun.delete(0, 'end')
    ippw.delete(0, 'end')
    ipsn.insert(0, sn)
    ipun.insert(0, un)
    ippw.insert(0, pw)


t = tk.Label(window, text="Please input desired password length:")
t.grid(row=1, column=0, sticky=tk.E + tk.W)
input_text = tk.Entry(window, textvariable=entry_len)
input_text.grid(row=1, column=1, sticky=tk.E + tk.W)
print_pw = tk.Label(window, text=f"Your password is: {password}")
print_pw.grid(row=2, column=0, sticky=tk.E + tk.W)
sendBtn = tk.Button(window, text="Generate", command=click)
addBtn = tk.Button(window, text="Add", command=add_button)
sendBtn.grid(row=3, column=0, sticky=tk.E + tk.W)
addBtn.grid(row=3, column=1, sticky=tk.E + tk.W)
sendBtn.config(height=2)
addBtn.config(height=2)
tvData = Treeview(window, columns=columns, show='headings')
tvData.grid(row=4, column=0, columnspan=5, sticky='NSEW')
window.grid_rowconfigure(4, weight=1)
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)
window.grid_columnconfigure(2, weight=1)
window.grid_columnconfigure(3, weight=1)
window.grid_columnconfigure(4, weight=1)
tvData.heading('Site name', text='Site name')
tvData.heading('Username', text='Username')
tvData.heading('Password', text='Password')
tvData.heading('ID', text='ID')
tvScrollbar = Scrollbar()
tvScrollbar.config(command=tvData.yview)
tvData.config(yscrollcommand=tvScrollbar.set)
tvScrollbar.grid(row=4, column=4, sticky='NSE')
deleteBtn = tk.Button(window, text="Delete", command=deleteRecord)
deleteBtn.grid(row=5, column=0, rowspan=1, sticky=tk.E + tk.W + tk.N + tk. S)
editBtn = tk.Button(window, text="Edit", command=editRecord)
editBtn.grid(row=5, column=1, rowspan=1, sticky=tk.E + tk.W + tk.N + tk.S)
copyBtn = tk.Button(window, text="Copy", command=copy)
copyBtn.grid(row=5, column=2, rowspan=1, sticky=tk.E + tk.W + tk.N + tk.S)
deleteBtn.config(height=3)
editBtn.config(height=3)
copyBtn.config(height=3)


count = 0
for i in records:
    tvData.insert(parent='', index='end', values=(records[count][0], records[count][1], records[count][2], records[count][3]))
    count += 1


last = c.execute("SELECT * FROM data ORDER BY id DESC LIMIT 1")
last = c.fetchone()


if last is None:
    index = 0
else:
    index = last[0] + 1

window.mainloop()
