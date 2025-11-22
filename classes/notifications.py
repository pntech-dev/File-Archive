from resources import resources_rc
from ui import Ui_MessageBoxDialog, Ui_ActionMessageBoxDialog

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPixmap, QIcon


class CustomMessageBox(QDialog):
    def __init__(self, msg_type=str, title=str, text=str, button_text=str, parent=None):
        super().__init__(parent)

        # Applications icon
        icon = QIcon(":/icons/icon.ico")
        self.setWindowIcon(icon)

        # Remove "?" button
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Connect UI
        self.ui = Ui_MessageBoxDialog()
        self.ui.setupUi(self)
        self.ui.message_text_label.setTextFormat(Qt.PlainText)

        # Configurate the UI
        self.setWindowTitle(title) # Set the window title
        self.ui.message_icon_label.setPixmap(QPixmap(f":/icons/notifications/{msg_type}.svg")) # Installing an icon
        self.ui.message_text_label.setText(text) # Setting the text of the notification window
        self.ui.message_text_label.adjustSize() # Stretch the text
        self.ui.action_pushButton.setText(button_text) # Setting the button text
        self.ui.action_pushButton.clicked.connect(self.accept) # Connecting button click processing

        # Process notification types. Set the icon and button style
        if msg_type == "info":
            self.ui.action_pushButton.setStyleSheet(main_button_style)

        elif msg_type == "warning":
            self.ui.action_pushButton.setStyleSheet(secondary_button_style)

        elif msg_type == "error":
            self.ui.action_pushButton.setStyleSheet(secondary_button_style)


class CustomActionsMessageBox(QDialog):
    def __init__(self, msg_type=str, title=str, text=str, buttons_texts=list[str], parent=None):
        super().__init__(parent)

        # Set the application icon
        icon = QIcon(":/icons/icon.ico")
        self.setWindowIcon(icon)

        # Remove "?" button
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Connect UI
        self.ui = Ui_ActionMessageBoxDialog()
        self.ui.setupUi(self)
        self.ui.message_text_label.setTextFormat(Qt.PlainText)

        # Configurate the UI
        self.setWindowTitle(title) # Setting the window name
        self.ui.message_text_label.setText(text) # Setting the text of the notification window
        self.ui.message_text_label.adjustSize() # Stretching the text
        self.ui.main_action_pushButton.setText(buttons_texts[0]) # Setting the text of the accent button
        self.ui.secondary_action_pushButton.setText(buttons_texts[1]) # Setting the text of the secondary button
        self.ui.main_action_pushButton.setStyleSheet(main_button_style) # Setting the style of the accent button
        self.ui.secondary_action_pushButton.setStyleSheet(secondary_button_style) # Setting the style of the secondary button
        self.ui.message_icon_label.setPixmap(QPixmap(f":/icons/notifications/{msg_type}.svg")) # Installing the icon

        # Enabling button actions
        self.ui.main_action_pushButton.clicked.connect(self.accept)
        self.ui.secondary_action_pushButton.clicked.connect(self.reject)

class Notification:
    def show_notification(msg_type: str, title: str, text: str, button_text: str) -> None:
        """Show a modal notification dialog.

        The dialog blocks execution until the user closes it.

        Args:
            msg_type: Notification category ('info', 'warning', 'error').
            title: Title of the dialog window.
            text: Text content of the notification.
            button_text: Label of the confirmation button.
        """
        CustomMessageBox(msg_type, title, text, button_text).exec()

    def show_actions_notification(msg_type: str, title: str, text: str, buttons_texts: list[str]) -> int:
        """Show a modal notification dialog with multiple action buttons.

        The dialog blocks execution and returns the index of the pressed button.

        Args:
            msg_type: Notification category ('info', 'warning', 'error').
            title: Title of the dialog window.
            text: Text content of the notification.
            buttons_texts: Button labels in the order they are displayed.

        Returns:
            Index of the pressed button (0-based).
        """
        btn_index = CustomActionsMessageBox(msg_type, title, text, buttons_texts).exec()

        return btn_index
    

# Buttons styles
main_button_style = """
/* === Акцентная кнопка=== */
QPushButton {
    background-color: #2563EB;       /* Основной синий */
    color: #FFFFFF;                  /* Белый текст */
    font-weight: bold;               /* Жирный шрифт */
    border: none;                    /* Без рамки */
    border-radius: 6px;              /* Скругления */
    padding: 6px 12px;               /* Отступы для аккуратности */
}

/* === Наведение (hover) === */
QPushButton:hover {
    background-color: #5283EF;       /* Более светлый синий */
}

/* === Нажатие (pressed / checked) === */
QPushButton:pressed,
QPushButton:checked {
    background-color: #124CC9;       /* Тёмно-синий при клике */
}

/* === Отключена (disabled) === */
QPushButton:disabled {
    background-color: #DEE8FC;       /* Бледно-синий фон */
    color: #FFFFFF;                  /* Белый текст (можно осветлить при желании) */
    border: none;
    border-radius: 6px;
}
"""

secondary_button_style = """
QPushButton {
    background-color: transparent;   /* Без заливки */
    color: #334155;                  /* Основной цвет текста */
    font-weight: normal;             /* Обычная жирность */
    border: 1px solid #64748B;       /* Серо-синяя рамка */
    border-radius: 6px;              /* Скругления */
    padding: 6px 12px;               /* Внутренние отступы */
}

/* === Наведение (hover) === */
QPushButton:hover {
    border: 1px solid #8B98AA;       /* Более светлая рамка */
}

/* === Нажатие (pressed / checked) === */
QPushButton:pressed,
QPushButton:checked {
    border: 1px solid #515E71;       /* Более тёмная рамка */
}

/* === Отключена (disabled) === */
QPushButton:disabled {
    color: #E2E8F0;                  /* Бледный текст */
    border: 1px solid #F8FAFC;       /* Светлая рамка */
}
"""