from resources import resources_rc

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLineEdit


class View:
    def __init__(self, ui):
        self.ui = ui

        # Иконка строки поиска
        search_icon = QIcon(":/icons/search_64748B.svg")
        self.ui.search_lineEdit.addAction(search_icon, QLineEdit.LeadingPosition)

        # Иконки для кнопок разделов (ПО УМОЛЧАНИЮ)
        download_icon = QIcon(":/icons/download_tab_white.svg")
        add_icon = QIcon(":/icons/add_tab_white.svg")
        delete_icon = QIcon(":/icons/delete_tab_white.svg")
        self.ui.download_tab_pushButton.setIcon(download_icon)
        self.ui.add_tab_pushButton.setIcon(add_icon)
        self.ui.delete_tab_pushButton.setIcon(delete_icon)

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