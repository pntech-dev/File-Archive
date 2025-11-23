# File Archive

> Russian version available: README_RU.md

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Framework](https://img.shields.io/badge/Framework-PyQt5-39a)
![Security](https://img.shields.io/badge/Encryption-Fernet-green)
![Access Modes](https://img.shields.io/badge/Access-Full%20%2F%20Standard-orange)
![Status](https://img.shields.io/badge/Status-Maintained-yellow)
![License](https://img.shields.io/badge/License-MIT-success)
![UI](https://img.shields.io/badge/UI-Modern%20Design-blueviolet)

Desktop application for encrypted versioned storage, distribution, and controlled access to engineering files within an organization.

---

## 🖼 Screenshots

### Authorization window:
Secure login screen with password authentication.  
Allows switching between Full Access mode and Standard mode, and provides an option to change the password.

![auth_tab](screenshots/authorization.png)

### Download Tab:
Displays all products and their latest available versions.  
Users can search, select a product, choose a version, and download files (automatically to Desktop or to a custom location).

![download_tab](screenshots/download_tab.png)

### Add Tab:
Available in Full Access mode.  
Allows adding new versions or attaching DOCX instruction files to existing or newly created product groups.

![add_tab](screenshots/add_tab.png)

### Delete Tab:
Available in Full Access mode.  
Allows deleting specific versions or entire product groups, with confirmation protection to prevent accidental removal.

![delete_tab](screenshots/delete_tab.png)

---

## 📥 Download workflow

1. Select a product by clicking once in the table  
   (the latest available version is selected automatically)

2. Optional: double-click a product to open version listing  
   and select **any previous version** if it was uploaded earlier

3. Choose a save location:  
   - by default, the file will be downloaded to the Desktop  
   - or a custom folder can be selected

4. Click **Download**  
   The selected version is decrypted and saved to the chosen destination

This workflow allows engineers to retrieve current releases  
and operators to safely download only approved versions.

---

## 📌 Overview

**File Archive** provides a secure and structured way to store, update, distribute, and retrieve versioned project files and technical documentation.  

The application ensures data confidentiality using user-generated cryptographic keys and supports different access modes for engineers and production personnel. 

Designed for environments where controlled access, integrity, and up-to-date versions, secure distribution is critical.

---

## 🎯 Key Features

### ✅ Versioned file storage
- Organized by **groups (products)** and **versions**
- Automatic latest version detection
- Encrypted at rest

### ✅ Two access modes
#### 🔐 Full Access Mode (after password authentication)
- Add new versions
- Add `.docx` instruction files
- Delete versions or entire groups
- Manage archive structure
- Engineers / supervisors

#### ✅ Standard Mode
- Tabs Add/Delete are visible but **disabled**
- Users can **only download**
- Operators / factory workers

### ✅ DOCX instructions support
Attach documentation for each product for use in a production environment.

### ✅ Encryption model
- Fernet symmetric encryption
- User-generated keyfile and password file
- No shared keys in repository
- Encrypted files stored with `.enc` extension

### ✅ UI/UX highlights
- PyQt5 interface
- Layered navigation
- Search across all versions
- Progress indicators
- Action notifications

---

## 🧩 Who is this for?

✅ Engineering departments  
✅ Manufacturing and production environments  
✅ Teams distributing controlled documentation  
✅ Organizations requiring secure versioned file access  
✅ Workplaces with separated access levels (engineers vs operators)

---

## 🧠 What this project demonstrates about me

✅ Python OOP  
✅ PyQt GUI engineering  
✅ MVC architecture  
✅ Multithreading for blocking operations  
✅ Secure file handling  
✅ UX logic and state management  
✅ Clean code and documentation discipline  
✅ Configuration & deployment awareness  
✅ Real-world application thinking  

---

## 🏗 Architecture
```
┌──────┐     ┌────────────┐     ┌───────┐
│ View │ <-- │ Controller │ --> │ Model │
└──────┘     └────────────┘     └───────┘
```

UI Layer Signal/Slot Encryption
Widgets coordination File ops
State visuals Flow logic Versioning

---

## 🛠 Tech Stack

- Python **3.10**
- PyQt5
- cryptography (Fernet)
- PyYAML
- threading
- pathlib

---

## 🔧 Installation

```bash
git clone https://github.com/pntech-dev/File-Archive.git
cd File-Archive
pip install -r requirements.txt
```

---

## 🔑 Key generation & initialization

1. Run the key generation script: `python generate_keyfiles.py`
1. A `config.yaml` file is created based on `config_template.yaml`
2. Keys are stored locally and never committed
3. Application can now operate securely
   
---

## 🏗 Building (optional)

The application can be packaged using PyInstaller with the provided spec:

```bash
pyinstaller "File Archive.spec"
```

---

## 📂 Project Structure

```
FILE-ARCHIVE/
│ app.py
│ config_template.yaml
│ generate_keyfiles.py
│ File Archive.spec
│ requirements.txt
│ README.md
│
├─ mvc/
│ ├─ controller.py
│ ├─ model.py
│ ├─ view.py
│ └─ __init__.py
│
├─ classes/
│ ├─ notifications.py
│ ├─ password_dialog.py
│ └─ __init__.py
│
├─ resources/
│ ├─ resources.qrc
│ ├─ resources_rc.py
│ ├─ icon.ico
│ ├─ checkbox_check.svg
│ ├─ combobox_arrow.svg
│ ├─ auth/
│ ├─ notifications/
│ ├─ radio_buttons/
│ ├─ search/
│ └─ tabs/
│
├─ ui/
│ └─ (Qt Designer UI files)
│
└─ screenshots/
└─ (application images)
```

---

## 🔒 Security Model

✅ Encrypted storage  
✅ No plaintext password saving  
✅ No cryptographic keys in repository  
✅ User-specific initialization  
✅ Safe for internal distribution  

---

## 🚦 Project Status

✅ Stable  
✅ Maintained when needed  
✅ Bug fixes and improvements possible  
❌ No active feature expansion planned  

---

## 📜 License

MIT License

Copyright (c) 2025 Pavel (PN Tech)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files...

---

## 👤 Author

**Pavel (PN Tech)**  
Python desktop and web developer, UI/UX designer, electronics engineer  