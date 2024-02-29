import string
import secrets
import tkinter.messagebox
import pyperclip
import sqlite3
import tkinter as tk
import webbrowser
from cryptography.fernet import Fernet
from tkinter.ttk import *
from tkinter import filedialog


window = tk.Tk()
window.title('RandPyPwGen v.0.7.2')
window.geometry('800x600')
alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
password = ""
pw_len = 0
entry_len = tk.StringVar()
entry_search = tk.StringVar()
columns = ('ID', 'Site name', 'Username', 'Password', 'Group')
site_name = ''
username = ''
password_str = ''
group = ''

try:
    conn = sqlite3.connect('./db/data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM data")
    records = c.fetchall()
except sqlite3.OperationalError:
    # THIS ERROR COULD BE MADE BETTER, IS SQL LITE INSTALLED, OR IS INSTALL.PY NOT RAN? MAKE MORE INFORMATIONAL
    # I.E. DATABASE FOLDER NOT FOUND, PLEASE RUN INSTALL.PY BEFORE EXECUTING PROGRAM
    # OR SQLITE3 NOT FOUND, PLEASE SEE DOCUMENTATION AND INSTALL BEFORE USING PROGRAM
    tkinter.messagebox.showerror(title="SQLite not installed", message="Please install SQLite before use.")
    exit()


try:
    conn2 = sqlite3.connect('./db/unlock.db')
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
# Add groups (Streaming, random, sports, etc... Groups of PWs)
# Fix UI
# Make UI fit screen (grow/shrink with window size)


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
    global group
    global ipsn
    global ipun
    global ippw
    global ipgroup
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
    lblgroup = Label(new, text="Group:")
    lblgroup.grid()
    ipgroup = tk.Entry(new, textvariable=group)
    ipgroup.grid()
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
    group = ipgroup.get()

    pw_copy = bytes(password_str, 'utf-8')
    enc = f.encrypt(pw_copy)

    tvData.insert(parent='', index='end', values=(index, site_name, username, password_str, group))
    c.execute("INSERT INTO data VALUES (?,?,?,?,?)", (index, site_name, username, enc, group))
    index = index + 1
    conn.commit()
    new.destroy()


def cancel_button():
    ipsn.delete(0, 'end')
    ipun.delete(0, 'end')
    ippw.delete(0, 'end')
    ipgroup.delete(0, 'end')


def add_button():
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
    global ipgroup
    global new
    try:
        # index group = d[4] out of range error
        cur = tvData.focus()
        v = tvData.item(cur)
        d = v['values']
        sn = d[1]
        un = d[2]
        pw = d[3]
        groups = d[4]
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
        lblgroup = Label(new, text="Group:")
        lblgroup.grid()
        ipgroup = tk.Entry(new, textvariable=group)
        ipgroup.grid()
        btnSubmit = Button(new, text="Update", command=update_info)
        btnSubmit.grid()
        btnCancel = Button(new, text="Cancel", command=cancel_edit)
        btnCancel.grid()
        btnExit = Button(new, text="Exit", command=exit_button)
        btnExit.grid()
        ipsn.insert(0, sn)
        ipun.insert(0, un)
        ippw.insert(0, pw)
        ipgroup.insert(0, groups)
    except IndexError:
        tkinter.messagebox.showerror(title="Cannot edit record", message="Please choose a record to edit.")


def exit_button():
    new.destroy()


def update_info():
    global ipsn
    global ipun
    global ippw
    global ipgroup
    global new
    sel = tvData.focus()
    item = tvData.item(sel)
    get_values = item['values']
    selected_index = get_values[0]
    val = tvData.item(sel, values=(selected_index, ipsn.get(), ipun.get(), ippw.get(), ipgroup.get()))

    pw_copy = bytes(ippw.get(), 'utf-8')
    enc = f.encrypt(pw_copy)

    values = []
    temp_sn = ipsn.get()
    temp_un = ipun.get()
    temp_pw = ippw.get()
    temp_group = ipgroup.get()
    values.append(temp_sn)
    values.append(temp_un)
    values.append(enc)
    values.append(temp_group)
    c.execute("UPDATE data SET site = (?), username = (?), password = (?), groups = (?) WHERE id = (?)", (values[0], values[1], values[2], values[3], selected_index))
    conn.commit()
    new.destroy()


def cancel_edit():
    """
    This function clears the input boxes and puts the original un-edited
    passwords back in the input boxes when the cancel button is clicked
    """
    global ipsn
    global ipun
    global ippw
    global ipgroup
    cur = tvData.focus()
    v = tvData.item(cur)
    d = v['values']
    sn = d[1]
    un = d[2]
    pw = d[3]
    gr = d[4]
    ipsn.delete(0, 'end')
    ipun.delete(0, 'end')
    ippw.delete(0, 'end')
    ipgroup.delete(0, 'end')
    ipsn.insert(0, sn)
    ipun.insert(0, un)
    ippw.insert(0, pw)
    ipgroup.insert(0, gr)


def clear_button():
    """
    This function clears the password, and password length
    """
    global pw_len
    global password
    global password_str
    pw_len = 0
    password = ''
    password_str = ''
    print_pw.configure(text=f"Your password is {password}")  # Update password label


def open_help():
    """
    This function opens the GitHub repository in the default web browser
    """
    webbrowser.open("https://github.com/HaydenHildreth/RandPyPwMan")


def import_passwords():
    """
    This function will be used to import passwords into the data table
    it should be able to see the group from import_window() then it will
    read the .CSV file and add it to the database and treeview. The index
    of the last password should be found when this is clicked, in case the
    user has added any passwords whilst the import window has been open.
    """
    global c
    global source
    last_import = c.execute("SELECT * FROM data ORDER BY id DESC LIMIT 1")
    last_import = c.fetchone()
    if last_import is None:
        last_index = 0
    else:
        last_index = last_import[0] + 1
    print(last_index)
    source = entry_data_source.get()
    print(source)
    pass


def import_window():
    """
    Opens new window for importing passwords
    """
    global source
    global entry_data_source
    global filename
    source_list = ["", "Chrome", "Firefox", "Safari"]
    new_import_window = tk.Toplevel(window)
    source = tk.StringVar(new_import_window)
    new_import_window.title("Import passwords")
    new_import_window.geometry("200x200")
    data_source = Label(new_import_window, text="Data source:")
    data_source.grid()
    # source.set(source_list[0])
    source.set("Select an option")
    entry_data_source = OptionMenu(new_import_window, source, *source_list)
    entry_data_source.grid()
    file_btn = Button(new_import_window, text="Browse files", command=browse_files)
    file_btn.grid()
    btn_import = Button(new_import_window, text="Import password", command=import_passwords)
    btn_import.grid()
    btn_import_exit = Button(new_import_window, text="Exit", command=new_import_window.destroy)
    btn_import_exit.grid()


def browse_files():
    global filename
    filename = filedialog.askopenfilename(initialdir="/", title="Select a file", filetypes=(("CSV files", "*.csv"),))
    print(filename)
    pass



def create_group():
    """
    This function will create a group, which you could then assign to a password
    """
    pass


def search():
    global entry_search
    global c
    entry_search = input_search.get()

    c = conn.cursor()
    c.execute("SELECT * FROM data where site like ? "
              "OR username like ? OR "
              "groups like ?"
              "ORDER BY id",('%'+entry_search+'%','%'+entry_search+'%','%'+entry_search+'%',))
    search_records = c.fetchall()

    # Clear treeview
    tvData.delete(*tvData.get_children())

    # Put search/filtered data to treeview
    # It needs to decrypt because it is accessing db directly
    count_search = 0
    for j in search_records:
        decrypted_search = f.decrypt(search_records[count_search][3])
        decrypted_search = decrypted_search.decode('utf-8')
        tvData.insert(parent='', index='end', values=(search_records[count_search][0], search_records[count_search][1], search_records[count_search][2], decrypted_search, search_records[count_search][4]))
        count_search += 1


def set_tv_filter():
    pass


t = tk.Label(window, text="Please input desired password length:")
t.grid(row=1, column=0, sticky=tk.E + tk.W)
input_text = tk.Entry(window, textvariable=entry_len)
input_text.grid(row=1, column=1, sticky=tk.E + tk.W)
print_pw = tk.Label(window, text=f"Your password is: {password}")
print_pw.grid(row=2, column=0, sticky=tk.E + tk.W)
sendBtn = tk.Button(window, text="Generate", command=click)
addBtn = tk.Button(window, text="Add", command=add_button)
clearBtn = tk.Button(window, text="Clear", command=clear_button)
add_group_btn = tk.Button(window, text="Add/Remove group", command='')
sendBtn.grid(row=3, column=0, sticky=tk.E + tk.W)
addBtn.grid(row=3, column=1, sticky=tk.E + tk.W)
clearBtn.grid(row=3, column=2, sticky=tk.E + tk.W)
add_group_btn.grid(row=3, column=3, sticky=tk.E + tk.W)
sendBtn.config(height=2)
addBtn.config(height=2)
clearBtn.config(height=2)
add_group_btn.config(height=2)

lbl_search = Label(window, text="Search:")
lbl_search.grid(row=4, column=0, sticky=tk.E)
input_search = tk.Entry(window, textvariable=entry_search)
input_search.grid(row=4, column=1, sticky=tk.E + tk.W)
btn_search = tk.Button(window, text="Search", command=search)
btn_search.grid(row=4, column=2, sticky=tk.E + tk.W)

tvData = Treeview(window, columns=columns, show='headings')
tvData.grid(row=5, column=0, columnspan=5, sticky='NSEW')
window.grid_rowconfigure(5, weight=1)
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)
window.grid_columnconfigure(2, weight=1)
window.grid_columnconfigure(3, weight=1)
window.grid_columnconfigure(4, weight=1)
tvData.heading('Site name', text='Site name')
tvData.heading('Username', text='Username')
tvData.heading('Password', text='Password')
tvData.heading('ID', text='ID')
tvData.heading('Group', text='Group')
tvScrollbarRight = Scrollbar()
tvScrollbarRight.config(command=tvData.yview)
tvData.config(yscrollcommand=tvScrollbarRight.set)
tvScrollbarBottom = Scrollbar(tvData, orient='horizontal')      # orient='horizontal'
tvScrollbarBottom.config(command=tvData.xview)
tvScrollbarRight.grid(row=5, column=4, sticky='NSE')
tvScrollbarBottom.grid(row=5, column=0, sticky='N', columnspan=6)
deleteBtn = tk.Button(window, text="Delete", command=deleteRecord)
deleteBtn.grid(row=6, column=0, rowspan=1, sticky=tk.E + tk.W + tk.N + tk. S)
editBtn = tk.Button(window, text="Edit", command=editRecord)
editBtn.grid(row=6, column=1, rowspan=1, sticky=tk.E + tk.W + tk.N + tk.S)
copyBtn = tk.Button(window, text="Copy", command=copy)
copyBtn.grid(row=6, column=2, rowspan=1, sticky=tk.E + tk.W + tk.N + tk.S)
deleteBtn.config(height=3)
editBtn.config(height=3)
copyBtn.config(height=3)


# MENU SECTION
menubar = tk.Menu(window)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Import", command=import_window)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=window.quit)
menubar.add_cascade(label="File", menu=filemenu)


helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="Help Index", command=open_help)
menubar.add_cascade(label="Help", menu=helpmenu)


count = 0
for i in records:
    decrypted = f.decrypt(records[count][3])
    decrypted = decrypted.decode('utf-8')
    tvData.insert(parent='', index='end', values=(records[count][0], records[count][1], records[count][2], decrypted, records[count][4]))
    count += 1


last = c.execute("SELECT * FROM data ORDER BY id DESC LIMIT 1")
last = c.fetchone()


if last is None:
    index = 0
else:
    index = last[0] + 1

window.config(menu=menubar)
window.mainloop()
