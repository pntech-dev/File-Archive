import sys

from ui import Ui_MainWindow
from resources import resources_rc
from mvc import Model, View, Controller
from classes import Notification, PasswordDialog

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.model = Model()

        # Проверяем что данные получены
        if not type(self.model.config_data) == dict:
            Notification.show_notification(msg_type="error", 
                                           title="Ошибка", 
                                           text="Произошла ошибка при получении данных из файла конфигурации.", 
                                           button_text="Закрыть")
            sys.exit()

        # Проверяем пароль
        self.authentication_status = self.check_password()
        if self.authentication_status is not None:
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            
            # Иконка приложения
            icon = QIcon(":/icons/icon.ico")
            self.setWindowIcon(icon)

            self.view = View(ui=self.ui, authenticated=self.authentication_status)
            self.controller = Controller(model=self.model, view=self.view)
        else:
            sys.exit()

    def check_password(self):
        """Функция проверяет пароль"""
        # Получаем пароль из файла конфигурации
        password = self.model.config_data.get("password")

        if password:
            dialog = PasswordDialog(correct_password=password)
            dialog.password_changed.connect(self.set_password)
            result = dialog.exec_()

            if result == QDialog.Accepted: # Входим в полный режим
                return True
            
            elif result == 2: # Входим в обычный режим
                return False
        
            else: 
                return None
            
        else: # Если пароьль не задан, входим в обычный режим
            return False

    def set_password(self, new_password):
        """Функция устанавливает новый пароль"""
        self.model.set_password(new_password)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    application = MyWindow()
    application.show()
    sys.exit(app.exec_())