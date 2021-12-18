import os
import string
import secrets
import tkinter.messagebox

import pyperclip
from tkinter import *


window = Tk()
window.title('RandPyPwGen v.0.1')
window.geometry("800x600")
name = os.getlogin()
alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
password = ""
pw_len = 12  # Default length if not specified
entry_len = StringVar()


def click():
    global password
    global pw_len
    '''
    if not entry_len.get():
        pass
    else:
        pw_len = int(entry_len.get())
    password = ''.join(secrets.choice(alphabet) for i in range(pw_len))
    print_pw.configure(text=f"Your password is {password}")
    '''
    try:
        pw_len = int(entry_len.get())
        if pw_len > 100 or pw_len <= 0:
            raise RuntimeError

        password = ''.join(secrets.choice(alphabet) for i in range(pw_len))
        print_pw.configure(text=f"Your password is {password}")
    except ValueError:
        tkinter.messagebox.showerror(title="Invalid input", message="Enter an integer...")
        print('Enter an integer...')
    except RuntimeError:
        tkinter.messagebox.showerror(title="Invalid input", message="Password length must be non-negative and less than 100 characters")


def copy():
    global password
    pyperclip.copy(password)


greeting = Label(window, text=f"Hello {name}.").pack()
t = Label(window, text="Please input desired password length:").pack()
input_text = Entry(window, textvariable=entry_len)
input_text.pack()
print_pw = Label(window, text=f"Your password is: {password}")
print_pw.pack()
sendBtn = Button(window, text="Generate!", command=click)
copyBtn = Button(window, text="Copy!", command=copy)
sendBtn.pack(side=BOTTOM)
copyBtn.pack(side=BOTTOM)
window.mainloop()
