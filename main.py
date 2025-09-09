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
import csv
import bcrypt
import os
import sys
from tkinter import messagebox


# SPLASHSCREEN + PATH validation
def unlock():
    global master
    global tb_ss

    master = tb_ss.get()
    master = bytes(master, 'utf-8')

    try:
        # Check if database folder exists
        if not os.path.exists('db/'):
            tk.messagebox.showerror(
                title="Database folder not found", 
                message="Database folder not found. Please run install.py before executing the program."
            )
            exit()
        
        # Check if unlock database file exists
        if not os.path.exists('db/unlock.db'):
            tk.messagebox.showerror(
                title="Encryption key not found", 
                message="Encryption key not found. Please run install.py before executing the program."
            )
            exit()

        ss_conn = sqlite3.connect('db/unlock.db')
        ss_c = ss_conn.cursor()
        
        # Check if master table exists
        ss_c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='master'")
        if not ss_c.fetchone():
            # Unable to retrieve data
            tk.messagebox.showerror(
                title="Database not initialized", 
                message="Unable to retrieve data. Please run install.py to set up the database properly."
            )
            exit()

        ss_c.execute("SELECT * FROM master")
        fetch = ss_c.fetchone()
        
        if not fetch:
            tk.messagebox.showerror(
                title="No master password found", 
                message="No master password configured. Please run install.py to set up the database properly."
            )
            exit()
            
        ss_key = fetch[0]

        if bcrypt.checkpw(master, ss_key):
            splashscreen.destroy()
        else:
            # Wrong password
            tk.messagebox.showerror(title="Incorrect password...", message="Incorrect master key.")
            
    except sqlite3.OperationalError as e:
        tk.messagebox.showerror(
            title="Database Error", 
            message=f"Unable to access unlock database. Please run install.py.\n\nError: {str(e)}"
        )
        exit()
    except Exception as e:
        tk.messagebox.showerror(
            title="Unexpected Error", 
            message=f"An unexpected error occurred during unlock.\n\nError: {str(e)}"
        )
        exit()

# Check if database folder and database files exist
def check_database_setup():
    if not os.path.exists('./db/'):
        tkinter.messagebox.showerror(
            title="Database folder not found", 
            message="Database folder not found. Please run install.py before executing the program."
        )
        sys.exit(1)
    
    if not os.path.exists('./db/data.db'):
        tkinter.messagebox.showerror(
            title="Data file not found", 
            message="Data file not found. Data not configured correctly or corrupted. Please run install.py again to set up the program."
        )
        sys.exit(1)
    
    if not os.path.exists('./db/unlock.db'):
        tkinter.messagebox.showerror(
            title="Encryption key not found", 
            message="Encryption key not found. Please run install.py before executing the program."
        )
        sys.exit(1)

# Check database setup first
check_database_setup()

try:
    conn = sqlite3.connect('./db/data.db')
    c = conn.cursor()
    # Check if the data table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='data'")
    if not c.fetchone():
        raise sqlite3.OperationalError("Table 'data' does not exist")
    
    c.execute("SELECT * FROM data")
    records = c.fetchall()
except sqlite3.OperationalError as e:
    if "no such table" in str(e).lower() or "does not exist" in str(e).lower():
        tkinter.messagebox.showerror(
            title="Database not properly initialized", 
            message="Database tables not found. Please run install.py to set up the database properly."
        )
    else:
        tkinter.messagebox.showerror(
            title="Database error", 
            message=f"Database error occurred: {str(e)}"
        )
    sys.exit(1)
except Exception as e:
    tkinter.messagebox.showerror(
        title="Unexpected error", 
        message=f"An unexpected error occurred: {str(e)}"
    )
    sys.exit(1)


try:
    conn2 = sqlite3.connect('./db/unlock.db')
    c2 = conn2.cursor()
    # Check if the master table exists
    c2.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='master'")
    if not c2.fetchone():
        raise sqlite3.OperationalError("Table 'master' does not exist")
    
    c2.execute("SELECT enc_key FROM master")
    records2 = c2.fetchall()
    conv = records2[0]
    conv2 = conv[0]
    key = conv2
    f = Fernet(key)
except sqlite3.OperationalError as e:
    if "no such table" in str(e).lower() or "does not exist" in str(e).lower():
        tkinter.messagebox.showerror(
            title="Encryption key database not initialized", 
            message="Master password database not found. Please run install.py to set up the database properly."
        )
    else:
        tkinter.messagebox.showerror(
            title="Encryption key error", 
            message="Encryption key not found. Please run install.py again."
        )
    sys.exit(1)
except IndexError:
    tkinter.messagebox.showerror(
        title="Encryption key error", 
        message="No encryption key found in database. Please run install.py again."
    )
    sys.exit(1)
except Exception as e:
    tkinter.messagebox.showerror(
        title="Unexpected error", 
        message=f"An unexpected error occurred while setting up encryption: {str(e)}"
    )
    sys.exit(1)


# Prevent user from prematurelaty exiting splashscreen
def on_closing():
        exit()


splashscreen = tk.Tk()
splashscreen.title('RandPyPwGen login')
splashscreen.geometry('200x50')

key = b''
master = b''
lbl_ss = tk.Label(splashscreen, text='master key:')
tb_ss = tk.Entry(splashscreen, textvariable=master, show='*')
btn_ss = tk.Button(splashscreen, text='Unlock', command=unlock)
lbl_ss.grid(row=0, column=0)
tb_ss.grid(row=0, column=1)
btn_ss.grid(column=0, row=1, columnspan=2)
splashscreen.protocol("WM_DELETE_WINDOW", on_closing)
splashscreen.mainloop()


window = tk.Tk()
window.title('RandPyPwGen v.1.0.1')
window.geometry('800x600')
alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
password = ""
pw_len = 0
entry_len = tk.StringVar()
entry_search = tk.StringVar()
columns = ('ID', 'Site name', 'Username', 'Password')
site_name = ''
username = ''
password_str = ''


# Global variable to track password visibility state
passwords_visible = True
stored_passwords = {}  # Dictionary to store passwords while hidden


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

    last_insert = find_last_index()
    index_insert = last_insert + 1

    pw_copy = bytes(password_str, 'utf-8')
    enc = f.encrypt(pw_copy)

    # Add to treeview considering current visibility state
    if passwords_visible:
        tvData.insert(parent='', index='end', values=(index_insert, site_name, username, password_str))
    else:
        stored_passwords[index_insert] = password_str
        masked_password = '*' * min(len(password_str), 12)
        tvData.insert(parent='', index='end', values=(index_insert, site_name, username, masked_password))
    
    c.execute("INSERT INTO data VALUES (?,?,?,?)", (index_insert, site_name, username, enc))
    conn.commit()
    new.destroy()


def cancel_button():
    ipsn.delete(0, 'end')
    ipun.delete(0, 'end')
    ippw.delete(0, 'end')


def add_button():
    new_window()


def copy():
    sel = tvData.selection()[0]
    item = tvData.item(sel)
    v = item['values']
    item_id = v[0]
    
    # Get the actual password
    if passwords_visible:
        password_to_copy = v[3]
    else:
        password_to_copy = stored_passwords.get(item_id, v[3])
    
    pyperclip.copy(password_to_copy)


def deleteRecord():
    try:
        sel = tvData.selection()
        selection_len = len(sel)
        for j in range(selection_len):
            v = tvData.item(sel[j])
            item_id = v['values'][0]
            tvData.delete(sel[j])
            d = v['values']
            iid = d[0]
            
            # Remove from stored passwords if present
            if item_id in stored_passwords:
                del stored_passwords[item_id]
            
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
        item_id = d[0]
        sn = d[1]
        un = d[2]
        
        # Get actual password
        if passwords_visible:
            pw = d[3]
        else:
            pw = stored_passwords.get(item_id, d[3])
        
        new = tk.Toplevel(window)
        new.title("Edit record...")
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
    
    new_password = ippw.get()
    
    # Update treeview considering current visibility setting
    if passwords_visible:
        val = tvData.item(sel, values=(selected_index, ipsn.get(), ipun.get(), new_password))
    else:
        stored_passwords[selected_index] = new_password
        masked_password = '*' * min(len(new_password), 12)
        val = tvData.item(sel, values=(selected_index, ipsn.get(), ipun.get(), masked_password))

    pw_copy = bytes(new_password, 'utf-8')
    enc = f.encrypt(pw_copy)

    values = []
    temp_sn = ipsn.get()
    temp_un = ipun.get()
    temp_pw = new_password
    values.append(temp_sn)
    values.append(temp_un)
    values.append(enc)
    c.execute("UPDATE data SET site = (?), username = (?), password = (?) WHERE id = (?)", (values[0], values[1], values[2], selected_index))
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

    cur = tvData.focus()
    v = tvData.item(cur)
    d = v['values']
    item_id = d[0]
    sn = d[1]
    un = d[2]
    
    # Get actual password
    if passwords_visible:
        pw = d[3]
    else:
        pw = stored_passwords.get(item_id, d[3])
    
    ipsn.delete(0, 'end')
    ipun.delete(0, 'end')
    ippw.delete(0, 'end')
    ipsn.insert(0, sn)
    ipun.insert(0, un)
    ippw.insert(0, pw)


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
    # Update password label
    print_pw.configure(text=f"Your password is {password}") 


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
    global filename
    global new_import_window
    last_import = find_last_index()
    if last_import is None:
        last_index = 0
    else:
        last_index = last_import + 1

    import_source = source.get()

    # VARIABLE TO OPEN FILE
    file = open(filename, "r")
    reader = csv.reader(file)

    match import_source:
        case "Chrome":
            for line in reader:
                t_reader = line[0], line[2], line[3]
                pw_copy_insert = bytes(line[3], 'utf-8')
                enc_insert = f.encrypt(pw_copy_insert)

                # Add to treeview considering current visibility setting
                if passwords_visible:
                    tvData.insert(parent='', index='end', values=(last_index, line[0],  line[2],  line[3]))
                else:
                    stored_passwords[last_index] = line[3]
                    masked_password = '*' * min(len(line[3]), 12)
                    tvData.insert(parent='', index='end', values=(last_index, line[0],  line[2],  masked_password))
                
                c.execute("INSERT INTO data VALUES (?,?,?,?)", (last_index, line[0],  line[2],  enc_insert))
                last_index += 1
                conn.commit()
                new_import_window.destroy()
        case "Firefox":
            for line in reader:
                t_reader = line[0], line[1], line[2]
                pw_copy_insert = bytes(line[2], 'utf-8')
                enc_insert = f.encrypt(pw_copy_insert)

                # Add to treeview considering current visibility setting
                if passwords_visible:
                    tvData.insert(parent='', index='end', values=(last_index, line[0], line[1], line[2]))
                else:
                    stored_passwords[last_index] = line[2]
                    masked_password = '*' * min(len(line[2]), 12)
                    tvData.insert(parent='', index='end', values=(last_index, line[0], line[1], masked_password))
                
                c.execute("INSERT INTO data VALUES (?,?,?,?)", (last_index, line[0], line[1], enc_insert))
                last_index += 1
                conn.commit()
                new_import_window.destroy()


def import_window():
    """
    Opens new window for importing passwords
    """
    global source
    global entry_data_source
    global filename
    global new_import_window
    global btn_import  # <-- make it global so browse_files() can access it
    
    source_list = ["", "Chrome", "Firefox"]
    new_import_window = tk.Toplevel(window)
    source = tk.StringVar(new_import_window)
    new_import_window.title("Import passwords")
    new_import_window.geometry("200x200")
    
    data_source = Label(new_import_window, text="Data source:")
    data_source.grid()
    source.set("Select an option")
    
    entry_data_source = OptionMenu(new_import_window, source, *source_list)
    entry_data_source.grid()
    
    file_btn = Button(new_import_window, text="Browse files", command=browse_files)
    file_btn.grid()
    
    # Import button starts disabled
    btn_import = Button(new_import_window, text="Import password", command=import_passwords, state="disabled")
    btn_import.grid()
    
    btn_import_exit = Button(new_import_window, text="Exit", command=new_import_window.destroy)
    btn_import_exit.grid()


def browse_files():
    global filename
    filename = filedialog.askopenfilename(
        initialdir="/",
        title="Select a file",
        filetypes=(("CSV files", "*.csv"),)
    )
    
    # If user selected a file, enable the import button
    if filename:
        btn_import.config(state="normal")


def search():
    """
    THIS FUNCTION ALLOWS SEARCHING OF PASSWORDS, USERNAME AND SITES FROM DATABASE
    """
    global entry_search
    global c
    entry_search = input_search.get()

    c = conn.cursor()
    c.execute("SELECT * FROM data where site like ? "
              "OR username like ? "
              "ORDER BY id",('%'+entry_search+'%','%'+entry_search+'%',))
    search_records = c.fetchall()

    # Clear treeview and stored passwords
    tvData.delete(*tvData.get_children())
    stored_passwords.clear()

    # Put search/filtered data to treeview
    # It needs to decrypt because it is accessing db directly
    count_search = 0
    for j in search_records:
        decrypted_search = f.decrypt(search_records[count_search][3])
        decrypted_search = decrypted_search.decode('utf-8')
        
        if passwords_visible:
            tvData.insert(parent='', index='end', values=(search_records[count_search][0], search_records[count_search][1], search_records[count_search][2], decrypted_search))
        else:
            record_id = search_records[count_search][0]
            stored_passwords[record_id] = decrypted_search
            masked_password = '*' * min(len(decrypted_search), 12)
            tvData.insert(parent='', index='end', values=(record_id, search_records[count_search][1], search_records[count_search][2], masked_password))
        
        count_search += 1


def find_last_index():
    """
    THIS FUNCTION FINDS THE LAST INDEX. IT IS USEFUL FOR DETERMINING 
    HOW MANY PASSWORDS ARE IN DB UPON STARTUP, AS WELL AS KEEPING
    TRACK OF HOW MANY PASSWORDS ARE STORED FOR INDEXING PURPOSES
    """
    last = c.execute("SELECT id FROM data ORDER BY id DESC LIMIT 1")
    last = c.fetchone()
    if last == None:
        last = 0
    else:
        last = last[0]

    return last


def clear_search():
    """
    THIS FUNCTION CLEARS OUT THE SEARCH AND RESETS THE SEARCH INPUT BOX
    """
    # Use the refresh function to maintain visibility setting
    refresh_treeview_with_visibility()
    
    # CLEAR OUT INPUT BOX
    input_search.delete(0, 'end')
    
    
def change_master_pw():
    """
    THIS FUNCTION WILL CHANGE THE MASTER PASSWORD OF THE DATABASE (PASSWORD TO UNLOCK DATABASE)
    """
    
    def set_master():
        global password, f, key
        new_password = tb_password.get()
        new_password = bytes(new_password, 'utf-8')
        hash_master = bcrypt.hashpw(new_password, bcrypt.gensalt())
        
        # Generate new encryption key
        new_enc_key = Fernet.generate_key()
        new_f = Fernet(new_enc_key)
        
        # Get all existing passwords and decrypt them with old key
        c.execute("SELECT id, password FROM data")
        all_passwords = c.fetchall()
        
        # Re-encrypt all passwords with new key
        for record in all_passwords:
            record_id = record[0]
            old_encrypted_password = record[1]
            
            try:
                # Decrypt with old key
                decrypted_password = f.decrypt(old_encrypted_password)
                
                # Re-encrypt with new key
                new_encrypted_password = new_f.encrypt(decrypted_password)
                
                # Update database with new encrypted password
                c.execute("UPDATE data SET password = ? WHERE id = ?", (new_encrypted_password, record_id))
            except Exception as e:
                tkinter.messagebox.showerror(title="Error", message=f"Failed to re-encrypt password for record {record_id}: {str(e)}")
                return
        
        # Update master password and encryption key
        c2.execute("UPDATE master SET key = ?, enc_key = ?", (hash_master, new_enc_key))
        conn.commit()
        conn2.commit()
        
        # Update global encryption objects
        key = new_enc_key
        f = new_f
        
        tkinter.messagebox.showinfo(title="Success", message="Master password changed successfully!")
        change_pw_window.destroy()

    # Connect to unlock database
    conn2 = sqlite3.connect('db/unlock.db')
    c2 = conn2.cursor()
    c2.execute("SELECT * from master")

    # Create password change window
    change_pw_window = tk.Tk()
    change_pw_window.title('RandPyPwMan password change')
    change_pw_window.geometry('300x100')
    password = b''

    lbl_password = tk.Label(change_pw_window, text='Enter new master password:')
    tb_password = tk.Entry(change_pw_window, show='*')
    lbl_password.grid(column=0, row=0, padx=10, pady=5)
    tb_password.grid(column=1, row=0, padx=10, pady=5)
    btn_create = tk.Button(change_pw_window, text='Change master password', command=set_master)
    btn_create.grid(column=0, row=1, columnspan=2, padx=10, pady=10)
    btn_cancel = tk.Button(change_pw_window, text='Cancel', command=change_pw_window.destroy)
    btn_cancel.grid(column=0, row=2, columnspan=2, padx=10, pady=5)

    change_pw_window.mainloop()
    
    
def toggle_password_visibility():
    """
    THIS FUNCTION CHANGES THE VISIBILITY SETTING. THIS WILL TOGGLE BETWEEN THE TWO SETTINGS
    """
    global passwords_visible
    global stored_passwords
    
    passwords_visible = not passwords_visible
    
    # Get all items in treeview
    all_items = tvData.get_children()
    
    if passwords_visible:
        # Show passwords
        for item in all_items:
            item_values = tvData.item(item)['values']
            item_id = item_values[0]
            if item_id in stored_passwords:
                # Replace asterisks with actual password
                tvData.item(item, values=(item_values[0], item_values[1], item_values[2], stored_passwords[item_id]))
        
        # Update button text
        toggle_btn.config(text="Hide Passwords")
        
    else:
        # Hide passwords with asterisks
        stored_passwords.clear()  # Clear previous stored passwords
        
        for item in all_items:
            item_values = tvData.item(item)['values']
            item_id = item_values[0]
            actual_password = str(item_values[3])  # Convert to string to ensure it's a string
            
            # Store actual password
            stored_passwords[item_id] = actual_password
            
            # Replace password with asterisks
            masked_password = '*' * min(len(actual_password), 12)  # Now len() will work
            tvData.item(item, values=(item_values[0], item_values[1], item_values[2], masked_password))


def refresh_treeview_with_visibility():
    """
    THIS FUNCTION FACILITATES THE UPDATING/REFRESHING OF THE TREEVIEW WHEN USER
    TOGGLES THE VISIBILITY STATE
    """
    global passwords_visible
    global stored_passwords
    
    # Clear treeview
    tvData.delete(*tvData.get_children())
    stored_passwords.clear()
    
    # Get all records from database
    c.execute("SELECT * FROM data")
    all_records = c.fetchall()
    
    # Add records to treeview
    for record in all_records:
        decrypted = f.decrypt(record[3])
        decrypted = decrypted.decode('utf-8')
        
        if passwords_visible:
            # Show actual password
            tvData.insert(parent='', index='end', values=(record[0], record[1], record[2], decrypted))
        else:
            # Store actual password and show masked version
            stored_passwords[record[0]] = decrypted
            masked_password = '*' * min(len(decrypted), 12)
            tvData.insert(parent='', index='end', values=(record[0], record[1], record[2], masked_password))
    
    
def delete_hotkey(event):
    """
    THIS FUNCTION FACILITATES DELETING OF RECORDS VIA THE HOTKEY OF
    DELETE ON USER'S KEYBOARD. ONLY FUNCTIONS WHEN THE TREEVIEW
    IS IN FOCUS.
    """
    
    # Check if the treeview has focus and there's a selection
    if window.focus_get() == tvData and tvData.selection():
        try:
            sel = tvData.selection()
            if not sel:
                return
            
            # Get the selected item details for confirmation message
            first_item = tvData.item(sel[0])
            site_name = first_item['values'][1]
            
            # Create confirmation message
            if len(sel) == 1:
                message = f"Are you sure you want to delete the password for '{site_name}'?"
                title = "Confirm Delete"
            else:
                message = f"Are you sure you want to delete {len(sel)} selected password records?"
                title = "Confirm Delete Multiple"
            
            # Show confirmation dialog
            result = tkinter.messagebox.askyesno(
                title=title,
                message=message,
                icon='warning'
            )
            
            if result:  # Clicked Yes
                # Delete records
                for item in sel:
                    v = tvData.item(item)
                    item_id = v['values'][0]
                    tvData.delete(item)
                    
                    # Remove from stored passwords if present
                    if item_id in stored_passwords:
                        del stored_passwords[item_id]
                    
                    # Remove from database
                    c.execute("DELETE FROM data WHERE id = ?", (item_id,))
                
                conn.commit()
                
                # Show success message
                if len(sel) == 1:
                    tkinter.messagebox.showinfo("Deleted", f"Password for '{site_name}' has been deleted.")
                else:
                    tkinter.messagebox.showinfo("Deleted", f"{len(sel)} password records have been deleted.")
                    
        except Exception as e:
            tkinter.messagebox.showerror(
                title="Error", 
                message=f"An error occurred while deleting the record(s): {str(e)}"
            )


# PASSWORD GENERATION SECTION
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
sendBtn.config(height=2)
addBtn.config(height=2)
clearBtn.config(height=2)


# SEARCH SECTION
lbl_search = Label(window, text="Search:")
lbl_search.grid(row=4, column=0, sticky=tk.E)
input_search = tk.Entry(window, textvariable=entry_search)
input_search.grid(row=4, column=1, sticky=tk.E + tk.W)
btn_search = tk.Button(window, text="Search", command=search)
btn_search.grid(row=4, column=2, sticky=tk.E + tk.W)
btn_clear_search = tk.Button(window, text="Clear", command=clear_search)
btn_clear_search.grid(row=4, column=3, sticky=tk.E + tk.W)


# TREEVIEW SECTION
tvData = Treeview(window, columns=columns, show='headings')
tvData.grid(row=5, column=0, columnspan=5, sticky='NSEW')
window.grid_rowconfigure(5, weight=1)
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)
window.grid_columnconfigure(2, weight=1)
window.grid_columnconfigure(3, weight=1)
window.grid_columnconfigure(4, weight=1)
tvData.column(0, width=50)
tvData.heading('Site name', text='Site name')
tvData.heading('Username', text='Username')
tvData.heading('Password', text='Password')
tvData.heading('ID', text='ID')
tvScrollbarRight = Scrollbar()
tvScrollbarRight.config(command=tvData.yview)
tvData.config(yscrollcommand=tvScrollbarRight.set)
# NO IDEA WHY I CANNOT GET THIS TO WORK, BUT IT FITS OK IN CURRENT VIEW AS LONG AS ADDITIONAL COLUMNS AREN'T ADDED
# tvScrollbarBottom = Scrollbar(tvData, orient='horizontal')      # orient='horizontal'
# tvScrollbarBottom.config(command=tvData.xview)
tvScrollbarRight.grid(row=5, column=4, sticky='NSE')
# tvScrollbarBottom.grid(row=5, column=0, sticky='N', columnspan=6)


# BUTTONS SECTION WITH TOGGLE PASSWORD VISIBILITY
deleteBtn = tk.Button(window, text="Delete", command=deleteRecord)
deleteBtn.grid(row=6, column=0, rowspan=1, sticky=tk.E + tk.W + tk.N + tk. S)
editBtn = tk.Button(window, text="Edit", command=editRecord)
editBtn.grid(row=6, column=1, rowspan=1, sticky=tk.E + tk.W + tk.N + tk.S)
copyBtn = tk.Button(window, text="Copy", command=copy)
copyBtn.grid(row=6, column=2, rowspan=1, sticky=tk.E + tk.W + tk.N + tk.S)
toggle_btn = tk.Button(window, text="Hide Passwords", command=toggle_password_visibility)
toggle_btn.grid(row=6, column=3, rowspan=1, sticky=tk.E + tk.W + tk.N + tk.S)
deleteBtn.config(height=3)
editBtn.config(height=3)
copyBtn.config(height=3)
toggle_btn.config(height=3)


# Bind Delete key hotkey to the window - only when on Treeview
window.bind("<Delete>", delete_hotkey)


# FILE MENU SECTION
menubar = tk.Menu(window)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Import", command=import_window)
filemenu.add_command(label="Change master password", command=change_master_pw)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=window.quit)
menubar.add_cascade(label="File", menu=filemenu)
helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="Help index", command=open_help)
menubar.add_cascade(label="Help", menu=helpmenu)


# UNENCRYPT PASSWORDS AND POPULATE TREEVIEW
count = 0
for i in records:
    decrypted = f.decrypt(records[count][3])
    decrypted = decrypted.decode('utf-8')
    tvData.insert(parent='', index='end', values=(records[count][0], records[count][1], records[count][2], decrypted))
    count += 1


last = find_last_index()


window.config(menu=menubar)
window.mainloop()
