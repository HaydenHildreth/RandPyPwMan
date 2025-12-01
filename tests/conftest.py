#!/usr/bin/env python3
"""
Pytest configuration for RandPyPwGen tests
"""

import pytest
import sys
import os

def pytest_configure(config):
    """Configure pytest for cross-platform testing"""
    # Mock tkinter for headless testing on Linux
    if sys.platform == 'linux':
        # Don't set DISPLAY, instead mock tkinter
        if 'DISPLAY' not in os.environ:
            os.environ['DISPLAY'] = ''
    
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
    # Mock tkinter completely for headless testing
    import sys
    from unittest.mock import MagicMock
    
    # Create mock modules
    mock_tk = MagicMock()
    mock_ttk = MagicMock()
    mock_messagebox = MagicMock()
    
    # Configure mocks
    mock_messagebox.showerror = MagicMock(return_value=None)
    mock_messagebox.showinfo = MagicMock(return_value=None)
    mock_messagebox.showwarning = MagicMock(return_value=None)
    mock_messagebox.askyesno = MagicMock(return_value=True)
    mock_messagebox.askokcancel = MagicMock(return_value=True)
    
    # Store originals if they exist
    originals = {}
    if 'tkinter' in sys.modules:
        originals['tkinter'] = sys.modules['tkinter']
        originals['tkinter.ttk'] = sys.modules.get('tkinter.ttk')
        originals['tkinter.messagebox'] = sys.modules.get('tkinter.messagebox')
    
    # Replace with mocks
    sys.modules['tkinter'] = mock_tk
    sys.modules['tkinter.ttk'] = mock_ttk
    sys.modules['tkinter.messagebox'] = mock_messagebox
    
    # Set up mock Tk class
    mock_tk.Tk = MagicMock
    mock_tk.Toplevel = MagicMock
    mock_tk.StringVar = MagicMock
    mock_tk.BooleanVar = MagicMock
    mock_tk.IntVar = MagicMock
    mock_tk.Frame = MagicMock
    mock_tk.Label = MagicMock
    mock_tk.Entry = MagicMock
    mock_tk.Button = MagicMock
    mock_tk.Listbox = MagicMock
    mock_tk.Canvas = MagicMock
    mock_tk.Menu = MagicMock
    mock_tk.messagebox = mock_messagebox
    
    mock_ttk.Frame = MagicMock
    mock_ttk.Label = MagicMock
    mock_ttk.Entry = MagicMock
    mock_ttk.Button = MagicMock
    mock_ttk.Combobox = MagicMock
    mock_ttk.Treeview = MagicMock
    mock_ttk.Scrollbar = MagicMock
    mock_ttk.LabelFrame = MagicMock
    mock_ttk.Checkbutton = MagicMock
    mock_ttk.Spinbox = MagicMock
    mock_ttk.Separator = MagicMock
    mock_ttk.Style = MagicMock
    
    yield
    
    # Restore originals
    if originals:
        sys.modules['tkinter'] = originals.get('tkinter')
        if originals.get('tkinter.ttk'):
            sys.modules['tkinter.ttk'] = originals['tkinter.ttk']
        if originals.get('tkinter.messagebox'):
            sys.modules['tkinter.messagebox'] = originals['tkinter.messagebox']
