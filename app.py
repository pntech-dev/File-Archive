import sys

from classes import Notification

from resources import resources_rc

from ui import Ui_MainWindow

from mvc import Model, View, Controller

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Иконка приложения
        icon = QIcon(":/icons/icon.ico")
        self.setWindowIcon(icon)

        self.model = Model()

        # Проверяем что данные получены
        if not type(self.model.config_data) == dict:
            Notification.show_notification(msg_type="error", 
                                           title="Ошибка", 
                                           text="Произошла ошибка при получении данных из файла конфигурации.", 
                                           button_text="Закрыть")
            sys.exit()

        self.view = View(ui=self.ui)
        self.controller = Controller(model=self.model, view=self.view)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    application = MyWindow()
    application.show()
    sys.exit(app.exec_())