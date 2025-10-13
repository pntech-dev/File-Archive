from resources import resources_rc

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLineEdit


class View:
    def __init__(self, ui):
        self.ui = ui

        # Иконка строки поиска
        self.search_action = self.ui.search_lineEdit.addAction(QIcon(":/icons/search/search_icon.svg"), 
                                                               QLineEdit.LeadingPosition)

        # Иконки для кнопок разделов (ПО УМОЛЧАНИЮ)
        self.ui.download_tab_pushButton.setIcon(QIcon(":/icons/tabs/download_tab.svg"))
        self.ui.add_tab_pushButton.setIcon(QIcon(":/icons/tabs/add_tab.svg"))
        self.ui.delete_tab_pushButton.setIcon(QIcon(":/icons/tabs/delete_tab.svg"))

        # Словарь кнопок разделов, где ключ - кнопка, значение - раздел
        self.tabs_dict = {
            self.ui.download_tab_pushButton: self.ui.download_page,
            self.ui.add_tab_pushButton: self.ui.add_page,
            self.ui.delete_tab_pushButton: self.ui.delete_page
        }

        # Словарь вариантов добавления, где ключ - радио кнопка, значение - вариант
        self.add_options_dict = {
            self.ui.version_radioButton: self.ui.version_page,
            self.ui.instruction_radioButton: self.ui.instruction_page
        }

        # Словарь вариантов удаления, где ключ - радио кнопка, значение - вариант
        self.delete_options_dict = {
            self.ui.what_delete_file_radioButton: self.ui.delete_file_page,
            self.ui.what_delete_group_radioButton: self.ui.delete_group_page
        }

    def get_tab_page(self, button):
        """Функция возвращает страницу для переданной кнопки раздела"""
        return self.tabs_dict[button]
    
    def get_add_option_page(self, button):
        """Функция возвращает страницу для переданной кнопки варианта добавления"""
        return self.add_options_dict[button]
    
    def get_delete_option_page(self, button):
        """Функция возвращает страницу для переданной кнопки варианта удаления"""
        return self.delete_options_dict[button]
    
    def set_tab_page(self, page):
        """Функция устанавливает страницу для отображения"""
        self.ui.tabs_stackedWidget.setCurrentWidget(page)

    def set_add_option_page(self, page):
        """Функция устанавливает страницу отображения варианта добавления"""
        self.ui.add_format_stackedWidget.setCurrentWidget(page)

    def set_delete_option_page(self, page):
        """Функция устанавливает страницу отображения варианта удаления"""
        self.ui.delete_stackedWidget.setCurrentWidget(page)

    def set_search_icon_state(self, state):
        """Функция устанавливает иконку строки поиска в зависимости от состояния строки поиска"""
        if state:
            self.search_action.setIcon(QIcon(":/icons/search/search_icon_focus.svg"))
        else:
            self.search_action.setIcon(QIcon(":/icons/search/search_icon.svg"))

    def update_create_group_button_state(self):
        """Функция обновляет состояние кнопки создания группы"""
        text = self.ui.group_name_lineEdit.text() # Получаем текст из QLineEdit
        
        if text: # Если текст не пустой
            self.ui.create_group_pushButton.setEnabled(True) # Включаем кнопку
        else:
            self.ui.create_group_pushButton.setEnabled(False) # Выключаем кнопку

    def tab_button_clicked(self, handler):
        """Функция устанавливает обработчик нажатия на кнопку раздела"""
        for button in self.tabs_dict.keys():
            button.clicked.connect(lambda _, btn=button: handler(btn))

    def add_options_button_clicked(self, handler):
        """Функция устанавливает обработчик нажатия на кнопку выбора варианта добавления"""
        for button in self.add_options_dict.keys():
            button.clicked.connect(lambda _, btn=button: handler(btn))

    def delete_options_button_clicked(self, handler):
        """Функция устанавливает обработчик нажатия на кнопку выбора варианта удаления"""
        for button in self.delete_options_dict.keys():
            button.clicked.connect(lambda _, btn=button: handler(btn))

    def create_group_lineedit_text_changed(self, handler):
        """Функция устанавливает обработчик изменения текста в строке ввода имени группы"""
        self.ui.group_name_lineEdit.textChanged.connect(handler)

    def create_group_button_clicked(self, handler):
        """Функция устанавливает обработчик нажатия на кнопку создания группы"""
        self.ui.create_group_pushButton.clicked.connect(handler)