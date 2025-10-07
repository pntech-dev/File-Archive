# File Archive (English Version)

A simple and powerful desktop application for managing and distributing versioned files and software.

## Description

**File Archive** is a desktop application designed for teams that need to manage and distribute different versions of their files or software. It automates the process of organizing, versioning, and accessing files from a centralized location.

The application scans a structured network directory where each software or file group is represented by a folder, and different versions are stored within these folders. File Archive allows users to browse these versions, download them, and, for authenticated users, add or delete versions and groups.

## Key Features

-   **Hierarchical Browsing**: Navigate through groups and their respective file versions.
-   **Download Functionality**: Download any version of a file or software to your local machine.
-   **Version Management**: Authenticated users can add new groups, add new versions to existing groups, and delete old files or entire groups.
-   **Password Protection**: The application is password-protected to prevent unauthorized modifications.
-   **Search**: Smart search for groups and versions with support for partial matches.
-   **Auto-Update**: The application automatically checks for a new version on the server and prompts for an update.
-   **Modern UI**: A clean and responsive user interface built with PyQt5.

## How It Works

For the application to function correctly, the data must be stored in a specific structure within the folder specified in `config.yaml`.

1.  **Root Folder**: The main folder containing all version groups, specified in the `versions_path` parameter in `config.yaml`.
2.  **Group Folder**: Each product or file group is a folder within the root folder.
3.  **Version Folder**: Inside each group folder, there are folders representing different versions. The version name is the name of the folder.

## Installation and Launch

To run the project from the source code, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone <repository URL>
    cd "File Archive"
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirments.txt
    ```

4.  **Configure the application:**
    -   Open the `config.yaml` file.
    -   Set the correct path to the network folder with version groups in the `versions_path` parameter.
    -   Specify the path to the folder with the current version of the program on the server in `server_program_path`.

5.  **Run the application:**
    ```bash
    python app.py
    ```

## Technology Stack

-   **Language**: Python
-   **GUI**: PyQt5
-   **Configuration**: PyYAML
-   **Architecture**: MVC (Model-View-Controller)

---

# File Archive (Русская версия)

Простое и мощное настольное приложение для управления и распространения версий программного обеспечения.

## Описание

**File Archive** — это десктопное приложение, разработанное для команд, которым необходимо управлять и распространять различные версии своих файлов или программного обеспечения. Оно автоматизирует процесс организации, версионирования и доступа к файлам из централизованного расположения.

Приложение сканирует структурированную сетевую директорию, где каждая группа программного обеспечения или файлов представлена папкой, а разные версии хранятся в этих папках. File Archive позволяет пользователям просматривать эти версии, загружать их, а аутентифицированным пользователям — добавлять или удалять версии и группы.

## Ключевые возможности

-   **Иерархический просмотр**: Навигация по группам и их соответствующим версиям файлов.
-   **Функциональность загрузки**: Загрузка любой версии файла или программного обеспечения на ваш локальный компьютер.
-   **Управление версиями**: Аутентифицированные пользователи могут добавлять новые группы, добавлять новые версии в существующие группы и удалять старые файлы или целые группы.
-   **Защита паролем**: Приложение защищено паролем для предотвращения несанкционированных изменений.
-   **Поиск**: Умный поиск по группам и версиям с поддержкой частичных совпадений.
-   **Автообновление**: Приложение автоматически проверяет наличие новой версии на сервере и предлагает выполнить обновление.
-   **Современный интерфейс**: Понятный и отзывчивый интерфейс, созданный с помощью PyQt5.

## Принцип работы

Для корректной работы приложения необходимо соблюдать определённую структуру хранения данных в папке, указанной в `config.yaml`.

1.  **Корневая папка**: Основная папка, содержащая все группы версий, указанная в параметре `versions_path` в `config.yaml`.
2.  **Папка группы**: Каждая группа продуктов или файлов — это папка в корневой папке.
3.  **Папка версии**: Внутри каждой папки группы находятся папки, представляющие разные версии. Имя версии — это имя папки.

## Установка и запуск

Для запуска проекта из исходного кода выполните следующие шаги:

1.  **Клонируйте репозиторий:**
    ```bash
    git clone <URL репозитория>
    cd "File Archive"
    ```

2.  **Создайте и активируйте виртуальное окружение:**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Установите зависимости:**
    ```bash
    pip install -r requirments.txt
    ```

4.  **Настройте конфигурацию:**
    -   Откройте файл `config.yaml`.
    -   Укажите корректный путь к сетевой папке с группами версий в параметре `versions_path`.
    -   Укажите путь к папке с актуальной версией программы на сервере в `server_program_path`.

5.  **Запустите приложение:**
    ```bash
    python app.py
    ```

## Технологический стек

-   **Язык**: Python
-   **GUI**: PyQt5
-   **Конфигурация**: PyYAML
-   **Архитектура**: MVC (Model-View-Controller)
