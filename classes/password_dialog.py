from ui import Ui_PasswordDialog
from classes import Notification
from resources import resources_rc

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QDialog, QLineEdit
from PyQt5.QtCore import Qt, QEvent, pyqtSignal


class PasswordDialog(QDialog):
    password_changed = pyqtSignal(str)
    UNAUTHENTICATED_LOGIN_RESULT = 2
    MIN_PASSWORD_LENGTH = 4

    def __init__(self, correct_password=str, parent=None):
        """Initialize the password dialog.

        Args:
            correct_password: Stored password used for validation.
            parent: Optional parent widget.
        """
        super().__init__(parent)

        self.ui = Ui_PasswordDialog()
        self.ui.setupUi(self)

        self.correct_password = correct_password

        # Window configuration
        self.setWindowTitle("Авторизация")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowIcon(QIcon(":/icons/icon.ico"))

        # Background image
        self.ui.photo_label.setPixmap(QPixmap(f":/icons/auth/auth_bg_photo.png"))

        # Icons for password input fields
        self.password_action = self.ui.password_lineEdit.addAction(QIcon(":/icons/auth/lock_white.svg"), QLineEdit.LeadingPosition)
        self.old_password_action = self.ui.old_password_lineEdit.addAction(QIcon(":/icons/auth/lock_white.svg"), QLineEdit.LeadingPosition)
        self.new_password_action = self.ui.new_password_lineEdit.addAction(QIcon(":/icons/auth/lock_white.svg"), QLineEdit.LeadingPosition)
        
        # Register focus event handler for icon updates
        self.ui.password_lineEdit.installEventFilter(self)
        self.ui.old_password_lineEdit.installEventFilter(self)
        self.ui.new_password_lineEdit.installEventFilter(self)

        # Page switching bindings
        self.ui.change_password_label.mousePressEvent = self.switch_to_change_password_page
        self.ui.back_auth_label.mousePressEvent = self.switch_to_auth_page

        # Input validators to enable/disable buttons
        self.ui.password_lineEdit.textChanged.connect(self.update_ok_button_state)
        self.ui.old_password_lineEdit.textChanged.connect(self.update_change_button_state)
        self.ui.new_password_lineEdit.textChanged.connect(self.update_change_button_state)
        
        # Mode buttons
        self.ui.full_mode_pushButton.clicked.connect(self.check_password)
        self.ui.base_mode_pushButton.clicked.connect(self.unauthenticated_login)
        self.ui.change_pushButton.clicked.connect(self.change_password)

        # Default page
        self.ui.stackedWidget.setCurrentWidget(self.ui.auth_page)

    def _update_hint_style(self, label, is_valid: bool) -> None:
        """Apply color style based on input validity."""
        if is_valid:
            label.setStyleSheet("color: #16A34A")
        else:
            label.setStyleSheet("color: #64748B")
        
    def eventFilter(self, source, event) -> bool:
        """Highlight input icons on focus.

        Args:
            source: The widget generating the event.
            event: Event instance.

        Returns:
            True if the event was processed, otherwise False.
        """

        if source in [self.ui.password_lineEdit, self.ui.old_password_lineEdit, self.ui.new_password_lineEdit]:
            action = None
            if source == self.ui.password_lineEdit:
                action = self.password_action
            elif source == self.ui.old_password_lineEdit:
                action = self.old_password_action
            elif source == self.ui.new_password_lineEdit:
                action = self.new_password_action

            if action:
                if event.type() == QEvent.FocusIn:
                    action.setIcon(QIcon(":/icons/auth/lock_blue.svg"))
                elif event.type() == QEvent.FocusOut:
                    action.setIcon(QIcon(":/icons/auth/lock_white.svg"))

        return super().eventFilter(source, event)

    def switch_to_change_password_page(self, event) -> None:
        """Switch interface to password change mode."""
        self.ui.stackedWidget.setCurrentWidget(self.ui.change_password_page)

    def switch_to_auth_page(self, event) -> None:
        """Switch interface back to authentication mode."""
        self.ui.stackedWidget.setCurrentWidget(self.ui.auth_page)

    def unauthenticated_login(self) -> None:
        """Close dialog returning unauthenticated login code."""
        self.done(self.UNAUTHENTICATED_LOGIN_RESULT)

    def update_ok_button_state(self) -> None:
        """Enable login button only when password length is valid."""
        is_long_enough = len(self.ui.password_lineEdit.text()) >= self.MIN_PASSWORD_LENGTH
        self.ui.full_mode_pushButton.setEnabled(is_long_enough)
        self._update_hint_style(self.ui.hint_label, is_long_enough)

    def update_change_button_state(self) -> None:
        """Enable password change button only when both fields are valid."""
        old_pass_valid = len(self.ui.old_password_lineEdit.text()) >= self.MIN_PASSWORD_LENGTH
        new_pass_valid = len(self.ui.new_password_lineEdit.text()) >= self.MIN_PASSWORD_LENGTH
        is_valid = old_pass_valid and new_pass_valid
        self.ui.change_pushButton.setEnabled(is_valid)
        self._update_hint_style(self.ui.hint_label_2, new_pass_valid)

    def check_password(self) -> None:
        """Validate password and authorize user."""
        if self.ui.password_lineEdit.text() == self.correct_password:
            self.accept()
        else:
            Notification.show_notification(
                msg_type="error",
                title="Ошибка",
                text="Введен неверный пароль!",
                button_text="Закрыть"
            )

    def change_password(self) -> None:
        """Attempt to change password and emit success signal."""
        old_password = self.ui.old_password_lineEdit.text()
        if old_password == self.correct_password:
            new_password = self.ui.new_password_lineEdit.text()
            self.password_changed.emit(new_password)
            Notification.show_notification(
                msg_type="info",
                title="Успех",
                text="Пароль успешно изменен!",
                button_text="Ок"
            )
            self.accept()
        else:
            Notification.show_notification(
                msg_type="error",
                title="Ошибка",
                text="Старый пароль введен неверно!",
                button_text="Закрыть"
            )

    def get_password(self) -> str:
        """Return entered password after successful authentication.

        Returns:
            Entered password string.
        """
        return self.ui.password_lineEdit.text()