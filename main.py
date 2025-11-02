#!/usr/bin/env python3

import os
import sys
import csv
import string
import secrets
import sqlite3
import webbrowser
import time
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
import bcrypt
import pyperclip
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from cryptography.fernet import Fernet


THEMES = {
    'Light': {
        'bg': '#FFFFFF',
        'fg': '#1F2937',
        'accent': '#2563EB',
        'button_bg': '#F3F4F6',
        'button_fg': '#1F2937',
        'entry_bg': '#FFFFFF',
        'entry_fg': '#1F2937',
        'active_bg': '#E5E7EB',
        'active_fg': '#111827',
        'tree_bg': '#FFFFFF',
        'tree_fg': '#111827',
        'tree_sel_bg': '#2563EB',
        'tree_sel_fg': '#FFFFFF',
        'menu_bg': '#FFFFFF',
        'menu_fg': '#111827',
    },
    'Dark': {
        'bg': '#1E1E1E',
        'fg': '#E5E5E5',
        'accent': '#569CD6',
        'button_bg': '#2D2D2D',
        'button_fg': '#E5E5E5',
        'entry_bg': '#252526',
        'entry_fg': '#E5E5E5',
        'active_bg': '#3A3A3A',
        'active_fg': '#FFFFFF',
        'tree_bg': '#1E1E1E',
        'tree_fg': '#E5E5E5',
        'tree_sel_bg': '#094771',
        'tree_sel_fg': '#FFFFFF',
        'menu_bg': '#2D2D2D',
        'menu_fg': '#E5E5E5',
    },
    'Nord': {
        'bg': '#2E3440',
        'fg': '#D8DEE9',
        'accent': '#88C0D0',
        'button_bg': '#3B4252',
        'button_fg': '#ECEFF4',
        'entry_bg': '#3B4252',
        'entry_fg': '#ECEFF4',
        'active_bg': '#4C566A',
        'active_fg': '#ECEFF4',
        'tree_bg': '#2E3440',
        'tree_fg': '#D8DEE9',
        'tree_sel_bg': '#5E81AC',
        'tree_sel_fg': '#ECEFF4',
        'menu_bg': '#3B4252',
        'menu_fg': '#ECEFF4',
    },
    'Dracula': {
        'bg': '#282A36',
        'fg': '#F8F8F2',
        'accent': '#BD93F9',
        'button_bg': '#44475A',
        'button_fg': '#F8F8F2',
        'entry_bg': '#44475A',
        'entry_fg': '#F8F8F2',
        'active_bg': '#6272A4',
        'active_fg': '#F8F8F2',
        'tree_bg': '#282A36',
        'tree_fg': '#F8F8F2',
        'tree_sel_bg': '#6272A4',
        'tree_sel_fg': '#F8F8F2',
        'menu_bg': '#44475A',
        'menu_fg': '#F8F8F2',
    },
    'Solarized Dark': {
        'bg': '#002B36',
        'fg': '#EEE8D5',
        'accent': '#268BD2',
        'button_bg': '#073642',
        'button_fg': '#EEE8D5',
        'entry_bg': '#073642',
        'entry_fg': '#EEE8D5',
        'active_bg': '#094352',
        'active_fg': '#FDF6E3',
        'tree_bg': '#002B36',
        'tree_fg': '#EEE8D5',
        'tree_sel_bg': '#268BD2',
        'tree_sel_fg': '#FDF6E3',
        'menu_bg': '#073642',
        'menu_fg': '#EEE8D5',
    },
    'Solarized Light': {
        'bg': '#FDF6E3',
        'fg': '#073642',
        'accent': '#268BD2',
        'button_bg': '#EEE8D5',
        'button_fg': '#073642',
        'entry_bg': '#FFFFFF',
        'entry_fg': '#073642',
        'active_bg': '#E1DBC9',
        'active_fg': '#002B36',
        'tree_bg': '#FDF6E3',
        'tree_fg': '#073642',
        'tree_sel_bg': '#268BD2',
        'tree_sel_fg': '#FDF6E3',
        'menu_bg': '#EEE8D5',
        'menu_fg': '#073642',
    },
    'Gruvbox Dark': {
        'bg': '#282828',
        'fg': '#EBDBB2',
        'accent': '#83A598',
        'button_bg': '#3C3836',
        'button_fg': '#EBDBB2',
        'entry_bg': '#3C3836',
        'entry_fg': '#EBDBB2',
        'active_bg': '#504945',
        'active_fg': '#FBF1C7',
        'tree_bg': '#282828',
        'tree_fg': '#EBDBB2',
        'tree_sel_bg': '#83A598',
        'tree_sel_fg': '#1D2021',
        'menu_bg': '#3C3836',
        'menu_fg': '#EBDBB2',
    },
    'Monokai': {
        'bg': '#272822',
        'fg': '#F8F8F2',
        'accent': '#A6E22E',
        'button_bg': '#3E3D32',
        'button_fg': '#F8F8F2',
        'entry_bg': '#3E3D32',
        'entry_fg': '#F8F8F2',
        'active_bg': '#75715E',
        'active_fg': '#F8F8F2',
        'tree_bg': '#272822',
        'tree_fg': '#F8F8F2',
        'tree_sel_bg': '#A6E22E',
        'tree_sel_fg': '#272822',
        'menu_bg': '#3E3D32',
        'menu_fg': '#F8F8F2',
    },
}


class DatabaseManager:
    """Handles all database operations and encryption"""
    
    def __init__(self, db_path: str = "./db"):
        self.db_path = Path(db_path)
        self.data_db = self.db_path / "data.db"
        self.unlock_db = self.db_path / "unlock.db"
        self.fernet: Optional[Fernet] = None
        self._ensure_db_setup()
    
    def _ensure_db_setup(self):
        """Verify database directory and files exist"""
        if not self.db_path.exists() or not self.data_db.exists() or not self.unlock_db.exists():
            if not self._setup_databases():
                sys.exit(1)
        
        self._load_encryption_key()
        self._migrate_database()
    
    def _load_encryption_key(self):
        """Load encryption key from database"""
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
    
    def _migrate_database(self):
        """Add fields to table if they do not exist. This is useful for updating to new versions"""
        try:
            conn = sqlite3.connect(self.data_db)
            c = conn.cursor()
            
            # Check if group_name column exists
            c.execute("PRAGMA table_info(data)")
            columns = [column[1] for column in c.fetchall()]
            
            if 'group_name' not in columns:
                c.execute("ALTER TABLE data ADD COLUMN group_name varchar(100)")
                conn.commit()
            else:
                c.execute("UPDATE data SET group_name = NULL WHERE group_name = 'All'")
                conn.commit()
            
            # Check if date_added column exists
            if 'date_added' not in columns:
                c.execute("ALTER TABLE data ADD COLUMN date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                conn.commit()
            
            # Check if date_modified column exists
            if 'date_modified' not in columns:
                c.execute("ALTER TABLE data ADD COLUMN date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                conn.commit()
            
            # Create groups table if it doesn't exist
            c.execute("""CREATE TABLE IF NOT EXISTS groups(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name varchar(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
            conn.commit()
            
            # Move existing groups from data table to groups table
            c.execute("SELECT DISTINCT group_name FROM data WHERE group_name IS NOT NULL AND group_name != ''")
            existing_groups = [row[0] for row in c.fetchall()]
            
            for group in existing_groups:
                try:
                    c.execute("INSERT OR IGNORE INTO groups (name) VALUES (?)", (group,))
                except:
                    pass
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Migration warning: {e}")
    
    def _setup_databases(self) -> bool:
        """Setup databases if they don't exist"""
        try:
            self.db_path.mkdir(exist_ok=True)
            
            conn = sqlite3.connect(self.data_db)
            c = conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS data(
                id INTEGER PRIMARY KEY,
                site varchar(100) NOT NULL,
                username varchar(100) NOT NULL,
                password varchar(100) NOT NULL,
                group_name varchar(100),
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
            
            # Create groups table
            c.execute("""CREATE TABLE IF NOT EXISTS groups(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name varchar(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
            conn.commit()
            conn.close()
            
            conn2 = sqlite3.connect(self.unlock_db)
            c2 = conn2.cursor()
            c2.execute("""CREATE TABLE IF NOT EXISTS master(
                key varchar(255),
                enc_key varchar(255)
            )""")
            c2.execute("""CREATE TABLE IF NOT EXISTS settings(
                key varchar(100) PRIMARY KEY,
                value varchar(255)
            )""")
            conn2.commit()
            conn2.close()
            
            self._set_default_settings()
            
            if not self._has_master_password():
                return self._setup_master_password()
            
            return True
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to setup databases: {str(e)}")
            return False
    
    def _set_default_settings(self):
        """Set default values for new installs"""
        try:
            conn = sqlite3.connect(self.unlock_db)
            c = conn.cursor()
            
            c.execute("SELECT COUNT(*) FROM settings")
            count = c.fetchone()[0]
            
            if count == 0:
                # New installation - set all defaults
                c.execute("INSERT OR IGNORE INTO settings VALUES ('auto_lock_enabled', '1')")
                c.execute("INSERT OR IGNORE INTO settings VALUES ('auto_lock_minutes', '5')")
                c.execute("INSERT OR IGNORE INTO settings VALUES ('theme', 'Light')")
                conn.commit()
            else:
                # Existing installation - check for missing settings and add them
                # This upgrades the databases and tables for older versions
                
                # Check if theme setting exists
                c.execute("SELECT COUNT(*) FROM settings WHERE key='theme'")
                if c.fetchone()[0] == 0:
                    c.execute("INSERT INTO settings VALUES ('theme', 'Light')")
                    conn.commit()
                
                # Check if auto_lock_enabled exists
                c.execute("SELECT COUNT(*) FROM settings WHERE key='auto_lock_enabled'")
                if c.fetchone()[0] == 0:
                    c.execute("INSERT INTO settings VALUES ('auto_lock_enabled', '1')")
                    conn.commit()
                
                # Check if auto_lock_minutes exists
                c.execute("SELECT COUNT(*) FROM settings WHERE key='auto_lock_minutes'")
                if c.fetchone()[0] == 0:
                    c.execute("INSERT INTO settings VALUES ('auto_lock_minutes', '5')")
                    conn.commit()
            
            conn.close()
        except Exception as e:
            print(f"Settings initialization warning: {e}")
    
    def get_setting(self, key: str, default: str = '') -> str:
        """Get a setting value"""
        try:
            conn = sqlite3.connect(self.unlock_db)
            c = conn.cursor()
            c.execute("SELECT value FROM settings WHERE key=?", (key,))
            result = c.fetchone()
            conn.close()
            return result[0] if result else default
        except:
            return default
    
    def set_setting(self, key: str, value: str) -> bool:
        """Set a setting value"""
        try:
            conn = sqlite3.connect(self.unlock_db)
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO settings VALUES (?, ?)", (key, value))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Failed to save setting: {e}")
            return False
    
    def _has_master_password(self) -> bool:
        """Check if master password is setup"""
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
        """Create initial master password"""
        class MasterPasswordSetup:
            def __init__(self, db_manager):
                self.db_manager = db_manager
                self.success = False
                self.password_entry = None
                self.window = tk.Tk()
                self.window.title('RandPyPwGen Setup')
                self.window.geometry('400x200')
                self.window.resizable(False, False)
                
                self.window.update_idletasks()
                x = (self.window.winfo_screenwidth() // 2) - (400 // 2)
                y = (self.window.winfo_screenheight() // 2) - (200 // 2)
                self.window.geometry(f'400x200+{x}+{y}')
                
                self._create_widgets()
                self.window.protocol("WM_DELETE_WINDOW", self._on_close)
            
            def _create_widgets(self):
                main_frame = tk.Frame(self.window, padx=20, pady=20)
                main_frame.pack(fill=tk.BOTH, expand=True)
                
                title_label = tk.Label(main_frame, text="Welcome to RandPyPwGen Setup", 
                                     font=("Arial", 12, "bold"))
                title_label.pack(pady=(0, 20))
                
                instruction_label = tk.Label(main_frame, text="Enter master password:")
                instruction_label.pack(pady=(0, 10))
                
                self.password_entry = tk.Entry(main_frame, show='*', width=30, font=("Arial", 10))
                self.password_entry.pack(pady=(0, 20))
                self.password_entry.focus_set()
                
                button_frame = tk.Frame(main_frame)
                button_frame.pack()
                
                setup_btn = tk.Button(button_frame, text="Setup", command=self._setup_password,
                                    font=("Arial", 10), padx=20)
                setup_btn.pack(side=tk.LEFT, padx=(0, 10))
                
                exit_btn = tk.Button(button_frame, text="Exit", command=self._on_close,
                                   font=("Arial", 10), padx=20)
                exit_btn.pack(side=tk.LEFT)
                
                self.window.bind('<Return>', lambda e: self._setup_password())
                self.password_entry.bind('<Return>', lambda e: self._setup_password())
            
            def _setup_password(self):
                if self.password_entry is None:
                    messagebox.showerror("Error", "Internal error: password entry not found")
                    return
                
                try:
                    password = self.password_entry.get()
                    
                    if not password:
                        messagebox.showerror("Error", "Password cannot be empty!")
                        self.password_entry.focus_set()
                        return
                    
                    password = password.strip()
                    
                    if not password:
                        messagebox.showerror("Error", "Password cannot be empty!")
                        self.password_entry.focus_set()
                        return
                    
                    if len(password) < 4:
                        messagebox.showerror("Error", "Password must be at least 4 characters long!")
                        self.password_entry.focus_set()
                        return
                    
                    password_bytes = password.encode('utf-8')
                    hash_master = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
                    enc_key = Fernet.generate_key()
                    
                    conn = sqlite3.connect(self.db_manager.unlock_db)
                    c = conn.cursor()
                    c.execute("INSERT INTO master VALUES (?,?)", (hash_master, enc_key))
                    conn.commit()
                    conn.close()
                    
                    messagebox.showinfo("Success", "Master password set successfully!")
                    self.success = True
                    self.window.quit()
                    self.window.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to set master password: {str(e)}")
            
            def _on_close(self):
                self.window.quit()
                self.window.destroy()
            
            def run(self):
                self.window.mainloop()
                return self.success
        
        setup = MasterPasswordSetup(self)
        return setup.run()
    
    def verify_master_password(self, password: str) -> bool:
        """Check the master password"""
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
    
    def get_all_records(self, group_filter: str = "All") -> List[Tuple]:
        """Return all records from data table"""
        try:
            conn = sqlite3.connect(self.data_db)
            c = conn.cursor()
            
            if group_filter == "All":
                c.execute("SELECT * FROM data ORDER BY id")
            else:
                c.execute("SELECT * FROM data WHERE group_name=? ORDER BY id", (group_filter,))
            
            records = c.fetchall()
            conn.close()
            return records
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to retrieve records: {str(e)}")
            return []
    
    def get_all_groups(self) -> List[str]:
        """Return all groups from groups table"""
        try:
            conn = sqlite3.connect(self.data_db)
            c = conn.cursor()
            c.execute("SELECT name FROM groups ORDER BY name")
            groups = [row[0] for row in c.fetchall()]
            conn.close()
            
            # Always add "All" for group at start
            groups.insert(0, 'All')
            
            return groups
        except Exception as e:
            print(f"Error getting groups: {e}")
            return ['All']
    
    def add_group(self, group_name: str) -> bool:
        """Create new group in the groups table"""
        try:
            if not group_name or group_name.strip() == '':
                return False
            
            group_name = group_name.strip()
            
            if group_name.lower() == 'all':
                return False
            
            conn = sqlite3.connect(self.data_db)
            c = conn.cursor()
            c.execute("INSERT INTO groups (name) VALUES (?)", (group_name,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Group already exists
            return False
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add group: {str(e)}")
            return False
    
    def delete_group(self, group_name: str) -> bool:
        """Remove a group from the groups table"""
        try:
            conn = sqlite3.connect(self.data_db)
            c = conn.cursor()
            
            # Delete group from table
            c.execute("DELETE FROM groups WHERE name=?", (group_name,))
            
            # Set passwords with that group to NULL
            c.execute("UPDATE data SET group_name=NULL WHERE group_name=?", (group_name,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete group: {str(e)}")
            return False
    
    def rename_group(self, old_name: str, new_name: str) -> bool:
        """Rename a group"""
        try:
            if new_name == '':
                new_name = None
            
            conn = sqlite3.connect(self.data_db)
            c = conn.cursor()
            
            # Update the groups table with new name
            if new_name:
                c.execute("UPDATE groups SET name=? WHERE name=?", (new_name, old_name))
            else:
                c.execute("DELETE FROM groups WHERE name=?", (old_name,))
            
            # Update all passwords with this group to new group name
            c.execute("UPDATE data SET group_name=? WHERE group_name=?", (new_name, old_name))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"Group '{new_name}' already exists!")
            return False
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to rename group: {str(e)}")
            return False
    
    def search_records(self, search_term: str, group_filter: str = "All") -> List[Tuple]:
        """Search for records on site or username"""
        try:
            conn = sqlite3.connect(self.data_db)
            c = conn.cursor()
            
            if group_filter == "All":
                c.execute("""SELECT * FROM data WHERE site LIKE ? OR username LIKE ? ORDER BY id""",
                         (f'%{search_term}%', f'%{search_term}%'))
            else:
                c.execute("""SELECT * FROM data WHERE (site LIKE ? OR username LIKE ?) AND group_name=? ORDER BY id""",
                         (f'%{search_term}%', f'%{search_term}%', group_filter))
            
            records = c.fetchall()
            conn.close()
            return records
        except Exception as e:
            messagebox.showerror("Search Error", f"Failed to search records: {str(e)}")
            return []
    
    def add_record(self, site: str, username: str, password: str, group_name: Optional[str] = None) -> Optional[int]:
        """Add a new password"""
        try:
            encrypted_password = self.fernet.encrypt(password.encode('utf-8'))
            
            if group_name == '':
                group_name = None
            
            conn = sqlite3.connect(self.data_db)
            c = conn.cursor()
            c.execute("""INSERT INTO data (site, username, password, group_name, date_added, date_modified) 
                        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
                     (site, username, encrypted_password, group_name))
            record_id = c.lastrowid
            conn.commit()
            conn.close()
            return record_id
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add record: {str(e)}")
            return None
    
    def update_record(self, record_id: int, site: str, username: str, password: str, group_name: Optional[str] = None) -> bool:
        """Update existing password"""
        try:
            encrypted_password = self.fernet.encrypt(password.encode('utf-8'))
            
            if group_name == '':
                group_name = None
            
            conn = sqlite3.connect(self.data_db)
            c = conn.cursor()
            c.execute("""UPDATE data SET site=?, username=?, password=?, group_name=?, date_modified=CURRENT_TIMESTAMP 
                        WHERE id=?""",
                     (site, username, encrypted_password, group_name, record_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update record: {str(e)}")
            return False
    
    def get_record_by_id(self, record_id: int) -> Optional[Tuple]:
        """Return one password/record using ID"""
        try:
            conn = sqlite3.connect(self.data_db)
            c = conn.cursor()
            c.execute("SELECT * FROM data WHERE id=?", (record_id,))
            record = c.fetchone()
            conn.close()
            return record
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to retrieve record: {str(e)}")
            return None
    
    def delete_record(self, record_id: int) -> bool:
        """Delete a password"""
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
        """Decrypt password"""
        try:
            return self.fernet.decrypt(encrypted_password).decode('utf-8')
        except Exception as e:
            raise Exception(f"Failed to decrypt password: {str(e)}")
    
    def change_master_password(self, new_password: str) -> bool:
        """Update master password and re-encrypt all data"""
        try:
            new_enc_key = Fernet.generate_key()
            new_fernet = Fernet(new_enc_key)
            
            records = self.get_all_records()
            
            conn = sqlite3.connect(self.data_db)
            c = conn.cursor()
            
            for record in records:
                # Handle different value lengths
                if len(record) >= 7:
                    record_id, site, username, encrypted_password, group_name, date_added, date_modified = record[:7]
                elif len(record) == 5:
                    record_id, site, username, encrypted_password, group_name = record
                else:
                    record_id, site, username, encrypted_password = record[:4]
                
                decrypted = self.decrypt_password(encrypted_password)
                new_encrypted = new_fernet.encrypt(decrypted.encode('utf-8'))
                c.execute("UPDATE data SET password=? WHERE id=?", (new_encrypted, record_id))
            
            conn.commit()
            conn.close()
            
            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            
            conn2 = sqlite3.connect(self.unlock_db)
            c2 = conn2.cursor()
            c2.execute("UPDATE master SET key=?, enc_key=?", (new_hash, new_enc_key))
            conn2.commit()
            conn2.close()
            
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
        """Generate a random password of desired length"""
        if length <= 0 or length > 100:
            raise ValueError("Password length must be between 1 and 100")
        
        return ''.join(secrets.choice(self.alphabet) for _ in range(length))


class ThemedWidget:
    """Mixin class for themed widgets"""
    
    def apply_theme(self, theme_name: str):
        """Apply theme to widget - to be implemented by subclasses"""
        pass


class LoginFrame(ttk.Frame, ThemedWidget):
    """Frame for master password authentication"""
    
    def __init__(self, parent, db_manager, on_success_callback):
        super().__init__(parent, padding="20")
        self.db_manager = db_manager
        self.on_success_callback = on_success_callback
        self._create_widgets()
        self._apply_current_theme()
    
    def _create_widgets(self):
        self.title_label = ttk.Label(self, text="RandPyPwGen", font=("Arial", 16, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        ttk.Label(self, text="Master Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(self, textvariable=self.password_var, show='*', width=30)
        self.password_entry.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.password_entry.focus()
        
        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Unlock", command=self._authenticate).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Exit", command=self.quit).pack(side=tk.LEFT)
        
        self.password_entry.bind('<Return>', lambda e: self._authenticate())
    
    def _authenticate(self):
        password = self.password_var.get()
        if self.db_manager.verify_master_password(password):
            self.on_success_callback()
        else:
            messagebox.showerror("Authentication Failed", "Incorrect master password.")
            self.password_var.set("")
            self.password_entry.focus()
    
    def _apply_current_theme(self):
        """Apply the saved theme"""
        theme_name = self.db_manager.get_setting('theme', 'Light')
        self.apply_theme(theme_name)
    
    def apply_theme(self, theme_name: str):
        """Apply theme to login frame"""
        if theme_name not in THEMES:
            theme_name = 'Light'
        
        theme = THEMES[theme_name]
        
        # Apply to self
        self.configure(style='Themed.TFrame')
        
        # Configure styles
        style = ttk.Style()
        style.configure('Themed.TFrame', background=theme['bg'])
        style.configure('Themed.TLabel', background=theme['bg'], foreground=theme['fg'])
        style.configure('Themed.TEntry', fieldbackground=theme['entry_bg'], foreground=theme['entry_fg'])
        style.configure('Themed.TButton', background=theme['button_bg'], foreground=theme['button_fg'])
        
        # Apply to root window
        self.master.configure(bg=theme['bg'])


class MainFrame(ttk.Frame, ThemedWidget):
    """Main app frame"""
    
    def __init__(self, parent, db_manager, lock_callback):
        super().__init__(parent)
        self.db_manager = db_manager
        self.lock_callback = lock_callback
        self.password_generator = PasswordGenerator()
        self.passwords_visible = True
        self.stored_passwords: Dict[int, str] = {}
        self.current_group = "All"
        
        self.auto_lock_timer = None
        self.last_activity_time = None
        
        self._create_widgets()
        self._populate_treeview()
        self._start_activity_monitoring()
        self._apply_current_theme()
    
    def _create_widgets(self):
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        
        self._create_password_generation_section()
        self._create_group_filter_section()
        self._create_search_section()
        self._create_treeview_section()
        self._create_button_section()
        self._create_menu()
    
    def _create_password_generation_section(self):
        """Create password generation section. This is the top frame"""
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
    
    def _create_group_filter_section(self):
        """Create group filter section. This is the second frame from top, below password generation"""
        group_frame = ttk.LabelFrame(self, text="Group Filter", padding="10")
        group_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        group_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(group_frame, text="Group:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.group_var = tk.StringVar(value="All")
        self.group_combo = ttk.Combobox(group_frame, textvariable=self.group_var, state='readonly', width=25)
        self.group_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.group_combo.bind('<<ComboboxSelected>>', lambda e: self._on_group_change())
        
        ttk.Button(group_frame, text="New Group", command=self._show_new_group_dialog).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(group_frame, text="Manage Groups", command=self._show_manage_groups_dialog).grid(row=0, column=3)
        
        self._refresh_groups()
    
    def _create_search_section(self):
        """Create search section. This is the third frame from top, and is below group filter"""
        search_frame = ttk.LabelFrame(self, text="Search", padding="10")
        search_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        search_entry.bind('<Return>', lambda e: self._search())
        
        ttk.Button(search_frame, text="Search", command=self._search).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(search_frame, text="Clear", command=self._clear_search).grid(row=0, column=3)
    
    def _create_treeview_section(self):
        """Create treeview section and its scrollbar. This is the fourth from the top. This is below search"""
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        columns = ('ID', 'Site', 'Username', 'Password', 'Group')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Site', text='Site Name')
        self.tree.heading('Username', text='Username')
        self.tree.heading('Password', text='Password')
        self.tree.heading('Group', text='Group')
        
        self.tree.column('ID', width=50, minwidth=50)
        self.tree.column('Site', width=200, minwidth=100)
        self.tree.column('Username', width=150, minwidth=100)
        self.tree.column('Password', width=150, minwidth=100)
        self.tree.column('Group', width=100, minwidth=80)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Delete>', self._delete_selected)
    
    def _on_double_click(self, event):
        """Double click event, calls edit function"""
        region = self.tree.identify_region(event.x, event.y)
        
        if region == "cell":
            self._show_edit_dialog()
    
    def _create_button_section(self):
        """Create buttons. This is the fifth from the top, and is the bottom most section/frame. This is below the treeview."""
        button_frame = ttk.Frame(self)
        button_frame.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E))
        
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
        """Create toolbar menus"""
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import Passwords...", command=self._show_import_dialog)
        file_menu.add_command(label="Change Master Password...", command=self._change_master_password)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)
        
        options_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Options", menu=options_menu)
        options_menu.add_command(label="Auto-Lock Settings...", command=self._show_autolock_settings)
        options_menu.add_command(label="Theme Settings...", command=self._show_theme_settings)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Help", command=self._open_help)
    
    def _start_activity_monitoring(self):
        """Begin to monitor activity"""
        self._register_activity()
        self._check_auto_lock()
    
    def _register_activity(self):
        """Register an activity event"""
        self.last_activity_time = time.time()
    
    def _check_auto_lock(self):
        """Check if auto-lock should apply"""
        if self.auto_lock_timer:
            self.after_cancel(self.auto_lock_timer)
        
        enabled = self.db_manager.get_setting('auto_lock_enabled', '1') == '1'
        
        if enabled and self.last_activity_time:
            minutes = int(self.db_manager.get_setting('auto_lock_minutes', '5'))
            timeout_seconds = minutes * 60
            
            elapsed = time.time() - self.last_activity_time
            
            if elapsed >= timeout_seconds:
                self._lock_application()
                return
        
        self.auto_lock_timer = self.after(10000, self._check_auto_lock)
    
    def _lock_application(self):
        """Lock the application and return to login screen"""
        if self.auto_lock_timer:
            self.after_cancel(self.auto_lock_timer)
        
        self.lock_callback()
    
    def _show_autolock_settings(self):
        """Show auto-lock settings"""
        self._register_activity()
        AutoLockSettingsDialog(self, self.db_manager)
    
    def _show_theme_settings(self):
        """Show theme settings"""
        self._register_activity()
        ThemeSettingsDialog(self, self.db_manager, self._apply_current_theme)
    
    def _apply_current_theme(self):
        """Apply the saved theme"""
        theme_name = self.db_manager.get_setting('theme', 'Light')
        self.apply_theme(theme_name)
    
    def apply_theme(self, theme_name: str):
        """Apply theme to main frame"""
        if theme_name not in THEMES:
            theme_name = 'Light'
        
        theme = THEMES[theme_name]
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')  # Use clam theme as base for better customization
        
        # Frame styles
        style.configure('TFrame', background=theme['bg'])
        style.configure('TLabelframe', background=theme['bg'], foreground=theme['fg'])
        style.configure('TLabelframe.Label', background=theme['bg'], foreground=theme['fg'])
        
        # Label styles
        style.configure('TLabel', background=theme['bg'], foreground=theme['fg'])
        
        # Entry styles
        style.configure('TEntry', fieldbackground=theme['entry_bg'], foreground=theme['entry_fg'], 
                       insertcolor=theme['fg'])
        style.map('TEntry',
                 fieldbackground=[('readonly', theme['active_bg'])],
                 foreground=[('readonly', theme['active_fg'])])
        
        # Button styles
        style.configure('TButton', background=theme['button_bg'], foreground=theme['button_fg'])
        style.map('TButton',
                 background=[('active', theme['active_bg']), ('pressed', theme['active_bg'])],
                 foreground=[('active', theme['active_fg']), ('pressed', theme['active_fg'])])
        
        # Combobox styles
        style.configure('TCombobox', fieldbackground=theme['entry_bg'], background=theme['button_bg'],
                       foreground=theme['entry_fg'], arrowcolor=theme['fg'])
        style.map('TCombobox',
                 fieldbackground=[('readonly', theme['entry_bg'])],
                 selectbackground=[('readonly', theme['entry_bg'])],
                 selectforeground=[('readonly', theme['entry_fg'])])
        
        # Treeview styles
        style.configure('Treeview', background=theme['tree_bg'], foreground=theme['tree_fg'],
                       fieldbackground=theme['tree_bg'])
        style.map('Treeview',
                 background=[('selected', theme['tree_sel_bg'])],
                 foreground=[('selected', theme['tree_sel_fg'])])
        style.configure('Treeview.Heading', background=theme['button_bg'], foreground=theme['button_fg'])
        
        # Scrollbar styles
        style.configure('Vertical.TScrollbar', background=theme['button_bg'], 
                       troughcolor=theme['bg'], arrowcolor=theme['fg'])
        
        # Apply to root window and menu
        self.master.configure(bg=theme['bg'])
        
        # Update password label color
        if hasattr(self, 'password_label'):
            self.password_label.configure(foreground=theme['accent'])
        
        # Try to update menu colors (note: this may not work on all platforms)
        try:
            menubar = self.master.nametowidget(self.master.cget('menu'))
            menubar.configure(bg=theme['menu_bg'], fg=theme['menu_fg'],
                            activebackground=theme['active_bg'], activeforeground=theme['active_fg'])
            
            for i in range(menubar.index('end') + 1):
                try:
                    submenu = menubar.nametowidget(menubar.entrycget(i, 'menu'))
                    submenu.configure(bg=theme['menu_bg'], fg=theme['menu_fg'],
                                    activebackground=theme['active_bg'], activeforeground=theme['active_fg'])
                except:
                    pass
        except:
            pass
    
    def _refresh_groups(self):
        """Refresh the list of groups in the dropdown"""
        groups = self.db_manager.get_all_groups()
        self.group_combo['values'] = groups
        
        if self.current_group not in groups:
            self.current_group = "All"
            self.group_var.set("All")
    
    def _on_group_change(self):
        """Handle group selection change"""
        self._register_activity()
        self.current_group = self.group_var.get()
        self._populate_treeview()
    
    def _show_new_group_dialog(self):
        """Show window to create a new group"""
        self._register_activity()
        NewGroupDialog(self, self.db_manager, callback=self._on_data_changed)
    
    def _show_manage_groups_dialog(self):
        """Show window to manage existing groups"""
        self._register_activity()
        ManageGroupsDialog(self, self.db_manager, callback=self._on_data_changed)
    
    def _generate_password(self):
        """Generate a new password"""
        self._register_activity()
        try:
            length = int(self.length_var.get())
            password = self.password_generator.generate(length)
            self.generated_password_var.set(f"Generated: {password}")
            self._current_generated_password = password
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid password length.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate password: {str(e)}")
    
    def _clear_password(self):
        """Clear generated password"""
        self._register_activity()
        self.generated_password_var.set("")
        self._current_generated_password = ""
    
    def _show_add_dialog(self):
        """Show add password window"""
        self._register_activity()
        default_group = None if self.current_group == "All" else self.current_group
        AddEditDialog(self, self.db_manager, callback=self._on_data_changed,
                     initial_password=getattr(self, '_current_generated_password', ''),
                     default_group=default_group)
    
    def _show_edit_dialog(self):
        """Show edit password window"""
        self._register_activity()
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a record to edit.")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        record_id = values[0]
        
        # Get full record from database
        full_record = self.db_manager.get_record_by_id(record_id)
        
        if not full_record:
            messagebox.showerror("Error", "Failed to retrieve record details.")
            return
        
        # Extract data from full record
        if len(full_record) >= 7:
            _, site, username, encrypted_password, group_name, date_added, date_modified = full_record[:7]
        else:
            # Fallback for older records without dates
            if len(full_record) == 5:
                _, site, username, encrypted_password, group_name = full_record
            else:
                _, site, username, encrypted_password = full_record[:4]
                group_name = None
            date_added = None
            date_modified = None
        
        # Decrypt password
        password = self.db_manager.decrypt_password(encrypted_password)
        
        AddEditDialog(self, self.db_manager, callback=self._on_data_changed,
                     record_id=record_id, site=site, username=username, 
                     password=password, group=group_name, 
                     date_added=date_added, date_modified=date_modified)
    
    def _delete_selected(self, event=None):
        """Delete selected records"""
        self._register_activity()
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select record(s) to delete.")
            return
        
        count = len(selection)
        message = f"Are you sure you want to delete {count} record(s)?"
        if not messagebox.askyesno("Confirm Deletion", message):
            return
        
        for item in selection:
            values = self.tree.item(item)['values']
            record_id = values[0]
            self.db_manager.delete_record(record_id)
            
            if record_id in self.stored_passwords:
                del self.stored_passwords[record_id]
        
        self._on_data_changed()
    
    def _copy_password(self):
        """Copy selected password to clipboard"""
        self._register_activity()
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a record to copy password.")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        record_id = values[0]
        
        if not self.passwords_visible and record_id in self.stored_passwords:
            password = self.stored_passwords[record_id]
        else:
            password = values[3]
        
        pyperclip.copy(password)
        messagebox.showinfo("Copied", "Password copied to clipboard!")
    
    def _toggle_password_visibility(self):
        """Toggle password visibility in treeview"""
        self._register_activity()
        self.passwords_visible = not self.passwords_visible
        self._populate_treeview()
    
    def _search(self):
        """Search for records"""
        self._register_activity()
        search_term = self.search_var.get().strip()
        if not search_term:
            self._populate_treeview()
            return
        
        records = self.db_manager.search_records(search_term, self.current_group)
        self._populate_treeview(records)
    
    def _clear_search(self):
        """Clear search and show all records"""
        self._register_activity()
        self.search_var.set("")
        self._populate_treeview()
    
    def _on_data_changed(self):
        """Called when data is added, edited, or deleted"""
        self._refresh_groups()
        self._populate_treeview()
    
    def _populate_treeview(self, records=None):
        """Populate treeview with records"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.stored_passwords.clear()
        
        if records is None:
            records = self.db_manager.get_all_records(self.current_group)
        
        for record in records:
            # Handle different record lengths for backward compatibility
            if len(record) >= 7:
                record_id, site, username, encrypted_password, group_name, date_added, date_modified = record[:7]
            elif len(record) == 5:
                record_id, site, username, encrypted_password, group_name = record
            else:
                record_id, site, username, encrypted_password = record[:4]
                group_name = None
            
            password = self.db_manager.decrypt_password(encrypted_password)
            
            if self.passwords_visible:
                display_password = password
            else:
                self.stored_passwords[record_id] = password
                display_password = '*' * min(len(password), 12)
            
            display_group = group_name if group_name else ""
            
            self.tree.insert('', 'end', values=(record_id, site, username, display_password, display_group))
    
    def _show_import_dialog(self):
        """Show import window"""
        self._register_activity()
        default_group = None if self.current_group == "All" else self.current_group
        ImportDialog(self, self.db_manager, callback=self._on_data_changed, current_group=default_group)
    
    def _change_master_password(self):
        """Change master password"""
        self._register_activity()
        ChangeMasterPasswordDialog(self, self.db_manager)
    
    def _show_about(self):
        """Show about window"""
        self._register_activity()
        messagebox.showinfo("About", "RandPyPwGen v1.99.8\nA secure password manager\n\nWith auto-lock timer, groups, and theming features")
    
    def _open_help(self):
        """Open help in browser"""
        self._register_activity()
        webbrowser.open("https://github.com/HaydenHildreth/RandPyPwMan")


class ThemeSettingsDialog:
    """Dialog for configuring theme settings"""
    
    def __init__(self, parent, db_manager, theme_callback):
        self.db_manager = db_manager
        self.theme_callback = theme_callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Theme Settings")
        self.window.geometry("450x550")
        self.window.resizable(True, True)  # Allow resizing
        self.window.minsize(400, 500)  # Set minimum size
        
        self.window.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        x = parent_x + 100
        y = parent_y + 100
        self.window.geometry(f"450x550+{x}+{y}")
        
        self._create_widgets()
        self.window.transient(parent)
        self.window.grab_set()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Make the main frame expandable
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(10, weight=1)  # Make space expandable
        
        ttk.Label(main_frame, text="Theme Configuration", 
                 font=("Arial", 11, "bold")).grid(row=0, column=0, pady=(0, 20), sticky=tk.W)
        
        ttk.Label(main_frame, text="Select Theme:", 
                 font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        # Get current theme
        current_theme = self.db_manager.get_setting('theme', 'Light')
        
        # Create radio buttons for each theme
        self.theme_var = tk.StringVar(value=current_theme)
        
        themes_list = list(THEMES.keys())
        
        for i, theme_name in enumerate(themes_list):
            ttk.Radiobutton(main_frame, text=theme_name, 
                          variable=self.theme_var, 
                          value=theme_name,
                          command=self._preview_theme).grid(row=i+2, column=0, sticky=tk.W, pady=2)
        
        # Preview label
        preview_frame = ttk.LabelFrame(main_frame, text="Preview", padding="10")
        preview_frame.grid(row=len(themes_list)+2, column=0, sticky=(tk.W, tk.E), pady=(15, 15))
        
        self.preview_label = ttk.Label(preview_frame, text="Preview colors will appear here")
        self.preview_label.pack()
        
        self.preview_canvas = tk.Canvas(preview_frame, width=350, height=60)
        self.preview_canvas.pack(pady=(10, 0))
        
        # Show initial preview
        self._preview_theme()
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(themes_list)+3, column=0, pady=(20, 0), sticky=tk.S)
        
        ttk.Button(button_frame, text="Apply", command=self._apply_theme).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT)
    
    def _preview_theme(self):
        """Show a preview of the selected theme"""
        theme_name = self.theme_var.get()
        if theme_name not in THEMES:
            return
        
        theme = THEMES[theme_name]
        
        # Clear canvas
        self.preview_canvas.delete('all')
        
        # Draw color swatches
        x_start = 10
        y = 10
        width = 60
        height = 40
        
        colors = [
            ('BG', theme['bg']),
            ('Text', theme['fg']),
            ('Accent', theme['accent']),
            ('Button', theme['button_bg']),
            ('Entry', theme['entry_bg']),
        ]
        
        for i, (label, color) in enumerate(colors):
            x = x_start + (i * (width + 10))
            self.preview_canvas.create_rectangle(x, y, x + width, y + height, 
                                                fill=color, outline='gray')
            self.preview_canvas.create_text(x + width//2, y + height + 10, 
                                           text=label, font=('Arial', 8))
    
    def _apply_theme(self):
        """Apply the selected theme"""
        theme_name = self.theme_var.get()
        
        if self.db_manager.set_setting('theme', theme_name):
            messagebox.showinfo("Success", f"Theme '{theme_name}' applied successfully!")
            self.theme_callback()
            self.window.destroy()
        else:
            messagebox.showerror("Error", "Failed to save theme setting.")


class NewGroupDialog:
    """Dialog for creating a new group"""
    
    def __init__(self, parent, db_manager, callback):
        self.db_manager = db_manager
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("New Group")
        self.window.geometry("350x130")
        self.window.resizable(False, False)
        
        self.window.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        x = parent_x + 100
        y = parent_y + 100
        self.window.geometry(f"350x130+{x}+{y}")
        
        self._create_widgets()
        self.window.transient(parent)
        self.window.grab_set()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(main_frame, text="Create New Group", 
                 font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        ttk.Label(main_frame, text="Group Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.group_var = tk.StringVar()
        group_entry = ttk.Entry(main_frame, textvariable=self.group_var, width=25)
        group_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        group_entry.focus()
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(15, 0))
        
        ttk.Button(button_frame, text="Create", command=self._create_group).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT)
        
        self.window.bind('<Return>', lambda e: self._create_group())
        self.window.bind('<Escape>', lambda e: self.window.destroy())
    
    def _create_group(self):
        """Create the new group"""
        group_name = self.group_var.get().strip()
        
        if not group_name:
            messagebox.showerror("Error", "Group name cannot be empty!")
            return
        
        if group_name.lower() == "all":
            messagebox.showerror("Error", "'All' is a reserved group name!")
            return
        
        if self.db_manager.add_group(group_name):
            messagebox.showinfo("Success", f"Group '{group_name}' created successfully!")
            self.callback()
            self.window.destroy()
        else:
            messagebox.showerror("Error", f"Group '{group_name}' already exists!")


class ManageGroupsDialog:
    """Dialog for managing existing groups"""
    
    def __init__(self, parent, db_manager, callback):
        self.db_manager = db_manager
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Manage Groups")
        self.window.geometry("400x350")
        self.window.resizable(False, False)
        
        self.window.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        x = parent_x + 75
        y = parent_y + 75
        self.window.geometry(f"400x350+{x}+{y}")
        
        self._create_widgets()
        self.window.transient(parent)
        self.window.grab_set()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        ttk.Label(main_frame, text="Manage Groups", 
                 font=("Arial", 11, "bold")).grid(row=0, column=0, pady=(0, 15))
        
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        self.groups_listbox = tk.Listbox(list_frame, height=10)
        self.groups_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.groups_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.groups_listbox.configure(yscrollcommand=scrollbar.set)
        
        self._populate_groups()
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=(0, 10))
        
        ttk.Button(button_frame, text="Rename Group", command=self._rename_group).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Delete Group", command=self._delete_group).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Close", command=self.window.destroy).pack(side=tk.LEFT)
        
    
    def _populate_groups(self):
        """Populate the listbox with groups"""
        self.groups_listbox.delete(0, tk.END)
        groups = self.db_manager.get_all_groups()
        
        if 'All' in groups:
            groups.remove('All')
        
        if not groups:
            self.groups_listbox.insert(tk.END, "(No groups created yet)")
        else:
            for group in groups:
                self.groups_listbox.insert(tk.END, group)
    
    def _rename_group(self):
        """Rename selected group"""
        selection = self.groups_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a group to rename.")
            return
        
        old_name = self.groups_listbox.get(selection[0])
        
        if old_name == "(No groups created yet)":
            return
        
        RenameGroupDialog(self.window, self.db_manager, old_name, self._on_change_complete)
    
    def _delete_group(self):
        """Delete selected group"""
        selection = self.groups_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a group to delete.")
            return
        
        group_name = self.groups_listbox.get(selection[0])
        
        if group_name == "(No groups created yet)":
            return
        
        if not messagebox.askyesno("Confirm Deletion", 
                                   f"Are you sure you want to delete the group '{group_name}'?\n\n"
                                   "Passwords in this group will not be deleted, but will have no group assigned."):
            return
        
        if self.db_manager.delete_group(group_name):
            messagebox.showinfo("Success", f"Group '{group_name}' deleted successfully!")
            self._on_change_complete()
    
    def _on_change_complete(self):
        """Called after a group is renamed or deleted"""
        self._populate_groups()
        self.callback()


class RenameGroupDialog:
    """Dialog for renaming a group"""
    
    def __init__(self, parent, db_manager, old_name, callback):
        self.db_manager = db_manager
        self.old_name = old_name
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Rename Group")
        self.window.geometry("350x150")
        self.window.resizable(False, False)
        
        self.window.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        x = parent_x + 50
        y = parent_y + 50
        self.window.geometry(f"350x150+{x}+{y}")
        
        self._create_widgets()
        self.window.transient(parent)
        self.window.grab_set()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(main_frame, text=f"Rename Group: {self.old_name}", 
                 font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        ttk.Label(main_frame, text="New Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.new_name_var = tk.StringVar(value=self.old_name)
        name_entry = ttk.Entry(main_frame, textvariable=self.new_name_var, width=25)
        name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        name_entry.focus()
        name_entry.select_range(0, tk.END)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(15, 0))
        
        ttk.Button(button_frame, text="Rename", command=self._rename).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT)
        
        self.window.bind('<Return>', lambda e: self._rename())
        self.window.bind('<Escape>', lambda e: self.window.destroy())
    
    def _rename(self):
        """Perform the rename"""
        new_name = self.new_name_var.get().strip()
        
        if not new_name:
            messagebox.showerror("Error", "Group name cannot be empty!")
            return
        
        if new_name.lower() == "all":
            messagebox.showerror("Error", "'All' is a reserved name!")
            return
        
        if new_name == self.old_name:
            self.window.destroy()
            return
        
        if self.db_manager.rename_group(self.old_name, new_name):
            messagebox.showinfo("Success", f"Group renamed from '{self.old_name}' to '{new_name}'!")
            self.callback()
            self.window.destroy()


class AutoLockSettingsDialog:
    """Dialog for configuring auto-lock settings"""
    
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        
        self.window = tk.Toplevel(parent)
        self.window.title("Auto-Lock Settings")
        self.window.geometry("400x180")
        self.window.resizable(False, False)
        
        self.window.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        x = parent_x + 100
        y = parent_y + 100
        self.window.geometry(f"400x180+{x}+{y}")
        
        self._create_widgets()
        self.window.transient(parent)
        self.window.grab_set()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(main_frame, text="Auto-Lock Configuration", 
                 font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        self.enabled_var = tk.BooleanVar()
        enabled_value = self.db_manager.get_setting('auto_lock_enabled', '1')
        self.enabled_var.set(enabled_value == '1')
        
        ttk.Checkbutton(main_frame, text="Enable auto-lock", 
                       variable=self.enabled_var,
                       command=self._toggle_enabled).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        timeout_frame = ttk.Frame(main_frame)
        timeout_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(timeout_frame, text="Lock after:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.minutes_var = tk.StringVar()
        current_minutes = self.db_manager.get_setting('auto_lock_minutes', '5')
        self.minutes_var.set(current_minutes)
        
        self.minutes_spinbox = ttk.Spinbox(timeout_frame, from_=1, to=60, 
                                          textvariable=self.minutes_var, 
                                          width=10,
                                          state='readonly' if not self.enabled_var.get() else 'normal')
        self.minutes_spinbox.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(timeout_frame, text="minutes of inactivity").pack(side=tk.LEFT)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2)
        
        ttk.Button(button_frame, text="Save", command=self._save_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT)
    
    def _toggle_enabled(self):
        """Toggle the enabled state of timeout controls"""
        if self.enabled_var.get():
            self.minutes_spinbox.config(state='normal')
        else:
            self.minutes_spinbox.config(state='readonly')
    
    def _save_settings(self):
        """Save auto-lock settings"""
        try:
            enabled = '1' if self.enabled_var.get() else '0'
            minutes = self.minutes_var.get().strip()
            
            try:
                minutes_int = int(minutes)
                if minutes_int < 1 or minutes_int > 60:
                    messagebox.showerror("Invalid Input", "Timeout must be between 1 and 60 minutes.")
                    return
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number of minutes.")
                return
            
            self.db_manager.set_setting('auto_lock_enabled', enabled)
            self.db_manager.set_setting('auto_lock_minutes', minutes)
            
            messagebox.showinfo("Success", "Auto-lock settings saved successfully!")
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")


class AddEditDialog:
    """Dialog for adding/editing password records"""
    
    def __init__(self, parent, db_manager, callback, record_id=None, site='', username='', password='', 
                 group=None, initial_password='', default_group=None, date_added=None, date_modified=None):
        self.db_manager = db_manager
        self.callback = callback
        self.record_id = record_id
        self.date_added = date_added
        self.date_modified = date_modified
        
        if not password and initial_password:
            password = initial_password
        
        if group is None and default_group is not None:
            group = default_group
        
        self.window = tk.Toplevel(parent)
        self.window.title("Edit Record" if record_id else "Add Record")
        
        # Adjust window height if editing (to show dates)
        window_height = 340 if record_id and (date_added or date_modified) else 250
        self.window.geometry(f"450x{window_height}")
        self.window.resizable(False, False)
        
        self.window.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        x = parent_x + 50
        y = parent_y + 50
        self.window.geometry(f"450x{window_height}+{x}+{y}")
        
        self._create_widgets(site, username, password, group)
        self.window.transient(parent)
        self.window.grab_set()
    
    def _create_widgets(self, site, username, password, group):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_columnconfigure(1, weight=1)
        
        current_row = 0
        
        ttk.Label(main_frame, text="Site Name:").grid(row=current_row, column=0, sticky=tk.W, pady=5)
        self.site_var = tk.StringVar(value=site)
        site_entry = ttk.Entry(main_frame, textvariable=self.site_var)
        site_entry.grid(row=current_row, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        site_entry.focus()
        current_row += 1
        
        ttk.Label(main_frame, text="Username:").grid(row=current_row, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar(value=username)
        username_entry = ttk.Entry(main_frame, textvariable=self.username_var)
        username_entry.grid(row=current_row, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        current_row += 1
        
        ttk.Label(main_frame, text="Password:").grid(row=current_row, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar(value=password)
        password_entry = ttk.Entry(main_frame, textvariable=self.password_var)
        password_entry.grid(row=current_row, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        current_row += 1
        
        ttk.Label(main_frame, text="Group:").grid(row=current_row, column=0, sticky=tk.W, pady=5)
        self.group_var = tk.StringVar(value=group if group else "")
        
        groups = self.db_manager.get_all_groups()
        if 'All' in groups:
            groups.remove('All')
        
        self.group_combo = ttk.Combobox(main_frame, textvariable=self.group_var, values=groups)
        self.group_combo.grid(row=current_row, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        current_row += 1
        
        # Show date fields only when editing
        if self.record_id and (self.date_added or self.date_modified):
            # Add separator
            separator = ttk.Separator(main_frame, orient='horizontal')
            separator.grid(row=current_row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=15)
            current_row += 1
            
            # Date Added
            if self.date_added:
                ttk.Label(main_frame, text="Date Added:", font=("Arial", 9, "bold")).grid(
                    row=current_row, column=0, sticky=tk.W, pady=3)
                date_added_label = ttk.Label(main_frame, text=self._format_date(self.date_added), 
                                             font=("Arial", 9), foreground="blue")
                date_added_label.grid(row=current_row, column=1, sticky=tk.W, padx=(10, 0), pady=3)
                current_row += 1
            
            # Date Modified
            if self.date_modified:
                ttk.Label(main_frame, text="Last Modified:", font=("Arial", 9, "bold")).grid(
                    row=current_row, column=0, sticky=tk.W, pady=3)
                date_modified_label = ttk.Label(main_frame, text=self._format_date(self.date_modified), 
                                                font=("Arial", 9), foreground="blue")
                date_modified_label.grid(row=current_row, column=1, sticky=tk.W, padx=(10, 0), pady=3)
                current_row += 1
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=current_row, column=0, columnspan=2, pady=(20, 0))
        
        action_text = "Update" if self.record_id else "Add"
        ttk.Button(button_frame, text=action_text, command=self._save).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT)
        
        self.window.bind('<Return>', lambda e: self._save())
        self.window.bind('<Escape>', lambda e: self._cancel())
    
    def _format_date(self, date_str):
        """Format date string for display"""
        if not date_str:
            return "N/A"
        
        try:
            # Try to parse and format the date nicely
            from datetime import datetime
            
            # Handle different date formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%B %d, %Y at %I:%M %p')
                except ValueError:
                    continue
            
            # If parsing fails, return as is
            return date_str
        except:
            return date_str
    
    def _save(self):
        """Save the record"""
        site = self.site_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        group = self.group_var.get().strip()
        
        if not site:
            messagebox.showerror("Validation Error", "Site name is required!")
            return
        
        if not password:
            messagebox.showerror("Validation Error", "Password is required!")
            return
        
        if not group:
            group = None
        
        try:
            if self.record_id:
                success = self.db_manager.update_record(self.record_id, site, username, password, group)
                if success:
                    messagebox.showinfo("Success", "Record updated successfully!")
                else:
                    return
            else:
                record_id = self.db_manager.add_record(site, username, password, group)
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
    
    def __init__(self, parent, db_manager, callback, current_group=None):
        self.db_manager = db_manager
        self.callback = callback
        self.current_group = current_group
        self.filename = None
        
        self.window = tk.Toplevel(parent)
        self.window.title("Import Passwords")
        self.window.geometry("350x250")
        self.window.resizable(False, False)
        
        self.window.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        x = parent_x + 75
        y = parent_y + 75
        self.window.geometry(f"350x250+{x}+{y}")
        
        self._create_widgets()
        self.window.transient(parent)
        self.window.grab_set()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(main_frame, text="Select data source:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.source_var = tk.StringVar(value="Chrome")
        sources = [("Chrome", "Chrome"), ("Firefox", "Firefox")]
        
        for i, (text, value) in enumerate(sources):
            ttk.Radiobutton(main_frame, text=text, variable=self.source_var, 
                           value=value).grid(row=i+1, column=0, sticky=tk.W, pady=2)
        
        ttk.Label(main_frame, text="Import to group:", font=("Arial", 10)).grid(
            row=3, column=0, sticky=tk.W, pady=(15, 5))
        
        self.group_var = tk.StringVar(value=self.current_group if self.current_group else "")
        groups = self.db_manager.get_all_groups()
        if 'All' in groups:
            groups.remove('All')
        
        groups.insert(0, "(None)")
        
        group_combo = ttk.Combobox(main_frame, textvariable=self.group_var, values=groups, width=25)
        group_combo.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(10, 10))
        file_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="File:").grid(row=0, column=0, sticky=tk.W)
        self.file_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_var, state='readonly', width=20)
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10))
        ttk.Button(file_frame, text="Browse", command=self._browse_file).grid(row=0, column=2)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, pady=(10, 0))
        
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
            group = self.group_var.get().strip()
            
            if group == "(None)" or group == "":
                group = None
            
            imported_count = 0
            
            with open(self.filename, 'r', newline='', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                
                try:
                    first_row = next(csv_reader)
                    if not any(field.startswith('http') for field in first_row):
                        pass
                    else:
                        file.seek(0)
                        csv_reader = csv.reader(file)
                except StopIteration:
                    messagebox.showerror("Error", "The selected file appears to be empty.")
                    return
                
                for row in csv_reader:
                    if len(row) < 3:
                        continue
                    
                    try:
                        if source == "Chrome":
                            if len(row) >= 4:
                                site = row[0] or row[1]
                                username = row[2]
                                password = row[3]
                        else:
                            site = row[0]
                            username = row[1]
                            password = row[2]
                        
                        if site and password:
                            if self.db_manager.add_record(site, username, password, group):
                                imported_count += 1
                    
                    except Exception as e:
                        print(f"Error processing row {row}: {e}")
                        continue
            
            if imported_count > 0:
                group_msg = f"to group '{group}'" if group else "without a group"
                messagebox.showinfo("Success", f"Successfully imported {imported_count} password(s) {group_msg}!")
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
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Change Password", command=self._change_password).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT)
        
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
        
        if not messagebox.askyesno("Confirm", "This will re-encrypt all your passwords. Continue?"):
            return
        
        if self.db_manager.change_master_password(new_password):
            messagebox.showinfo("Success", "Master password changed successfully!")
            self.window.destroy()


class PasswordManagerApp:
    """Main application class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("RandPyPwGen v1.99.8")
        self.root.geometry("900x700")
        
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"900x700+{x}+{y}")
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.db_manager = DatabaseManager()
        
        self.current_frame = None
        self._show_login()
    
    def _show_login(self):
        """Show login frame"""
        if self.current_frame:
            self.current_frame.destroy()
        
        self.current_frame = LoginFrame(self.root, self.db_manager, self._show_main)
        self.current_frame.grid(row=0, column=0)
        
        self.root.geometry("400x200")
        self.root.title("RandPyPwGen - Login")
    
    def _show_main(self):
        """Show main application frame"""
        if self.current_frame:
            self.current_frame.destroy()
        
        self.root.geometry("900x700")
        self.root.title("RandPyPwGen v1.99.8")
        
        self.current_frame = MainFrame(self.root, self.db_manager, self._show_login)
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
