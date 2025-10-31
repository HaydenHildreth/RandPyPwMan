# RandPyPwMan

## What is RandPyPwMan
It is a simple and easy to use password generator/manager that is open-source and made in Python 3 using Tkinter. It is cross-platform, and able to ran on most major Operating Systems. Program screenshots are available below, or you can view the screenshot folder in the repository.

## Screenshots
![Screenshot](https://github.com/HaydenHildreth/RandPyPwMan/blob/main/screenshots/screenshot6.png)
![Screenshot](https://github.com/HaydenHildreth/RandPyPwMan/blob/main/screenshots/screenshot1.png)
![Screenshot](https://github.com/HaydenHildreth/RandPyPwMan/blob/main/screenshots/screenshot2.png)
![Screenshot](https://github.com/HaydenHildreth/RandPyPwMan/blob/main/screenshots/screenshot3.png)
![Screenshot](https://github.com/HaydenHildreth/RandPyPwMan/blob/main/screenshots/screenshot4.png)
![Screenshot](https://github.com/HaydenHildreth/RandPyPwMan/blob/main/screenshots/screenshot5.png)
![Screenshot](https://github.com/HaydenHildreth/RandPyPwMan/blob/main/screenshots/screenshot7.png)

## How to use it?
### Windows
Make sure you have [Python 3.10](https://www.python.org/downloads/) or higher installed. You will also need to install [sqlite3](https://www.sqlite.org/download.html) for a database engine. [Make sure you've added sqlite3 to your system PATH](https://dev.to/dendihandian/installing-sqlite3-in-windows-44eb). Users can copy/download the repository and skip cloning the repository, or [install git](https://git-scm.com/download/win) and follow the instructions below.

* Then clone the repository by using (alternatively you can simply download the files):
```
git clone https://github.com/HaydenHildreth/RandPyPwMan.git
```

* Open your terminal and change directory to the correct folder:
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

### MacOS
* Ensure Python 3.10 or higher is installed

* Clone the repository:
```
git clone https://github.com/HaydenHildreth/RandPyPwMan.git
```

* Open your terminal and change directory to the correct folder:
```
cd <path-to-repo>\
```

* Install dependencies:
```
brew install -r requirements.txt
```

* Run install script:
```
python install.py
```

* Run main script:
```
python main.py
```

### Linux
* Ensure Python 3.10 or higher is installed

* Clone the repository:
```
git clone https://github.com/HaydenHildreth/RandPyPwMan.git
```

* Open your terminal and change directory to the correct folder:
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

## Major Release Notes
- #### See [CHANGELOG.MD](https://github.com/HaydenHildreth/RandPyPwMan/blob/main/CHANGELOG.md) for more detailed information.
- In version 1.0.3 I've added additional themes, Light, Dark, Nord, Dracula, Solarized Light/Dark, Gruvbox Dark and Monokai. See CHANGELOG.md.
- In version 1.0.2 I've added some new database fields, last_modified and date_created. See CHANGELOG.md.
- In version 1.0.1 I've added a hotkey to delete passwords from the software. I've also made minor verbiage changes to several window titles. See CHANGELOG.md.
- In version 1.0.0 I've added much more additional error checking. The program has better capacity to handle misuse from input user. See CHANGELOG.md.
- In version 0.9.3 I've added hiding of passwords, and have added logic to prevent errors from user error. Also, this build features a major bug fix. See CHANGELOG.md.
- In version 0.9.2 I've added the ability for the user to update their master password via the file menu. See CHANGELOG.md.
- In version 0.9.0 I've improved the documentation immensely, added files to help new contributors, and removed a few features temporarily. See CHANGELOG.md.
- In version 0.8.5 I've made many changes, but there is new install and program usage logic. See CHANGELOG.md.
- In version 0.8.0 I've removed the group field, change the insert and search functionality and more. See CHANGELOG.md.
- In version 0.7.8 I've added the ability to use a hotkey to delete selected password(s). See commit logs or CHANGELOG.md for more info.
- In version 0.7.6 I've added the ability to import passwords from browsers. See commit logs or CHANGELOG.md for more info.
- In version 0.7.0 I've added search functionality.
- In version 0.6.2 I've added CHANGELOG.md. Visit this file for more detailed information regarding version changes. Major changes will still be present in this section of the README.md.
- In version 0.6.0 I've added encryption of passwords sent to database. It is possible to convert raw passwords to encrypted. Please contact me directly if you were using a past build and need to know how to update your existing passwords. See dev or encryption branch/issues for more details.
- In version 0.4.5 I've added a login screen/splash screen. Alongside a hashed master password. See the dev branch for more details.
