import sys

from resources import resources_rc

from ui.main_ui import Ui_MainWindow

from mvc import Model, View, Controller
from classes.password_dialog import PasswordDialog

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        icon = QIcon(":/icons/icon.ico")
        self.setWindowIcon(icon)

        # Инициализация MVC
        self.model = Model()
        
        authenticated = self.check_password()

        self.view = View(ui=self.ui, authenticated=authenticated)
        self.controller = Controller(model=self.model, view=self.view)

    def check_password(self):
        config_data = self.model.get_config_data()
        if not config_data:
            return True # Не удалось загрузить конфиг, разрешаем доступ

        password = config_data.get('password')
        if password:
            dialog = PasswordDialog()
            if dialog.exec_() == QDialog.Accepted:
                entered_password = dialog.get_password()
                if entered_password == password:
                    return True
            return False
        return True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    application = MyWindow()
    application.show()
    sys.exit(app.exec_())
