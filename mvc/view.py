from resources import resources_rc

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLineEdit, QPushButton


class View:
    def __init__(self, ui):
        self.ui = ui

        # Иконка строки поиска
        search_icon = QIcon(":/icons/search_64748B.svg")
        self.ui.search_lineEdit.addAction(search_icon, QLineEdit.LeadingPosition)