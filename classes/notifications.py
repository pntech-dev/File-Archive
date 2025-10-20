from ui import Ui_MessageBoxDialog, Ui_ActionMessageBoxDialog

from resources import resources_rc

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPixmap, QIcon


class CustomMessageBox(QDialog):
    def __init__(self, msg_type, title, text, button_text, parent=None):
        super().__init__(parent)

        # Иконка приложения
        icon = QIcon(":/icons/icon.ico")
        self.setWindowIcon(icon)

        # Убиарем кнопку "?" у окна
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Подключаем UI
        self.ui = Ui_MessageBoxDialog()
        self.ui.setupUi(self)
        self.ui.message_text_label.setTextFormat(Qt.PlainText)

        # Настраиваем UI
        self.setWindowTitle(title) # Устанавливаем название окна
        self.ui.message_icon_label.setPixmap(QPixmap(f":/icons/notifications/{msg_type}.svg")) # Устанавливаем иконку
        self.ui.message_text_label.setText(text) # Устанавливаем текст окна уведомления
        self.ui.message_text_label.adjustSize() # Растягиваем текст
        self.ui.action_pushButton.setText(button_text) # Устанавливаем текст кнопки
        self.ui.action_pushButton.clicked.connect(self.accept) # Подключаем обработку нажатия на кнопку

        # Обрабатываем типы уведомлений. Устанавлвиаем иконку и стиль кнопки
        if msg_type == "info":
            self.ui.action_pushButton.setStyleSheet(main_button_style)

        elif msg_type == "warning":
            self.ui.action_pushButton.setStyleSheet(secondary_button_style)

        elif msg_type == "error":
            self.ui.action_pushButton.setStyleSheet(secondary_button_style)


class CustomActionsMessageBox(QDialog):
    def __init__(self, msg_type, title, text, buttons_texts, parent=None):
        super().__init__(parent)

        # Иконка приложения
        icon = QIcon(":/icons/icon.ico")
        self.setWindowIcon(icon)

        # Убиарем кнопку "?" у окна
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Подключаем UI
        self.ui = Ui_ActionMessageBoxDialog()
        self.ui.setupUi(self)
        self.ui.message_text_label.setTextFormat(Qt.PlainText)

        # Настраиваем UI
        self.setWindowTitle(title) # Устанавливаем название окна
        self.ui.message_text_label.setText(text) # Устанавливаем текст окна уведомления
        self.ui.message_text_label.adjustSize() # Растягиваем текст
        self.ui.main_action_pushButton.setText(buttons_texts[0]) # Устанавливаем текст акцентной кнопки
        self.ui.secondary_action_pushButton.setText(buttons_texts[1]) # Устанавливаем текст второстепенной кнопки
        self.ui.main_action_pushButton.setStyleSheet(main_button_style) # Устанавливаем стиль акцентной кнопки
        self.ui.secondary_action_pushButton.setStyleSheet(secondary_button_style) # Устанавливаем стиль второстепенной кнопки
        self.ui.message_icon_label.setPixmap(QPixmap(f":/icons/notifications/{msg_type}.svg")) # Устанавливаем иконку

        # Подключаем действия кнопок
        self.ui.main_action_pushButton.clicked.connect(self.accept)
        self.ui.secondary_action_pushButton.clicked.connect(self.reject)

class Notification:
    def show_notification(msg_type, title, text, button_text):
        """Функция показывает уведомление"""
        CustomMessageBox(msg_type, title, text, button_text).exec()

    def show_actions_notification(msg_type, title, text, buttons_texts):
        """Функция показывает уведомление с возможностью выбора действия"""
        result = CustomActionsMessageBox(msg_type, title, text, buttons_texts).exec()
        return result
    

# Стили кнопок
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