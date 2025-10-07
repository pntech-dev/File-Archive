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

        self.model = Model()
        self.authentication_status = self.check_password() # Can be True, False, or None

        if self.authentication_status is not None:
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)

            icon = QIcon(":/icons/icon.ico")
            self.setWindowIcon(icon)

            self.view = View(ui=self.ui, authenticated=self.authentication_status)
            self.controller = Controller(model=self.model, view=self.view)

    def check_password(self):
        config_data = self.model.get_password()
        if not config_data:
            return False # Treat as unauthenticated

        password = config_data.get('password')
        if password:
            dialog = PasswordDialog(correct_password=password)
            result = dialog.exec_()

            if result == QDialog.Accepted: # 1
                return True # Authenticated
            elif result == 2:
                return False # Unauthenticated
            else: # 0 (Rejected) or any other case
                return None # Exit application
        return True # No password set, treat as authenticated

if __name__ == "__main__":
    app = QApplication(sys.argv)
    application = MyWindow()
    if application.authentication_status is not None:
        application.show()
        sys.exit(app.exec_())