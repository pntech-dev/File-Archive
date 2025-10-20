from ui import Ui_PasswordDialog
from resources import resources_rc
from classes import Notification

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QDialog, QLineEdit


class PasswordDialog(QDialog):
    UNAUTHENTICATED_LOGIN_RESULT = 2
    MIN_PASSWORD_LENGTH = 4

    def __init__(self, correct_password, parent=None):
        super().__init__(parent)

        self.ui = Ui_PasswordDialog()
        self.ui.setupUi(self)

        self.correct_password = correct_password

        self.setWindowTitle("Авторизация")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowIcon(QIcon(":/icons/icon.ico"))

        self.ui.photo_label.setPixmap(QPixmap(f":/icons/auth/auth_bg_photo.png"))

        # Устанавливаем иконку в строку ввода пароля
        self.password_action = self.ui.password_lineEdit.addAction(QIcon(":/icons/auth/lock_white.svg"), QLineEdit.LeadingPosition)
        self.ui.password_lineEdit.installEventFilter(self)

        self.ui.password_lineEdit.textChanged.connect(self.update_ok_button_state)
        self.ui.full_mode_pushButton.clicked.connect(self.check_password)
        self.ui.base_mode_pushButton.clicked.connect(self.unauthenticated_login)
        
    def eventFilter(self, source, event):
        if source == self.ui.password_lineEdit:
            if event.type() == QEvent.FocusIn:
                self.set_password_icon_state(True)
            elif event.type() == QEvent.FocusOut:
                self.set_password_icon_state(False)
        return super().eventFilter(source, event)

    def set_password_icon_state(self, state):
        """Функция устанавливает иконку строки поиска в зависимости от состояния строки поиска"""
        if state:
            self.password_action.setIcon(QIcon(":/icons/auth/lock_blue.svg"))
        else:
            self.password_action.setIcon(QIcon(":/icons/auth/lock_white.svg"))

    def unauthenticated_login(self):
        self.done(self.UNAUTHENTICATED_LOGIN_RESULT)

    def _update_hint_style(self, is_valid):
        if is_valid:
            self.ui.hint_label.setStyleSheet("color: #16A34A")
        else:
            self.ui.hint_label.setStyleSheet("color: #64748B")

    def update_ok_button_state(self):
        is_long_enough = len(self.ui.password_lineEdit.text()) >= self.MIN_PASSWORD_LENGTH
        self.ui.full_mode_pushButton.setEnabled(is_long_enough)
        self._update_hint_style(is_long_enough)

    def check_password(self):
        if self.ui.password_lineEdit.text() == self.correct_password:
            self.accept()
        else:
            Notification.show_notification(msg_type="error", 
                                           title="Ошибка", 
                                           text="Введен неверный пароль!", 
                                           button_text="Закрыть")

    def get_password(self):
        return self.ui.password_lineEdit.text()