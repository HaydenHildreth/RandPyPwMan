import os
import string
import random
from tkinter import *

window = Tk()
window.title('RandPyPwGen v.0.0')

# Get username NOTE: This might be Windows only, need to look into in the future
name = os.getlogin()

textOnly = string.ascii_letters
textAndNumbers = string.digits + string.ascii_letters
textNumberAndSpecial = string.digits + string.punctuation + string.ascii_letters

pw = ""
pwLen = 0
var = StringVar(window, "1")

difficulty = {"Text only": "1",
              "Text and numbers": "2",
              "Text, numbers and special characters": "3"}

greeting = Label(window, text=f"Hello {name}.")
greeting.pack()
t = Label(window, text="Please input desired password length:")
t.pack()
inputText = Text(window, height=1, width=3)
inputText.pack()

for (text, value) in difficulty.items():
    Radiobutton(window, text=text, variable=var, value=value).pack(side=TOP, ipady=5)

sendBtn = Button(window, text="Generate")
sendBtn.pack(side=BOTTOM)

window.mainloop()
