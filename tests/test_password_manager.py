#!/usr/bin/env python3
"""
Unit Testing for RandPyPwMan
"""

import pytest
import sqlite3
import tempfile
import shutil
import bcrypt
from pathlib import Path
from cryptography.fernet import Fernet

# Import from main.py
from main import DatabaseManager, PasswordGenerator


class TestPasswordGenerator:
    """Test password generation functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.generator = PasswordGenerator()
    
    def test_generate_valid_length(self):
        """Test generating passwords of valid lengths"""
        for length in [8, 16, 32, 64]:
            password = self.generator.generate(length)
            assert len(password) == length
            assert isinstance(password, str)
    
    def test_generate_minimum_length(self):
        """Test minimum password length"""
        password = self.generator.generate(1)
        assert len(password) == 1
    
    def test_generate_maximum_length(self):
        """Test maximum password length"""
        password = self.generator.generate(100)
        assert len(password) == 100
    
    def test_generate_invalid_length_zero(self):
        """Test that zero length raises ValueError"""
        with pytest.raises(ValueError):
            self.generator.generate(0)
    
    def test_generate_invalid_length_negative(self):
        """Test that negative length raises ValueError"""
        with pytest.raises(ValueError):
            self.generator.generate(-5)
    
    def test_generate_invalid_length_too_large(self):
        """Test that length over 100 raises ValueError"""
        with pytest.raises(ValueError):
            self.generator.generate(101)
    
    def test_generate_uniqueness(self):
        """Test that generated passwords are unique"""
        passwords = [self.generator.generate(20) for _ in range(100)]
        # Should be highly unlikely to generate duplicates
        assert len(set(passwords)) > 95
    
    def test_generate_contains_valid_characters(self):
        """Test that generated passwords contain expected character types"""
        import string
        valid_chars = set(string.ascii_lowercase + string.ascii_uppercase + 
                         string.digits + string.punctuation)
        
        password = self.generator.generate(50)
        for char in password:
            assert char in valid_chars


class TestDatabaseManager:
    """Test database operations and encryption"""
    
    def setup_method(self):
        """Setup temporary database for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_db"
        
        # Create database structure manually to avoid GUI
        self.db_path.mkdir(exist_ok=True)
        self.data_db = self.db_path / "data.db"
        self.unlock_db = self.db_path / "unlock.db"
        
        # Initialize databases
        self._setup_test_databases()
        
        # Create DatabaseManager instance
        self.db_manager = DatabaseManager(str(self.db_path))
    
    def teardown_method(self):
        """Cleanup after each test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _setup_test_databases(self):
        """Setup test databases with master password"""
        # Setup data.db
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
        c.execute("""CREATE TABLE IF NOT EXISTS groups(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name varchar(100) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.commit()
        conn.close()
        
        # Setup unlock.db with test master password
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
        
        # Create master password "test123"
        test_password = "test123"
        hash_master = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
        enc_key = Fernet.generate_key()
        
        c2.execute("INSERT INTO master VALUES (?,?)", (hash_master, enc_key))
        c2.execute("INSERT INTO settings VALUES ('theme', 'Light')")
        c2.execute("INSERT INTO settings VALUES ('auto_lock_enabled', '1')")
        c2.execute("INSERT INTO settings VALUES ('auto_lock_minutes', '5')")
        conn2.commit()
        conn2.close()
    
    def test_verify_master_password_correct(self):
        """Test verifying correct master password"""
        assert self.db_manager.verify_master_password("test123") == True
    
    def test_verify_master_password_incorrect(self):
        """Test verifying incorrect master password"""
        assert self.db_manager.verify_master_password("wrong") == False
    
    def test_verify_master_password_empty(self):
        """Test verifying empty master password"""
        assert self.db_manager.verify_master_password("") == False
    
    def test_add_record_basic(self):
        """Test adding a basic password record"""
        record_id = self.db_manager.add_record("example.com", "user@test.com", "password123")
        assert record_id is not None
        assert isinstance(record_id, int)
    
    def test_add_record_with_group(self):
        """Test adding a password record with a group"""
        record_id = self.db_manager.add_record("test.com", "user", "pass", "Work")
        assert record_id is not None
        
        # Verify group was created
        groups = self.db_manager.get_all_groups()
        assert "Work" in groups
    
    def test_get_record_by_id(self):
        """Test retrieving a record by ID"""
        record_id = self.db_manager.add_record("site.com", "username", "password")
        record = self.db_manager.get_record_by_id(record_id)
        
        assert record is not None
        assert record[1] == "site.com"
        assert record[2] == "username"
    
    def test_get_record_nonexistent(self):
        """Test retrieving a non-existent record"""
        record = self.db_manager.get_record_by_id(99999)
        assert record is None
    
    def test_update_record(self):
        """Test updating an existing record"""
        record_id = self.db_manager.add_record("old.com", "olduser", "oldpass")
        success = self.db_manager.update_record(record_id, "new.com", "newuser", "newpass")
        
        assert success == True
        
        record = self.db_manager.get_record_by_id(record_id)
        assert record[1] == "new.com"
        assert record[2] == "newuser"
    
    def test_delete_record(self):
        """Test deleting a record"""
        record_id = self.db_manager.add_record("delete.com", "user", "pass")
        success = self.db_manager.delete_record(record_id)
        
        assert success == True
        
        record = self.db_manager.get_record_by_id(record_id)
        assert record is None
    
    def test_get_all_records_empty(self):
        """Test getting all records when database is empty"""
        records = self.db_manager.get_all_records()
        assert records == []
    
    def test_get_all_records_multiple(self):
        """Test getting all records with multiple entries"""
        self.db_manager.add_record("site1.com", "user1", "pass1")
        self.db_manager.add_record("site2.com", "user2", "pass2")
        self.db_manager.add_record("site3.com", "user3", "pass3")
        
        records = self.db_manager.get_all_records()
        assert len(records) == 3
    
    def test_search_records_by_site(self):
        """Test searching records by site name"""
        self.db_manager.add_record("github.com", "user1", "pass1")
        self.db_manager.add_record("gitlab.com", "user2", "pass2")
        self.db_manager.add_record("example.com", "user3", "pass3")
        
        results = self.db_manager.search_records("git")
        assert len(results) == 2
    
    def test_search_records_by_username(self):
        """Test searching records by username"""
        self.db_manager.add_record("site1.com", "john@email.com", "pass1")
        self.db_manager.add_record("site2.com", "jane@email.com", "pass2")
        self.db_manager.add_record("site3.com", "admin", "pass3")
        
        results = self.db_manager.search_records("john")
        assert len(results) == 1
    
    def test_search_records_case_insensitive(self):
        """Test that search is case-insensitive"""
        self.db_manager.add_record("GitHub.com", "User", "pass")
        
        results = self.db_manager.search_records("github")
        assert len(results) == 1
    
    def test_encryption_decrypt_password(self):
        """Test password encryption and decryption"""
        original_password = "MySecretPassword123!"
        record_id = self.db_manager.add_record("test.com", "user", original_password)
        
        record = self.db_manager.get_record_by_id(record_id)
        encrypted_password = record[3]
        
        # Decrypt and verify
        decrypted = self.db_manager.decrypt_password(encrypted_password)
        assert decrypted == original_password
    
    def test_encryption_different_passwords_different_ciphertext(self):
        """Test that same password produces different ciphertext (due to encryption)"""
        password = "SamePassword"
        record_id1 = self.db_manager.add_record("site1.com", "user1", password)
        record_id2 = self.db_manager.add_record("site2.com", "user2", password)
        
        record1 = self.db_manager.get_record_by_id(record_id1)
        record2 = self.db_manager.get_record_by_id(record_id2)
        
        # Encrypted values should be different due to Fernet's IV
        assert record1[3] != record2[3]
        
        # But they should decrypt to the same value
        decrypted1 = self.db_manager.decrypt_password(record1[3])
        decrypted2 = self.db_manager.decrypt_password(record2[3])
        assert decrypted1 == decrypted2 == password
    
    def test_group_operations(self):
        """Test group creation, retrieval, and deletion"""
        # Add groups
        assert self.db_manager.add_group("Personal") == True
        assert self.db_manager.add_group("Work") == True
        
        # Get all groups
        groups = self.db_manager.get_all_groups()
        assert "Personal" in groups
        assert "Work" in groups
        
        # Try to add duplicate
        assert self.db_manager.add_group("Personal") == False
        
        # Delete group
        assert self.db_manager.delete_group("Personal") == True
        
        groups = self.db_manager.get_all_groups()
        assert "Personal" not in groups
    
    def test_rename_group(self):
        """Test renaming a group"""
        self.db_manager.add_group("OldName")
        self.db_manager.add_record("site.com", "user", "pass", "OldName")
        
        success = self.db_manager.rename_group("OldName", "NewName")
        assert success == True
        
        # Verify group was renamed
        groups = self.db_manager.get_all_groups()
        assert "NewName" in groups
        assert "OldName" not in groups
        
        # Verify record was updated
        records = self.db_manager.get_all_records()
        assert records[0][4] == "NewName"
    
    def test_settings_get_set(self):
        """Test getting and setting configuration values"""
        # Default value
        theme = self.db_manager.get_setting('theme', 'Dark')
        assert theme == 'Light'
        
        # Set new value
        self.db_manager.set_setting('theme', 'Dark')
        theme = self.db_manager.get_setting('theme')
        assert theme == 'Dark'
    
    def test_settings_nonexistent_default(self):
        """Test getting a non-existent setting returns default"""
        value = self.db_manager.get_setting('nonexistent', 'default_value')
        assert value == 'default_value'
    
    def test_filter_by_group(self):
        """Test filtering records by group"""
        self.db_manager.add_record("site1.com", "user1", "pass1", "Work")
        self.db_manager.add_record("site2.com", "user2", "pass2", "Personal")
        self.db_manager.add_record("site3.com", "user3", "pass3", "Work")
        
        work_records = self.db_manager.get_all_records("Work")
        assert len(work_records) == 2
        
        personal_records = self.db_manager.get_all_records("Personal")
        assert len(personal_records) == 1


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def setup_method(self):
        """Setup for integration tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_db"
        self.db_path.mkdir(exist_ok=True)
        
        # Setup databases
        data_db = self.db_path / "data.db"
        unlock_db = self.db_path / "unlock.db"
        
        # Initialize data.db
        conn = sqlite3.connect(data_db)
        c = conn.cursor()
        c.execute("""CREATE TABLE data(
            id INTEGER PRIMARY KEY,
            site varchar(100),
            username varchar(100),
            password varchar(100),
            group_name varchar(100),
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        c.execute("""CREATE TABLE groups(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name varchar(100) UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.commit()
        conn.close()
        
        # Initialize unlock.db
        conn2 = sqlite3.connect(unlock_db)
        c2 = conn2.cursor()
        c2.execute("CREATE TABLE master(key varchar(255), enc_key varchar(255))")
        c2.execute("CREATE TABLE settings(key varchar(100) PRIMARY KEY, value varchar(255))")
        
        password = "master123"
        hash_master = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        enc_key = Fernet.generate_key()
        
        c2.execute("INSERT INTO master VALUES (?,?)", (hash_master, enc_key))
        c2.execute("INSERT INTO settings VALUES ('theme', 'Light')")
        conn2.commit()
        conn2.close()
        
        self.db_manager = DatabaseManager(str(self.db_path))
        self.password_gen = PasswordGenerator()
    
    def teardown_method(self):
        """Cleanup"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_password_workflow(self):
        """Test a complete workflow: generate, save, retrieve, update, delete"""
        # Generate password
        password = self.password_gen.generate(16)
        assert len(password) == 16
        
        # Save to database
        record_id = self.db_manager.add_record("example.com", "testuser", password, "Personal")
        assert record_id is not None
        
        # Retrieve and verify
        record = self.db_manager.get_record_by_id(record_id)
        decrypted = self.db_manager.decrypt_password(record[3])
        assert decrypted == password
        
        # Update
        new_password = self.password_gen.generate(20)
        self.db_manager.update_record(record_id, "example.com", "newuser", new_password, "Work")
        
        updated_record = self.db_manager.get_record_by_id(record_id)
        assert updated_record[2] == "newuser"
        assert self.db_manager.decrypt_password(updated_record[3]) == new_password
        
        # Delete
        self.db_manager.delete_record(record_id)
        assert self.db_manager.get_record_by_id(record_id) is None
    
    def test_multiple_groups_workflow(self):
        """Test managing multiple groups with passwords"""
        # Create groups
        groups = ["Work", "Personal", "Social"]
        for group in groups:
            self.db_manager.add_group(group)
        
        # Add passwords to different groups
        for i, group in enumerate(groups):
            password = self.password_gen.generate(12)
            self.db_manager.add_record(f"site{i}.com", f"user{i}", password, group)
        
        # Verify each group has one password
        for group in groups:
            records = self.db_manager.get_all_records(group)
            assert len(records) == 1
        
        # Verify all records
        all_records = self.db_manager.get_all_records()
        assert len(all_records) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
