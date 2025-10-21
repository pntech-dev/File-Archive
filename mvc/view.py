from resources import resources_rc

from classes import Notification

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLineEdit, QHeaderView, QTableWidgetItem, QAbstractItemView, QScroller


class View:
    def __init__(self, ui, authenticated):
        self.ui = ui
        self.authenticated = authenticated

        if not self.authenticated:
            self.ui.add_tab_pushButton.setEnabled(False)
            self.ui.delete_tab_pushButton.setEnabled(False)

        self.current_group_name = ""

        """=== Таблица ==="""
        self.table_groups_layer_headers = ["Изделие", "Последняя версия"]
        self.table_versions_layer_headers = ["Версия"]
        self.create_table_columns(headers=self.table_groups_layer_headers)

        # Планый скролл таблицы перетаскиванием
        QScroller.grabGesture(self.ui.tableWidget.viewport(), QScroller.LeftMouseButtonGesture)
        self.ui.tableWidget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.ui.tableWidget.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        # UI
        self.ui.tableWidget.setAlternatingRowColors(True)

        """=== Иконки ==="""
        # Устанавливаем иконку строки поиска
        self.search_action = self.ui.search_lineEdit.addAction(QIcon(":/icons/search/search_icon.svg"), 
                                                               QLineEdit.LeadingPosition)

        # Устанавливаем иконки для кнопок разделов
        self.ui.download_tab_pushButton.setIcon(QIcon(":/icons/tabs/download_tab.svg"))
        self.ui.add_tab_pushButton.setIcon(QIcon(":/icons/tabs/add_tab.svg"))
        self.ui.delete_tab_pushButton.setIcon(QIcon(":/icons/tabs/delete_tab.svg"))

        """=== Словари страниц ==="""
        # Словарь кнопок разделов, где ключ - кнопка, значение - раздел
        self.tabs_dict = {self.ui.download_tab_pushButton: self.ui.download_page,
                          self.ui.add_tab_pushButton: self.ui.add_page,
                          self.ui.delete_tab_pushButton: self.ui.delete_page}

        # Словарь вариантов добавления, где ключ - радио кнопка, значение - вариант
        self.add_options_dict = {self.ui.version_radioButton: self.ui.version_page,
                                 self.ui.instruction_radioButton: self.ui.instruction_page}

        # Словарь вариантов удаления, где ключ - радио кнопка, значение - вариант
        self.delete_options_dict = {self.ui.what_delete_file_radioButton: self.ui.delete_file_page,
                                    self.ui.what_delete_group_radioButton: self.ui.delete_group_page}
        
        """=== Словари кнопок ==="""
        self.add_page_choose_push_buttons_dict = {self.ui.choose_version_folder_pushButton: self.ui.choose_version_folder_lineEdit,
                                                   self.ui.choose_instruction_file_pushButton: self.ui.choose_instruction_file_lineEdit}
        
        self.add_page_add_push_buttons_dict = {self.ui.add_version_pushButton: "version",
                                                self.ui.add_instruction_pushButton: "instruction"}
        
        self.delete_page_delete_push_buttons_dict = {self.ui.delete_file_pushButton: "file",
                                                      self.ui.delete_group_pushButton: "group"}
        
        """=== Словари строк ввода ==="""
        self.add_page_paths_lineedits_dict = {self.ui.choose_version_folder_lineEdit: self.ui.add_version_pushButton,
                                         self.ui.choose_instruction_file_lineEdit: self.ui.add_instruction_pushButton}

        """=== Словари комбобоксов ==="""
        self.delete_page_comboboxes_dict = {self.ui.choose_group_to_delete_comboBox: "file",
                                            self.ui.choose_file_to_delete_comboBox: "file",
                                                   self.ui.choose_group_to_delete_comboBox_2: "group"}

        """=== Словари чекбоксов ==="""
        self.delete_page_checkboxes_dict = {self.ui.accept_file_delete_checkBox: "file",
                                             self.ui.accept_group_delete_checkBox: "group"}
        
        """=== Списки ==="""
        self.groups_comboboxes_lst = [self.ui.groups_comboBox,
                                 self.ui.choose_group_to_delete_comboBox,
                                 self.ui.choose_group_to_delete_comboBox_2]
    
    # === Общие функции ===

    def set_groups_comboboxes_data(self, group_names):
        """Функция утанавливает данные в комбобоксах групп"""
        for combobox in self.groups_comboboxes_lst:
            combobox.clear()
            combobox.addItems(group_names)

    def set_version_combobox_data(self, versions):
        """Функция утанавливает данные в комбобоксе версий"""
        self.ui.choose_file_to_delete_comboBox.clear()
        self.ui.choose_file_to_delete_comboBox.addItems(versions)

    # === Панель НАВИГАЦИИ ===
    # Кнопки "Скачать", "Добавить", "Удалить"
    
    def set_tab_page(self, button):
        """Функция устанавливает страницу для отображения"""
        page = self.tabs_dict.get(button)
        self.ui.tabs_stackedWidget.setCurrentWidget(page)

    def tab_button_clicked(self, handler):
        """Функция устанавливает обработчик нажатия на кнопку раздела"""
        for button in self.tabs_dict.keys():
            button.clicked.connect(lambda _, btn=button: handler(btn))
    
    # === Вкладка СКАЧАТЬ ===
    # Строка поиска, чек-боксы, таблица, кнопка "Назад", лайнэдиты, кнопка "Скачать"

    def get_table_row_data(self, row):
        """Функция возвращает данные из строки таблицы в разделе 'Скачать'"""
        data = []
        for column in range(self.ui.tableWidget.columnCount()):
            data.append(self.ui.tableWidget.item(row, column).text())

        return data

    def get_choosen_label_text(self):
        """Функция возвращает текст в строке выбранного файла в разделе 'Скачать'"""
        return self.ui.choose_file_label.text()

    def get_search_lineedit_text(self):
        """Функция возвращает текст в строке поиска в разделе 'Скачать'"""
        return self.ui.search_lineEdit.text()
    
    def get_download_save_path(self):
        """Функция возвращает текст из строки ввода пути сохранения файла в разделе 'Скачать'"""
        return self.ui.save_file_path_lineEdit.text()

    def set_search_icon_state(self, state):
        """Функция устанавливает иконку строки поиска в зависимости от состояния строки поиска"""
        if state:
            self.search_action.setIcon(QIcon(":/icons/search/search_icon_focus.svg"))
        else:
            self.search_action.setIcon(QIcon(":/icons/search/search_icon.svg"))

    def set_download_save_path(self, save_path):
        """Функция устанавливает путь сохранения файла в строке ввода пуьт в разделе 'Скачать'"""
        self.ui.save_file_path_lineEdit.setText(save_path)

    def set_layer_one_table_data(self, layer_one_data):
        """Функция устанавливает данные в таблице ГРУППЫ"""
        self.clear_table() # Очищаем таблицу

        self.ui.tableWidget.setColumnCount(len(self.table_groups_layer_headers))

        self.ui.tableWidget.setHorizontalHeaderLabels(self.table_groups_layer_headers) # Устанавливаем заголовки
        header = self.ui.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents) # Растяжение всех колонок по содержимому

        for data_row in layer_one_data:
            row = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(row)
            
            self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(data_row[0]))
            version = data_row[1][:-4] if not data_row[1] is None and data_row[1].endswith(".enc") else data_row[1]
            self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(version))

    def set_layer_two_table_data(self, layer_two_data):
        """Функция устанавливает данные в таблице ВЕРСИИ"""
        self.clear_table() # Очищаем таблицу

        self.ui.tableWidget.setColumnCount(len(self.table_versions_layer_headers))

        self.ui.tableWidget.setHorizontalHeaderLabels(self.table_versions_layer_headers) # Устанавливаем заголовки
        header = self.ui.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents) # Растяжение всех колонок по содержимому

        for data_row in layer_two_data:
            row = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(row)
            
            version = data_row[:-4] if not data_row is None and data_row.endswith(".enc") else data_row
            self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(version))

    def set_choosen_label_text(self, data, in_group_flag):
        """Функция изменяет текст в строке выбранного файла в разделе 'Скачать'"""
        if data is None:
            self.ui.choose_file_label.setText("Выбрано изделие:")
            self.current_group_name = ""
            return

        if not in_group_flag:
            # Режим просмотра групп - data = [group_name, version]
            self.current_group_name = data[0]
            self.ui.choose_file_label.setText(f"Выбрано изделие: {data[0]}, Версия: {data[1]}")
        else:
            # Режим просмотра версий внутри группы - data = [version]
            self.ui.choose_file_label.setText(f"Выбрано изделие: {self.current_group_name}, Версия: {data[0]}")
    
    def set_back_button_state(self, state):
        """Функция устанавливает состояние кнопки 'Назад' в разделе 'Скачать'"""
        self.ui.back_pushButton.setEnabled(state)

    def set_download_button_state(self, state):
        """Функция устанавливает состояние кнопки 'Скачать' в разделе 'Скачать'"""
        self.ui.download_file_pushButton.setEnabled(state)

    def clear_table(self):
        """Функция очищает таблицу"""
        self.ui.tableWidget.clear()
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.setColumnCount(0)

    def create_table_columns(self, headers):
        """Функция создает столбцы таблицы"""
        self.ui.tableWidget.setColumnCount(len(headers))
        self.ui.tableWidget.setHorizontalHeaderLabels(headers)

    def download_page_table_row_clicked(self, handler):
        """Функция устанавливает обработчик нажатия на строку таблицы в разделе 'Скачать'"""
        self.ui.tableWidget.cellClicked.connect(lambda row: handler(row=row))

    def download_page_table_row_double_clicked(self, handler):
        """Функция устанавливает обработчик двойного нажатия на строку таблицы в разделе 'Скачать'"""
        self.ui.tableWidget.cellDoubleClicked.connect(lambda row: handler(row=row))

    def download_page_search_lineedit_text_changed(self, handler):
        """Функция устанавливает обработчик изменения текста в строке поиска в разделе 'Скачать'"""
        self.ui.search_lineEdit.textChanged.connect(handler)

    def download_page_search_all_versions_checkbox_state_changed(self, handler):
        """Функция устанавливает обработчик изменения состояния чекбоксов в разделе 'Скачать'"""
        self.ui.search_all_versions_checkBox.stateChanged.connect(lambda state: handler(state=state))

    def download_page_back_push_button_clicked(self, handler):
        """Функция устанавливает обработчик нажатия на кнопку 'Назад' в разделе 'Скачать'"""
        self.ui.back_pushButton.clicked.connect(handler)

    def download_page_lineedits_text_changed(self, handler):
        """Функция устанавливает обработчик изменения текста в строках ввода в разделе 'Скачать'"""
        for lineedit in self.download_page_lineedits:
            lineedit.textChanged.connect(handler)

    def download_page_choose_push_button_clicked(self, handler):
        """Функция устанавливает обработчик нажатия на кнопку 'Выбрать' в разделе 'Скачать'"""
        self.ui.save_file_path_choose_pushButton.clicked.connect(handler)

    def download_page_download_push_buttons_clicked(self, handler):
        """Функция устанавливает обработчик нажатия на кнопку 'Скачать' в разделе 'Скачать'"""
        self.ui.download_file_pushButton.clicked.connect(handler)

    # === Вкладка ДОБАВИТЬ ===
    # Комбобокс, кнопка "Создать", радио-кнопки, лайнэдиты, кнопки "Добавить"

    def get_add_option_page(self, button):
        """Функция возвращает страницу для отображения варианта добавления в разделе 'Добавить'"""
        return self.add_options_dict.get(button)
    
    def get_path_lineedit(self, button):
        """Функция возвращает строку ввода пути в разделе 'Добавить'"""
        return self.add_page_choose_push_buttons_dict.get(button)
    
    def get_new_group_name_lineedit_text(self):
        """Функция возвращает текст в строке ввода имени новой группы в разделе 'Добавить'"""
        return self.ui.group_name_lineEdit.text()
    
    def get_add_page_paths_lineedits_datas(self):
        """Функция возвращает элементы, которые зависят от текста в строках ввода в разделе 'Добавить'"""
        lineedits_datas = {}
        for lineedit, button in self.add_page_paths_lineedits_dict.items():
            lineedits_datas[lineedit] = {"text": lineedit.text(), "button": button}

        return lineedits_datas
    
    def get_add_page_combobox_current_group_name(self):
        """Функция возвращает текущий текст комбобокса имени группы в разделе 'Добавить'"""
        return self.ui.groups_comboBox.currentText()
    
    def get_version_path_lineedit_text(self):
        """Функция возвращает текст в строке ввода пути версии в разделе 'Добавить'"""
        return self.ui.choose_version_folder_lineEdit.text()
    
    def get_instruction_path_lineedit_text(self):
        """Функция возвращает текст в строке ввода пути инструкции в разделе 'Добавить'"""
        return self.ui.choose_instruction_file_lineEdit.text()

    def set_add_option_page(self, page):
        """Функция устанавливает страницу отображения варианта добавления в разделе 'Добавить'"""
        self.ui.add_format_stackedWidget.setCurrentWidget(page)

    def set_lineedit_path(self, lineedit, path):
        """Функция устанавливает путь в строке ввода в разделе 'Добавить'"""
        lineedit.setText(path)

    def set_add_button_state(self, state, button):
        """Функция устанавливает состояние кнопки 'Добавить' в разделе 'Добавить'"""
        button.setEnabled(state)

    def set_new_group_to_combobox(self, new_group_name):
        """Функция устанавливает новую группу в комбобокесе как выбранную"""
        self.ui.groups_comboBox.setCurrentText(new_group_name)

    def update_add_page_create_push_button_state(self, state):
        """Функция обновляет состояние кнопки 'Создать' в разделе 'Добавить'"""
        self.ui.create_group_pushButton.setEnabled(state)

    def add_page_comboboxes_state_changed(self, handler):
        """Функция устанавливает обработчик изменения состояния комбобоксов в разделе 'Добавить'"""
        for combobox in self.add_page_comboboxes:
            combobox.currentIndexChanged.connect(handler)

    def add_page_new_group_name_lineedit_text_changed(self, handler):
        """Функция устанавливает обработчик изменения текста в строке ввода имени новой группы в разделе 'Добавить'"""
        self.ui.group_name_lineEdit.textChanged.connect(handler)

    def add_page_create_push_buttons_clicked(self, handler):
        """Функция устанавливает обработчик нажатия на кнопку 'Создать' в разделе 'Добавить'"""
        self.ui.create_group_pushButton.clicked.connect(handler)

    def add_page_radio_buttons_state_changed(self, handler):
        """Функция устанавливает обработчик изменения состояния радио-кнопок в разделе 'Добавить'"""
        for button in self.add_options_dict.keys():
            button.toggled.connect(lambda _, btn=button: handler(button=btn))

    def add_page_paths_lineedits_text_changed(self, handler):
        """Функция устанавливает обработчик изменения текста в строках ввода в разделе 'Добавить'"""
        for lineedit in self.add_page_paths_lineedits_dict.keys():
            lineedit.textChanged.connect(handler)

    def add_page_choose_folder_path_push_buttons_clicked(self, handler):
        """Функция устанавливает обработчик нажатия на кнопки 'Выбрать' папку в разделе 'Добавить'"""
        button = self.ui.choose_version_folder_pushButton
        self.ui.choose_version_folder_pushButton.clicked.connect(lambda: handler(button=button))

    def add_page_choose_file_path_push_buttons_clicked(self, handler):
        """Функция устанавливает обработчик нажатия на кнопки 'Выбрать' файл в разделе 'Добавить'"""
        button = self.ui.choose_instruction_file_pushButton
        self.ui.choose_instruction_file_pushButton.clicked.connect(lambda: handler(button=button))

    def add_page_add_push_buttons_clicked(self, handler):
        """Функция устанавливает обработчик нажатия на кнопки 'Добавить' в разделе 'Добавить'"""
        for button in self.add_page_add_push_buttons_dict.keys():
            button_type = self.add_page_add_push_buttons_dict.get(button)
            button.clicked.connect(lambda _, btn_type=button_type: handler(button_type=btn_type))

    def add_page_group_name_combobox_item_changed(self, handler):
        """Функция устанавливает обработчик изменения комбобокса имени группы в разделе 'Добавить'"""
        self.ui.groups_comboBox.currentTextChanged.connect(handler)

    # === Вкладка УДАЛИТЬ ===
    # Радио-кнопки, комбобоксы, чек-боксы, кнопки "Удалить"

    def get_delete_option_page(self, button):
        """Функция возвращает страницу для отображения варианта удаления"""
        return self.delete_options_dict.get(button)
    
    def get_delete_page_comboboxes_datas(self):
        """Функция возвращает состояния комбобоксов в разделе 'Удалить'"""
        comboboxes_datas = {}
        for combobox in self.delete_page_comboboxes_dict.keys():
            text = combobox.currentText()
            what_delete = self.delete_page_comboboxes_dict.get(combobox)
            comboboxes_datas[combobox] = {"text": text, "what_delete": what_delete}

        return comboboxes_datas

    def get_delete_page_checkboxes_datas(self):
        """Функция возвращает состояния чекбоксов в разделе 'Удалить'"""
        checkboxes_datas = {}
        for checkbox in self.delete_page_checkboxes_dict.keys():
            checkbox_state = checkbox.isChecked()
            what_delete = self.delete_page_checkboxes_dict.get(checkbox)
            checkboxes_datas[checkbox] = {"state": checkbox_state, "what_delete": what_delete}

        return checkboxes_datas
    
    def get_delete_page_version_combobox_current_text(self):
        """Функция возвращает текущий текст комбобокса версии в разделе 'Удалить'"""
        return self.ui.choose_group_to_delete_comboBox.currentText()
    
    def get_delete_page_combobox_text(self, combobox):
        """Функция возвращает текст комбобокса в разделе 'Удалить'"""
        return combobox.currentText()

    def set_delete_option_page(self, page):
        """Функция устанавливает страницу отображения варианта удаления"""
        self.ui.delete_stackedWidget.setCurrentWidget(page)

    def set_delete_button_state(self, state, button_type):
        """Функция устанавливает состояние кнопки 'Удалить' в разделе 'Удалить'"""
        for button in self.delete_page_delete_push_buttons_dict.keys():
            if self.delete_page_delete_push_buttons_dict.get(button) == button_type:
                button.setEnabled(state)

    def set_delete_checkboxes_state(self, type, state):
        """Функция устанавливает состояние чекбоксов в разделе 'Удалить'"""
        for checkbox in self.delete_page_checkboxes_dict.keys():
            if self.delete_page_checkboxes_dict.get(checkbox) == type:
                checkbox.setChecked(state)

    def delete_page_radio_buttons_state_changed(self, handler):
        """Функция устанавливает обработчик изменения состояния радио-кнопок в разделе 'Удалить'"""
        for button in self.delete_options_dict.keys():
            button.toggled.connect(lambda _, btn=button: handler(button=btn))

    def delete_page_group_comboboxes_state_changed(self, handler):
        """Функция устанавливает обработчик изменения состояния комбобоксов в разделе 'Удалить'"""
        for combobox in self.delete_page_comboboxes_dict.keys():
            combobox.currentIndexChanged.connect(lambda _, cb=combobox: handler(cb))

    def delete_page_checkboxes_state_changed(self, handler):
        """Функция устанавливает обработчик изменения состояния чекбоксов в разделе 'Удалить'"""
        for checkbox in self.delete_page_checkboxes_dict.keys():
            checkbox.stateChanged.connect(handler)

    def delete_page_delete_push_buttons_clicked(self, handler):
        """Функция устанавливает обработчик нажатия на кнопку 'Удалить' в разделе 'Удалить'"""
        for button in self.delete_page_delete_push_buttons_dict.keys():
            button_type = self.delete_page_delete_push_buttons_dict.get(button)
            button.clicked.connect(lambda _, btn_type=button_type: handler(button_type=btn_type))

    # === Прогресс бар ===
    # Текста прогресс бара, прогресс бар

    def set_progress_bar_process_text(self, text, set_to_zero=False):
        """Функция устанавливает текст прогресс бара"""
        self.ui.process_label.setText(f"Процесс: {text}" if not set_to_zero else "Процесс...")

    def set_progress_bar_percents_text(self, percents):
        """Функция устанавливает текст прогресс бара"""
        self.ui.percent_label.setText(percents)

    def set_progress_bar_value(self, value):
        """Функция устанавливает значение прогресс бара"""
        self.ui.progressBar.setValue(value)

    # === Уведомления ===
    def show_notification(self, msg_type, title, text, button_text):
        """Функция показывает уведомление"""
        Notification.show_notification(msg_type=msg_type, title=title, text=text, button_text=button_text)

    def show_action_notification(self, msg_type, title, text, buttons_texts):
        """Функция показывает сообщение с кнопками действий"""
        return Notification.show_actions_notification(msg_type=msg_type, title=title, text=text, buttons_texts=buttons_texts)