import os
import string
import secrets
import tkinter.messagebox
import pyperclip
import passlib
import tkinter as tk
from tkinter.ttk import *

window = tk.Tk()
window.title('RandPyPwGen v.0.1.5')
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
# - Splashscreen/login page
# - Encrypt/Decrypt passwords - Also, display raw passwords in Treeview
# - Edit/Remove records
# - Connect to DB
# - Fix UI
# - Add groups (Streaming, random, sports, etc... Groups of PWs)


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
    ippw.insert(0, password)


def insert_info():
    site_name = ipsn.get()
    username = ipun.get()
    password_str = ippw.get()
    tvData.insert(parent='', index='end', values=(site_name, username, password_str))
    # close window


def add_button():
    pw_len_verify = int(len(password))
    if pw_len_verify > 100 or pw_len_verify <= 0:
        raise RuntimeError(tkinter.messagebox.showerror(title="Invalid usage", message="Generate a password first..."))
    else:
        new_window()


def copy():
    global password
    pyperclip.copy(password)


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


tvData.insert(parent='', index='end', values=("Test", "Testt", "Testtt"))


window.mainloop()
