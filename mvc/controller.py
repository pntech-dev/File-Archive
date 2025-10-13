from PyQt5.QtCore import QObject, QEvent


class Controller(QObject):
    def __init__(self, model, view):
        super().__init__()

        self.model = model
        self.view = view

        # Устанавливаем фильтр событий для строки поиска
        self.view.ui.search_lineEdit.installEventFilter(self)

        # Обработчики
        self.view.tab_button_clicked(self.on_tab_button_clicked) # Нажатие на кнопку раздела
        self.view.add_options_button_clicked(self.on_add_options_button_clicked) # Нажатие на кнопку выбора варианта добавления
        self.view.delete_options_button_clicked(self.on_delete_options_button_clicked) # Нажатие на кнопку выбора варианта удаления
        
        self.view.create_group_lineedit_text_changed(self.on_create_group_lineedit_text_changed) # Изменение текста в строке ввода имени группы

        self.view.create_group_button_clicked(self.on_create_group_button_clicked) # Нажатие на кнопку создания группы

    def eventFilter(self, obj, event):
        """Функция устанавливает иконку строки поиска в зависимости от состояния строки поиска"""
        if obj is self.view.ui.search_lineEdit:
            if event.type() == QEvent.FocusIn:
                self.view.set_search_icon_state(state=True)
            elif event.type() == QEvent.FocusOut:
                self.view.set_search_icon_state(state=False)
                
        return super().eventFilter(obj, event)

    def on_tab_button_clicked(self, button):
        """Функция обрабатывает нажатие на кнопку раздела"""
        page = self.view.get_tab_page(button)
        self.view.set_tab_page(page)

    def on_add_options_button_clicked(self, button):
        """Функция обрабатывает нажатие на кнопку выбора варианта добавления"""
        page = self.view.get_add_option_page(button)
        self.view.set_add_option_page(page)

    def on_delete_options_button_clicked(self, button):
        """Функция обрабатывает нажатие на кнопку выбора варианта удаления"""
        page = self.view.get_delete_option_page(button)
        self.view.set_delete_option_page(page)

    def on_create_group_lineedit_text_changed(self):
        """Функция обрабатывает изменение текста в строке ввода имени группы"""
        self.view.update_create_group_button_state()

    def on_create_group_button_clicked(self):
        """Функция обрабатывает нажатие на кнопку создания группы"""
        print("=== СОЗДАТЬ ГРУППУ ===")