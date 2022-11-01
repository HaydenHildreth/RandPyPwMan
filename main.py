import os
import string
import secrets
import tkinter.messagebox
import pyperclip
import passlib
import tkinter as tk
from tkinter.ttk import *

window = tk.Tk()
window.title('RandPyPwGen v.0.1.7')
window.geometry("800x600")
name = os.getlogin()
alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
password = ""
pw_len = 0
entry_len = tk.StringVar()
columns = ('Site name', 'Username', 'Password')
site_name = ''
username = ''
password_str = ''

# TO DO:
# 1. Add scrollbar functionality
# 2. Add groups (Streaming, random, sports, etc... Groups of PWs)
# 3. Connect to DB -- add/remove from DB/table -- mysql, sql_lite, etc...
# 4. Encrypt/Decrypt passwords - Also, display raw passwords in Treeview
# 5. Fix UI
# 6. Splashscreen/login page
# 7. Make UI fit screen (grow/shrink with window size)
# ? (not sure if it will be implemented) NOT NULL functionality? Should things be allowed to be blank?


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
    site_name = ipsn.get()
    username = ipun.get()
    password_str = ippw.get()
    tvData.insert(parent='', index='end', values=(site_name, username, password_str))
    """
    INSERT INTO DB
    """
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
    global password
    pyperclip.copy(password)


def deleteRecord():
    sel = tvData.selection()[0]
    tvData.delete(sel)
    """
    REMOVE FROM DB
    """


def editRecord():
    global ipsn
    global ipun
    global ippw
    global new
    cur = tvData.focus()
    v = tvData.item(cur)
    d = v['values']
    sn = d[0]
    un = d[1]
    pw = d[2]
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
    print(cur)
    """
    ERROR HANDLING FOR IF EDITRECORD() IS CLICKED WITH NOTHING SELECTED
    """


def exit_button():
    new.destroy()


def update_info():
    global ipsn
    global ipun
    global ippw
    global new
    sel = tvData.focus()
    val = tvData.item(sel, values=(ipsn.get(), ipun.get(), ippw.get()))
    """
    EDIT IN DB
    """
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


greeting = tk.Label(window, text=f"Greetings {name}.")
greeting.grid(row=0, column=0, sticky=tk.W)
t = tk.Label(window, text="Please input desired password length:")
t.grid(row=1, column=0, sticky=tk.E + tk.W)
input_text = tk.Entry(window, textvariable=entry_len)
input_text.grid(row=1, column=1, sticky=tk.E + tk.W)
print_pw = tk.Label(window, text=f"Your password is: {password}")
print_pw.grid(row=2, column=0, sticky=tk.E + tk.W)
sendBtn = tk.Button(window, text="Generate", command=click)
copyBtn = tk.Button(window, text="Copy", command=copy)
addBtn = tk.Button(window, text="Add", command=add_button)
sendBtn.grid(row=3, column=0, sticky=tk.E + tk.W)
copyBtn.grid(row=3, column=1, sticky=tk.E + tk.W)
addBtn.grid(row=3, column=2, sticky=tk.E + tk.W)
tvData = Treeview(window, columns=columns, show='headings')
tvData.grid(row=4, column=0, columnspan=5)
tvData.heading('Site name', text='Site name')
tvData.heading('Username', text='Username')
tvData.heading('Password', text='Password')
deleteBtn = tk.Button(window, text="Delete", command=deleteRecord)
deleteBtn.grid(row=5, column=0, sticky=tk.E + tk.W)
editBtn = tk.Button(window, text="Edit", command=editRecord)
editBtn.grid(row=5, column=1, sticky=tk.E + tk.W)


tvData.insert(parent='', index='end', values=("Test", "Testt", "Testtt"))
tvData.insert(parent='', index='end', values=("Netflix", "hayden@gmail.org", "Testtt"))
tvData.insert(parent='', index='end', values=("HackerRank", "steven@linux.net", "BadPassword123"))
tvData.insert(parent='', index='end', values=("Debug", "debugging@replacethisemail.com", "ahhhh281"))
tvData.insert(parent='', index='end', values=("Please", "Work", "Now"))
tvData.insert(parent='', index='end', values=("Test", "Testt", "Testtt"))
tvData.insert(parent='', index='end', values=("Netflix", "hayden@gmail.org", "Testtt"))
tvData.insert(parent='', index='end', values=("HackerRank", "steven@linux.net", "BadPassword123"))
tvData.insert(parent='', index='end', values=("Debug", "debugging@replacethisemail.com", "ahhhh281"))
tvData.insert(parent='', index='end', values=("Please", "Work", "Now"))
tvData.insert(parent='', index='end', values=("Test", "Testt", "Testtt"))
tvData.insert(parent='', index='end', values=("Netflix", "hayden@gmail.org", "Testtt"))
tvData.insert(parent='', index='end', values=("HackerRank", "steven@linux.net", "BadPassword123"))
tvData.insert(parent='', index='end', values=("Debug", "debugging@replacethisemail.com", "ahhhh281"))
tvData.insert(parent='', index='end', values=("Please", "Work", "Now"))


window.mainloop()
