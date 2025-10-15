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
        self.view.tab_button_clicked(self.on_tab_button_clicked) # Нажатия на кнопки раздела
        self.view.download_page_choose_push_button_clicked(self.on_download_page_choose_folder_path_button_clicked) # Нажатие на кнопку выбора папки
        self.view.add_page_choose_folder_path_push_buttons_clicked(self.on_add_page_choose_folder_path_button_clicked) # Нажатие на кнопку выбора папки
        self.view.add_page_choose_file_path_push_buttons_clicked(self.on_add_page_choose_file_path_button_clicked) # Нажатие на кнопку выбора файла
        self.view.add_page_create_push_buttons_clicked(self.on_add_page_create_push_button_clicked) # Нажатие на кнопку создания группы

        # Радио-кнопки
        self.view.add_page_radio_buttons_state_changed(self.on_add_options_button_clicked) # Нажатия на радио-кнопки выбора варианта добавления
        self.view.delete_page_radio_buttons_state_changed(self.on_delete_options_button_clicked) # Нажатия на радио-кнопки выбора варианта удаления

        # Лайнэдиты
        self.view.add_page_new_group_name_lineedit_text_changed(self.on_add_page_new_group_name_lineedit_text_changed) # Изменение текста в строке ввода имени новой группы

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

    def on_download_page_choose_folder_path_button_clicked(self):
        """Функция обрабатывает нажатие на кнопку выбора папки в разделе 'Скачать'"""
        self.view.set_download_save_path(QFileDialog.getExistingDirectory())

    # === Вкладка ДОБАВИТЬ ===

    def on_add_options_button_clicked(self, button):
        """Функция обрабатывает нажатие на кнопку выбора варианта добавления"""
        page = self.view.get_add_option_page(button)
        self.view.set_add_option_page(page)

    def on_add_page_choose_folder_path_button_clicked(self, button):
        """Функция обрабатывает нажатие на кнопку выбора папки в разделе 'Добавить'"""
        lineedit = self.view.get_path_lineedit(button=button)
        self.view.set_lineedit_path(lineedit=lineedit, path=QFileDialog.getExistingDirectory())

    def on_add_page_choose_file_path_button_clicked(self, button):
        """Функция обрабатывает нажатие на кнопку выбора файла в разделе 'Добавить'"""
        lineedit = self.view.get_path_lineedit(button=button)
        path, _ = QFileDialog.getOpenFileName(
            None,
            "Выбрать файл",
            "",
            "Докумен Word (*.doc *.docx);;All Files (*)"
        )

        self.view.set_lineedit_path(lineedit=lineedit, path=path)

    def on_add_page_create_push_button_clicked(self):
        """Функция обрабатывает нажатие на кнопку создания группы в разделе 'Добавить'"""
        print("=== Создать группу ===")

    def on_add_page_new_group_name_lineedit_text_changed(self, text):
        """Функция обрабатывает изменение текста в строке ввода имени новой группы в разделе 'Добавить'"""
        group_name = self.view.get_new_group_name_lineedit_text()
        self.view.update_add_page_create_push_button_state(state=True if group_name else False)

    # === Вкладка УДАЛИТЬ ===

    def on_delete_options_button_clicked(self, button):
        """Функция обрабатывает нажатие на кнопку выбора варианта удаления"""
        page = self.view.get_delete_option_page(button)
        self.view.set_delete_option_page(page)