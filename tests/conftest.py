#!/usr/bin/env python3
"""
Pytest configuration for RandPyPwGen tests
"""

import pytest
import sys
import os

def pytest_configure(config):
    """Configure pytest for cross-platform testing"""
    # Set headless mode for GUI testing on Linux
    if sys.platform == 'linux':
        os.environ['DISPLAY'] = ':99'
    
    # Add markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "gui: marks tests that require GUI components"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


@pytest.fixture(scope="session")
def platform_info():
    """Provide platform information to tests"""
    return {
        'system': sys.platform,
        'is_windows': sys.platform == 'win32',
        'is_mac': sys.platform == 'darwin',
        'is_linux': sys.platform == 'linux',
        'python_version': sys.version
    }


@pytest.fixture(autouse=True)
def suppress_gui():
    """Suppress GUI elements during testing"""
    # Mock tkinter messagebox if tests don't need real GUI
    import tkinter.messagebox
    original_showerror = tkinter.messagebox.showerror
    original_showinfo = tkinter.messagebox.showinfo
    original_showwarning = tkinter.messagebox.showwarning
    original_askyesno = tkinter.messagebox.askyesno
    
    # Replace with no-ops for non-GUI tests
    tkinter.messagebox.showerror = lambda *args, **kwargs: None
    tkinter.messagebox.showinfo = lambda *args, **kwargs: None
    tkinter.messagebox.showwarning = lambda *args, **kwargs: None
    tkinter.messagebox.askyesno = lambda *args, **kwargs: True
    
    yield
    
    # Restore original functions
    tkinter.messagebox.showerror = original_showerror
    tkinter.messagebox.showinfo = original_showinfo
    tkinter.messagebox.showwarning = original_showwarning
    tkinter.messagebox.askyesno = original_askyesno
