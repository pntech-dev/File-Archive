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
        # Разделы, радио-кнопки, чекбоксы
        self.view.tab_button_clicked(self.on_tab_button_clicked) # Нажатие на кнопку раздела
        self.view.add_options_button_clicked(self.on_add_options_button_clicked) # Нажатие на кнопку выбора варианта добавления
        self.view.delete_options_button_clicked(self.on_delete_options_button_clicked) # Нажатие на кнопку выбора варианта удаления
        self.view.accept_version_delete_checkbox_clicked(self.on_accept_version_delete_checkbox_clicked) # Нажатие на чек-бокс подтверждения удаления версии
        self.view.accept_group_delete_checkbox_clicked(self.on_accept_group_delete_checkbox_clicked) # Нажатие на чек-бокс подтверждения удаления группы
        
        # Лайнэдиты
        self.view.create_group_lineedit_text_changed(self.on_create_group_lineedit_text_changed) # Изменение текста в строке ввода имени группы
        self.view.add_tab_folder_path_lineedit_text_changed(self.on_add_tab_folder_path_lineedit_text_changed) # Изменение текста в строке ввода пути папки
        self.view.add_tab_file_path_lineedit_text_changed(self.on_add_tab_file_path_lineedit_text_changed) # Изменение текста в строке ввода пути файла

        # Кнопки
        self.view.create_group_button_clicked(self.on_create_group_button_clicked) # Нажатие на кнопку создания группы
        self.view.select_folder_button_clicked(self.on_select_folder_button_clicked) # Нажатие на кнопку выбора папки
        self.view.select_file_button_clicked(self.on_select_file_button_clicked) # Нажатие на кнопку выбора файла

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

    def on_select_folder_button_clicked(self, button):
        """Функция обрабатывает нажатие на кнопку выбора папки"""
        folder_path = QFileDialog.getExistingDirectory()
        self.view.set_selected_folder_path(folder_path=folder_path, button=button)

    def on_select_file_button_clicked(self):
        """Функция обрабатывает нажатие на кнопку выбора файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Выбрать файл",
            "",
            "Докумен Word (*.doc *.docx);;All Files (*)"
        )

        self.view.set_selected_file_path(file_path=file_path)

    def on_add_tab_folder_path_lineedit_text_changed(self):
        """Функция обрабатывает изменение текста в строке ввода пути папки в разделе 'Добавить версию'"""
        self.view.update_add_version_button_state()

    def on_add_tab_file_path_lineedit_text_changed(self):
        """Функция обрабатывает изменение текста в строке ввода пути файла в разделе 'Добавить инструкцию'"""
        self.view.update_add_instruction_button_state()

    def on_accept_version_delete_checkbox_clicked(self, button):
        """Функция обрабатывает нажатие на чек-бокс подтверждения удаления версии"""
        self.view.update_delete_button_state(button=button)

    def on_accept_group_delete_checkbox_clicked(self, button):
        """Функция обрабатывает нажатие на чек-бокс подтверждения удаления группы"""
        self.view.update_delete_button_state(button=button)