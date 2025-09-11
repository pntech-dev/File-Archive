from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView

class View:
    def __init__(self, ui, authenticated):
        self.ui = ui

        if not authenticated:
            self.ui.tabWidget.setTabEnabled(1, False)
            self.ui.tabWidget.setTabEnabled(2, False)

        self.group_comboboxes = [ # Список комбобоксов групп
            self.ui.add_tab_group_frame_select_group_frame_comboBox,
            self.ui.delete_tab_group_groupBox_frame_comboBox,
            self.ui.delete_tab_file_groupBox_group_frame_comboBox
        ]
        
        self.file_comboboxes = { # Словарь пар комбобоксов, где ключ - комбобокс группы, значение - комбобокс файла версии
            self.ui.delete_tab_file_groupBox_group_frame_comboBox: self.ui.delete_tab_file_groupBox_file_frame_comboBox
        }

        self.checkboxes_lst = [ # Список чекбоксов
            self.ui.delete_tab_group_groupBox_checkBox,
            self.ui.delete_tab_file_groupBox_checkBox
        ]

        self.choose_buttons_dir = { # Словарь, где ключи - кнопка "Выбрать", значение - лайнэдит соответствующей копки
            self.ui.download_tab_select_save_path_frame_editing_frame_choose_pushButton: self.ui.download_tab_select_save_path_frame_editing_frame_lineEdit,
            self.ui.add_tab_choose_file_frame_editing_frame_choose_pushButton: self.ui.add_tab_choose_file_frame_editing_frame_lineEdit
        }
        
        # Растяжение колонок в таблице
        header = self.ui.download_tab_tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

    def get_comboboxes_data(self):
        """Функция возвращает словрь данных, в котором ключ - текст комбобокса групп, значение - объект комбобокса версий"""
        comboboxes_data = {} # Словарь, где ключ - текст объекта ключа, значение - значение
        for key, value in self.file_comboboxes.items(): # Перебираем все пары ключ/значение в словаре
            comboboxes_data[key.currentText()] = value # Добавляем пары ключ/значение в новый словрь

        return comboboxes_data
    
    def get_table_row_group_data(self, row):
        """Функция возвращает данные первой колонки для переданой строки"""
        item = self.ui.download_tab_tableWidget.item(row, 0) # Получаем объект данных из таблицы

        return item.text() # Возвращаем текст объекта
    
    def get_table_row_file_data(self, row):
        """Функция возвращает данные из всех ячеек для переданной строки"""
        columns = self.ui.download_tab_tableWidget.columnCount() # Получаем количество колонок в таблице
        
        if row == None or columns == None: # Если строка не перередана или колонок нет
            return []

        data = [] # Создаем объект данных
        if columns > 1: # Если колонок больше чем 1
            # Перебираем все колонки и записываем данные из каждой ячейки в переданной строке и колонке
            for col in range(columns):
                data.append(self.ui.download_tab_tableWidget.item(row, col).text())
        else: # Если колонка 1, записываем из неё данные
            data.append(self.ui.download_tab_tableWidget.item(row, 0).text())

        return data
    
    def get_new_group_lineedit_text(self):
        """Функция возвращает текст из строки ввода имени новой группы"""
        text = self.ui.add_tab_group_frame_new_group_frame_editing_frame_lineEdit.text()
        return text
    
    def get_new_file_lineedit_text(self):
        """Функция возвращает текст из строки ввода пути к папке новой версии"""
        text = self.ui.add_tab_choose_file_frame_editing_frame_lineEdit.text()
        return text
    
    def get_add_group_combobox_text(self):
        """Функция возвращает данные из комбобокса группы вкладки 'Добавить'"""
        text = self.ui.add_tab_group_frame_select_group_frame_comboBox.currentText()
        return text
    
    def get_delete_group_combobox_text(self):
        """Функция возвращает данные из комбобокса группы вкладки 'Удалить'"""
        text = self.ui.delete_tab_group_groupBox_frame_comboBox.currentText()
        return text
    
    def get_delete_file_group_combobox_text(self):
        """Функция возвращает данные из комбобокса группы вкладки 'Удалить' раздела удаления файла"""
        text = self.ui.delete_tab_file_groupBox_group_frame_comboBox.currentText()
        return text
    
    def get_delete_file_combobox_text(self):
        """Функция возвращает данные из комбобокса файла вкладки 'Удалить'"""
        text = self.ui.delete_tab_file_groupBox_file_frame_comboBox.currentText()
        return text
    
    def get_search_all_versions_checkbox_state(self):
        """Функция возвращает состояние чекбокса 'Поиск всех версий'"""
        return self.ui.search_all_versions_checkBox.isChecked()
        
    def update_group_comboboxes_data(self, data):
        """Функция обновляет данные в комбобоксах групп"""
        if data: # Если переданные данные не пусты
            for combobox in self.group_comboboxes: # Перебираем комбобоксы
                combobox.clear() # Очищаем
                combobox.addItems(data)

    def update_file_combobox_data(self, data):
        """Функция обновляет данные в комбобоксе файлов версий"""
        for key, value in data.items(): # Перебираем данные в переданном словаре
            key.clear() # Очищаем
            key.addItems(value)

    def update_table_data(self, data):
        """Функция обновляет данные в таблице на основном уровне"""
        self.ui.download_tab_tableWidget.setRowCount(0) # Очищачем таблицу
        self.ui.download_tab_tableWidget.setColumnCount(2) # Устанавливаем количесвто колонок
        self.ui.download_tab_tableWidget.setHorizontalHeaderLabels(["Изделие", "Последняя версия"]) # Устанавливаем заголовок для колонки

        for i in data: # Перебираем списки пар групп/версий в списке
            row = self.ui.download_tab_tableWidget.rowCount() # Получаем количество строк
            self.ui.download_tab_tableWidget.insertRow(row) # Добавляем новую строку

            group = QTableWidgetItem(str(i[0]))
            version = QTableWidgetItem(str(i[1])) 
            self.ui.download_tab_tableWidget.setItem(row, 0, group)
            self.ui.download_tab_tableWidget.setItem(row, 1, version)

    def update_table_files_data(self, data):
        """Функция обновляет данные в таблице на уровне версий группы"""
        self.ui.download_tab_tableWidget.setColumnCount(1) # Устанавливаем 1 колонку
        self.ui.download_tab_tableWidget.setRowCount(0) # Очищаем строки

        self.ui.download_tab_tableWidget.setHorizontalHeaderLabels(["Версии"]) # Устанавливаем заголовок для колонки

        for version in data: # Перебираем все версии в данных
            row = self.ui.download_tab_tableWidget.rowCount() # Получаем количество строк
            self.ui.download_tab_tableWidget.insertRow(row) # Добавляем новую строку

            item = QTableWidgetItem(version) # Создаём объект данных для таблицы с значением version
            # Устанавливаем объект в таблицу в строку - row, в колонку - 0, объект - item
            self.ui.download_tab_tableWidget.setItem(row, 0, item)

    def update_back_button_state(self, flag):
        """Функция обновляет состояние кнопки 'Назад'"""
        if flag: # Если флаг True
            self.ui.download_tab_choose_file_frame_back_pushButton.setEnabled(True) # Включаем кнопку
        else:
            self.ui.download_tab_choose_file_frame_back_pushButton.setEnabled(False) # Выключаем кнопку

    def update_clear_search_button_state(self):
        """Функция обновляет состояние кнопки 'Очистить'"""
        if self.ui.download_tab_search_frame_lineEdit.text(): # Если в строке поиска есть текст
            self.ui.download_tab_search_frame_clear_pushButton.setEnabled(True) # Включаем кнопку
        else:
            self.ui.download_tab_search_frame_clear_pushButton.setEnabled(False) # Выключаем кнопку

    def update_add_group_button_state(self):
        """Функция обновляет состояние кнопки 'Добавить' новую группу"""
        if self.ui.add_tab_group_frame_new_group_frame_editing_frame_lineEdit.text():
            self.ui.add_tab_group_frame_new_group_frame_editing_frame_add_pushButton.setEnabled(True) # Включаем кнопку
        else:
            self.ui.add_tab_group_frame_new_group_frame_editing_frame_add_pushButton.setEnabled(False) # Выключаем кнопку

    def update_add_version_button_state(self):
        """Функция обновляет состояние кнопки 'Добавить' версию"""
        # Если в комбобоксе группы есть текст и в строке пути к папке с файлами версии есть текст
        if self.ui.add_tab_group_frame_select_group_frame_comboBox.currentText() and self.ui.add_tab_choose_file_frame_editing_frame_lineEdit.text():
            self.ui.add_tab_add_pushButton.setEnabled(True) # Включаем кнопку
        else:
            self.ui.add_tab_add_pushButton.setEnabled(False) # Выключаем кнопку
    
    def update_download_version_button_state(self):
        """Функция обновляет состояние кнопки 'Скачать'"""
        label_text = self.ui.download_tab_choose_file_frame_label.text()  # Получаем текст из QLabel, отображающий выбранный файл
        enabled = False  # Флаг для состояния кнопки

        # Проверяем, выбран ли файл (текст отличается от стандартного)
        if label_text != "Выбран файл:":
            parts = label_text.split(",")  # Разделяем строку по запятой: ожидается формат "Выбран файл:, путь"
            # Проверяем, что после запятой есть текст
            if len(parts) > 1 and parts[1].strip():
                enabled = True  # Включаем кнопку

        self.ui.download_tab_download_pushButton.setEnabled(enabled)  # Устанавливаем состояние кнопки

    def update_delete_group_button_state(self):
        """Функция обновляет состояние кнопки 'Удалить' группу"""
        # Если чекбокс нажат и в комбобоксе выбран объект
        if self.ui.delete_tab_group_groupBox_checkBox.isChecked() and self.ui.delete_tab_group_groupBox_frame_comboBox.currentText():
            self.ui.delete_tab_group_groupBox_frame_delete_pushButton.setEnabled(True) # Включаем кнопку
        else:
            self.ui.delete_tab_group_groupBox_frame_delete_pushButton.setEnabled(False) # Выключаем кнопку

    def update_delete_file_button_state(self):
        """Функция обновляет состояние кнопки 'Удалить' файл группы"""
        # Если чекбокс нажат и в комбобоксах группы и файла выбраны объекты
        if self.ui.delete_tab_file_groupBox_checkBox.isChecked() and self.ui.delete_tab_file_groupBox_group_frame_comboBox.currentText() and self.ui.delete_tab_file_groupBox_file_frame_comboBox.currentText():
            self.ui.delete_tab_file_groupBox_delete_pushButton.setEnabled(True) # Включаем кнопку
        else:
            self.ui.delete_tab_file_groupBox_delete_pushButton.setEnabled(False) # Выключаем кнопку

    def update_choosen_file_label_text(self, string):
        """Функция изменяет текст в строке отображения выбранного файла"""
        self.ui.download_tab_choose_file_frame_label.setText(string) # Изменяем текст в QLabel

    def clear_lineedit(self):
        """Финкция очищает строку поиска"""
        self.ui.download_tab_search_frame_lineEdit.clear()

    def set_lineedit_path(self, lineedit, path):
        """Функция вставлят переданный путь в """
        lineedit.setText(path)

    def group_file_combobox_item_changed(self, handler):
        """Функция вызывает обработку смены текущего объекта в комбобоксе группы"""
        for combobox in self.file_comboboxes.keys(): # Перебираем все ключи в словаре комбобоксов
            combobox.currentTextChanged.connect(handler) # Вызываем обработчик при изменении объекта в комбобоксе

    def table_row_clicked(self, handler):
        """Функция вызывает оброботку одинарного нажатия на строку в таблице"""
        self.ui.download_tab_tableWidget.cellClicked.connect(handler)

    def table_row_double_ckicked(self, handler):
        """Функция вызывает оброботку двойного нажатия на строку в таблице"""
        self.ui.download_tab_tableWidget.cellDoubleClicked.connect(handler)

    def back_button_clicked(self, handler):
        """Функция вызывает обработку нажатия на кнопку назад"""
        self.ui.download_tab_choose_file_frame_back_pushButton.clicked.connect(handler)

    def search_lineedit_text_changed(self, handler):
        """Функция вызывает обработку изменений текста в строке поиска"""
        self.ui.download_tab_search_frame_lineEdit.textChanged.connect(handler)

    def search_all_versions_checkbox_changed(self, handler):
        """Функция вызывает обработку изменения состояния чекбокса 'Поиск всех версий'"""
        self.ui.search_all_versions_checkBox.stateChanged.connect(handler)

    def clear_button_clicked(self, handler):
        """Функция вызывает обработку нажатия на кнопку очистки строки поиска"""
        self.ui.download_tab_search_frame_clear_pushButton.clicked.connect(handler)

    def new_group_lineedit_text_changed(self, handler):
        """Функция обрабатывает изменение текста в строке названия новой группы"""
        self.ui.add_tab_group_frame_new_group_frame_editing_frame_lineEdit.textChanged.connect(handler)

    def add_version_folder_path_lineedit_text_changed(self, handler):
        """Функция вызывает обработку нажатия на кнопку добавления версии"""
        self.ui.add_tab_choose_file_frame_editing_frame_lineEdit.textChanged.connect(handler)

    def checkboxes_checked_state_changed(self, handler):
        """Функция вызывает обработку изменения состояния включения чекбоксов"""
        for checkbox in self.checkboxes_lst:
            checkbox.stateChanged.connect(handler)

    def choose_folder_path_buttons_clicked(self, handler):
        """Функция вызывает обработку нажатия на кнопки выбор папки"""
        for key, value in self.choose_buttons_dir.items():
            key.clicked.connect(lambda state, btn=key, line=value: handler(btn, line))

    def choosen_path_to_download_lineedit_text_changed(self, handler):
        """Функция вызывает обработку изменения текста в строке выбранного пути для загрузки версии"""
        lineedit = self.ui.download_tab_select_save_path_frame_editing_frame_lineEdit
        lineedit.textChanged.connect(handler)

    def download_button_clicked(self, handler):
        """Функция вызывает обработку нажатия на кнопку скачать"""
        self.ui.download_tab_download_pushButton.clicked.connect(handler)
    
    def add_group_button_pressed(self, handler):
        """Функция вызывает обработку нажатия на кнопку добавления группы"""
        self.ui.add_tab_group_frame_new_group_frame_editing_frame_add_pushButton.clicked.connect(handler)
    
    def add_file_button_pressed(self, handler):
        """Функция вызывает обработку нажатия на кнопку добавления файла"""
        self.ui.add_tab_add_pushButton.clicked.connect(handler)

    def delete_group_button_pressed(self, handler):
        """Функция вызывает обработку нажатия на кнопку удаления группы"""
        self.ui.delete_tab_group_groupBox_frame_delete_pushButton.clicked.connect(handler)

    def delete_file_button_pressed(self, handler):
        """Функция вызывает обработку нажатия на кнопку удаления файла"""
        self.ui.delete_tab_file_groupBox_delete_pushButton.clicked.connect(handler)

    def set_progress_bar_value(self, value):
        """Функция изменяет значение в прогресс баре"""
        self.ui.progressBar.setValue(value) # Устанавливаем значение для прогресс бара

    def set_delete_group_checkbox_state(self, state):
        """Функция изменяет состояние чекбокса удаления группы"""
        self.ui.delete_tab_group_groupBox_checkBox.setChecked(state) # Устанавливаем значение для чекбокса

    def set_delete_file_checkbox_state(self, state):
        """Функция изменяет состояние чекбокса удаления файла"""
        self.ui.delete_tab_file_groupBox_checkBox.setChecked(state) # Устанавливаем значение для чекбокса

    def set_search_all_checkbox_enabled_state(self, state):
        """Функция изменяет состояние включения чекбокса поиска всех версий"""
        self.ui.search_all_versions_checkBox.setEnabled(state) # Устанавливаем значение для чекбокса
