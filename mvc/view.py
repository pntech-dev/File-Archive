from resources import resources_rc

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLineEdit, QPushButton


class View:
    def __init__(self, ui):
        self.ui = ui

        # Иконка строки поиска
        search_icon = QIcon(":/icons/search_64748B.svg")
        self.ui.search_lineEdit.addAction(search_icon, QLineEdit.LeadingPosition)

        # Иконки для кнопок разделов (ПО УМОЛЧАНИЮ)
        download_icon = QIcon(":/icons/download_tab_white.svg")
        add_icon = QIcon(":/icons/add_tab_blue.svg")
        delete_icon = QIcon(":/icons/delete_tab_blue.svg")
        self.ui.download_tab_pushButton.setIcon(download_icon)
        self.ui.add_tab_pushButton.setIcon(add_icon)
        self.ui.delete_tab_pushButton.setIcon(delete_icon)