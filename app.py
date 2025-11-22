import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow

from ui import Ui_MainWindow
from resources import resources_rc
from mvc import Controller, Model, View
from classes import Notification, PasswordDialog


class MyWindow(QMainWindow):
    """The main application window.

    This class is responsible for initializing the core components of the
    application, including the model, view, and controller. It also manages
    the initial password authentication process.
    """

    def __init__(self) -> None:
        """Initializes the main window and its components."""
        super().__init__()

        self.model = Model()

        # Check if the configuration data was loaded successfully.
        if not isinstance(self.model.config_data, dict):
            Notification.show_notification(
                msg_type="error",
                title="Ошибка",
                text="Произошла ошибка при получении данных из "
                     "файла конфигурации.",
                button_text="Закрыть"
            )
            sys.exit()

        # Authenticate the user before showing the main window.
        self.authentication_status = self.check_password()
        if self.authentication_status is not None:
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)

            self.setWindowIcon(QIcon(":/icons/icon.ico"))

            # Initialize MVC components.
            self.view = View(
                ui=self.ui, authenticated=self.authentication_status
            )
            self.controller = Controller(model=self.model, view=self.view)
        else:
            # Exit if the user cancels authentication.
            sys.exit()

    def check_password(self) -> bool | None:
        """Checks the user's password.

        Retrieves the password from the configuration file. If a password
        is set, it displays a password dialog. If no password is set, it
        defaults to restricted access mode.

        Returns:
            True: If the correct password is provided for full access.
            False: If the user chooses restricted mode or no password is set.
            None: If the user closes or cancels the password dialog.
        """
        password = self.model.get_decrypted_password()

        if password:
            dialog = PasswordDialog(correct_password=password)
            dialog.password_changed.connect(self.set_password)
            result = dialog.exec_()

            if result == QDialog.Accepted:
                return True  # Full access mode.
            elif result == 2:
                return False  # Restricted mode.
            else:
                return None  # User canceled the dialog.
        else:
            # If no password is set, default to restricted mode.
            return False

    def set_password(self, new_password: str) -> None:
        """Sets a new password.

        Args:
            new_password: The new password to be encrypted and saved.
        """
        self.model.set_password(new_password)


if __name__ == "__main__":
    # Application entry point.
    app = QApplication(sys.argv)
    application = MyWindow()
    application.show()
    sys.exit(app.exec_())