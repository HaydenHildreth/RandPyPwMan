import os
import string
import secrets
from tkinter import *

window = Tk()
window.title('RandPyPwGen v.0.0')

# Get username NOTE: This might be Windows only, need to look into in the future
name = os.getlogin()

low = string.ascii_lowercase
high = string.ascii_uppercase
n = string.digits
symbols = string.punctuation
mix = low + high + n + symbols
pw = ""
pwLen = 0
var = StringVar(window, "1")

difficulty = {"Text only": "1",
              "Text and numbers": "2",
              "Text, numbers and special characters": "3"}

greeting = Label(window, text=f"Hello {name}.").pack
t = Label(window, text="Please input desired password length:").pack
inputText = Text(window, height=1, width=6)
inputText.pack()

for (text, value) in difficulty.items():
    Radiobutton(window, text=text, variable=var, value=value).pack(side=TOP, ipady=2)

sendBtn = Button(window, text="Generate")
sendBtn.pack(side=BOTTOM)


def click(pw):
    pw = ''.join(secrets.choice(mix) for i in range(pwLen))
    printed = Label(window, text=f"{pw}")


window.mainloop()
