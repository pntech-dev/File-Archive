from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Пароль")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        font = QFont()
        font.setPointSize(12)
        self.setFont(font)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(25)

        self.ok_button = QPushButton("ОК")
        self.ok_button.setMinimumHeight(25)
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.setMinimumHeight(25)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Введите пароль:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_password(self):
        return self.password_input.text()
