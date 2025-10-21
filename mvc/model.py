import os
import re
import sys
import yaml
import shutil
import datetime

from pathlib import Path
from packaging import version
from cryptography.fernet import Fernet, InvalidToken

from PyQt5.QtCore import QObject, pyqtSignal


class Model(QObject):
    progress_chehged = pyqtSignal(str, int) # Сигнал изменения прогресс бара
    show_notification = pyqtSignal(str, str) # Сигнал отображения уведомления (Тип, Текст)

    def __init__(self):
        super().__init__()

        # Определяем базовый путь для скрипта и скомпилированного приложения
        if getattr(sys, 'frozen', False):
            self.base_path = Path(sys.executable).parent
        else:
            # Путь к папке проекта (e.g., File Archive/)
            self.base_path = Path(__file__).parent.parent

        self.config_data = self.__load_config() # Получаем данные из файла конфигурации
        self.in_group = False # Флаг нахождения таблицы в отображении всех версий группы
        self.search_all_versions = False # Флаг поиска всех версий
        self.new_group_name = None # Имя новой группы
        self.keyfile_path = self.base_path / "_internal" / "keyfile.key" # Ключ шифрования
        self.password_file_path = self.base_path / "_internal" / "password.key" # Файл с паролем

        # Прогресс бар
        self.DOWNLOAD_PROGRESS_BAR_STEP = 3
        self.CREATE_NEW_GROUP_PROGRESS_BAR_STEP = 3
        self.ADD_PROGRESS_BAR_STEP = 2
        self.DELETE_PROGRESS_BAR_STEP = 2

    def __load_config(self):
        """Функция загружает данные из файла конфигурации"""
        try:
            config_path = self.base_path / "config.yaml"
            if not config_path.exists():
                self.show_notification.emit("error", f"Файл конфигурации не найден.\nПуть: {config_path}")
                return None
            
            with open(config_path, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
                # Удаляем ключ пароля, если он все еще там есть, т.к. он больше не используется
                if config and 'password' in config:
                    del config['password']
                return config

        except Exception as e:
            self.show_notification.emit("error", f"Произошла непредвиденная ошибка при чтении файла конфигурации.\nОшибка: {e}")
            return None

    def __parse_date(self, date_str):
        """Функция парсит дату в формате ДД.ММ.ГГГГ"""
        try:
            if date_str:
                return datetime.datetime.strptime(date_str, "%d.%m.%Y")
            else:
                return datetime.datetime.min
        except ValueError:
            return datetime.datetime.min
        
    def __encrypt_file(self, src_path: str, dst_path: str):
        """Шифрует один файл и сохраняет зашифрованную копию по указанному пути."""
        # Добавляем расширение .enc к файлу
        dst_path_obj = Path(str(dst_path) + ".enc")

        # Читаем ключ из файла
        with open(self.keyfile_path, "rb") as kf:
            key = kf.read().strip()

        fernet = Fernet(key)

        # Читаем исходные данные
        with open(src_path, "rb") as f:
            data = f.read()

        # Шифруем
        encrypted_data = fernet.encrypt(data)

        # Создаём каталог, если нужно
        dst_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Записываем зашифрованный файл
        with open(dst_path_obj, "wb") as f:
            f.write(encrypted_data)
    
    def __decryprt_file(self, src_path: str, dst_path: str):
        """Дешифрует один файл и сохраняет дешифрованную копию по указанному пути."""
        try:
            with open(self.keyfile_path, "rb") as kf:
                key = kf.read().strip()

            fernet = Fernet(key)

            with open(src_path, "rb") as f:
                encrypted_data = f.read()

            decrypted_data = fernet.decrypt(encrypted_data)

            Path(dst_path).parent.mkdir(parents=True, exist_ok=True)

            with open(dst_path, "wb") as f:
                f.write(decrypted_data)

        except FileNotFoundError:
            self.show_notification.emit("error", f"Ошибка: Не найден файл ключа или исходный файл для дешифрования.")
            return
        except InvalidToken:
            self.show_notification.emit("error", f"Ошибка дешифрования: ключ недействителен или данные повреждены.")
            return
        except Exception as e:
            self.show_notification.emit("error", f"Произошла непредвиденная ошибка при дешифровании файла.\nОшибка: {e}")
            return
        
    def _get_fernet(self):
        """Читает ключ из файла и возвращает объект Fernet."""
        with open(self.keyfile_path, "rb") as kf:
            key = kf.read().strip()
        return Fernet(key)
    
    def _encrypt_string(self, plaintext: str) -> str:
        """Шифрует строку и возвращает ее в виде base64-текста."""
        if not plaintext:
            return ""
        fernet = self._get_fernet()
        encrypted_bytes = fernet.encrypt(plaintext.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')

    def _decrypt_string(self, encrypted_text: str) -> str:
        """Дешифрует строку, с обратной совместимостью для открытого текста."""
        if not encrypted_text:
            return ""
        try:
            fernet = self._get_fernet()
            decrypted_bytes = fernet.decrypt(encrypted_text.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except InvalidToken:
            return encrypted_text
        except Exception:
            return ""
        
    def check_program_version(self):
        """Функция проверяет версию программы"""
        program_server_path = Path(self.config_data.get("server_program_path"))

        if not program_server_path.exists():
            return None
        
        program_server_files = [p.name for p in program_server_path.iterdir()]
        for file_name in program_server_files:
            # Ищем файл, который начинается с "config" и заканчивается ".yaml"
            if file_name.startswith("config") and file_name.endswith(".yaml"):
                try:
                    with open(program_server_path / file_name, "r", encoding="utf-8") as f:
                        config_data = yaml.safe_load(f)
                    
                    local_version = str(self.config_data.get("program_version_number"))
                    program_server_version = str(config_data.get("program_version_number"))

                    if not program_server_version:
                        return None

                    if version.parse(program_server_version) > version.parse(local_version):
                        return True
                    else:
                        return False
                    
                except IndexError:
                    # Если формат имени файла не соответствует ожидаемому, пропускаем его
                    continue
        
    def update_program(self):
        """Функция вызывает обновление программы"""
        updater_path = Path.cwd() / "updater.exe"
        
        # Проверяем, что updater.exe существует
        if not updater_path.exists():
            self.show_notification.emit("error", f"Не найдена программа автоматического обновления: {updater_path}")
            return

        # Запускаем updater.exe с запросом прав администратора
        try:
            os.startfile(updater_path)
        except OSError as e:
            self.show_notification.emit("error", f"Не удалось запустить программу обновления: {e}")

    def get_groups_names(self):
        """Функция возвращает список имен групп"""
        try:
            path_to_groups = Path(self.config_data.get("versions_path"))
            if not path_to_groups.exists():
                self.show_notification.emit("error", f"Путь к группам не существует или недоступен.\nПуть: {path_to_groups}")
                return []

            groups_names = [p.name for p in path_to_groups.iterdir()]
            return sorted(groups_names)

        except FileNotFoundError:
            self.show_notification.emit("error", f"Путь к группам не найден: {path_to_groups}")
            return []
        except PermissionError:
            self.show_notification.emit("error", f"Отсутствуют права доступа к папке с группами: {path_to_groups}")
            return []
        except Exception as e:
            self.show_notification.emit("error", f"Произошла непредвиденная ошибка при получении списка групп.\nОшибка: {e}")
            return []

    def get_group_versions(self, group_name):
        """Функция возвращает список версий группы"""
        try:
            versions_path = Path(self.config_data.get("versions_path"))
            path_to_group = versions_path / group_name
            if not path_to_group.exists():
                self.show_notification.emit("error", f"Путь к выбранной группе не существует или недоступен.\nПуть: {path_to_group}")
                return []

            versions = [p.name for p in path_to_group.iterdir()]
            
            dates = []
            for ver in versions:
                if not ver or ver.startswith("~"):
                    continue

                match = re.search(r"\d{2}\.\d{2}\.\d{4}", ver)
                dates.append([ver, match.group() if match else None])

            dates.sort(key=lambda x: self.__parse_date(x[1]), reverse=True)

            sorted_versions = [date[0] for date in dates]
            return sorted_versions

        except FileNotFoundError:
            self.show_notification.emit("error", f"Путь к группе не найден: {path_to_group}")
            return []
        except PermissionError:
            self.show_notification.emit("error", f"Отсутствуют права доступа к папке группы: {path_to_group}")
            return []
        except Exception as e:
            self.show_notification.emit("error", f"Произошла непредвиденная ошибка при получении версий группы.\nОшибка: {e}")
            return []
        
    def get_actual_version(self, versions):
        """Возвращает актуальную версию (папку или файл)."""
        base_path = Path(self.config_data.get("versions_path"))

        def extract_date(name):
            match = re.search(r"\d{2}\.\d{2}\.\d{4}", name)
            return self.__parse_date(match.group()) if match else None

        try:
            # --- фильтрация и разбор версий ---
            items = [(v, extract_date(v)) for v in versions if v]
            if not items:
                return None

            # --- определяем, что есть на ФС ---
            folders = [x for x in items if (base_path / x[0]).is_dir()]
            files   = [x for x in items if (base_path / x[0]).is_file()]

            # fallback: если нет данных о ФС
            target = folders or files or items
            is_folder = bool(folders or (not files and target is items))

            # --- сортировка ---
            has_dates = any(date for _, date in target)

            def sort_key(x):
                name, date = x
                # Дата по убыванию, имя — в зависимости от типа
                return (
                    date or datetime.datetime.min,
                    name.lower() if not is_folder else -ord(name[0].lower())
                )

            if has_dates:
                # Если есть даты — сортируем по дате ↓, потом по имени (в зависимости от типа)
                target.sort(key=lambda x: (x[1] or datetime.datetime.min, 
                                        x[0].lower() if not is_folder else x[0].lower()),
                            reverse=True)
            else:
                # Без дат — только по имени (по правилам)
                target.sort(key=lambda x: x[0].lower(), reverse=is_folder)

            return target[0][0]

        except Exception as e:
            self.show_notification.emit("error", f"Ошибка при получении актуальной версии: {e}")
            return None
        
    def get_desktop_path(self):
        """Функция возвращает путь к папке Desktop"""
        try:
            # Проверяем сначала путь к рабочему столу в OneDrive с русским названием
            onedrive_desktop_path = Path.home() / "OneDrive" / "Рабочий стол"
            if onedrive_desktop_path.exists():
                return onedrive_desktop_path

            # Проверяем снова путь к рабочему столу в OneDrive
            onedrive_desktop_path = Path.home() / "OneDrive" / "Desktop"
            if onedrive_desktop_path.exists():
                return onedrive_desktop_path

            # Если не найден, используем стандартный путь
            desktop_path = Path.home() / "Desktop"
            return desktop_path

        except Exception as e:
            self.show_notification.emit("error", f"Произошла ошибка при получении пути к папке Desktop.\nОшибка: {e}")
            return
        
    def search(self, text):
        """Функция выполняет поиск в таблице ПОСЛДЕНИЕ ВЕРСИИ ГРУПП"""
        try:
            if not text:
                return []

            groups = self.get_groups_names()
            if not groups:
                return []

            groups_versions = []
            for group in groups:
                versions = self.get_group_versions(group)
                actual_version = self.get_actual_version(versions)
                groups_versions.append([group, actual_version])

            result = []
            search_text = text.lower().strip()
            for group_version in groups_versions:
                group_name = group_version[0].lower().strip()

                if group_version[1] is None:
                    if search_text in group_name and group_version not in result:
                        result.append(group_version)
                    continue

                version = group_version[1].lower().strip()

                if (search_text in group_name or search_text in version) and group_version not in result:
                    result.append(group_version)

            return result

        except Exception as e:
            self.show_notification.emit("error", f"Произошла непредвиденная ошибка при поиске.\nОшибка: {e}")
            return []

    def search_all(self, text):
        """Функция выполняет поиск в таблице ПО ВСЕМ ВЕРСИЯМ И ГРУППАМ"""
        try:
            if not text:
                return []

            groups = self.get_groups_names()
            if not groups:
                return []

            groups_versions = {}
            for group in groups:
                groups_versions[group] = self.get_group_versions(group)

            result = []
            search_text = text.lower().strip()
            for group, versions in groups_versions.items():
                group_text = group.lower().strip()

                if not versions:
                    if search_text in group_text and [group, None] not in result:
                        result.append([group, None])
                else:
                    for version in versions:
                        version_text = version.lower().strip() if version else ""
                        
                        if (search_text in group_text or search_text in version_text) and [group, version] not in result:
                            result.append([group, version])

            return result

        except Exception as e:
            self.show_notification.emit("error", f"Произошла непредвиденная ошибка при поиске по всем версиям.\nОшибка: {e}")
            return []
        
    def create_new_group(self, group_name):
        """Функция создает новую группу"""
        try:
            if not group_name:
                return 1

            progress_step_size = 100 // self.CREATE_NEW_GROUP_PROGRESS_BAR_STEP
            current_step = 0

            self.progress_chehged.emit("Формируем путь к группе...", current_step)
            group_path = Path(self.config_data.get("versions_path")) / group_name

            current_step += progress_step_size
            self.progress_chehged.emit("Проверяем существование группы...", current_step)
            if group_path.exists():
                self.show_notification.emit("error", f"Группа с именем {group_name} уже существует.")
                return 1

            current_step += progress_step_size
            self.progress_chehged.emit("Создаём группу...", current_step)
            group_path.mkdir(parents=True, exist_ok=True)
            
            self.progress_chehged.emit("Группа создана.", 100)
            self.show_notification.emit("info", f"Группа {group_name} успешно создана.")
            return 0

        except Exception as e:
            self.show_notification.emit("error", f"Произошла ошибка при создании новой группы.\nОшибка: {e}")
            return 1

    def delete_group(self, group_name):
        """Функция удаляет группу"""
        try:
            if not group_name:
                return 1
            
            progress_step_size = 100 // self.DELETE_PROGRESS_BAR_STEP
            current_step = 0 

            self.progress_chehged.emit("Формируем путь к группе...", current_step)
            group_path = Path(self.config_data.get("versions_path")) / group_name
            
            if not group_path.exists():
                self.show_notification.emit("error", f"Группа с именем {group_name} не существует.")
                return 1
            
            current_step += progress_step_size
            self.progress_chehged.emit("Удаляем группу...", current_step)
            shutil.rmtree(group_path)

            self.progress_chehged.emit("Группа удалена.", 100)
            self.show_notification.emit("info", f"Группа {group_name} успешно удалена.")
            return 0
            
        except Exception as e:
            self.show_notification.emit("error", f"Произошла ошибка при удалении группы.\nОшибка: {e}")
            return 1
        
    def delete_file(self, data):
        """Функция удаляет файл"""
        try:
            if not data:
                return 1
            
            progress_step_size = 100 // self.DELETE_PROGRESS_BAR_STEP
            current_step = 0 

            self.progress_chehged.emit("Формируем путь к файлу...", current_step)
            file_path = Path(self.config_data.get("versions_path")) / data[0] / data[1]

            if not file_path.exists():
                self.show_notification.emit("error", f"Файл не существует. Путь: {file_path}")
                return 1
            
            current_step += progress_step_size
            self.progress_chehged.emit("Удаляем файл...", current_step)
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir():
                shutil.rmtree(file_path)

            self.progress_chehged.emit("Файл удалён.", 100)
            self.show_notification.emit("info", f"Файл {file_path} успешно удалён.")
            return 0
            
        except Exception as e:
            self.show_notification.emit("error", f"Произошла ошибка при удалении файла.\nОшибка: {e}")
            return 1
        
    def add_version(self, version_path, group_name):
        """Функция добавляет версию"""
        try:
            if not version_path or not group_name:
                return 1
            
            progress_step_size = 100 // self.ADD_PROGRESS_BAR_STEP
            current_step = 0 
            
            self.progress_chehged.emit("Формируем путь к папке новой версии...", current_step)
            src_path = Path(version_path)
            dst_root = Path(self.config_data.get("versions_path")) / group_name / src_path.name
            
            if dst_root.exists():
                self.show_notification.emit("error", f"Папка {dst_root} уже существует.")
                return 1
            
            dst_root.mkdir(parents=True, exist_ok=True)

            current_step += progress_step_size
            self.progress_chehged.emit("Копируем и шифруем файлы...", current_step)
            
            for root, dirs, files in os.walk(version_path):
                root_path = Path(root)
                rel = root_path.relative_to(version_path)
                dst_dir = dst_root / rel
                dst_dir.mkdir(parents=True, exist_ok=True)

                for filename in files:
                    src_file = root_path / filename
                    dst_file = dst_dir / filename
                    self.__encrypt_file(str(src_file), str(dst_file))

            self.progress_chehged.emit("Версия добавлена.", 100)
            self.show_notification.emit("info", "Папка успешно скопирована и зашифрована.")
            return 0
        
        except Exception as e:
            self.show_notification.emit("error", f"Произошла ошибка при добавлении версии.\nОшибка: {e}")
            return 1
    
    def add_instruction(self, instruction_path, group_name):
        """Функция добавляет инструкцию"""
        try:
            if not instruction_path or not group_name:
                return 1
            
            progress_step_size = 100 // self.ADD_PROGRESS_BAR_STEP
            current_step = 0 
            
            self.progress_chehged.emit("Формируем путь к файлу...", current_step)
            instruction_path_obj = Path(instruction_path)
            dst_path = Path(self.config_data.get("versions_path")) / group_name / instruction_path_obj.name
            
            if dst_path.exists():
                self.show_notification.emit("error", f"Файл {dst_path} уже существует.")
                return 1

            current_step += progress_step_size
            self.progress_chehged.emit("Копируем и шифруем файл...", current_step)
            self.__encrypt_file(src_path=instruction_path, dst_path=str(dst_path))

            self.progress_chehged.emit("Инструкция добавлена.", 100)
            self.show_notification.emit("info", "Инструкция успешно скопирована и зашифрована.")
            return 0
        
        except Exception as e:
            self.show_notification.emit("error", f"Произошла ошибка при добавлении инструкции.\nОшибка: {e}")
            return 1
        
    def download(self, group, file, save_path):
        """Функция скачивает файл (версия/инструкция)"""
        try:
            file_path = Path(self.config_data.get("versions_path")) / group / file
        
            if not save_path:
                save_path = self.get_desktop_path()
                if not save_path or not save_path.exists():
                    return 1
            elif not Path(save_path).exists():
                self.show_notification.emit("error", f"Директория {save_path} не существует.")
                return 1
            
            if file_path.is_dir():
                progress_step_size = 100 // self.DOWNLOAD_PROGRESS_BAR_STEP
                current_step = 0 

                self.progress_chehged.emit("Создаём путь исходной папки...", current_step)
                src_path = file_path
                if not src_path.exists():
                    self.show_notification.emit("error", f"Директория {src_path} не существует.")
                    return 1

                current_step += progress_step_size
                self.progress_chehged.emit("Создаём путь сохранения...", current_step)
                dst_path = Path(save_path) / f"{group} {file}"
                if dst_path.exists():
                    self.show_notification.emit("error", f"Директория {dst_path} уже существует.")
                    return 1
                
                dst_path.mkdir(parents=True, exist_ok=True)
                
                current_step += progress_step_size
                self.progress_chehged.emit("Скачиаваем файлы...", current_step)
                for root, dirs, files in os.walk(src_path):
                    root_path = Path(root)
                    rel = root_path.relative_to(src_path)
                    dst_dir = dst_path / rel
                    dst_dir.mkdir(parents=True, exist_ok=True)

                    for filename in files:
                        if not filename.endswith(".enc"):
                            continue

                        src_file = root_path / filename
                        dst_file = dst_dir / filename[:-4]
                        self.__decryprt_file(str(src_file), str(dst_file))

            else:
                progress_step_size = 100 // self.DOWNLOAD_PROGRESS_BAR_STEP
                current_step = 0 

                self.progress_chehged.emit(f"Скачивание файла {file}...", current_step)
                src_path = Path(self.config_data.get("versions_path")) / group / f"{file}.enc"

                current_step += progress_step_size
                self.progress_chehged.emit(f"Скачивание файла {file}...", current_step)
                dst_path = Path(save_path) / f"{file}"

                current_step += progress_step_size
                self.progress_chehged.emit(f"Скачивание файла {file}...", current_step)
                self.__decryprt_file(str(src_path), str(dst_path))
        
            self.progress_chehged.emit("Скачивание завершено.", 100)
            self.show_notification.emit("info", "Файл успешно скачан.")
            return 0

        except Exception as e:
            self.show_notification.emit("error", f"Произошла ошибка при скачивании файла.\nОшибка: {e}")
            return 1

    def get_decrypted_password(self) -> str | None:
        """Получает и дешифрует пароль из файла password.key."""
        if not self.password_file_path.exists():
            return None
        
        try:
            with open(self.password_file_path, 'r', encoding='utf-8') as f:
                encrypted_password = f.read().strip()

            if not encrypted_password:
                return None
            
            return self._decrypt_string(encrypted_password)
        except Exception:
            return None

    def set_password(self, new_password):
        """Функция устанавливает новый пароль в password.key."""
        try:
            print(f"--- ДИАГНОСТИКА: Вызван метод set_password ---")
            print(f"--- ДИАГНОСТИКА: Попытка записи в файл: {self.password_file_path.resolve()} ---")
            encrypted_password = self._encrypt_string(new_password)
            print(f"--- ДИАГНОСТИКА: Новый зашифрованный пароль: {encrypted_password[:15]}... ---")
            
            with open(self.password_file_path, 'w', encoding='utf-8') as f:
                f.write(encrypted_password)
            
            print(f"--- ДИАГНОСТИКА: Файл password.key успешно записан. ---")
            return 0
        except Exception as e:
            print(f"--- ДИАГНОСТИКА: ОШИБКА при смене пароля: {e} ---")
            self.show_notification.emit("error", f"Произошла ошибка при смене пароля.\nОшибка: {e}")
            return 1