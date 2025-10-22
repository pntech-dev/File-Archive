import re
import sys

from PyQt5.QtWidgets import QFileDialog, QDialog
from PyQt5.QtCore import QObject, QEvent, pyqtSignal


class Controller(QObject):
    def __init__(self, model, view):
        super().__init__()

        self.model = model
        self.view = view

        self.__check_program_version() # Проверяем версию программы

        self._is_updating_versions = False

        # Настройки до запуска
        self.update_layer_one_table_data() # Загружаем данные в таблицу ГРУППЫ
        self.view.set_groups_comboboxes_data(self.model.get_groups_names()) # Загружаем данные в комбобоксы названий групп
        self.update_version_combobox_data() # Загружаем данные в комбобоксы версий групп

        # Устанавливаем фильтр событий для строки поиска
        self.view.ui.search_lineEdit.installEventFilter(self)

        """=== Обработчики ==="""
        # Кнопки
        self.view.tab_button_clicked(self.on_tab_button_clicked) # Нажатия на кнопки раздела
        self.view.download_page_choose_push_button_clicked(self.on_download_page_choose_folder_path_button_clicked) # Нажатие на кнопку выбора папки
        self.view.add_page_choose_folder_path_push_buttons_clicked(self.on_add_page_choose_folder_path_button_clicked) # Нажатие на кнопку выбора папки
        self.view.add_page_choose_file_path_push_buttons_clicked(self.on_add_page_choose_file_path_button_clicked) # Нажатие на кнопку выбора файла
        self.view.add_page_create_push_buttons_clicked(self.on_add_page_create_push_button_clicked) # Нажатие на кнопку создания группы
        self.view.add_page_add_push_buttons_clicked(self.on_add_page_add_push_button_clicked) # Нажатие на кнопку добавления
        self.view.delete_page_delete_push_buttons_clicked(self.on_delete_page_delete_push_button_clicked) # Нажатие на кнопки удаления
        self.view.download_page_back_push_button_clicked(self.on_download_page_back_push_button_clicked) # Нажатие на кнопку 'Назад'
        self.view.download_page_download_push_buttons_clicked(self.on_download_page_download_push_button_clicked) # Нажатие на кнопку 'Скачать'

        # Радио-кнопки
        self.view.add_page_radio_buttons_state_changed(self.on_add_options_button_clicked) # Нажатия на радио-кнопки выбора варианта добавления
        self.view.delete_page_radio_buttons_state_changed(self.on_delete_options_button_clicked) # Нажатия на радио-кнопки выбора варианта удаления

        # Лайнэдиты
        self.view.add_page_new_group_name_lineedit_text_changed(self.on_add_page_new_group_name_lineedit_text_changed) # Изменение текста в строке ввода имени новой группы
        self.view.add_page_paths_lineedits_text_changed(self.on_add_page_paths_lineedits_text_changed) # Изменение текста в строках ввода
        self.view.download_page_search_lineedit_text_changed(self.on_download_page_search_lineedit_text_changed) # Изменение текста в строке поиска

        # Комбобоксы
        self.view.add_page_group_name_combobox_item_changed(self.on_add_page_group_name_combobox_item_changed) # Изменение объекта в комбобоксе раздела Добавить
        self.view.delete_page_group_comboboxes_state_changed(self.on_delete_page_group_comboboxes_state_changed) # Изменение объектоы в комбобоксах раздела Удалить

        # Чек-боксы
        self.view.delete_page_checkboxes_state_changed(self.on_delete_page_checkboxes_state_changed) # Изменение состояния чек-боксов раздела Удалить
        self.view.download_page_search_all_versions_checkbox_state_changed(self.on_download_page_search_all_versions_checkbox_state_changed) # Изменение состояния чек-бокса поиска всех версий

        # Таблица
        self.view.download_page_table_row_clicked(self.on_download_page_table_row_clicked) # Нажатие на строку таблицы
        self.view.download_page_table_row_double_clicked(self.on_download_page_table_row_double_clicked) # Двойное нажатие на строку таблицы

        # Сигналы
        self.model.progress_chehged.connect(self.on_progress_bar_changed) # Сигнал изменения прогресс бара
        self.model.show_notification.connect(self.on_show_notification) # Сигнал показа уведомления
        self.model.operation_finished.connect(self.on_operation_finished) # Сигнал завершения операции

    # === Основные функции ===

    def __check_program_version(self):
        """Функция проверяет версию программы"""
        is_version = self.model.check_program_version() # Проверяем версию программы

        # Если произошла ошибка во время проверки версии
        if is_version is None:
            self.on_show_notification(msg_type="error", text="Во время проверки версии произошла ошибка!\nОшибка связана с путём к файлу конфигурации")
            exit()

        # Если версия не совпадает (требуется обновление)
        elif is_version:
        
            action = self.on_show_action_notification(msg_type="warning", 
                                                      title="Обновление", 
                                                      text="Обнаружена новая версия программы.\nПродолжить работу без обновления невозможно.\nЖелаете обновить?", 
                                                      buttons_texts=["Обновить", "Закрыть"])
            print("Action: ", action)
            if action == 1:
                self.model.update_program()
                sys.exit() # Закрываем основное приложение после запуска обновления
            else:
                sys.exit()


    def update_layer_one_table_data(self, data=None):
        """Функция обновляет данные в таблице ГРУППЫ"""
        if data is None:
            groups_names = self.model.get_groups_names() # Получаем список всех групп

            layer_one_data = []
            for group_name in groups_names:
                versions = self.model.get_group_versions(group_name) # Получаем список всех версий группы
                actual_version = self.model.get_actual_version(versions) # Получаем актуальную версию для группы
                layer_one_data.append([group_name, actual_version]) # Фирмируем список строк для талицы

            self.view.set_layer_one_table_data(layer_one_data) # Вызываем заполнение таблицы
        else:
            self.view.set_layer_one_table_data(data)

    def update_version_combobox_data(self):
        if self._is_updating_versions:
            return

        self._is_updating_versions = True
        try:
            group_name = self.view.get_delete_page_version_combobox_current_text()
            versions = self.model.get_group_versions(group_name)
            self.view.set_version_combobox_data(versions)
        finally:
            self._is_updating_versions = False

    # === Иконки ===

    def eventFilter(self, obj, event):
        """Функция устанавливает иконку строки поиска в зависимости от состояния строки поиска"""
        if obj is self.view.ui.search_lineEdit:
            if event.type() == QEvent.FocusIn:
                self.view.set_search_icon_state(state=True)
            elif event.type() == QEvent.FocusOut:
                self.view.set_search_icon_state(state=False)
                
        return super().eventFilter(obj, event)
    
    # === Панель НАВИГАЦИИ ===

    def on_tab_button_clicked(self, button):
        """Функция обрабатывает нажатие на кнопку раздела"""
        self.view.set_tab_page(button)

    # === Вкладка СКАЧАТЬ ===

    def update_back_push_button_state(self, state=None):
        """Функция обновляет состояние кнопки 'Назад' в разделе 'Скачать'"""
        if state is None:
            self.view.set_back_button_state(state=self.model.in_group)
        else:
            self.view.set_back_button_state(state=state)

    def update_download_button_state(self):
        """Функция обновляет состояние кнопки 'Скачать' в разделе 'Скачать'"""
        label_text = self.view.get_choosen_label_text().strip()
        if label_text != "Выбрано изделие:" and not label_text.endswith("Версия:"):
            self.view.set_download_button_state(state=True)
        else:
            self.view.set_download_button_state(state=False)

    def on_download_page_search_lineedit_text_changed(self):
        """Функция обрабатывает изменение текста в строке поиска в разделе 'Скачать'"""
        search_text = self.view.get_search_lineedit_text() # Получаем текст из строки поиска
        if search_text:
            if not self.model.search_all_versions:
                search_results = self.model.search(text=search_text) # Вызываем обычный поиск
                self.update_layer_one_table_data(data=search_results) # Обновляем данные в таблице ГРУППЫ
            else:
                search_results = self.model.search_all(text=search_text) # Вызываем поиск по всем файлам
                self.update_layer_one_table_data(data=search_results) # Обновляем данные в таблице ГРУППЫ
        else:
            self.update_layer_one_table_data() # Обновляем данные в таблице ГРУППЫ

    def on_download_page_search_all_versions_checkbox_state_changed(self, state):
        """Функция обрабатывает изменение состояния чек-бокса поиска всех версий в разделе 'Скачать'"""
        self.model.search_all_versions = state
        self.on_download_page_search_lineedit_text_changed() # Иммитируем изменение текста в строке поиска

    def on_download_page_choose_folder_path_button_clicked(self):
        """Функция обрабатывает нажатие на кнопку выбора папки в разделе 'Скачать'"""
        self.view.set_download_save_path(QFileDialog.getExistingDirectory())

    def on_download_page_table_row_clicked(self, row):
        """Функция обрабатывает нажатие на строку таблицы в разделе 'Скачать'"""
        row_data = self.view.get_table_row_data(row=row)
        self.view.set_choosen_label_text(data=row_data, in_group_flag=self.model.in_group)
        self.update_download_button_state()

    def on_download_page_table_row_double_clicked(self, row):
        """Функция обрабатывает двойное нажатие на строку таблицы в разделе 'Скачать'"""
        if not self.model.in_group:
            row_data = self.view.get_table_row_data(row=row)

            # Получаем версии группы и устанавливаем данные в таблицу
            layer_two_data = self.model.get_group_versions(group_name=row_data[0])
            self.view.set_layer_two_table_data(layer_two_data)

            self.model.in_group = True # Устанавливаем флаг нахождения в группе

            self.update_back_push_button_state() # Обновляем состояние кнопки 'Назад'

    def on_download_page_back_push_button_clicked(self):
        """Функция обрабатывает нажатие на кнопку 'Назад' в разделе 'Скачать'"""
        self.model.in_group = False # Устанавливаем флаг нахождения вне группы
        self.update_layer_one_table_data() # Обновляем данные в таблице ГРУППЫ
        self.update_back_push_button_state(state=False) # Обновляем состояние кнопки 'Назад'
        self.view.set_choosen_label_text(data=None, in_group_flag=None)
        self.update_download_button_state() # Обновляем состояние кнопки 'Скачать'

    def on_download_page_download_push_button_clicked(self):
        """Функция обрабатывает нажатие на кнопку 'Скачать' в разделе 'Скачать'"""
        text = self.view.get_choosen_label_text() # Получаем выбранный файл и группу

        group = re.search(r"Выбрано изделие:\s*(.*?)\s*,\s*Версия:", text).group(1) # Получаем группу
        file = re.search(r"Версия:\s*(.*)", text).group(1) # Получаем файл
        save_path = self.view.get_download_save_path() # Получаем путь сохранения

        self.view.update_page_enabled_state(page="download", state=False) # Отключаем страницу

        self.model.download_in_thread(group=group, file=file, save_path=save_path) # Вызываем скачивание

    # === Вкладка ДОБАВИТЬ ===

    def update_add_push_buttons_state(self):
        """Функция обновляет состояние кнопок 'Добавить' в разделе 'Добавить'"""
        group_name = self.view.get_add_page_combobox_current_group_name()
        lineedits_texts = self.view.get_add_page_paths_lineedits_datas()

        for value in lineedits_texts.values():
            text = value.get("text")
            button = value.get("button")
            
            self.view.set_add_button_state(state=True if group_name and text else False, button=button)

    def on_add_options_button_clicked(self, button):
        """Функция обрабатывает нажатие на кнопку выбора варианта добавления"""
        page = self.view.get_add_option_page(button)
        self.view.set_add_option_page(page)

    def on_add_page_choose_folder_path_button_clicked(self, button):
        """Функция обрабатывает нажатие на кнопку выбора папки в разделе 'Добавить'"""
        lineedit = self.view.get_path_lineedit(button=button)
        self.view.set_lineedit_path(lineedit=lineedit, path=QFileDialog.getExistingDirectory())

    def on_add_page_choose_file_path_button_clicked(self, button):
        """Функция обрабатывает нажатие на кнопку выбора файла в разделе 'Добавить'"""
        lineedit = self.view.get_path_lineedit(button=button)
        path, _ = QFileDialog.getOpenFileName(
            None,
            "Выбрать файл",
            "",
            "Докумен Word (*.doc *.docx);;All Files (*)"
        )

        self.view.set_lineedit_path(lineedit=lineedit, path=path)

    def on_add_page_create_push_button_clicked(self):
        """Функция обрабатывает нажатие на кнопку создания группы в разделе 'Добавить'"""
        new_group_name = self.view.get_new_group_name_lineedit_text() # Получаем имя новой группы
        self.model.new_group_name = new_group_name # Запоминаем имя новой группы

        self.view.update_page_enabled_state(page="add", state=False) # Отключаем страницу

        self.model.create_group_in_thread(group_name=new_group_name) # Создаём группу

    def on_add_page_new_group_name_lineedit_text_changed(self, text):
        """Функция обрабатывает изменение текста в строке ввода имени новой группы в разделе 'Добавить'"""
        group_name = self.view.get_new_group_name_lineedit_text()
        self.view.update_add_page_create_push_button_state(state=True if group_name else False)

    def on_add_page_paths_lineedits_text_changed(self):
        """Функция обрабатывает изменение текста в строках ввода в разделе 'Добавить'"""
        self.update_add_push_buttons_state()

    def on_add_page_group_name_combobox_item_changed(self):
        """Функция обрабатывает изменение объекта в комбобоксе в разделе 'Добавить'"""
        self.update_add_push_buttons_state()

    def on_add_page_add_push_button_clicked(self, button_type):
        """Функция обрабатывает нажатие на кнопку добавления в разделе 'Добавить'"""
        group_name = self.view.get_add_page_combobox_current_group_name() # Получаем имя группы

        # Добавление версии
        if button_type == "version":
            version_path = self.view.get_version_path_lineedit_text() # Получаем путь к версии
            self.view.update_page_enabled_state(page="add", state=False) # Отключаем страницу
            self.model.add_version_in_thread(version_path=version_path, group_name=group_name) # Вызываем добавление

        # Добавление инструкции
        elif button_type == "instruction":
            instruction_path = self.view.get_instruction_path_lineedit_text() # Получаем путь к инструкции
            self.view.update_page_enabled_state(page="add", state=False) # Отключаем страницу
            self.model.add_instruction_in_thread(instruction_path=instruction_path, group_name=group_name) # Вызываем добавление

    # === Вкладка УДАЛИТЬ ===

    def update_delete_push_buttons_state(self):
        """Обновляет состояние кнопок 'Удалить'."""
        comboboxes_data = self.view.get_delete_page_comboboxes_datas()
        checkboxes_data = self.view.get_delete_page_checkboxes_datas()

        for checkbox_data in checkboxes_data.values():
            checkbox_state = checkbox_data.get("state")
            what_delete = checkbox_data.get("what_delete")

            button_state = False
            if checkbox_state:
                relevant_comboboxes = [cb for cb in comboboxes_data.values() if cb.get("what_delete") == what_delete]
                button_state = all(cb.get("text") for cb in relevant_comboboxes)
            
            self.view.set_delete_button_state(state=button_state, button_type=what_delete)
            
    def on_delete_options_button_clicked(self, button):
        """Функция обрабатывает нажатие на кнопку выбора варианта удаления"""
        page = self.view.get_delete_option_page(button)
        self.view.set_delete_option_page(page)

    def on_delete_page_group_comboboxes_state_changed(self, combobox):
        """Функция обрабатывает изменение объектов в комбобоксах в разделе 'Удалить'"""
        # Мы обновляем список версий только в том случае, если был изменён комбобкс групп
        if combobox is self.view.ui.choose_group_to_delete_comboBox:
            self.update_version_combobox_data()
        
        self.update_delete_push_buttons_state()

    def on_delete_page_checkboxes_state_changed(self):
        """Функция обрабатывает изменение состояния чек-боксов в разделе 'Удалить'"""
        self.update_delete_push_buttons_state()

    def on_delete_page_delete_push_button_clicked(self, button_type):
        """Функция обрабатывает нажатие на кнопку удаления в разделе 'Удалить'"""
        if not button_type:
            return

        comboboxes_datas = self.view.get_delete_page_comboboxes_datas()

        if button_type == "file":
            file_page_data = []
            # Ищем комбобоксы страницы удаления файлов
            for combobox in comboboxes_datas.keys():
                if comboboxes_datas[combobox].get("what_delete") == "file":
                    # Получаем выбранные элементы из комбобоксов
                    file_page_data.append(self.view.get_delete_page_combobox_text(combobox=combobox))

            if file_page_data:
                self.view.update_page_enabled_state(page="delete", state=False) # Отключаем страницу
                self.model.delete_file_in_thread(data=file_page_data)

        elif button_type == "group":
            group_name = None
            # Ищем комбобокс страницы удаления группы
            for combobox in comboboxes_datas.keys():
                if comboboxes_datas[combobox].get("what_delete") == "group":
                    # Получаем выбранный элемент из комбобокса
                    group_name = self.view.get_delete_page_combobox_text(combobox=combobox)
                    break
            
            if group_name: # Если текст получен, удаляем
                self.view.update_page_enabled_state(page="delete", state=False) # Отключаем страницу
                self.model.delete_group_in_thread(group_name=group_name)

    # === Сигналы ===

    def on_progress_bar_changed(self, process_text, value):
        """Функция обрабатывает изменение состояния прогресс бара"""
        self.view.set_progress_bar_process_text(text=process_text)
        self.view.set_progress_bar_percents_text(percents=str(value) + "%")
        self.view.set_progress_bar_value(value=value)

    def on_show_notification(self, msg_type, text):
        """Функция обрабатывает показ уведомления"""
        if msg_type == "info":
            self.view.show_notification(msg_type=msg_type, title="Информация", text=text, button_text="Ок")
        elif msg_type == "warning":
            self.view.show_notification(msg_type=msg_type, title="Предупреждение", text=text, button_text="Ок")
        elif msg_type == "error":
            self.view.show_notification(msg_type=msg_type, title="Ошибка", text=text, button_text="Закрыть")
        
        # Обеуляем прогресс бар
        self.view.set_progress_bar_process_text(text="", set_to_zero=True)
        self.view.set_progress_bar_percents_text(percents="0%")
        self.view.set_progress_bar_value(value=0)

    def on_show_action_notification(self, msg_type, title, text, buttons_texts):
        """Функция обрабатывает показ уведомления с кнопкамими действия"""
        notification = self.view.show_action_notification(msg_type=msg_type, title=title, text=text, buttons_texts=buttons_texts)
        return notification

    def on_operation_finished(self, operation_name, status_code):
        """Функция обрабатывает завершение фоновой операции."""
        if status_code != 0:
            return # Если операция не успешна, ничего не делаем

        if operation_name == "create_group":
            self.update_layer_one_table_data()
            self.view.set_groups_comboboxes_data(self.model.get_groups_names())
            self.view.set_new_group_to_combobox(new_group_name=self.model.new_group_name)
            self.update_version_combobox_data()

        elif operation_name in ["add_version", "add_instruction"]:
            self.update_layer_one_table_data()
            self.view.set_groups_comboboxes_data(self.model.get_groups_names())
            self.update_version_combobox_data()

        elif operation_name == "delete_file":
            self.update_layer_one_table_data()
            self.view.set_groups_comboboxes_data(self.model.get_groups_names())
            self.update_version_combobox_data()
            self.view.set_delete_checkboxes_state(type="file", state=False)
            self.view.set_choosen_label_text(data=None, in_group_flag=None)

        elif operation_name == "delete_group":
            self.update_layer_one_table_data()
            self.view.set_groups_comboboxes_data(self.model.get_groups_names())
            self.update_version_combobox_data()
            self.view.set_delete_checkboxes_state(type="group", state=False)
            self.view.set_choosen_label_text(data=None, in_group_flag=None)

        # Обновляем состояние страниц
        self.view.update_page_enabled_state(state=True, check_all=True)