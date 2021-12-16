import os
import string
import secrets
from tkinter import *


window = Tk()
window.title('RandPyPwGen v0.1')

# Get username NOTE: This might be Windows only, need to look into in the future
name = os.getlogin()

alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
password = ""


def click():
    global password
    password = ''.join(secrets.choice(alphabet) for i in range(20))
    print_pw.configure(text=f"Your password is {password}.")


greeting = Label(window, text=f"Hello {name}.").pack()
"""
Will be the input for future dev
"""
# t = Label(window, text="Please input desired password length:").pack()
# input_text = Entry().pack()
print_pw = Label(window, text=f"Your password is {password}.")
print_pw.pack()


sendBtn = Button(window, text="Generate!", command=click)
sendBtn.pack(side=BOTTOM)
window.mainloop()
