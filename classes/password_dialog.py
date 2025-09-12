from resources import resources_rc

from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

class PasswordDialog(QDialog):
    def __init__(self, correct_password, parent=None):
        super().__init__(parent)

        self.correct_password = correct_password

        self.setWindowTitle("Авторизация")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowIcon(QIcon(":/icons/icon.ico"))
        self.setMinimumSize(300, 150)
        self.setMaximumSize(300, 150)

        font = QFont()
        font.setPointSize(12)
        self.setFont(font)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(25)
        self.password_input.setPlaceholderText("Пароль...")
        self.password_input.textChanged.connect(self.update_ok_button_state)

        self.ok_button = QPushButton("ОК")
        self.ok_button.setMinimumHeight(25)
        self.ok_button.setEnabled(False)
        self.cancel_button = QPushButton("Войти без пароля")
        self.cancel_button.setMinimumHeight(25)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Введите пароль:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

        self.ok_button.clicked.connect(self.check_password)
        self.cancel_button.clicked.connect(self.unauthenticated_login)

    def unauthenticated_login(self):
        self.done(2)

    def update_ok_button_state(self):
        self.ok_button.setEnabled(bool(len(self.password_input.text()) >= 4))

    def check_password(self):
        if self.password_input.text() == self.correct_password:
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Введен неверный пароль!")

    def get_password(self):
        return self.password_input.text()
