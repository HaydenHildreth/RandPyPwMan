#!/usr/bin/env python3
"""
RandPyPwGen version 1.99.1
Modular, secure, easy to use password manager
Written by Hayden Hildreth
"""

import os
import sys
import csv
import string
import secrets
import sqlite3
import webbrowser
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
import bcrypt
import pyperclip
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from cryptography.fernet import Fernet


class DatabaseManager:
    """Handles all database operations and encryption"""
    
    def __init__(self, db_path: str = "./db"):
        self.db_path = Path(db_path)
        self.data_db = self.db_path / "data.db"
        self.unlock_db = self.db_path / "unlock.db"
        self.fernet: Optional[Fernet] = None
        self._ensure_db_setup()
    
    def _ensure_db_setup(self):
        """Ensure database directory and files exist"""
        if not self.db_path.exists() or not self.data_db.exists() or not self.unlock_db.exists():
            if not self._setup_databases():
                sys.exit(1)
        
        # Load encryption key
        self._load_encryption_key()
    
    def _setup_databases(self) -> bool:
        """Setup databases if they don't exist"""
        try:
            # Create directory
            self.db_path.mkdir(exist_ok=True)
            
            # Setup data database
            conn = sqlite3.connect(self.data_db)
            c = conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS data(
                id INTEGER PRIMARY KEY,
                site varchar(100) NOT NULL,
                username varchar(100) NOT NULL,
                password varchar(100) NOT NULL
            )""")
            conn.commit()
            conn.close()
            
            # Setup unlock database
            conn2 = sqlite3.connect(self.unlock_db)
            c2 = conn2.cursor()
            c2.execute("""CREATE TABLE IF NOT EXISTS master(
                key varchar(255),
                enc_key varchar(255)
            )""")
            conn2.commit()
            conn2.close()
            
            # Check if master password exists
            if not self._has_master_password():
                return self._setup_master_password()
            
            return True
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to setup databases: {str(e)}")
            return False
    
    def _has_master_password(self) -> bool:
        """Check if master password is configured"""
        try:
            conn = sqlite3.connect(self.unlock_db)
            c = conn.cursor()
            c.execute("SELECT * FROM master")
            result = c.fetchone()
            conn.close()
            return result is not None
        except:
            return False
    
    def _setup_master_password(self) -> bool:
        """Setup initial master password"""
        class MasterPasswordSetup:
            def __init__(self, db_manager):
                self.db_manager = db_manager
                self.success = False
                self.password_entry = None
                self.window = tk.Tk()
                self.window.title('RandPyPwGen Setup')
                self.window.geometry('400x200')
                self.window.resizable(False, False)
                
                # Center window
                self.window.update_idletasks()
                x = (self.window.winfo_screenwidth() // 2) - (400 // 2)
                y = (self.window.winfo_screenheight() // 2) - (200 // 2)
                self.window.geometry(f'400x200+{x}+{y}')
                
                self._create_widgets()
                self.window.protocol("WM_DELETE_WINDOW", self._on_close)
            
            def _create_widgets(self):
                # Use regular tk widgets instead of ttk to rule out ttk issues
                main_frame = tk.Frame(self.window, padx=20, pady=20)
                main_frame.pack(fill=tk.BOTH, expand=True)
                
                title_label = tk.Label(main_frame, text="Welcome to RandPyPwGen Setup", 
                                     font=("Arial", 12, "bold"))
                title_label.pack(pady=(0, 20))
                
                instruction_label = tk.Label(main_frame, text="Enter master password:")
                instruction_label.pack(pady=(0, 10))
                
                # Use regular Entry widget
                self.password_entry = tk.Entry(main_frame, show='*', width=30, font=("Arial", 10))
                self.password_entry.pack(pady=(0, 20))
                self.password_entry.focus_set()
                
                # Button frame
                button_frame = tk.Frame(main_frame)
                button_frame.pack()
                
                setup_btn = tk.Button(button_frame, text="Setup", command=self._setup_password,
                                    font=("Arial", 10), padx=20)
                setup_btn.pack(side=tk.LEFT, padx=(0, 10))
                
                exit_btn = tk.Button(button_frame, text="Exit", command=self._on_close,
                                   font=("Arial", 10), padx=20)
                exit_btn.pack(side=tk.LEFT)
                
                # Bind Enter key
                self.window.bind('<Return>', lambda e: self._setup_password())
                self.password_entry.bind('<Return>', lambda e: self._setup_password())
            
            def _setup_password(self):
                # Debug information
                print("Setup password called")
                if self.password_entry is None:
                    print("ERROR: password_entry is None!")
                    messagebox.showerror("Error", "Internal error: password entry not found")
                    return
                
                try:
                    password = self.password_entry.get()
                    print(f"Raw password: '{password}' (length: {len(password)})")
                    
                    # Don't strip yet, check what we actually get
                    if not password:
                        print("Password is empty or None")
                        messagebox.showerror("Error", "Password cannot be empty!")
                        self.password_entry.focus_set()
                        return
                    
                    password = password.strip()
                    print(f"Stripped password: '{password}' (length: {len(password)})")
                    
                    if not password:
                        print("Password is empty after stripping")
                        messagebox.showerror("Error", "Password cannot be empty!")
                        self.password_entry.focus_set()
                        return
                    
                    if len(password) < 4:
                        print(f"Password too short: {len(password)} characters")
                        messagebox.showerror("Error", "Password must be at least 4 characters long!")
                        self.password_entry.focus_set()
                        return
                    
                    print("Password validation passed, attempting to save...")
                    
                    password_bytes = password.encode('utf-8')
                    hash_master = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
                    enc_key = Fernet.generate_key()
                    
                    conn = sqlite3.connect(self.db_manager.unlock_db)
                    c = conn.cursor()
                    c.execute("INSERT INTO master VALUES (?,?)", (hash_master, enc_key))
                    conn.commit()
                    conn.close()
                    
                    print("Password saved successfully!")
                    messagebox.showinfo("Success", "Master password set successfully!")
                    self.success = True
                    self.window.destroy()
                    
                except Exception as e:
                    print(f"Exception in _setup_password: {e}")
                    messagebox.showerror("Error", f"Failed to set master password: {str(e)}")
            
            def _on_close(self):
                print("Setup window closed")
                self.window.destroy()
            
            def run(self):
                print("Starting setup window mainloop")
                self.window.mainloop()
                print(f"Setup window closed, success = {self.success}")
                return self.success
        
        setup = MasterPasswordSetup(self)
        return setup.run()
    
    def _load_encryption_key(self):
        """Load the encryption key from database"""
        try:
            conn = sqlite3.connect(self.unlock_db)
            c = conn.cursor()
            c.execute("SELECT enc_key FROM master")
            result = c.fetchone()
            conn.close()
            
            if result:
                self.fernet = Fernet(result[0])
            else:
                raise Exception("No encryption key found")
                
        except Exception as e:
            messagebox.showerror("Encryption Error", f"Failed to load encryption key: {str(e)}")
            sys.exit(1)
    
    def verify_master_password(self, password: str) -> bool:
        """Verify the master password"""
        try:
            conn = sqlite3.connect(self.unlock_db)
            c = conn.cursor()
            c.execute("SELECT key FROM master")
            result = c.fetchone()
            conn.close()
            
            if result:
                return bcrypt.checkpw(password.encode('utf-8'), result[0])
            return False
            
        except Exception as e:
            messagebox.showerror("Authentication Error", f"Failed to verify password: {str(e)}")
            return False
    
    def get_all_records(self) -> List[Tuple]:
        """Get all password records from database"""
        try:
            conn = sqlite3.connect(self.data_db)
            c = conn.cursor()
            c.execute("SELECT * FROM data ORDER BY id")
            records = c.fetchall()
            conn.close()
            return records
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to retrieve records: {str(e)}")
            return []
    
    def search_records(self, search_term: str) -> List[Tuple]:
        """Search for records by site name or username"""
        try:
            conn = sqlite3.connect(self.data_db)
            c = conn.cursor()
            c.execute("""SELECT * FROM data WHERE site LIKE ? OR username LIKE ? ORDER BY id""",
                     (f'%{search_term}%', f'%{search_term}%'))
            records = c.fetchall()
            conn.close()
            return records
        except Exception as e:
            messagebox.showerror("Search Error", f"Failed to search records: {str(e)}")
            return []
    
    def add_record(self, site: str, username: str, password: str) -> Optional[int]:
        """Add a new password record"""
        try:
            encrypted_password = self.fernet.encrypt(password.encode('utf-8'))
            
            conn = sqlite3.connect(self.data_db)
            c = conn.cursor()
            c.execute("INSERT INTO data (site, username, password) VALUES (?, ?, ?)",
                     (site, username, encrypted_password))
            record_id = c.lastrowid
            conn.commit()
            conn.close()
            return record_id
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add record: {str(e)}")
            return None
    
    def update_record(self, record_id: int, site: str, username: str, password: str) -> bool:
        """Update an existing password record"""
        try:
            encrypted_password = self.fernet.encrypt(password.encode('utf-8'))
            
            conn = sqlite3.connect(self.data_db)
            c = conn.cursor()
            c.execute("UPDATE data SET site=?, username=?, password=? WHERE id=?",
                     (site, username, encrypted_password, record_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update record: {str(e)}")
            return False
    
    def delete_record(self, record_id: int) -> bool:
        """Delete a password record"""
        try:
            conn = sqlite3.connect(self.data_db)
            c = conn.cursor()
            c.execute("DELETE FROM data WHERE id=?", (record_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete record: {str(e)}")
            return False
    
    def decrypt_password(self, encrypted_password: bytes) -> str:
        """Decrypt a password"""
        try:
            return self.fernet.decrypt(encrypted_password).decode('utf-8')
        except Exception as e:
            raise Exception(f"Failed to decrypt password: {str(e)}")
    
    def change_master_password(self, new_password: str) -> bool:
        """Change the master password and re-encrypt all data"""
        try:
            # Generate new encryption key
            new_enc_key = Fernet.generate_key()
            new_fernet = Fernet(new_enc_key)
            
            # Get all records and re-encrypt
            records = self.get_all_records()
            
            conn = sqlite3.connect(self.data_db)
            c = conn.cursor()
            
            for record in records:
                record_id, site, username, encrypted_password = record
                # Decrypt with old key
                decrypted = self.decrypt_password(encrypted_password)
                # Re-encrypt with new key
                new_encrypted = new_fernet.encrypt(decrypted.encode('utf-8'))
                # Update record
                c.execute("UPDATE data SET password=? WHERE id=?", (new_encrypted, record_id))
            
            conn.commit()
            conn.close()
            
            # Update master password and encryption key
            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            
            conn2 = sqlite3.connect(self.unlock_db)
            c2 = conn2.cursor()
            c2.execute("UPDATE master SET key=?, enc_key=?", (new_hash, new_enc_key))
            conn2.commit()
            conn2.close()
            
            # Update current encryption key
            self.fernet = new_fernet
            
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to change master password: {str(e)}")
            return False


class PasswordGenerator:
    """Handles password generation"""
    
    def __init__(self):
        self.alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    
    def generate(self, length: int) -> str:
        """Generate a random password of specified length"""
        if length <= 0 or length > 100:
            raise ValueError("Password length must be between 1 and 100")
        
        return ''.join(secrets.choice(self.alphabet) for _ in range(length))


class LoginFrame(ttk.Frame):
    """Login frame for master password authentication"""
    
    def __init__(self, parent, db_manager, on_success_callback):
        super().__init__(parent, padding="20")
        self.db_manager = db_manager
        self.on_success_callback = on_success_callback
        self._create_widgets()
    
    def _create_widgets(self):
        # Title
        ttk.Label(self, text="RandPyPwGen", font=("Arial", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Master password input
        ttk.Label(self, text="Master Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(self, textvariable=self.password_var, show='*', width=30)
        self.password_entry.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.password_entry.focus()
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Unlock", command=self._authenticate).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Exit", command=self.quit).pack(side=tk.LEFT)
        
        # Bind Enter key
        self.password_entry.bind('<Return>', lambda e: self._authenticate())
    
    def _authenticate(self):
        password = self.password_var.get()
        if self.db_manager.verify_master_password(password):
            self.on_success_callback()
        else:
            messagebox.showerror("Authentication Failed", "Incorrect master password.")
            self.password_var.set("")
            self.password_entry.focus()


class MainFrame(ttk.Frame):
    """Main application frame"""
    
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.password_generator = PasswordGenerator()
        self.passwords_visible = True
        self.stored_passwords: Dict[int, str] = {}
        
        self._create_widgets()
        self._populate_treeview()
    
    def _create_widgets(self):
        # Configure grid weights
        self.grid_rowconfigure(2, weight=1)  # Treeview row
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        
        self._create_password_generation_section()
        self._create_search_section()
        self._create_treeview_section()
        self._create_button_section()
        self._create_menu()
    
    def _create_password_generation_section(self):
        """Create password generation widgets"""
        gen_frame = ttk.LabelFrame(self, text="Password Generation", padding="10")
        gen_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        gen_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(gen_frame, text="Password Length:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.length_var = tk.StringVar()
        length_entry = ttk.Entry(gen_frame, textvariable=self.length_var, width=10)
        length_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        ttk.Button(gen_frame, text="Generate", command=self._generate_password).grid(
            row=0, column=2, padx=(0, 10))
        ttk.Button(gen_frame, text="Add to DB", command=self._show_add_dialog).grid(
            row=0, column=3, padx=(0, 10))
        ttk.Button(gen_frame, text="Clear", command=self._clear_password).grid(
            row=0, column=4)
        
        self.generated_password_var = tk.StringVar()
        self.password_label = ttk.Label(gen_frame, textvariable=self.generated_password_var,
                                       font=("Courier", 10), foreground="blue")
        self.password_label.grid(row=1, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def _create_search_section(self):
        """Create search widgets"""
        search_frame = ttk.LabelFrame(self, text="Search", padding="10")
        search_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        search_entry.bind('<Return>', lambda e: self._search())
        
        ttk.Button(search_frame, text="Search", command=self._search).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(search_frame, text="Clear", command=self._clear_search).grid(row=0, column=3)
    
    def _create_treeview_section(self):
        """Create treeview and scrollbar"""
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview
        columns = ('ID', 'Site', 'Username', 'Password')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        # Configure columns
        self.tree.heading('ID', text='ID')
        self.tree.heading('Site', text='Site Name')
        self.tree.heading('Username', text='Username')
        self.tree.heading('Password', text='Password')
        
        self.tree.column('ID', width=50, minwidth=50)
        self.tree.column('Site', width=200, minwidth=100)
        self.tree.column('Username', width=150, minwidth=100)
        self.tree.column('Password', width=200, minwidth=100)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind double-click to edit
        self.tree.bind('<Double-1>', lambda e: self._show_edit_dialog())
        
        # Bind Delete key
        self.tree.bind('<Delete>', self._delete_selected)
    
    def _create_button_section(self):
        """Create action buttons"""
        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E))
        
        buttons = [
            ("Add", self._show_add_dialog),
            ("Edit", self._show_edit_dialog),
            ("Delete", self._delete_selected),
            ("Copy Password", self._copy_password),
            ("Toggle Visibility", self._toggle_password_visibility)
        ]
        
        for i, (text, command) in enumerate(buttons):
            ttk.Button(button_frame, text=text, command=command).grid(
                row=0, column=i, padx=5, sticky=(tk.W, tk.E))
            button_frame.grid_columnconfigure(i, weight=1)
    
    def _create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import Passwords...", command=self._show_import_dialog)
        file_menu.add_command(label="Change Master Password...", command=self._change_master_password)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Help", command=self._open_help)
    
    def _generate_password(self):
        """Generate a new password"""
        try:
            length = int(self.length_var.get())
            password = self.password_generator.generate(length)
            self.generated_password_var.set(f"Generated: {password}")
            # Store the generated password for easy access
            self._current_generated_password = password
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid password length.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate password: {str(e)}")
    
    def _clear_password(self):
        """Clear generated password"""
        self.generated_password_var.set("")
        self._current_generated_password = ""
    
    def _show_add_dialog(self):
        """Show add password dialog"""
        AddEditDialog(self, self.db_manager, callback=self._populate_treeview,
                     initial_password=getattr(self, '_current_generated_password', ''))
    
    def _show_edit_dialog(self):
        """Show edit password dialog"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a record to edit.")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        record_id = values[0]
        
        # Get actual password if hidden
        if not self.passwords_visible and record_id in self.stored_passwords:
            password = self.stored_passwords[record_id]
        else:
            password = values[3]
        
        AddEditDialog(self, self.db_manager, callback=self._populate_treeview,
                     record_id=record_id, site=values[1], username=values[2], password=password)
    
    def _delete_selected(self, event=None):
        """Delete selected records"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select record(s) to delete.")
            return
        
        # Confirm deletion
        count = len(selection)
        message = f"Are you sure you want to delete {count} record(s)?"
        if not messagebox.askyesno("Confirm Deletion", message):
            return
        
        # Delete records
        for item in selection:
            values = self.tree.item(item)['values']
            record_id = values[0]
            self.db_manager.delete_record(record_id)
            
            # Remove from stored passwords if present
            if record_id in self.stored_passwords:
                del self.stored_passwords[record_id]
        
        self._populate_treeview()
    
    def _copy_password(self):
        """Copy selected password to clipboard"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a record to copy password.")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        record_id = values[0]
        
        # Get actual password
        if not self.passwords_visible and record_id in self.stored_passwords:
            password = self.stored_passwords[record_id]
        else:
            password = values[3]
        
        pyperclip.copy(password)
        messagebox.showinfo("Copied", "Password copied to clipboard!")
    
    def _toggle_password_visibility(self):
        """Toggle password visibility in treeview"""
        self.passwords_visible = not self.passwords_visible
        self._populate_treeview()
    
    def _search(self):
        """Search for records"""
        search_term = self.search_var.get().strip()
        if not search_term:
            self._populate_treeview()
            return
        
        records = self.db_manager.search_records(search_term)
        self._populate_treeview(records)
    
    def _clear_search(self):
        """Clear search and show all records"""
        self.search_var.set("")
        self._populate_treeview()
    
    def _populate_treeview(self, records=None):
        """Populate treeview with records"""
        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.stored_passwords.clear()
        
        # Get records if not provided
        if records is None:
            records = self.db_manager.get_all_records()
        
        # Populate treeview
        for record in records:
            record_id, site, username, encrypted_password = record
            password = self.db_manager.decrypt_password(encrypted_password)
            
            if self.passwords_visible:
                display_password = password
            else:
                self.stored_passwords[record_id] = password
                display_password = '*' * min(len(password), 12)
            
            self.tree.insert('', 'end', values=(record_id, site, username, display_password))
    
    def _show_import_dialog(self):
        """Show import dialog"""
        ImportDialog(self, self.db_manager, callback=self._populate_treeview)
    
    def _change_master_password(self):
        """Change master password"""
        ChangeMasterPasswordDialog(self, self.db_manager)
    
    def _show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", "RandPyPwGen v1.99.1\nA secure password manager\n\nRefactored and improved version")
    
    def _open_help(self):
        """Open help in browser"""
        webbrowser.open("https://github.com/HaydenHildreth/RandPyPwMan")


class AddEditDialog:
    """Dialog for adding/editing password records"""
    
    def __init__(self, parent, db_manager, callback, record_id=None, site='', username='', password='', initial_password=''):
        self.db_manager = db_manager
        self.callback = callback
        self.record_id = record_id
        
        # Use initial_password if provided and password is empty
        if not password and initial_password:
            password = initial_password
        
        self.window = tk.Toplevel(parent)
        self.window.title("Edit Record" if record_id else "Add Record")
        self.window.geometry("400x200")
        self.window.resizable(False, False)
        
        # Center window
        self.window.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        x = parent_x + 50
        y = parent_y + 50
        self.window.geometry(f"400x200+{x}+{y}")
        
        self._create_widgets(site, username, password)
        self.window.transient(parent)
        self.window.grab_set()
    
    def _create_widgets(self, site, username, password):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Site name
        ttk.Label(main_frame, text="Site Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.site_var = tk.StringVar(value=site)
        site_entry = ttk.Entry(main_frame, textvariable=self.site_var)
        site_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        site_entry.focus()
        
        # Username
        ttk.Label(main_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar(value=username)
        username_entry = ttk.Entry(main_frame, textvariable=self.username_var)
        username_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Password
        ttk.Label(main_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar(value=password)
        password_entry = ttk.Entry(main_frame, textvariable=self.password_var)
        password_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        action_text = "Update" if self.record_id else "Add"
        ttk.Button(button_frame, text=action_text, command=self._save).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT)
        
        # Bind Enter key
        self.window.bind('<Return>', lambda e: self._save())
        self.window.bind('<Escape>', lambda e: self._cancel())
    
    def _save(self):
        """Save the record"""
        site = self.site_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not site:
            messagebox.showerror("Validation Error", "Site name is required!")
            return
        
        if not password:
            messagebox.showerror("Validation Error", "Password is required!")
            return
        
        try:
            if self.record_id:
                # Update existing record
                success = self.db_manager.update_record(self.record_id, site, username, password)
                if success:
                    messagebox.showinfo("Success", "Record updated successfully!")
                else:
                    return
            else:
                # Add new record
                record_id = self.db_manager.add_record(site, username, password)
                if record_id:
                    messagebox.showinfo("Success", "Record added successfully!")
                else:
                    return
            
            self.callback()
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save record: {str(e)}")
    
    def _cancel(self):
        """Cancel the dialog"""
        self.window.destroy()


class ImportDialog:
    """Dialog for importing passwords from CSV files"""
    
    def __init__(self, parent, db_manager, callback):
        self.db_manager = db_manager
        self.callback = callback
        self.filename = None
        
        self.window = tk.Toplevel(parent)
        self.window.title("Import Passwords")
        self.window.geometry("350x200")
        self.window.resizable(False, False)
        
        # Center window
        self.window.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        x = parent_x + 75
        y = parent_y + 75
        self.window.geometry(f"350x200+{x}+{y}")
        
        self._create_widgets()
        self.window.transient(parent)
        self.window.grab_set()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(main_frame, text="Select data source:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Data source selection
        self.source_var = tk.StringVar(value="Chrome")
        sources = [("Chrome", "Chrome"), ("Firefox", "Firefox")]
        
        for i, (text, value) in enumerate(sources):
            ttk.Radiobutton(main_frame, text=text, variable=self.source_var, 
                           value=value).grid(row=i+1, column=0, sticky=tk.W, pady=2)
        
        # File selection
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(20, 10))
        file_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="File:").grid(row=0, column=0, sticky=tk.W)
        self.file_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_var, state='readonly')
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10))
        ttk.Button(file_frame, text="Browse", command=self._browse_file).grid(row=0, column=2)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, pady=(10, 0))
        
        self.import_btn = ttk.Button(button_frame, text="Import", command=self._import_passwords, state='disabled')
        self.import_btn.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT)
    
    def _browse_file(self):
        """Browse for CSV file"""
        filename = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            self.filename = filename
            self.file_var.set(filename)
            self.import_btn.config(state='normal')
    
    def _import_passwords(self):
        """Import passwords from CSV file"""
        if not self.filename:
            messagebox.showerror("Error", "Please select a file to import.")
            return
        
        try:
            source = self.source_var.get()
            imported_count = 0
            
            with open(self.filename, 'r', newline='', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                
                # Skip header row if it exists
                try:
                    first_row = next(csv_reader)
                    # Check if first row looks like headers
                    if not any(field.startswith('http') for field in first_row):
                        pass  # Skip header row
                    else:
                        # Reset and process first row as data
                        file.seek(0)
                        csv_reader = csv.reader(file)
                except StopIteration:
                    messagebox.showerror("Error", "The selected file appears to be empty.")
                    return
                
                for row in csv_reader:
                    if len(row) < 3:
                        continue  # Skip incomplete rows
                    
                    try:
                        if source == "Chrome":
                            # Chrome format: name, url, username, password
                            if len(row) >= 4:
                                site = row[0] or row[1]  # Use name, fallback to url
                                username = row[2]
                                password = row[3]
                        else:  # Firefox
                            # Firefox format: url, username, password
                            site = row[0]
                            username = row[1]
                            password = row[2]
                        
                        if site and password:  # Only import if we have site and password
                            if self.db_manager.add_record(site, username, password):
                                imported_count += 1
                    
                    except Exception as e:
                        print(f"Error processing row {row}: {e}")
                        continue
            
            if imported_count > 0:
                messagebox.showinfo("Success", f"Successfully imported {imported_count} password(s)!")
                self.callback()
                self.window.destroy()
            else:
                messagebox.showwarning("No Data", "No valid password records were found in the file.")
        
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import passwords: {str(e)}")


class ChangeMasterPasswordDialog:
    """Dialog for changing master password"""
    
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        
        self.window = tk.Toplevel(parent)
        self.window.title("Change Master Password")
        self.window.geometry("400x150")
        self.window.resizable(False, False)
        
        # Center window
        self.window.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        x = parent_x + 100
        y = parent_y + 100
        self.window.geometry(f"400x150+{x}+{y}")
        
        self._create_widgets()
        self.window.transient(parent)
        self.window.grab_set()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(main_frame, text="Enter new master password:", 
                 font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        ttk.Label(main_frame, text="New Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(main_frame, textvariable=self.password_var, show='*')
        password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        password_entry.focus()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Change Password", command=self._change_password).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT)
        
        # Bind Enter key
        self.window.bind('<Return>', lambda e: self._change_password())
    
    def _change_password(self):
        """Change the master password"""
        new_password = self.password_var.get().strip()
        
        if not new_password:
            messagebox.showerror("Error", "Password cannot be empty!")
            return
        
        if len(new_password) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters long!")
            return
        
        # Confirm the change
        if not messagebox.askyesno("Confirm", "This will re-encrypt all your passwords. Continue?"):
            return
        
        if self.db_manager.change_master_password(new_password):
            messagebox.showinfo("Success", "Master password changed successfully!")
            self.window.destroy()


class PasswordManagerApp:
    """Main application class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("RandPyPwGen v1.99.1")
        self.root.geometry("900x700")
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"900x700+{x}+{y}")
        
        # Configure root grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Start with login frame
        self.current_frame = None
        self._show_login()
    
    def _show_login(self):
        """Show login frame"""
        if self.current_frame:
            self.current_frame.destroy()
        
        self.current_frame = LoginFrame(self.root, self.db_manager, self._show_main)
        self.current_frame.grid(row=0, column=0)
        
        # Configure window for login
        self.root.geometry("400x200")
        self.root.title("RandPyPwGen - Login")
    
    def _show_main(self):
        """Show main application frame"""
        if self.current_frame:
            self.current_frame.destroy()
        
        # Configure window for main app
        self.root.geometry("900x700")
        self.root.title("RandPyPwGen v1.99.1")
        
        self.current_frame = MainFrame(self.root, self.db_manager)
        self.current_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
    
    def _on_closing(self):
        """Handle application closing"""
        self.root.quit()


def main():
    """Main executable"""
    try:
        app = PasswordManagerApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        messagebox.showerror("Fatal Error", f"An unexpected error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
