from resources import resources_rc

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLineEdit


class View:
    def __init__(self, ui):
        self.ui = ui

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

    def set_search_icon_state(self, state):
        """Функция устанавливает иконку строки поиска в зависимости от состояния строки поиска"""
        if state:
            self.search_action.setIcon(QIcon(":/icons/search/search_icon_focus.svg"))
        else:
            self.search_action.setIcon(QIcon(":/icons/search/search_icon.svg"))

    def set_download_save_path(self, save_path):
        """Функция устанавливает путь сохранения файла в строке ввода пуьт в разделе 'Скачать'"""
        self.ui.save_file_path_lineEdit.setText(save_path)

    def download_page_search_lineedit_text_changed(self, handler):
        """Функция устанавливает обработчик изменения текста в строке поиска в разделе 'Скачать'"""
        self.ui.search_lineEdit.textChanged.connect(handler)

    def download_page_checkboxes_state_changed(self, handler):
        """Функция устанавливает обработчик изменения состояния чекбоксов в разделе 'Скачать'"""
        for checkbox in self.download_page_checkboxes:
            checkbox.stateChanged.connect(handler)

    # === === === === === === === === ===
    # 
    # Функции обработки изменения таблицы
    # 
    # === === === === === === === === ===

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

    def set_add_option_page(self, page):
        """Функция устанавливает страницу отображения варианта добавления в разделе 'Добавить'"""
        self.ui.add_format_stackedWidget.setCurrentWidget(page)

    def set_lineedit_path(self, lineedit, path):
        """Функция устанавливает путь в строке ввода в разделе 'Добавить'"""
        lineedit.setText(path)

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

    def add_page_lineedits_text_changed(self, handler):
        """Функция устанавливает обработчик изменения текста в строках ввода в разделе 'Добавить'"""
        for lineedit in self.add_page_lineedits:
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
        for button in self.add_page_add_push_buttons:
            button.clicked.connect(handler)
    
    # === Вкладка УДАЛИТЬ ===
    # Радио-кнопки, комбобоксы, чек-боксы, кнопки "Удалить"

    def get_delete_option_page(self, button):
        """Функция возвращает страницу для отображения варианта удаления"""
        return self.delete_options_dict.get(button)

    def set_delete_option_page(self, page):
        """Функция устанавливает страницу отображения варианта удаления"""
        self.ui.delete_stackedWidget.setCurrentWidget(page)

    def delete_page_radio_buttons_state_changed(self, handler):
        """Функция устанавливает обработчик изменения состояния радио-кнопок в разделе 'Удалить'"""
        for button in self.delete_options_dict.keys():
            button.toggled.connect(lambda _, btn=button: handler(button=btn))

    def delete_page_comboboxes_state_changed(self, handler):
        """Функция устанавливает обработчик изменения состояния комбобоксов в разделе 'Удалить'"""
        for combobox in self.delete_page_comboboxes:
            combobox.currentIndexChanged.connect(handler)

    def delete_page_checkboxes_state_changed(self, handler):
        """Функция устанавливает обработчик изменения состояния чекбоксов в разделе 'Удалить'"""
        for checkbox in self.delete_page_checkboxes:
            checkbox.stateChanged.connect(handler)

    def delete_page_delete_push_buttons_clicked(self, handler):
        """Функция устанавливает обработчик нажатия на кнопку 'Удалить' в разделе 'Удалить'"""
        for button in self.delete_page_delete_push_buttons:
            button.clicked.connect(lambda _, btn=button: handler(btn))

    # === Прогресс бар ===
    # Текста прогресс бара, прогресс бар