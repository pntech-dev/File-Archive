import os
import sys

from classes.notifications import Notification

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject

class Controller(QObject):
    file_added = pyqtSignal() # Сигнал добавления файла в группу
    delete_group = pyqtSignal() # Сиганл удаления группы
    delete_file = pyqtSignal() # Сиганл удаления файла

    def __init__(self, model, view):
        super().__init__()

        self.model = model
        self.view = view

        self.__check_program_version() # Проверяем версию программы
        
        self.load_group_comboboxes_data() # Вызываем обновление данных в комбобоксах групп
        self.load_file_comboboxes_data() # Вызываем обновление данных в комбобоксах файлов версий

        self.load_table_data() # Вызываем обновление данных в таблице

        # Комбобоксы
        self.view.group_file_combobox_item_changed(handler=self.on_group_file_combobox_item_chandged) # Подключаем оброботчик изменения состояния комбобоксов
        
        # Чекбоксы
        self.view.checkboxes_checked_state_changed(handler=self.on_checkboxes_checked_state_changed) # Подключаем обработчик изменения состояния включения чекбоксов
        self.view.search_all_versions_checkbox_changed(handler=self.on_search_all_versions_checkbox_changed)

        # Таблица
        self.view.table_row_clicked(handler=self.on_table_row_clicked) # Подключаем оброботчик одинарного нажатия на строку в таблице
        self.view.table_row_double_ckicked(handler=self.on_table_row_double_clicked) # Подключаем обработчик двойного нажатия на элемент в таблице

        # Кнопки
        self.view.back_button_clicked(handler=self.on_back_button_clicked) # Подключаем обработчик нажатия на кнопку "Назад"
        self.view.clear_button_clicked(handler=self.on_clear_button_clicked) # Подключаем обработчик нажатия на кнопку "Очистить"
        self.view.choose_folder_path_buttons_clicked(handler=self.on_choose_folder_path_buttons_clicked) # Подключаем обработчик нажатия на кнопку "Выбрать"
        self.view.download_button_clicked(handler=self.on_download_button_clicked) # Подключаем обработчик нажатия на кнопку "Скачать"
        self.view.add_group_button_pressed(handler=self.on_add_group_button_pressed) # Подключаем обработчк нажатия на кнопку "Добавить" группу
        self.view.add_file_button_pressed(handler=self.on_add_file_button_pressed) # Подключаем обработчк нажатия на кнопку "Добавить" файл
        self.view.delete_group_button_pressed(handler=self.on_delete_group_button_clicked) # Подключаем обработчик нажатия на кнопку "Удалить" группу
        self.view.delete_file_button_pressed(handler=self.on_delete_file_button_clicked) # Подключаем обработчик нажатия на кнопку "Удалить" файл

        # Лайнэдиты
        self.view.search_lineedit_text_changed(handler=self.on_search_lineedit_text_changed) # Подключаем обработчик изменения текста в строке поиска
        self.view.new_group_lineedit_text_changed(handler=self.on_new_group_lineedit_text_changed) # Подключаем обработчик изменения текста в строке названия новой группы
        self.view.add_version_folder_path_lineedit_text_changed(handler=self.on_add_version_folder_path_lineedit_text_changed) # Подключаем обработчик изменения текста в строке пути к версии
        self.view.choosen_path_to_download_lineedit_text_changed(handler=self.on_choosen_path_to_download_lineedit_text_changed) # Подключаем обработчик изменения текста в строке пути лайнэдита загрузки

        # Сигналы
        self.file_added.connect(self.on_file_was_added) # Подключаем обработку сигнала добавления файла
        self.delete_group.connect(self.on_delete_group) # Подключаем обработку сигнала удаления группы
        self.delete_file.connect(self.on_delete_file) # Подключаем обработку сигнала удаления файла
        self.model.show_notification.connect(self.show_notification_message) # Подключаем сигнал модели к методу показа уведомления
        self.model.progress_changed.connect(self.on_progress_changed) # Подключаем сигнал модели к методу изменения значения в прогресс баре

    def __check_program_version(self):
        """Функция проверяет версию программы"""
        is_version = self.model.check_program_version() # Проверяем версию программы

        # Если произошла ошибка во время проверки версии
        if is_version is None: 
            action = Notification().show_action_message(msg_type="error", 
                                                        title="Ошибка проверки версии", 
                                                        text="Во время проверки версии произошла ошибка!\nОшибка связана с путём к файлу конфигурации\nЖелаете открыть файл конфигурации?", 
                                                        buttons=["Да", "Нет"])

            if action:
                self.model.open_config_file()
                exit()
            else:
                exit()

        # Если версия не совпадает (требуется обновление)
        elif not is_version:
            action = Notification().show_action_message(msg_type="warning", 
                                                        title="Обновление", 
                                                        text="Обнаружена новая версия программы\nЖелаете обновить?", 
                                                        buttons=["Обновить", "Закрыть"])

            if action:
                self.model.update_program()
                sys.exit() # Закрываем основное приложение после запуска обновления
            else:
                sys.exit()

    def get_in_group_status(self):
        """Функция которая возвращает состояние нахождения таблицы в группе"""
        return self.model.in_group

    def load_group_comboboxes_data(self):
        """Функция вызывает заполнение данными комбобоксов групп"""
        self.model.update_versions_groups() # Обновляем спсиок групп версий
        self.view.update_group_comboboxes_data(data=self.model.versions_groups) # Вызыввем обновление комбобоксов

    def load_file_comboboxes_data(self):
        """Функция вызывает заполнение данными комбобоксов файлов версий"""
        # Получаем словарь данных в котором ключ - текст комбобокса группы, значение - объект комбобокса
        data = self.view.get_comboboxes_data()

        for key, value in data.items(): # Перебираем значения в словаре
            if key: # Если значение ключа не пустое
                group_files = self.model.get_group_files(group=key) # Получаем список файлов входящих в переданную группу
                files_data = {value: group_files} # Создаём словарь
                self.view.update_file_combobox_data(data=files_data) # Вызываем обновление данных в комбобоксах файлов

    def load_table_data(self, data=None):
        """Функция вызывает заполнение таблицы данными"""
        self.model.update_versions_groups() # Обновляем спсиок групп версий

        if data is None:
            data = []

            if self.model.versions_groups: # Если спиок групп версий не пуст
                for group in self.model.versions_groups: # Перебираем все группы в списке
                    group_files = self.model.get_group_files(group=group) # Получаем список версий для группы

                    if group_files:
                        data.append((group, group_files[0]))  # Добавляем пару ключ/значение в словарь
                    else:
                        data.append((group, ""))  # Добавляем пару ключ/значение в словарь

        self.view.update_table_data(data=data)

    def load_table_group_data(self, data=None):
        """Функция вызывает зополнение таблицы версиями для выбранной группы"""
        if data is None:
            files = self.model.get_group_files(group=self.model.current_group) # Получаем список версий для текущей группы
            self.model.current_group_versions = files # Записываем список версий для текущей группы
            self.view.update_table_files_data(data=self.model.current_group_versions) # Вызываем обновление данных в таблице
        else:
            self.view.update_table_files_data(data=data) # Вызываем обновление данных в таблице

    def load_table_group_data(self, data=[]):
        """Функция вызывает заполнение таблицы версиями для выбранной группы"""
        if not data:
            files = self.model.get_group_files(group=self.model.current_group) # Получаем список версий для текущей группы
            self.model.current_group_versions = files # Записываем список версий для текущей группы
            self.view.update_table_files_data(data=self.model.current_group_versions) # Вызываем обновление данных в таблице
        else:
            self.view.update_table_files_data(data=data) # Вызываем обновление данных в таблице
    
    def show_notification_message(self, msg_type, text):
        """Показывает информационное уведомление через Notification"""
        Notification().show_notification_message(msg_type=msg_type, text=text)
        self.view.set_progress_bar_value(0)

    def on_group_file_combobox_item_chandged(self):
        """Функция оброботывает изменение текщего объекта в комбобоксе"""
        self.load_file_comboboxes_data() # Вызываем обновление состояния комбобоксов
        self.view.update_add_version_button_state() # Вызываем обновление состояния кнопки добавления версии

    def on_table_row_clicked(self, row):
        """Функция обрабатывает одинарное нажатие на строку в таблице"""
        data = self.view.get_table_row_file_data(row=row) # Получаем данные из строки

        if not data: # Если список данных пуст
            return
        
        text = "Выберан файл: "
        if len(data) > 1: # Если элементов в списке больше чем 1
            text += f" {str(data[0])}, {str(data[1])}" # Формируем строку для отображения
            self.model.choosen_group = data[0] # Записываем выбранную группу
            self.model.choosen_version = data[1] # Записываем выбранную категорию
        else: # Если элемент 1
            text += f" {self.model.current_group}, {str(data[0])}"
            self.model.choosen_group = self.model.current_group # Записываем выбранную группу
            self.model.choosen_version = data[0] # Записываем выбранную категорию

        self.view.update_choosen_file_label_text(string=text)
        self.view.update_download_version_button_state()

    def on_table_row_double_clicked(self, row):
        """Функция обрабатывает двойное нажатие на строку в таблице"""
        if self.model.in_group: # Если флаг отоброжения файлов группы True
            return
        
        data = self.view.get_table_row_file_data(row=row) # Получаем данные из строки
        self.model.choosen_group = data[0] # Записываем выбранную группу
        self.model.choosen_version = data[1] # Записываем выбранную категорию

        self.model.in_group = True # Устанавливаем флаг как True

        self.view.update_back_button_state(flag=self.model.in_group)

        group = self.view.get_table_row_group_data(row=row) # Получаем выбранную группу
        self.model.current_group = group # Записываем выбранную группу

        self.load_table_group_data() # Вызываем заполнение таблицы файлами версии
        
        self.view.set_search_all_checkbox_enabled_state(state=False)
    
    def on_back_button_clicked(self):
        """Функция обрабатывает нажатие на кнопку 'Назад'"""
        self.model.in_group = False # Изменеяем флаг нахождения в группе на False
        self.model.current_group = None # Изменяем текущую выбранную группу
        self.model.current_group_versions = None # Изменяем список версий для выбранной группы

        self.model.choosen_group = "" # Записываем выбранную группу
        self.model.choosen_version = "" # Записываем выбранную категорию

        self.view.update_back_button_state(flag=self.model.in_group) # Вызываем изменение состояния кнопки "Назад"

        # Вызываем изменение текста в строке отображения выбранного файла
        self.view.update_choosen_file_label_text(string="Выбран файл:")
        self.view.update_download_version_button_state()

        if len(self.model.search_text) == 0: # Если нет текста в строке поиска
            self.load_table_data() # Вызываем загрузку данных в табицу
        else:
            self.on_search_lineedit_text_changed(lineedit_text=self.model.search_text) # Вызываем загрузку данных согласно поиска

        self.view.set_search_all_checkbox_enabled_state(state=True)

    def on_search_lineedit_text_changed(self, lineedit_text):
        """Функция обробатывает изменение текста в строке поиска"""
        self.model.search_text = lineedit_text # Устанавливам флаг поиска

        self.view.update_clear_search_button_state() # Вызываем изменение состояния кнопки очистки

        if lineedit_text: # Если в строке поиска есть текст
            search_all = self.view.get_search_all_versions_checkbox_state()
            if self.model.in_group: # Если в группе
                group_data = self.model.current_group_versions # Получаем список файлов текущей группы

                data = [] # Список данных подходящих под результаты поиска
                if group_data: # Если спиок файлов не пуст
                    for file in group_data: # Перебираем все файлы в списке
                        if all(word in file.lower() for word in lineedit_text.lower().split()): # Если все слова из строки поиска есть в имени файла
                            data.append(file) # Добавляем файл в список результатов поиска
                
                self.load_table_group_data(data=data) # Вызываем заполнение таблицы данными резульата поиска

            else: # Если не в группе
                search_data = self.model.search(text=lineedit_text, search_all=search_all)
                self.load_table_data(data=search_data)
            
        else: # Если в строке поиска удалили весь текст
            if self.model.in_group: # Если в группе
                self.load_table_group_data() # Вызываем заполнение таблицы данными для актуальной группы
            else: # Если не в группе
                self.load_table_data() # Вызываем заполнение таблицы данными

    def on_search_all_versions_checkbox_changed(self):
        """Функция обрабатывает изменение состояния чекбокса 'Поиск всех версий'"""
        self.on_search_lineedit_text_changed(self.model.search_text)

    def on_clear_button_clicked(self):
        """Функция обробатывает нажатие на кнопку очистки"""
        self.model.search_text = "" # Убираем текст для поиска
        self.view.clear_lineedit() # Вызываем очистку строки поиска
        self.view.update_clear_search_button_state() # Вызываем изменение состояния кнопки очистки
    
    def on_new_group_lineedit_text_changed(self):
        """Функция обрабатывает изменение текста в строке названия новой группы"""
        group_name = self.view.get_new_group_lineedit_text() # Получаем текст из строки ввода названия группы
        self.model.new_group_name = group_name # Записываем имя новой группы
        self.view.update_add_group_button_state()

    def on_add_version_folder_path_lineedit_text_changed(self):
        """Функция обрабатывает изменение текста в строке пути к папке версии"""
        file_path = self.view.get_new_file_lineedit_text() # Получяем текст из строки ввода пути к папке новой версии
        self.model.new_file_path = file_path # Записываем путь к папке новой версии
        self.view.update_add_version_button_state()

    def on_checkboxes_checked_state_changed(self):
        """Функция обрабатывает изменение состояния включения чекбоксов"""
        self.view.update_delete_group_button_state()
        self.view.update_delete_file_button_state()

    def on_choose_folder_path_buttons_clicked(self, button, lineedit):
        """Функция которая получает путь к папке через окно проводника и вызывает запись этого пути"""
        folder_path = QtWidgets.QFileDialog.getExistingDirectory()

        if folder_path:
            self.view.set_lineedit_path(lineedit, path=folder_path)

    def on_download_button_clicked(self):
        """Функция обробатывает нажатие на кнопку 'Скачать'"""
        self.model.download_file_in_theard()

    def on_choosen_path_to_download_lineedit_text_changed(self, text):
        """Функция обрабатывает изменение текста в строке пути загрузки"""
        self.model.choosen_path_to_download = text

    def on_add_group_button_pressed(self):
        """Функция обрабатывает нажатие на кнопку 'Добавить' группу"""
        self.model.add_group() # Вызываем добавление новой группы
        self.load_group_comboboxes_data() # Вызываем обновление данных в комбобоксах

        self.load_table_data()

    def on_add_file_button_pressed(self):
        """Функция обрабатывает нажатие на кнопку 'Добавить' файл"""
        group = self.view.get_add_group_combobox_text() # Получаем текущюю группу из комбобокса

        verefy_data = self.model.verefy_versions(group=group) # Вызываем проверку версий

        if verefy_data[0] == 4:
            Notification().show_notification_message(msg_type="error", text="Возникла неправильная ошибка во время проверки версий")

        elif verefy_data[0] == 3:
            Notification().show_notification_message(msg_type="error", text="Невозможно добавить выбранную версию\nТакая версия уже существует в выбранной группе!")

        elif verefy_data[0] == 2:
            self.model.add_file_in_theard(group=group, signal=self.file_added) # Вызывам добавление файла

        elif verefy_data[0] == 1:
            notification_action = Notification().show_action_message(title="Предупреждение", text="Нету изменений в версии\nВы уверены что хотите добавить версию?")

            if notification_action:
                self.model.add_file_in_theard(group=group, signal=self.file_added) # Вызывам добавление файла
        else:
            unchanged_files = ', '.join([os.path.basename(file) for file in verefy_data[1][0]])
            changed_files = '\n'.join([file for file in verefy_data[1][1]])  
            new_files_list = ', '.join([os.path.basename(file) for file in verefy_data[1][2]])
            missing_files_list = ', '.join([os.path.basename(file) for file in verefy_data[1][3]])

            notification_text = f"""
Файлы без изменений: {unchanged_files}\n
Файлы в которых есть изменения:\n{changed_files}\n
Новые файлы: {new_files_list}\n
Пропавшие файлы: {missing_files_list}
"""
            notification_action = Notification().show_action_message(msg_type="warning", 
                                                                     title="Изменения в версиях", 
                                                                     text=f"Обнаруженные изменения в новой версии:\n{notification_text}\nДобавить версию?",
                                                                     buttons=["Да", "Нет"])

            if notification_action:
                self.model.add_file_in_theard(group=group, signal=self.file_added) # Вызывам добавление файла

    def on_file_was_added(self):
        """Функция обрабатывает добавление файла в таблицу"""
        self.load_table_data()
        self.load_file_comboboxes_data()

    def on_delete_group_button_clicked(self):
        """Функция обрабатывает нажатие на кнопку 'Удалить' группу"""
        group = self.view.get_delete_group_combobox_text() # Получаем текущую группу из комбобокса
        self.model.delete_group_in_theard(group=group, signal=self.delete_group)

    def on_delete_file_button_clicked(self):
        """Функция обрабатывает нажатие на кнопку 'Удалить' файл"""
        group = self.view.get_delete_file_group_combobox_text() # Получаем текущую группу из комбобокса
        file = self.view.get_delete_file_combobox_text() # Получаем текущий файл из комбобокса
        self.model.delete_file_in_theard(group=group, file=file, signal=self.delete_file)

    def on_delete_group(self):
        """Функция обрабатывает удаление группы"""
        self.load_group_comboboxes_data() # Вызываем обновление данных в комбобоксах групп
        self.load_table_data() # Вызываем обновление данных в таблице
        self.view.set_delete_group_checkbox_state(False) # Изменяем состояние чекбокса

    def on_delete_file(self):
        """Функция обрабатывает удаление файла"""
        self.load_file_comboboxes_data() # Вызываем обновление данных в комбобоксах файлов
        self.load_table_data() # Вызываем обновление данных в таблице
        self.view.set_delete_file_checkbox_state(False) # Изменяем состояние чекбокса

    def on_progress_changed(self, value):
        self.view.set_progress_bar_value(value)  # Вызываем изменение значения прогресс бара
