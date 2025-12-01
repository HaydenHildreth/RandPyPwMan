# RandPyPwGen Testing Guide

This guide explains how to run tests for the RandPyPwGen password manager across different platforms.

## Project Structure

```
RandPyPwGen/
├── main.py                          # Main application
├── requirements.txt                 # Application dependencies
├── .github/
│   └── workflows/
│       ├── build.yml               # Build executables workflow
│       └── test.yml                # Testing workflow
└── tests/
    ├── __init__.py                 # Makes tests a package
    ├── conftest.py                 # Pytest configuration
    ├── test_password_manager.py    # Main test file
    └── requirements.txt            # Testing dependencies
```

## Setup Instructions

### 1. Install Dependencies

```bash
# Install testing dependencies
pip install -r tests/requirements.txt

# Or install individually
pip install pytest pytest-cov pytest-timeout
pip install pyperclip cryptography bcrypt
```

### 2. Create Test Directory Structure

```bash
mkdir -p tests
```

### 3. Add Test Files

Place these files in the `tests/` directory:
- `test_password_manager.py` - Main test suite
- `conftest.py` - Pytest configuration
- `requirements.txt` - Testing dependencies
- `__init__.py` - Empty file to make tests a package

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run with Coverage Report

```bash
pytest tests/ -v --cov=. --cov-report=html
```

This creates an HTML coverage report in `htmlcov/index.html`

### Run Specific Test Classes

```bash
# Test only password generation
pytest tests/test_password_manager.py::TestPasswordGenerator -v

# Test only database operations
pytest tests/test_password_manager.py::TestDatabaseManager -v

# Test only integration tests
pytest tests/test_password_manager.py::TestIntegration -v
```

### Run Specific Tests

```bash
pytest tests/test_password_manager.py::TestPasswordGenerator::test_generate_valid_length -v
```

### Platform-Specific Considerations

#### Linux
Tests will run in headless mode automatically. If you need X server:
```bash
# Install xvfb for headless testing
sudo apt-get install xvfb

# Run with xvfb
xvfb-run pytest tests/ -v
```

#### macOS
No special setup required. Tests run normally.

#### Windows
No special setup required. Tests run normally.

## Test Coverage

The test suite covers:

### Password Generation (`TestPasswordGenerator`)
- ✅ Valid length generation (1-100 characters)
- ✅ Invalid input handling (zero, negative, too large)
- ✅ Password uniqueness
- ✅ Character set validation

### Database Operations (`TestDatabaseManager`)
- ✅ Master password verification
- ✅ Record CRUD operations (Create, Read, Update, Delete)
- ✅ Password encryption/decryption
- ✅ Group management (create, rename, delete)
- ✅ Search functionality
- ✅ Settings storage
- ✅ Record filtering by group

### Integration Tests (`TestIntegration`)
- ✅ Complete password workflow (generate → save → retrieve → update → delete)
- ✅ Multiple groups management

## GitHub Actions CI/CD

The project includes two workflows:

### Testing Workflow (`.github/workflows/test.yml`)
Runs on every push and pull request:
- Tests on Ubuntu, Windows, and macOS
- Tests Python 3.10, 3.11, and 3.12
- Generates coverage reports
- Uploads coverage to Codecov

### Build Workflow (`.github/workflows/build.yml`)
Runs on version tags (e.g., `v1.0.0`):
- Builds executables for all platforms
- Creates GitHub releases
- Attaches executables to releases

## Continuous Integration

### Triggering Tests

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

### Viewing Results

1. Go to the **Actions** tab in your GitHub repository
2. Select the **Test Multi-Platform** workflow
3. View test results for each platform/Python version

### Coverage Reports

Coverage reports are uploaded to Codecov for the Ubuntu/Python 3.11 combination. To enable:

1. Sign up at [codecov.io](https://codecov.io)
2. Connect your GitHub repository
3. Coverage reports will appear automatically

## Troubleshooting

### Test Database Issues

If tests fail with database errors:
```bash
# Clean up any leftover test databases
rm -rf /tmp/pytest-*
```

### GUI-Related Errors on Linux

```bash
# Install required packages
sudo apt-get install python3-tk xvfb

# Run with virtual display
xvfb-run pytest tests/ -v
```

### Import Errors

Make sure you're running from the project root:
```bash
# Correct - from project root
pytest tests/

# Wrong - from tests directory
cd tests && pytest  # Don't do this
```

## Writing New Tests

### Test Structure

```python
class TestNewFeature:
    """Test description"""
    
    def setup_method(self):
        """Setup before each test"""
        pass
    
    def teardown_method(self):
        """Cleanup after each test"""
        pass
    
    def test_feature_works(self):
        """Test that feature works correctly"""
        # Arrange
        expected = "expected result"
        
        # Act
        result = some_function()
        
        # Assert
        assert result == expected
```

### Best Practices

1. **Use descriptive test names**: `test_password_generation_with_special_chars`
2. **One assertion per test**: Focus on testing one thing
3. **Use fixtures**: Share setup code across tests
4. **Clean up**: Always cleanup temp files and databases
5. **Test edge cases**: Empty strings, None, invalid input

## Test Markers

Use markers to categorize tests:

```python
@pytest.mark.slow
def test_performance():
    pass

@pytest.mark.gui
def test_ui_element():
    pass
```

Run specific markers:
```bash
pytest -m "not slow"  # Skip slow tests
pytest -m "gui"       # Run only GUI tests
```

## Questions?

If tests fail on a specific platform:
1. Check the GitHub Actions logs for details
2. Try running tests locally on that platform
3. Check for platform-specific issues in the error message
4. Ensure all dependencies are installed correctly
