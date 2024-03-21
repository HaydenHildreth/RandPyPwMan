# ONLY RUN THIS FILE IF YOU WERE USING A VERSION PRIOR TO
# v0.7.11/0.8.0. IF YOU'VE JUST INSTALLED THE PROGRAM DO NOT
# RUN THE FOLLOWING SCRIPT.

import sqlite3
import tkinter
from tkinter import messagebox

try:
    conn = sqlite3.connect('../db/data.db')
    c = conn.cursor()
    c.execute("ALTER TABLE data DROP COLUMN groups;")
except sqlite3.OperationalError:
    tkinter.messagebox.showerror(title="SQLite not installed", message="Please install SQLite before use.")
    exit()