# Change Log
All notable changes to this project will be documented in this file.

## [0.9.3] - 08-29-2025
  
No database changes.

### Added

- Ability hide passwords via button press. Instead of displaying passwords, it will now show *s if this is enabled. [Issue #86](https://github.com/HaydenHildreth/RandPyPwMan/issues/86)
- Feature that prevents the clicking of the "Import Passwords" button prematurely. Now, the user will need to choose a file from the File Explorer before they're able to click that button. [Issue #87](https://github.com/HaydenHildreth/RandPyPwMan/issues/87)
 
### Fixed

- Issue with updating master password, that caused the database to not be able to decrypt passwords. [Issue #84](https://github.com/HaydenHildreth/RandPyPwMan/issues/84)

### Notes

- Next version is likely to be v1.0.0

## [0.9.2] - 02-19-2025
  
No database changes.

### Added

- Ability to change master password
 
### Fixed

- [Issue #80](https://github.com/HaydenHildreth/RandPyPwMan/issues/80)

### Notes

- None

## [0.9.1] - 01-12-2025
  
No database changes.

### Added

- Clear search button and function
 
### Fixed

- [Issue #77](https://github.com/HaydenHildreth/RandPyPwMan/issues/77)
- Minor capitalization changes to some of file menu and a label

### Notes

- I will work to improve the layout of buttons before v1.0.0. I would also like to include some scaling in that as well.

## [0.9.0] - 01-10-2025
  
No database changes.

### Added

- The documentation has been improved tremendously, it is far more detailed and the installation process is much more seamless. I've also added other instructions for additional Operating Systems such as MacOS and Linux.
- [CONTRIBUTORS.md](https://github.com/HaydenHildreth/RandPyPwMan/blob/CONTRIBUTING.md) (Users who have contributed to this project in one way or another)
- [CONTRIBUTING.md](https://github.com/HaydenHildreth/RandPyPwMan/blob/CONTRIBUTORS.md) (If you'd like to contribute please read this before making a Pull Request)
- Removed delete hotkey until further notice
 
### Fixed

- [Issue #71](https://github.com/HaydenHildreth/RandPyPwMan/issues/71)
- Documentation (specifically the README.md and installation instructions)

### Notes

- Probably not going to add delete hotkey back until after v1.0.0.

## [0.8.6] - 04-15-2024
  
No database changes.

### Added

- Hotfix for importing
 
### Fixed

- Issue with importing passwords

### Notes

- Bug was introduced in v0.7.10.


## [0.8.5] - 04-11-2024
  
No database changes. Major overhaul to how to run/access program, and its installation.

### Added

- Requirements.txt
- Splashscreen to main program
- Updated README.md instructions
- Updated logic for last index and inserting data into tables
 
### Fixed

- [Issue #11](https://github.com/HaydenHildreth/RandPyPwMan/issues/11).
- [Issue #15](https://github.com/HaydenHildreth/RandPyPwMan/issues/15).
- [Issue #29](https://github.com/HaydenHildreth/RandPyPwMan/issues/28).
- Issue with SQL script in install.py.

### Notes

- Getting pretty close to v1.0.0.


## [0.8.0] - 03-19-2024
  
Minor database changes. Please run 0.8.0.py before updating your program.

### Added

- Removed group fields.
- Update folder for future updates
- Update script for v0.8.0
 
### Fixed
 
- [Issue #27](https://github.com/HaydenHildreth/RandPyPwMan/issues/27).

### Notes

- Building to v0.8.0 for release.


## [0.7.10] - 03-17-2024
  
No database changes. Feel free to upgrade without any needed changes.

### Added

- Find_last_index() function.
 
### Fixed
 
- Logic to find the last index. This stops repeated code by referencing the same function throughout program.

### Notes

- No notes for this one. Small change. Full build (v0.8.0) coming after next significant change/feature.



## [0.7.9] - 03-14-2024
  
No database changes. Feel free to upgrade without any needed changes.

### Added

- Limit default width of ID column.
 
### Fixed
 
- Issue with logic in insert_info() function introduced over the past builds.
- Issue with splashscreen logic when implemented into main program.

### Notes

- You can still resize the ID column if you choose to do so.
- Splashscreen.py will now be utilized again (this will only affect dev builds).


## [0.7.8] - 03-09-2024
  
No database changes. Feel free to upgrade without any needed changes.

### Added

- Added ability to use a hotkey to delete all selected values at once
 
### Fixed
 
- [Issue #18](https://github.com/HaydenHildreth/RandPyPwMan/issues/18)

### Notes

- May want to add a "are you sure you want to delete" screen.

## [0.7.6] - 03-06-2024
  
No database changes. Feel free to upgrade without any needed changes.

### Added

- Added ability to import passwords from both Chrome and Firefox
 
### Fixed
 
- [Issue #24](https://github.com/HaydenHildreth/RandPyPwMan/issues/24)
  This issue is fixed, however another new issue is now open.
- [NEW ISSUE #52](https://github.com/HaydenHildreth/RandPyPwMan/issues/52)
  Cleanup of new functionality by adding error handling.

### Notes

- Screen is a bit cluttered / UI is a bit ugly. Not a priority at this point though.

## [0.7.0] - 01-30-2024
  
No database changes. Feel free to upgrade without any needed changes.

### Added

- Added search functionality to sort and filter passwords
 
### Fixed
 
- [Issue #26](https://github.com/HaydenHildreth/RandPyPwMan/issues/26)
  This issue is one of the items I worked on besides search feature.

### Notes

- Screen is a bit cluttered / UI is a bit ugly. Not a priority at this point though.

## [0.6.2] - 09-05-2023
  
Minor database changes. Reach out if you need assitance upgrading from a previous version.

### Added

- Added password logic and database columns.
- Added clear_button function and button
 
### Fixed
 
- [Issue #35](https://github.com/HaydenHildreth/RandPyPwMan/issues/35)
  Clear button logic fixes this issue.
