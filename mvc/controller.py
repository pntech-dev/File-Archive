from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QObject, QEvent


class Controller(QObject):
    def __init__(self, model, view):
        super().__init__()

        self.model = model
        self.view = view

        # Устанавливаем фильтр событий для строки поиска
        self.view.ui.search_lineEdit.installEventFilter(self)

        """=== Обработчики ==="""
        # Кнопки
        self.view.tab_button_clicked(self.on_tab_button_clicked) # Нажатия на кнопки разделаэ

        # Радио-кнопки
        self.view.add_page_radio_buttons_state_changed(self.on_add_options_button_clicked) # Нажатия на радио-кнопки выбора варианта добавления
        self.view.delete_page_radio_buttons_state_changed(self.on_delete_options_button_clicked) # Нажатия на радио-кнопки выбора варианта удаления

    # === Иконки ===

    def eventFilter(self, obj, event):
        """Функция устанавливает иконку строки поиска в зависимости от состояния строки поиска"""
        if obj is self.view.ui.search_lineEdit:
            if event.type() == QEvent.FocusIn:
                self.view.set_search_icon_state(state=True)
            elif event.type() == QEvent.FocusOut:
                self.view.set_search_icon_state(state=False)
                
        return super().eventFilter(obj, event)
    
    # === Панель НАВИГАЦИИ ===

    def on_tab_button_clicked(self, button):
        """Функция обрабатывает нажатие на кнопку раздела"""
        self.view.set_tab_page(button)

    # === Вкладка СКАЧАТЬ ===

    # === Вкладка ДОБАВИТЬ ===

    def on_add_options_button_clicked(self, button):
        """Функция обрабатывает нажатие на кнопку выбора варианта добавления"""
        page = self.view.get_add_option_page(button)
        self.view.set_add_option_page(page)

    # === Вкладка УДАЛИТЬ ===

    def on_delete_options_button_clicked(self, button):
        """Функция обрабатывает нажатие на кнопку выбора варианта удаления"""
        page = self.view.get_delete_option_page(button)
        self.view.set_delete_option_page(page)