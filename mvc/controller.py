class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Обработчики
        self.view.tab_button_clicked(self.on_tab_button_clicked) # Нажатие на кнопку раздела
        self.view.add_options_button_clicked(self.on_add_options_button_clicked) # Нажатие на кнопку выбора варианта добавления

    def on_tab_button_clicked(self, button):
        """Функция обрабатывает нажатие на кнопку раздела"""
        page = self.view.get_tab_page(button)
        self.view.set_tab_page(page)

    def on_add_options_button_clicked(self, button):
        """Функция обрабатывает нажатие на кнопку выбора варианта добавления"""
        page = self.view.get_add_option_page(button)
        self.view.set_add_option_page(page)