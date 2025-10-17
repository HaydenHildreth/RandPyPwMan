# ONLY RUN THIS FILE IF YOU WERE USING A VERSION PRIOR TO
# v1.0.2. IF YOU'VE JUST INSTALLED THE PROGRAM DO NOT
# RUN THE FOLLOWING SCRIPT.

import sqlite3
import tkinter
from tkinter import messagebox

try:
    conn = sqlite3.connect('db/data.db')
    c = conn.cursor()
    c.execute("ALTER TABLE data ADD COLUMN date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
    c.execute("ALTER TABLE data ADD COLUMN date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
    c.execute("UPDATE data SET date_created = CURRENT_TIMESTAMP WHERE date_created IS NULL;")
    c.execute("UPDATE data SET date_modified = CURRENT_TIMESTAMP WHERE date_modified IS NULL;")
    conn.commit()
    conn.close()
    tkinter.messagebox.showinfo(title="Success", message="Database updated successfully!")
except sqlite3.OperationalError as e:
    tkinter.messagebox.showerror(title="Database Error", message=f"Error updating database: {str(e)}")
    exit()
