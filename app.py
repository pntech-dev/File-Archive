import sys

from resources import resources_rc

from ui.main_ui import Ui_MainWindow

from mvc import Model, View, Controller

from PyQt5. QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        icon = QIcon(":/icons/icon.ico")
        self.setWindowIcon(icon)

        # Инициализация MVC
        self.model = Model()
        self.view = View(ui=self.ui)
        self.controller = Controller(model=self.model, view=self.view)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    application = MyWindow()
    application.show()
    sys.exit(app.exec_())