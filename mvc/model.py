import os
import re
import sys
import yaml
import shutil
import datetime

from pathlib import Path
from cryptography.fernet import Fernet


class Model:
    def __init__(self):
        self.config_data = self.__load_config() # Получаем данные из файла конфигурации
        self.in_group = False # Флаг нахождения таблицы в отображении всех версий группы
        self.search_all_versions = False # Флаг поиска всех версий
        self.new_group_name = None # Имя новой группы
        self.keyfile_path = os.path.join(os.path.dirname(sys.argv[0]), "keyfile.key")

    def __load_config(self):
        """Функция загружает данные из файла конфигурации"""
        try:
            # Получаем путь к исполняемому файлу и проверяем существование
            exe_file_path = os.path.abspath(sys.argv[0])
            if not os.path.exists(exe_file_path):
                print(f"Произошла ошибка при получении пути к исполняемому файлу.\nПуть: {exe_file_path}")
                return 1
            
            # Получаем путь к файлу конфигурации и проверяем существование
            config_path = os.path.join(os.path.dirname(exe_file_path), "config.yaml")
            if not os.path.exists(config_path):
                print(f"Произошла ошибка при получении пути к файлу конфигурации.\nПуть: {config_path}")
                return 1
            
            try:
                # Загружаем данные из файла конфигурации
                with open(config_path, "r", encoding="utf-8") as file:
                    config_data = yaml.safe_load(file)

                return config_data
            except Exception as e:
                print(f"Произошла ошибка при загрузке данных из файла конфигурации.\nОшибка: {e}")
                return 1
            
        except Exception as e:
            print(f"Произошла непредвиденная ошибка.\nОшибка: {e}")

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
        dst_path = dst_path + ".enc"

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
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)

        # Записываем зашифрованный файл
        with open(dst_path, "wb") as f:
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

            os.makedirs(os.path.dirname(dst_path), exist_ok=True)

            with open(dst_path, "wb") as f:
                f.write(decrypted_data)

        except Exception as e:
            print(f"Произошла ошибка при дешифровании файла.\nОшибка: {e}")
            return

    def get_groups_names(self):
        """Функция возвращает список имен групп"""
        try:
            groups_names = []

            try:
                path_to_groups = self.config_data.get("versions_path")
            except Exception as e:
                print(f"Произошла ошибка при получении пути к группам из файла конфигурации.\nОшибка: {e}")
                return []
            
            if not os.path.exists(path_to_groups):
                print(f"Произошла ошибка при получении пути к группам.\nПуть: {path_to_groups}")
                return []
            try:
                groups_names = os.listdir(path_to_groups)

                return sorted(groups_names)
            
            except Exception as e:
                print(f"Произошла ошибка при получении списка имен групп.\nОшибка: {e}")
                return []
            
        except Exception as e:
            print(f"Произошла непредвиденная ошибка.\nОшибка: {e}")

    def get_group_versions(self, group_name):
        """Функция возвращает список версий группы"""
        try:
            try:
                path_to_group = os.path.join(self.config_data.get("versions_path"), group_name)
            except Exception as e:
                print(f"Произошла ошибка при получении пути к группе.\nОшибка: {e}")
                return []
            
            if not os.path.exists(path_to_group):
                print(f"Путь к выбранной группе не существует ли недоступен.\nПуть: {path_to_group}")
                return []

            try:
                versions = os.listdir(path_to_group)
                
                dates = []
                for ver in versions:
                    if not ver:
                        continue
                        
                    # Не добавляем временные файлы
                    if ver.startswith("~"):
                        continue

                    match = re.search(r"\d{2}\.\d{2}\.\d{4}", ver)
                    dates.append([ver, match.group() if match else None])

                dates.sort(key=lambda x: self.__parse_date(x[1]), reverse=True)

                sorted_versions = [date[0] for date in dates]

                return sorted_versions
            
            except Exception as e:
                print(f"Произошла ошибка при получении списка версий группы.\nОшибка: {e}")
                return []
        except Exception as e:
            print(f"Произошла непредвиденная ошибка.\nОшибка: {e}")
            return []
        
    def get_actual_version(self, versions):
        """Возвращает актуальную версию (папку или файл)."""
        base_path = self.config_data.get("versions_path")

        def extract_date(name):
            match = re.search(r"\d{2}\.\d{2}\.\d{4}", name)
            return self.__parse_date(match.group()) if match else None

        try:
            # --- фильтрация и разбор версий ---
            items = [(v, extract_date(v)) for v in versions if v]
            if not items:
                return None

            # --- определяем, что есть на ФС ---
            folders = [x for x in items if os.path.isdir(os.path.join(base_path, x[0]))]
            files   = [x for x in items if os.path.isfile(os.path.join(base_path, x[0]))]

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
            print(f"Ошибка при получении актуальной версии: {e}")
            return None
        
    def get_desktop_path(self):
        """Функция возвращает путь к папке Desktop"""
        try:
            # Проверяем сначала путь к рабочему столу в OneDrive с русским названием
            onedrive_desktop_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Рабочий стол")
            if os.path.exists(onedrive_desktop_path):
                return onedrive_desktop_path

            # Проверяем снова путь к рабочему столу в OneDrive
            onedrive_desktop_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
            if os.path.exists(onedrive_desktop_path):
                return onedrive_desktop_path

            # Если не найден, используем стандартный путь
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            return desktop_path

        except Exception as e:
            print(f"Произошла ошибка при получении пути к папке Desktop.\nОшибка: {e}")
            return
        
    def search(self, text):
        """Функция выполняет поиск в таблице ПОСЛДЕНИЕ ВЕРСИИ ГРУПП"""
        try:
            if not text:
                return []
            
            # Получаем список групп
            try:
                groups = self.get_groups_names()
                if not groups:
                    return []
            except Exception as e:
                print(f"Произошла ошибка при получении списка групп.\nОшибка: {e}")
                return []
            
            # Получаем список списков, в виде [[группа, актуальная версия]]
            groups_versions = []
            try:
                for group in groups:
                    try:
                        versions = self.get_group_versions(group)

                    except Exception as e:
                        print(f"Произошла ошибка при получении списка версий группы.\nОшибка: {e}")
                        continue

                    try:
                        actual_version = self.get_actual_version(versions)
                        
                    except Exception as e:
                        print(f"Произошла ошибка при получении актуальной версии группы.\nОшибка: {e}")
                        continue

                    groups_versions.append([group, actual_version])

            except Exception as e:
                print(f"Произошла ошибка в процессе формирования списков групп и версий.\nОшибка: {e}")
                return []
            
            # Выполняем поиск
            try:
                result = []
                for group_version in groups_versions:
                    text = text.lower().strip()
                    group_name = group_version[0].lower().strip()

                    if group_version[1] is None:
                        if text in group_name and group_version not in result:
                            result.append(group_version)
                        continue
                        
                    version = group_version[1].lower().strip()
                    
                    if text in group_name or text in version and group_version not in result:
                        result.append(group_version)

                return result
            
            except Exception as e:
                print(f"Произошла ошибка в процессе поиска.\nОшибка: {e}")
                return []
            
        except Exception as e:
            print(f"Произошла непредвиденная ошибка.\nОшибка: {e}")
            return []
        
    def search_all(self, text):
        """Функция выполняет поиск в таблице ПО ВСЕМ ВЕРСИЯМ И ГРУППАМ"""
        try:
            if not text:
                return []
            
            # Получаем спсиок групп
            try:
                groups = self.get_groups_names()

            except Exception as e:
                print(f"Произошла ошибка при получении списка групп.\nОшибка: {e}")
                return []

            if not groups:
                return []
            
            # Получаем словарь, где ключ - группа, значение - список версий
            try:
                groups_versions = {}
                for group in groups:
                    groups_versions[group] = self.get_group_versions(group)

            except Exception as e:
                print(f"Произошла ошибка при получении списка версий групп.\nОшибка: {e}")
                return []
            
            # Выполняем поиск

            try:
                result = []
                for group, versions in groups_versions.items():
                    text = text.lower().strip()
                    group_text = group.lower().strip()

                    if not versions:
                        if text in group_text and [group, None] not in result:
                            result.append([group, None])
                    else:
                        for version in versions:
                            version_text = version.lower().strip() if version else ""
                            
                            if (text in group_text or text in version_text) and [group, version] not in result:
                                result.append([group, version])

                return result

            except Exception as e:
                print(f"Произошла ошибка в процессе поиска.\nОшибка: {e}")
                return []
                                
        except Exception as e:
            print(f"Произошла непредвиденная ошибка.\nОшибка: {e}")
            return []
        
    def create_new_group(self, group_name):
        """Функция создает новую группу"""
        try:
            if not group_name:
                return
            
            # Создаём путь к новой группе
            try:
                group_path = os.path.join(self.config_data.get("versions_path"), group_name)

            except Exception as e:
                print(f"Произошла ошибка при формировании пути к новой группе.\nОшибка: {e}")
                return
            
            # Проверяем существут ли такая группа
            if os.path.exists(group_path):
                print(f"Группа с именем {group_name} уже существует.")
                return
            
            # Создаём группу
            try:
                os.makedirs(group_path)
                print(f"Группа {group_name} успешно создана.")
            
            except Exception as e:
                print(f"Произошла ошибка при создании новой группы.\nОшибка: {e}")
                return
        
        except Exception as e:
            print(f"Произошла непредвиденная ошибка.\nОшибка: {e}")
            return
        
    def delete_group(self, group_name):
        """Функция удаляет группу"""
        try:
            if not group_name:
                return 1

            # Формируем путь к группе
            try:
                group_path = os.path.join(self.config_data.get("versions_path"), group_name)

            except Exception as e:
                print(f"Произошла ошибка при формировании пути к удаляемой группе.\nОшибка: {e}")
                return 1
            
            if not os.path.exists(group_path):
                print(f"Группа с именем {group_name} не существует.")
                return 1
            
            # Удаляем группу
            try:
                shutil.rmtree(group_path)
                print(f"Группа {group_name} успешно удалена.")
                return 0
            
            except Exception as e:
                print(f"Произошла ошибка при удалении группы.\nОшибка: {e}")
                return 1
        except Exception as e:
            print(f"Произошла непредвиденная ошибка.\nОшибка: {e}")
            return 1
        
    def delete_file(self, data):
        """Функция удаляет файл"""
        try:
            if not data:
                return 1

            # Формируем путь
            try:
                file_path = os.path.join(self.config_data.get("versions_path"), data[0], data[1])

            except Exception as e:
                print(f"Произошла ошибка при формировании пути к удаляемому файлу.\nОшибка: {e}")
                return 1

            if not os.path.exists(file_path):
                print(f"Файл не существует. Путь: {file_path}")
                return 1
            
            # Удаляем файл
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)

                print(f"Файл {file_path} успешно удалён.")
                return 0
            
            except Exception as e:
                print(f"Произошла ошибка при удалении файла.\nОшибка: {e}")
                return 1
            
        except Exception as e:
            print(f"Произошла непредвиденная ошибка.\nОшибка: {e}")
            return 1
        
    def add_version(self, version_path, group_name):
        """Функция добавляет версию"""
        try:
            if not version_path or not group_name:
                return 1
            
            # Формируем путь к новой папке
            src_path = Path(version_path)
            
            try:
                dst_root = Path(os.path.join(self.config_data.get("versions_path"),group_name, src_path.name))

            except Exception as e:
                print(f"Произошла ошибка при формировании пути к новой папке.\nОшибка: {e}")
                return 1
            
            if dst_root.exists():
                print(f"Папка {dst_root} уже существует.")
                return 1
            
            try:
                dst_root.mkdir(parents=True, exist_ok=True)

            except Exception as e:
                print(f"Произошла ошибка при создании новой папки.\nОшибка: {e}")
                return 1

            # Копируем файлы и шифруем
            try:
                # Рекурсивно обходим исходную директорию
                for root, dirs, files in os.walk(version_path):
                    rel = Path(root).relative_to(version_path)  # относительный путь от корня исходной папки
                    dst_dir = dst_root / rel
                    dst_dir.mkdir(parents=True, exist_ok=True)

                    # Перебираем файлы
                    for filename in files:
                        src_file = Path(root) / filename
                        dst_file = dst_dir / filename
                        self.__encrypt_file(str(src_file), str(dst_file)) # Используем функцию шифрования файла

            except Exception as e:
                print(f"Произошла ошибка при копировании и шифровании файлов.\nОшибка: {e}")
                return 1

            print("Папка успешно скопирована и зашифрована.")

            return 0
        
        except Exception as e:
            print(f"Произошла непредвиденная ошибка.\nОшибка: {e}")
            return 1
    
    def add_instruction(self, instruction_path, group_name):
        """Функция добавляет инструкцию"""
        try:
            if not instruction_path and group_name:
                return 1
            
            # Формируем путь
            try:
                dst_path = os.path.join(self.config_data.get("versions_path"), group_name, os.path.basename(instruction_path))

            except Exception as e:
                print(f"Произошла ошибка при формировании пути пути файла.\nОшибка: {e}")
                return 1
            
            if os.path.exists(dst_path):
                print(f"Файл {dst_path} уже существует.")
                return 1

            # Копируем и шифруем
            try:
                self.__encrypt_file(src_path=instruction_path, dst_path=dst_path)

            except Exception as e:
                print(f"Произошла ошибка при копировании и шифровании файла.\nОшибка: {e}")
                return 1

            print("Инструкция успешно скопирована и зашифрована.")

            return 0
        
        except Exception as e:
            print(f"Произошла непредвиденная ошибка.\nОшибка: {e}")
            return 1
        
    def download(self, group, file, save_path):
        """Функция скачивает файл (версия/инструкция)"""
        try:
            file_path = os.path.join(self.config_data.get("versions_path"), group, file)
        
        except Exception as e:
            print(f"Произошла ошибка при формировании пути к файлу.\nОшибка: {e}")
            return
        
        try:
            # Проверяем передан ли путь сохранения
            if not save_path: # Если не передан, сохраняем на рабочий стол
                save_path = self.get_desktop_path()

                # Проверяем получен ли путь рабочего стола
                if not os.path.exists(save_path):
                    return
            elif not os.path.exists(save_path):
                print(f"Директория {save_path} не существует.")
                return
        
        except Exception as e:
            print(f"Произошла ошибка при получении пути сохранения файла.\nОшибка: {e}")
            return
        
        try:
            if os.path.isdir(file_path):
                # Создаём путь исходной папки
                src_path = Path(os.path.join(self.config_data.get("versions_path"), group, file))
                if not src_path.exists():
                    print(f"Директория {src_path} не существует.")
                    return
                
                # Создаём путь сохранения
                dst_path = Path(os.path.join(save_path, f"{group} {file}"))
                if dst_path.exists():
                    print(f"Директория {dst_path} уже существует.")
                    return
                
                dst_path.mkdir(parents=True, exist_ok=True)
                
                # Рекурсивно обходим зашифрованную директорию
                for root, dirs, files in os.walk(src_path):
                    rel = Path(root).relative_to(src_path)
                    dst_dir = dst_path / rel
                    dst_dir.mkdir(parents=True, exist_ok=True)

                    # Перебираем файлы
                    for filename in files:
                        # Обрабатываем только зашифрованные папки
                        if not filename.endswith(".enc"):
                            continue

                        src_path = Path(root) / filename
                        dst_path = dst_dir / filename[:-4] # Убираем расширение .enc
                        self.__decryprt_file(src_path=src_path, dst_path=dst_path)

            else:
                src_path = os.path.join(self.config_data.get("versions_path"), group, f"{file}.enc")
                dst_path = os.path.join(save_path, f"{file}")
                self.__decryprt_file(src_path=src_path, dst_path=dst_path)
        
        except Exception as e:
            print(f"Произошла ошибка при скачивании файла.\nОшибка: {e}")
            return

        print("Файл успешно скачан.")
        return


    """ ================ """
    # НЕ выбираеться версия в разделе удалить
    """ ================ """