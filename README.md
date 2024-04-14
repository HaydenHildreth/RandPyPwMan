# RandPyPwMan

## What is RandPyPwMan - WIP [Work in progress]
It's a simple and easy to use password generator and password manager that's open-source and made in Python 3 using Tkinter. Do not get too attached to the name as it will likely be changing before the final release. Program screenshots are available in main branch README.

## Screenshots
![Screenshot](https://github.com/HaydenHildreth/RandPyPwMan/blob/main/screenshots/screenshot.png)
![Screenshot](https://github.com/HaydenHildreth/RandPyPwMan/blob/main/screenshots/pwman1.PNG)
![Screenshot](https://github.com/HaydenHildreth/RandPyPwMan/blob/main/screenshots/pwman2.png)
![Screenshot](https://github.com/HaydenHildreth/RandPyPwMan/blob/main/screenshots/pwman4.png)
![Screenshot](https://github.com/HaydenHildreth/RandPyPwMan/blob/main/screenshots/pwman5.png)
![Screenshot](https://github.com/HaydenHildreth/RandPyPwMan/blob/main/screenshots/pwman3.PNG)

## How to use it?
Make sure you have [Python 3.10](https://www.python.org/downloads/windows/) or higher installed. You will also need to install [sqlite3](https://www.sqlite.org/download.html) for a database engine. [Make sure you've added sqlite3 to your system PATH (if Windows)](https://dev.to/dendihandian/installing-sqlite3-in-windows-44eb). Windows users can copy/download the repository and skip cloning the repository, or install git and follow the instructions below.

* Then clone the repository by using:
```
git clone https://github.com/HaydenHildreth/RandPyPwMan.git
```

* Open your terminal and change direcotry to the correct folder:
```
cd <path-to-repo>\
```

* Install dependencies:
```
pip install -r requirements.txt
```

* Run install script:
```
python install.py
```

* Run main script:
```
python main.py
```


## Known problems
- Very ugly
    - Planning to fix UI/UX soon

## Major Release Notes
- #### See [CHANGELOG.MD](https://github.com/HaydenHildreth/RandPyPwMan/blob/main/CHANGELOG.md) for more detailed information.
- In version 0.8.5 I've made many changes, but there is new install and program usage logic. See CHANGELOG.md.
- In version 0.8.0 I've removed the group field, change the insert and search functionality and more. See CHANGELOG.md.
- In version 0.7.8 I've added the ability to use a hotkey to delete selected password(s). See commit logs or CHANGELOG.md for more info.
- In version 0.7.6 I've added the ability to import passwords from browsers. See commit logs or CHANGELOG.md for more info.
- In version 0.7.0 I've added search functionality.
    - In version 0.6.2 I've added CHANGELOG.md. Visit this file for more detailed information regarding version changes. Major changes will still be present in this section of the README.md.
- In version 0.6.0 I've added encryption of passwords sent to database. It is possible to convert raw passwords to encrypted. Please contact me directly if you were using a past build and need to know how to update your existing passwords. See dev or encryption branch/issues for more details.
- In version 0.4.5 I've added a login screen/splash screen. Alongside a hashed master password. See the dev branch for more details.
