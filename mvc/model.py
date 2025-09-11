import os
import sys
import yaml
import shutil
import hashlib
import threading
import subprocess

from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal

class Model(QObject):
    show_notification = pyqtSignal(str, str)  # Сигнал для показа уведомления
    progress_changed = pyqtSignal(int)  # Сигнал для изменения значения прогресс бара

    def __init__(self):
        super().__init__()

        self.config_file_path = self.__get_config_file_path() # Получаем путь к файлу конфигурации
        self.versions_path = self.__get_versions_path() # Получаем путь к папке групп версий
        self.program_version_number = self.__get_program_version_number() # Получаем версию программы
        self.program_server_path = self.__get_program_server_path() # Получаем путь к программе на сервере

        self.versions_groups = None
        self.update_versions_groups() # Получаем список групп версий
        
        self.in_group = False # Флаг, определяющий что отображает таблица, группы или версии для группы
        self.current_group = None # Текущая выбранная группа
        self.current_group_versions = None # Список версий для выбранной группы

        self.search_text = "" # Текст в строке поиска

        self.choosen_path_to_download = "" # Путь для загрузки

        self.choosen_group = None # Выбранная группа
        self.choosen_version = None # Выбранная версия

        self.new_group_name = "" # Имя новой группы
        self.new_file_path = "" # Путь к папке новой версии

    def __get_config_file_path(self):
        """Функция возвращает путь к файлу конфигурации"""
        exe_file_path = os.path.abspath(sys.argv[0]) # Получаем путь к исполняемому файлу
        if not os.path.exists(exe_file_path): # Проверяем что путь существует
            return None
        
        exe_file_dir_path = os.path.dirname(exe_file_path) # Получаем папку исполняемого файла

        config_path = None # Путь к файлу конфигурации
        for file in os.listdir(exe_file_dir_path): # Перебираем все объекты в папке исполняемого файла
            if file == "config.yaml": # Если объект равен config.yaml
                config_path = os.path.join(exe_file_dir_path, file) # Создаём путь к файлу конфигурации

        return config_path
    
    def __get_config_data(self):
        """Функция возвращает данные файла конфигурации"""
        # Проверяем что путь к файлу конфигурации существует
        if not self.config_file_path or not os.path.exists(self.config_file_path):
            return None

        config_data = {} # Данные файла конфигурации
        with open(self.config_file_path, "r", encoding="utf-8") as f: # Чиатем файл конфигурации
            config_data = yaml.safe_load(f) # Сохраняем данные

        return config_data
    
    def __get_versions_path(self):
        """Функция возвращает путь к папке с версиями на сервере из файла конфигурации"""
        config_data = self.__get_config_data() # Получаем данные файла конфигурации

        if config_data: # Если данные файла конфигурации не пусты
            try:
                return config_data["versions_path"] # Возвращаем путь
            except:
                # Выводим ошибку и возвращаем None
                self.show_notification.emit("error", f"Не удалось найти путь к файлам версий в файле конфигурации: {self.config_file_path}")
                return None
            
    def __get_program_version_number(self):
        """Функция возвращает версию программы"""
        config_data = self.__get_config_data() # Получаем данные файла конфигурации

        if config_data: # Если данные файла конфигурации не пусты
            try:
                return config_data["program_version_number"] # Возвращаем версию
            except:
                # Выводим ошибку и возвращаем None
                self.show_notification.emit("error", f"Не удалось обнаружить номер версии программы в файле конфигурации: {self.config_file_path}")
                return None
            
    def __get_program_server_path(self):
        """Функция возвращает путь к программе на сервере"""
        config_data = self.__get_config_data() # Получаем данные файла конфигурации

        if config_data: # Если данные файла конфигурации не пусты
            try:
                return config_data["server_program_path"] # Возвращаем путь
            except:
                # Выводим ошибку и возвращаем None
                self.show_notification.emit("error", f"Не удалось обнаружить путь к программе на сервере в файле конфигурации: {self.config_file_path}")
                return None
            
    def __get_file_hash(self, file_path):
        """Функция возвращает хеш файла"""""
        hasher = hashlib.md5()

        try:
            with open(file_path, 'rb') as file:
                for chunk in iter(lambda: file.read(4096), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            print(f"Ошибка при получении хеша файла: {file_path}. Ошибка: {str(e)}")
            return None
        
    def __get_all_files(self, path):
        """Функция возвращает список всех файлов в указанной папке"""
        files_lst = []

        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                files_lst.append(file_path)

        return files_lst

    def __extarct_date(self, version_string):
        """Функция извлекает дату из строки"""
        date_part = version_string[-10:] # Получаем дату из строки

        try:
            return datetime.strptime(date_part, "%d.%m.%Y") # Врзвращаем дату в формате: (2024, 11, 26)
        except:
            return datetime.min
        
    def __download_file(self):
        """Функция загружает выбранный файл на рабочий стол или по выбранному пути"""
        if len(self.choosen_path_to_download) == 0: # Скачиваем на рабочий стол
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

            src = os.path.join(self.versions_path, self.choosen_group, self.choosen_version) # Формируем путь к папке выбранной версии
            if not os.path.exists(src):
                self.show_notification.emit("error", "Ошибка при загрузке!\nВыбранный файл версии недоступен на сервере")
                return
            
            dst = os.path.join(desktop_path, f"{self.choosen_group} {self.choosen_version}") # Формируем путь к итоговой папке

        else:
            if not os.path.exists(self.choosen_path_to_download):
                self.show_notification.emit("error", "Ошибка при загрузке!\nВыбранный путь не существует или недоступен")
                return
            
            dst = os.path.join(self.choosen_path_to_download, f"{self.choosen_group} {self.choosen_version}") # Формируем путь к итоговой папке
            
            src = os.path.join(self.versions_path, self.choosen_group, self.choosen_version) # Формируем путь к папке выбранной версии
            if not os.path.exists(src):
                self.show_notification.emit("error", "Ошибка при загрузке!\nВыбранный файл версии недоступен на сервере")
                return
        
        if src and dst:
            if os.path.exists(dst):
                self.show_notification.emit("error", f"Целевая папка уже существует: {dst}")
                return
            try:
                # Создаем корневую папку назначения, даже если она пустая
                os.makedirs(dst, exist_ok=True)

                # Собираем список файлов для копирования
                files = []
                for root, dirs, file_names in os.walk(src):
                    for file_name in file_names:
                        files.append(os.path.join(root, file_name))
                total = len(files)
                copied = 0
                try:
                    if total > 0: # Если есть файлы для копирования
                        for file_path in files:
                            copied += 1
                            percent = int(copied / total * 100)
                            self.progress_changed.emit(percent)  # Передаем прогресс
                            
                            rel_path = os.path.relpath(file_path, src)
                            dst_path = os.path.join(dst, rel_path)
                            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                            shutil.copy2(file_path, dst_path)
                    else: # Если папка пуста, прогресс сразу 100%
                        self.progress_changed.emit(100)
                except Exception as e: # Добавил e для отладки
                    self.show_notification.emit("error", f"Возникла непредвиденная ошибка при загрузке файла: {e}")
                    self.progress_changed.emit(0)

                self.show_notification.emit("info", f"Файл '{self.choosen_version}' успешно загружен!\nПуть: {dst}")

            except FileExistsError:
                self.show_notification.emit("error", f"Целевая папка уже существует: {dst}")
                
            except Exception as e:
                self.show_notification.emit("error", f"Ошибка при загрузке файла: {e}")

    def __add_file(self, group, signal):
        """Функция добавляет новую версию в выбранную группу (копируется вся папка с прогрессом)"""
        self.progress_changed.emit(0)  # Устанавливаем прогресс в 0% перед началом

        # Проверяем, что группа выбрана
        if not group:
            self.progress_changed.emit(100)
            self.show_notification.emit("error", "Не выбрана группа в которую будет добавляться версия")
            return

        src = self.new_file_path  # Путь к папке новой версии
        dst = os.path.join(self.versions_path, group, os.path.basename(self.new_file_path))  # Путь назначения на сервере

        # Проверяем, что исходная папка существует
        if not os.path.exists(src):
            self.progress_changed.emit(100)
            self.show_notification.emit("error", f"Путь к папке новой версии не существует или недоступен\nПуть: {src}")
            return

        if os.path.exists(dst):
            self.progress_changed.emit(100)
            self.show_notification.emit("error", f"Целевая папка уже существует!\nПуть: {dst}")
            return

        try:
            files = []
            dirs = []

            # Собираем список всех папок и файлов
            for root, subdirs, file_names in os.walk(src):
                # добавляем директории (чтобы скопировать пустые)
                for subdir in subdirs:
                    rel_dir = os.path.relpath(os.path.join(root, subdir), src)
                    dirs.append(os.path.join(dst, rel_dir))
                # добавляем файлы
                for file_name in file_names:
                    rel_file = os.path.relpath(os.path.join(root, file_name), src)
                    files.append(os.path.join(rel_file))

            # Сначала создаём корневую папку назначения
            os.makedirs(dst, exist_ok=True)

            # Создаём все директории (включая пустые)
            for d in dirs:
                os.makedirs(d, exist_ok=True)

            total = len(files)
            copied = 0

            # Копируем файлы по одному с прогрессом
            for rel_file in files:
                src_path = os.path.join(src, rel_file)
                dst_path = os.path.join(dst, rel_file)
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.copy2(src_path, dst_path)
                copied += 1
                percent = int(copied / total * 100) if total > 0 else 100
                self.progress_changed.emit(percent)

            self.progress_changed.emit(100)  # Завершаем прогресс
            self.show_notification.emit("info", "Папка успешно добавлена на сервер!")
            signal.emit()  # Сигнал об успешном завершении
        except Exception as e:
            self.progress_changed.emit(100)
            self.show_notification.emit("error", f"Ошибка при добавлении папки на сервер: {e}")

    def __delete_group(self, group, signal):
        """Функция удаляет переданную группу с прогрессом удаления файлов"""
        # Проверяем, что группа выбрана
        if not group:
            self.show_notification.emit("error", "Не выбранна группа для удаления")
            return

        group_path = os.path.join(self.versions_path, group)  # Путь к группе

        # Проверяем, что папка группы существует
        if not os.path.exists(group_path):
            self.show_notification.emit("error", f"Путь к выбранной группе не существует или недоступен. Путь: {group_path}")
            return

        try:
            # Собираем список всех файлов и папок внутри группы
            files = []
            for root, dirs, file_names in os.walk(group_path):
                for file_name in file_names:
                    files.append(os.path.join(root, file_name))
                for dir_name in dirs:
                    files.append(os.path.join(root, dir_name))

            total = len(files)  # Общее количество файлов и папок для удаления
            deleted = 0  # Счетчик удалённых файлов/папок

            # Удаляем все файлы
            for file_path in files:
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.remove(file_path)  # Удаляем файл или ссылку
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  # Удаляем папку
                except Exception as e:
                    # Если ошибка при удалении, показываем уведомление, но продолжаем
                    self.show_notification.emit("error", f"Ошибка при удалении: {file_path}\n{e}")
                deleted += 1
                percent = int(deleted / total * 100) if total > 0 else 100
                self.progress_changed.emit(percent)  # Обновляем прогресс бар

            # После удаления всех файлов и папок, удаляем саму группу
            if os.path.exists(group_path):
                shutil.rmtree(group_path)

            self.show_notification.emit("info", f"Группа '{group}' успешно удалена")
            signal.emit()  # Сигнал об успешном завершении
        except Exception as e:
            self.show_notification.emit("error", f"Произошла ошибка во время удаления группы, ошибка: {e}")

    def __delete_file(self, group, file, signal):
        """Функция удаляет переданный файл (папку версии) из переданной группы с прогрессом удаления файлов"""
        # Проверяем, что выбраны группа и файл
        if not group or not file:
            self.show_notification.emit("error", "Не выбранна группа или файл для удаления")
            return

        file_path = os.path.join(self.versions_path, group, file)  # Путь к папке версии

        # Проверяем, что папка версии существует
        if not os.path.exists(file_path):
            self.show_notification.emit("error", f"Путь к выбранному файлу не существует или недоступен. Путь: {file_path}")
            return

        try:
            # Собираем список всех файлов и папок внутри версии
            items = []
            for root, dirs, file_names in os.walk(file_path):
                for file_name in file_names:
                    items.append(os.path.join(root, file_name))  # Добавляем файл
                for dir_name in dirs:
                    items.append(os.path.join(root, dir_name))  # Добавляем подпапку

            total = len(items)  # Общее количество файлов и папок для удаления
            deleted = 0  # Счетчик удалённых файлов/папок

            # Удаляем все файлы и папки по одному, обновляя прогресс
            for item_path in items:
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.remove(item_path)  # Удаляем файл или ссылку
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)  # Удаляем папку
                except Exception as e:
                    # Если ошибка при удалении, показываем уведомление, но продолжаем
                    self.show_notification.emit("error", f"Ошибка при удалении: {item_path}\n{e}")
                deleted += 1
                percent = int(deleted / total * 100) if total > 0 else 100
                self.progress_changed.emit(percent)  # Обновляем прогресс бар

            # После удаления всех файлов и папок, удаляем саму папку версии
            if os.path.exists(file_path):
                shutil.rmtree(file_path)

            self.show_notification.emit("info", f"Файл '{file}' в группе '{group}' успешно удален")
            signal.emit()  # Сигнал об успешном завершении
        except Exception as e:
            self.show_notification.emit("error", f"Произошла ошибка во время удаления файла, ошибка: {e}")

    def __compare_files(self, files_lst_1, files_lst_2):
        """Функция сверяет актуальную и добавляемую версию"""

        # Вычисляем относительные пути и хэши
        actual_version_files = {}
        for file_path in files_lst_1:
            file_hash = self.__get_file_hash(file_path)

            if file_hash:
                actual_version_files[file_path] = file_hash
        
        new_version_files = {}
        for file_path in files_lst_2:
            file_hash = self.__get_file_hash(file_path)

            if file_hash:
                new_version_files[file_path] = file_hash

        # Инициализируем списки для результатов
        unchanged = []    # неизмененные
        changed = []      # измененные  
        new_files = []    # новые
        deleted_files = []  # удаленные

        '''Проверка на изменения'''
        # Проверяем на наличие файлов без изменений
        for path, file_hash in actual_version_files.items(): # Перебираем все значения в словаре актуальной версии
            if file_hash in new_version_files.values(): # Если хэш файла в словаре новой версии
                unchanged.append(path) # Добавляем путь к файлу без изменений

        # Проверяем на наличие файлов с изменениями
        for path, file_hash in new_version_files.items(): # Перебираем все значения в словаре новой версии
            if file_hash not in actual_version_files.values(): # Если хэш файла в словаре актуальной версии
                changed.append(path) # Добавляем путь к файлу с изменениями

        '''Проверка на наличие файлов'''
        # Формируем словари файлов актуальной и новой версий
        files_lst_1_names = {file: os.path.basename(file) for file in files_lst_1} # Словарь файлов актуальной версии, где ключ: путь к файлу, значение: имя файла
        files_lst_2_names = {file: os.path.basename(file) for file in files_lst_2} # Словарь файлов новой версии, где ключ: путь к файлу, значение: имя файла
        
        # Проверяем на наличие новых файлов
        for path, name in files_lst_2_names.items(): # Перебираем все значения в словаре новой версии
            if name not in files_lst_1_names.values(): # Если имя файла не в словаре актуальной версии
                new_files.append(path) # Добавляем путь к новому файлу

        # Проверяем на наличие пропавших файлов
        for path, name in files_lst_1_names.items(): # Перебираем все значения в словаре актуальной версии
            if name not in files_lst_2_names.values(): # Если имя файла не в словаре новой версии
                deleted_files.append(path) # Добавляем путь к пропавшему файлу

        # Возвращаем в виде: файлы без измененний, файлы с изменениями, новые файлы, пропавшие файлы
        return unchanged, changed, new_files, deleted_files
    
    def check_program_version(self):
        """Функция проверяет версию программы"""
        if not self.program_server_path or not os.path.exists(self.program_server_path):
            return None
        
        program_server_files = os.listdir(self.program_server_path)
        for file_name in program_server_files:
            # Ищем файл, который начинается с "config" и заканчивается ".yaml"
            if file_name.startswith("config") and file_name.endswith(".yaml"):
                try:
                    with open(os.path.join(self.program_server_path, file_name), "r", encoding="utf-8") as f:
                        config_data = yaml.safe_load(f)

                    program_server_version = config_data["program_version_number"] # Получаем версию программы на сервере
                    
                    if not program_server_version:
                        return None

                    if program_server_version <= self.program_version_number:
                        return True
                except IndexError:
                    # Если формат имени файла не соответствует ожидаемому, пропускаем его
                    continue
        else:
            return False
        
    def update_program(self):
        """Функция вызывает обновление программы"""
        updater_path = os.path.join(os.getcwd(), "updater.exe") # Создаём путь к программе обновления
        
        # Проверяем, что updater.exe существует
        if not os.path.exists(updater_path):
            self.show_notification.emit("error", f"Не найден файл обновления: {updater_path}")
            return

        # Запускаем updater.exe с запросом прав администратора
        # Используем 'runas' для повышения прав
        subprocess.run(['powershell', '-Command', f'Start-Process "{updater_path}" -ArgumentList "{self.program_server_path}" -Verb RunAs'], shell=True)

    def open_config_file(self):
        """Функция открывает файл конфигурации"""
        os.startfile(self.config_file_path)
    
    def verefy_versions(self, group):
        """Функция вызывает проверку актуальной и новой версий и возвращает результаты"""

        # Возвращаемые статус коды:
        # 0 - Есть изменения в версиях
        # 1 - Нет изменений в версиях
        # 2 - Нет предыдущих версий
        # 3 - Имя новой версии совпадает с имененем предыдущей
        # 4 - Любая другая ошибка возникшая во время выполнения функции
        
        try:
            group_versions = self.get_group_files(group=group) # Получаем список версий для группы
        
            if not group_versions: 
                return [2]
        
            actual_version_name = os.path.basename(self.new_file_path) # Имя актуальной группы
            if actual_version_name == group_versions[0]:
                return [3]

            group_path = os.path.join(self.versions_path, group, group_versions[0]) # Путь к группе

            if not os.path.exists(group_path):
                return [4]

            files_lst_1 = self.__get_all_files(group_path) # Получаем список файлов актуальной версии
            files_lst_2 = self.__get_all_files(self.new_file_path) # Получаем список файлов новой версии

            verefy_data = self.__compare_files(files_lst_1=files_lst_1, files_lst_2=files_lst_2) # Вызываем проверку актуальной и новой версий

            if verefy_data[0] and all(not i for i in verefy_data[1:]):
                return [1]
            else:
                return [0, verefy_data]
        except:
            return [4]

    def add_group(self):
        """Функция добавляет новую пустую группу на сервер с прогрессом"""
        self.progress_changed.emit(0)

        if len(self.new_group_name) == 0:
            self.progress_changed.emit(100)  # Сначала прогресс, потом уведомление
            self.show_notification.emit("error", "Не удалось создать группу, имя группы не задано!")
            return
        
        if not os.path.exists(self.versions_path):
            self.progress_changed.emit(100)
            self.show_notification.emit("error", "Не удалось создать группу, путь к серверу не существует, недоступен или задан неверно в файле конфигурации!")
            return
        
        path = os.path.join(self.versions_path, self.new_group_name)
        
        try:
            os.mkdir(path)
            self.progress_changed.emit(100)  # Сначала прогресс, потом уведомление
            self.show_notification.emit("info", f"Группа '{self.new_group_name}' успешно создана!")
        except Exception as e:
            self.progress_changed.emit(100)
            self.show_notification.emit("error", f"Не удалось создать новую группу! Ошибка: {e}")

    def get_group_files(self, group):
        """Функция возвращает список файлов входящих в группу"""
        # Проверяем, что группа передана
        if not group:
            return []
        
        group_path = os.path.join(self.versions_path, group) # Путь к группе

        # Проверяем, что папка группы существует
        if os.path.exists(group_path):
            files_lst = os.listdir(group_path) # Получаем список файлов группы

            # Сортируем файлы по дате, извлеченной из имени
            sorted_files_lst = sorted(files_lst, key=self.__extarct_date, reverse=True)

            return sorted_files_lst
        else:
            return []

    def update_versions_groups(self):
        """Функция возвращает список групп версий"""
        # Проверяем, что путь к папке групп версий существует
        if not self.versions_path and not os.path.exists(self.versions_path):
            return
        
        groups_versions = sorted(os.listdir(self.versions_path)) # Получаем и сортируем список групп
        self.versions_groups = groups_versions # Сохраняем новые данные

    def download_file_in_theard(self):
        """Функция вызывает загрузку файла в новом потоке"""
        theard = threading.Thread(target=self.__download_file) # Создаем поток для загрузки файла
        theard.daemon = True # Делаем поток демоном
        theard.start() # Запускаем поток
        return theard
    
    def add_file_in_theard(self, group, signal):
        """Функция вызывает добавление папки версии в новом потоке"""
        theard = threading.Thread(target=self.__add_file, args=(group, signal,)) # Создаем поток для добавления файла
        theard.daemon = True
        theard.start()
        return theard
    
    def delete_group_in_theard(self, group, signal):
        """Функция вызывает удаление группы в новом потоке"""
        theard = threading.Thread(target=self.__delete_group, args=(group, signal,)) # Создаем поток для удаления группы
        theard.daemon = True
        theard.start()
        return theard
    
    def delete_file_in_theard(self, group, file, signal):
        """Функция вызывает удаление группы в новом потоке"""
        theard = threading.Thread(target=self.__delete_file, args=(group, file, signal,)) # Создаем поток для удаления файла
        theard.daemon = True
        theard.start()
        return theard
    
    def search(self, text, search_all):
        """Функция возвращает список резульатов поиска для переданного текста"""
        words_to_search = text.lower().split()
        results = []
        seen = set()

        # Поиск внутри группы (одна колонка)
        if self.in_group:
            if not self.current_group_versions:
                return []
            
            for version in self.current_group_versions:
                if all(word in version.lower() for word in words_to_search):
                    if version not in seen:
                        results.append(version)
                        seen.add(version)
            return results

        # Глобальный поиск (две колонки)
        self.update_versions_groups()
        if not self.versions_groups:
            return []

        for group in self.versions_groups:
            versions = self.get_group_files(group=group)

            if search_all:
                # Поиск по всем версиям группы
                if versions:
                    for version in versions:
                        combined_text = f"{group.lower()} {version.lower()}"
                        if all(word in combined_text for word in words_to_search):
                            if (group, version) not in seen:
                                results.append((group, version))
                                seen.add((group, version))
                else:  # Обработка групп без версий
                    if all(word in group.lower() for word in words_to_search):
                        if (group, "") not in seen:
                            results.append((group, ""))
                            seen.add((group, ""))
            else:
                # Поиск по названию группы и последней версии
                latest_version = versions[0] if versions else ""
                combined_text = f"{group.lower()} {latest_version.lower()}"
                if all(word in combined_text for word in words_to_search):
                    if (group, latest_version) not in seen:
                        results.append((group, latest_version))
                        seen.add((group, latest_version))

        return results
