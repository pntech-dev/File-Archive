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

    def get_tab_page(self, button):
        """Функция возвращает страницу для переданной кнопки"""
        return self.tabs_dict[button]
    
    def set_tab_page(self, page):
        """Функция устанавливает страницу для отображения"""
        self.ui.tabs_stackedWidget.setCurrentWidget(page)

    def tab_button_clicked(self, handler):
        """Функция устанавливает обработчик нажатия на кнопку раздела"""
        for button in self.tabs_dict.keys():
            button.clicked.connect(lambda _, btn=button: handler(btn))