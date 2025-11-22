from resources import resources_rc

from classes import Notification

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QLineEdit,
    QHeaderView,
    QTableWidgetItem,
    QAbstractItemView,
    QScroller,
)
from PyQt5.QtCore import QObject


class View(QObject):
    """Application view wrapper.

    This class connects the generated UI (self.ui) with higher-level
    helper methods and signal wiring used by the controller.
    It exposes convenience methods for working with widgets on all tabs.
    """

    def __init__(self, ui: object, authenticated: bool) -> None:
        """Initialize the view and configure initial UI state.

        Args:
            ui: An instance of the generated UI class (from Qt Designer).
            authenticated: Flag indicating whether the user is authenticated.
        """
        super().__init__()

        self.ui = ui
        self.authenticated = authenticated

        # Disable Add/Delete tabs if user is not authenticated
        if not self.authenticated:
            self.ui.add_tab_pushButton.setEnabled(False)
            self.ui.delete_tab_pushButton.setEnabled(False)

        self.current_group_name = ""

        # === Table configuration ===
        self.table_groups_layer_headers = ["Изделие", "Последняя версия"]
        self.table_versions_layer_headers = ["Версия"]
        self.create_table_columns(headers=self.table_groups_layer_headers)

        # Smooth scrolling for the table using mouse drag
        QScroller.grabGesture(self.ui.tableWidget.viewport(), QScroller.LeftMouseButtonGesture)
        self.ui.tableWidget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.ui.tableWidget.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        # UI options
        self.ui.tableWidget.setAlternatingRowColors(True)

        # === Icons ===
        # Search line edit icon
        self.search_action = self.ui.search_lineEdit.addAction(
            QIcon(":/icons/search/search_icon.svg"),
            QLineEdit.LeadingPosition,
        )

        # Tab buttons icons
        self.ui.download_tab_pushButton.setIcon(QIcon(":/icons/tabs/download_tab.svg"))
        self.ui.add_tab_pushButton.setIcon(QIcon(":/icons/tabs/add_tab.svg"))
        self.ui.delete_tab_pushButton.setIcon(QIcon(":/icons/tabs/delete_tab.svg"))

        # === Pages dictionaries ===
        # Tab buttons -> pages
        self.tabs_dict = {
            self.ui.download_tab_pushButton: self.ui.download_page,
            self.ui.add_tab_pushButton: self.ui.add_page,
            self.ui.delete_tab_pushButton: self.ui.delete_page,
        }

        # Add options: radio button -> page
        self.add_options_dict = {
            self.ui.version_radioButton: self.ui.version_page,
            self.ui.instruction_radioButton: self.ui.instruction_page,
        }

        # Delete options: radio button -> page
        self.delete_options_dict = {
            self.ui.what_delete_file_radioButton: self.ui.delete_file_page,
            self.ui.what_delete_group_radioButton: self.ui.delete_group_page,
        }

        # Pages -> internal page name
        self.pages_dict = {
            self.ui.download_page: "download",
            self.ui.add_page: "add",
            self.ui.delete_page: "delete",
        }

        # === Buttons dictionaries ===
        # Add page: choose path buttons -> corresponding line edits
        self.add_page_choose_push_buttons_dict = {
            self.ui.choose_version_folder_pushButton: self.ui.choose_version_folder_lineEdit,
            self.ui.choose_instruction_file_pushButton: self.ui.choose_instruction_file_lineEdit,
        }

        # Add page: add buttons -> action type
        self.add_page_add_push_buttons_dict = {
            self.ui.add_version_pushButton: "version",
            self.ui.add_instruction_pushButton: "instruction",
        }

        # Delete page: delete buttons -> type
        self.delete_page_delete_push_buttons_dict = {
            self.ui.delete_file_pushButton: "file",
            self.ui.delete_group_pushButton: "group",
        }

        # === Line edits dictionaries ===
        # Add page: path line edits -> related add buttons
        self.add_page_paths_lineedits_dict = {
            self.ui.choose_version_folder_lineEdit: self.ui.add_version_pushButton,
            self.ui.choose_instruction_file_lineEdit: self.ui.add_instruction_pushButton,
        }

        # === Comboboxes dictionaries ===
        self.delete_page_comboboxes_dict = {
            self.ui.choose_group_to_delete_comboBox: "file",
            self.ui.choose_file_to_delete_comboBox: "file",
            self.ui.choose_group_to_delete_comboBox_2: "group",
        }

        # === Checkboxes dictionaries ===
        self.delete_page_checkboxes_dict = {
            self.ui.accept_file_delete_checkBox: "file",
            self.ui.accept_group_delete_checkBox: "group",
        }

        # === Group comboboxes list ===
        self.groups_comboboxes_lst = [
            self.ui.groups_comboBox,
            self.ui.choose_group_to_delete_comboBox,
            self.ui.choose_group_to_delete_comboBox_2,
        ]

        # === Additional collections for handlers ===
        # These attributes are used by handler-binding methods below.
        self.download_page_lineedits = [
            self.ui.save_file_path_lineEdit,
        ]
        self.add_page_comboboxes = [
            self.ui.groups_comboBox,
        ]

    # === Common helper methods ===

    def set_groups_comboboxes_data(self, group_names: list[str]) -> None:
        """Set group names into all group comboboxes.

        Args:
            group_names: List of group names to display.
        """
        for combobox in self.groups_comboboxes_lst:
            combobox.clear()
            combobox.addItems(group_names)

    def set_version_combobox_data(self, versions: list[str]) -> None:
        """Set version names into the delete-file combobox.

        Args:
            versions: List of version names.
        """
        self.ui.choose_file_to_delete_comboBox.clear()
        self.ui.choose_file_to_delete_comboBox.addItems(versions)

    def update_page_enabled_state(self, page: str | None = None, state: bool = True, check_all: bool = False) -> None:
        """Enable or disable one or all pages.

        Args:
            page: Internal page name ('download', 'add', 'delete') or None.
            state: True to enable, False to disable.
            check_all: If True, apply state to all pages.
        """
        if check_all:
            # Update all pages
            for page_obj in self.pages_dict.keys():
                page_obj.setEnabled(state)
        else:
            if page is not None:
                # Update only the specified page
                for page_obj, page_name in self.pages_dict.items():
                    if page_name == page:
                        page_obj.setEnabled(state)

    # === Navigation bar (tabs) ===

    def set_tab_page(self, button) -> None:
        """Switch stacked widget page based on tab button.

        Args:
            button: Tab button that was clicked.
        """
        page = self.tabs_dict.get(button)
        if page is not None:
            self.ui.tabs_stackedWidget.setCurrentWidget(page)

    def tab_button_clicked(self, handler) -> None:
        """Bind handler to tab buttons click events.

        Args:
            handler: Callback that accepts a button argument.
        """
        for button in self.tabs_dict.keys():
            button.clicked.connect(lambda _, btn=button: handler(btn))

    # === Download tab ===

    def get_table_row_data(self, row: int) -> list[str]:
        """Return data from a specific table row on Download tab.

        Args:
            row: Row index in the table.

        Returns:
            List of cell texts for the given row.
        """
        data: list[str] = []
        for column in range(self.ui.tableWidget.columnCount()):
            item = self.ui.tableWidget.item(row, column)
            data.append(item.text() if item is not None else "")
        return data

    def get_choosen_label_text(self) -> str:
        """Return text of the 'chosen file' label on Download tab."""
        return self.ui.choose_file_label.text()

    def get_search_lineedit_text(self) -> str:
        """Return text from search line edit on Download tab."""
        return self.ui.search_lineEdit.text()

    def get_download_save_path(self) -> str:
        """Return text from save path line edit on Download tab."""
        return self.ui.save_file_path_lineEdit.text()

    def set_search_icon_state(self, state: bool) -> None:
        """Update search icon depending on focus state.

        Args:
            state: True if focused, False otherwise.
        """
        if state:
            self.search_action.setIcon(QIcon(":/icons/search/search_icon_focus.svg"))
        else:
            self.search_action.setIcon(QIcon(":/icons/search/search_icon.svg"))

    def set_download_save_path(self, save_path: str) -> None:
        """Set save path text on Download tab.

        Args:
            save_path: Path string to display.
        """
        self.ui.save_file_path_lineEdit.setText(save_path)

    def set_layer_one_table_data(self, layer_one_data: list[list[str | None]]) -> None:
        """Populate table with groups and their last versions.

        Args:
            layer_one_data: List of [group_name, version_name] rows.
        """
        self.clear_table()

        self.ui.tableWidget.setColumnCount(len(self.table_groups_layer_headers))
        self.ui.tableWidget.setHorizontalHeaderLabels(self.table_groups_layer_headers)

        header = self.ui.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

        for data_row in layer_one_data:
            row = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(row)

            group_name = data_row[0]
            version_raw = data_row[1]

            self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(group_name))

            if version_raw is not None and isinstance(version_raw, str) and version_raw.endswith(".enc"):
                version = version_raw[:-4]
            else:
                version = version_raw if version_raw is not None else ""

            self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(version))

    def set_layer_two_table_data(self, layer_two_data: list[str | None]) -> None:
        """Populate table with versions for a selected group.

        Args:
            layer_two_data: List of version names.
        """
        self.clear_table()

        self.ui.tableWidget.setColumnCount(len(self.table_versions_layer_headers))
        self.ui.tableWidget.setHorizontalHeaderLabels(self.table_versions_layer_headers)

        header = self.ui.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

        for data_row in layer_two_data:
            row = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(row)

            if data_row is not None and isinstance(data_row, str) and data_row.endswith(".enc"):
                version = data_row[:-4]
            else:
                version = data_row if data_row is not None else ""

            self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(version))

    def set_choosen_label_text(self, data, in_group_flag: bool | None) -> None:
        """Update 'chosen file' label text on Download tab.

        Args:
            data: Row data (group and version) or None to reset selection.
            in_group_flag: Flag indicating whether we are inside a specific group.
        """
        if data is None:
            self.ui.choose_file_label.setText("Выбрано изделие:")
            self.current_group_name = ""
            return

        if not in_group_flag:
            # Group view mode: data = [group_name, version]
            self.current_group_name = data[0]
            self.ui.choose_file_label.setText(f"Выбрано изделие: {data[0]}, Версия: {data[1]}")
        else:
            # Version view mode: data = [version]
            self.ui.choose_file_label.setText(
                f"Выбрано изделие: {self.current_group_name}, Версия: {data[0]}",
            )

    def set_back_button_state(self, state: bool) -> None:
        """Enable or disable 'Back' button on Download tab."""
        self.ui.back_pushButton.setEnabled(state)

    def set_download_button_state(self, state: bool) -> None:
        """Enable or disable 'Download' button on Download tab."""
        self.ui.download_file_pushButton.setEnabled(state)

    def clear_table(self) -> None:
        """Clear all data and structure from the table widget."""
        self.ui.tableWidget.clear()
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.setColumnCount(0)

    def create_table_columns(self, headers: list[str]) -> None:
        """Create table columns with the given headers.

        Args:
            headers: List of column header texts.
        """
        self.ui.tableWidget.setColumnCount(len(headers))
        self.ui.tableWidget.setHorizontalHeaderLabels(headers)

    def download_page_table_row_clicked(self, handler) -> None:
        """Bind handler for single row click on Download tab table.

        Args:
            handler: Callback accepting row index as 'row' keyword argument.
        """
        self.ui.tableWidget.cellClicked.connect(lambda row, _col: handler(row=row))

    def download_page_table_row_double_clicked(self, handler) -> None:
        """Bind handler for double row click on Download tab table.

        Args:
            handler: Callback accepting row index as 'row' keyword argument.
        """
        self.ui.tableWidget.cellDoubleClicked.connect(lambda row, _col: handler(row=row))

    def download_page_search_lineedit_text_changed(self, handler) -> None:
        """Bind handler for search line edit text changes on Download tab.

        Args:
            handler: Callback called on textChanged signal.
        """
        self.ui.search_lineEdit.textChanged.connect(handler)

    def download_page_search_all_versions_checkbox_state_changed(self, handler) -> None:
        """Bind handler for 'search all versions' checkbox state changes.

        Args:
            handler: Callback accepting 'state' keyword argument.
        """
        self.ui.search_all_versions_checkBox.stateChanged.connect(
            lambda state: handler(state=state),
        )

    def download_page_back_push_button_clicked(self, handler) -> None:
        """Bind handler for 'Back' button click on Download tab."""
        self.ui.back_pushButton.clicked.connect(handler)

    def download_page_lineedits_text_changed(self, handler) -> None:
        """Bind handler for text changes in Download tab line edits.

        Args:
            handler: Callback called on textChanged for each line edit.
        """
        for lineedit in self.download_page_lineedits:
            lineedit.textChanged.connect(handler)

    def download_page_choose_push_button_clicked(self, handler) -> None:
        """Bind handler for 'Choose' button click on Download tab.

        Args:
            handler: Callback for save path choose button.
        """
        self.ui.save_file_path_choose_pushButton.clicked.connect(handler)

    def download_page_download_push_buttons_clicked(self, handler) -> None:
        """Bind handler for 'Download' button click on Download tab.

        Args:
            handler: Callback for download button.
        """
        self.ui.download_file_pushButton.clicked.connect(handler)

    # === Add tab ===

    def get_add_option_page(self, button):
        """Return page widget for the selected Add option.

        Args:
            button: Radio button that defines the add option.

        Returns:
            Page widget corresponding to the button.
        """
        return self.add_options_dict.get(button)

    def get_path_lineedit(self, button):
        """Return line edit associated with a 'Choose' button on Add tab.

        Args:
            button: Button used to select a path.

        Returns:
            Corresponding QLineEdit widget.
        """
        return self.add_page_choose_push_buttons_dict.get(button)

    def get_new_group_name_lineedit_text(self) -> str:
        """Return text from 'new group name' line edit on Add tab."""
        return self.ui.group_name_lineEdit.text()

    def get_add_page_paths_lineedits_datas(self) -> dict:
        """Return mapping of Add tab path line edits to their texts and buttons.

        Returns:
            Dict mapping lineedit -> {'text': str, 'button': QPushButton}.
        """
        lineedits_datas: dict = {}
        for lineedit, button in self.add_page_paths_lineedits_dict.items():
            lineedits_datas[lineedit] = {"text": lineedit.text(), "button": button}
        return lineedits_datas

    def get_add_page_combobox_current_group_name(self) -> str:
        """Return currently selected group name on Add tab."""
        return self.ui.groups_comboBox.currentText()

    def get_version_path_lineedit_text(self) -> str:
        """Return version folder path from Add tab."""
        return self.ui.choose_version_folder_lineEdit.text()

    def get_instruction_path_lineedit_text(self) -> str:
        """Return instruction file path from Add tab."""
        return self.ui.choose_instruction_file_lineEdit.text()

    def set_add_option_page(self, page) -> None:
        """Switch page inside Add tab format stacked widget.

        Args:
            page: Page widget to display.
        """
        self.ui.add_format_stackedWidget.setCurrentWidget(page)

    def set_lineedit_path(self, lineedit, path: str) -> None:
        """Set path into a given line edit on Add tab.

        Args:
            lineedit: Target line edit.
            path: Path string to set.
        """
        lineedit.setText(path)

    def set_add_button_state(self, state: bool, button) -> None:
        """Enable or disable an 'Add' button on Add tab.

        Args:
            state: True to enable, False to disable.
            button: Target button.
        """
        button.setEnabled(state)

    def set_new_group_to_combobox(self, new_group_name: str) -> None:
        """Select newly created group in the groups combobox on Add tab.

        Args:
            new_group_name: Name of the created group.
        """
        self.ui.groups_comboBox.setCurrentText(new_group_name)

    def update_add_page_create_push_button_state(self, state: bool) -> None:
        """Enable or disable 'Create group' button on Add tab."""
        self.ui.create_group_pushButton.setEnabled(state)

    def add_page_comboboxes_state_changed(self, handler) -> None:
        """Bind handler for combobox state changes on Add tab.

        Args:
            handler: Callback for currentIndexChanged signals.
        """
        for combobox in self.add_page_comboboxes:
            combobox.currentIndexChanged.connect(handler)

    def add_page_new_group_name_lineedit_text_changed(self, handler) -> None:
        """Bind handler for 'new group name' text changes on Add tab."""
        self.ui.group_name_lineEdit.textChanged.connect(handler)

    def add_page_create_push_buttons_clicked(self, handler) -> None:
        """Bind handler for 'Create' button click on Add tab."""
        self.ui.create_group_pushButton.clicked.connect(handler)

    def add_page_radio_buttons_state_changed(self, handler) -> None:
        """Bind handler for radio button state changes on Add tab.

        Args:
            handler: Callback accepting 'button' keyword argument.
        """
        for button in self.add_options_dict.keys():
            button.toggled.connect(lambda _, btn=button: handler(button=btn))

    def add_page_paths_lineedits_text_changed(self, handler) -> None:
        """Bind handler for text changes in path line edits on Add tab."""
        for lineedit in self.add_page_paths_lineedits_dict.keys():
            lineedit.textChanged.connect(handler)

    def add_page_choose_folder_path_push_buttons_clicked(self, handler) -> None:
        """Bind handler for 'Choose folder' button click on Add tab.

        Args:
            handler: Callback accepting 'button' keyword argument.
        """
        button = self.ui.choose_version_folder_pushButton
        self.ui.choose_version_folder_pushButton.clicked.connect(
            lambda: handler(button=button),
        )

    def add_page_choose_file_path_push_buttons_clicked(self, handler) -> None:
        """Bind handler for 'Choose file' button click on Add tab.

        Args:
            handler: Callback accepting 'button' keyword argument.
        """
        button = self.ui.choose_instruction_file_pushButton
        self.ui.choose_instruction_file_pushButton.clicked.connect(
            lambda: handler(button=button),
        )

    def add_page_add_push_buttons_clicked(self, handler) -> None:
        """Bind handler for 'Add' buttons click on Add tab.

        Args:
            handler: Callback accepting 'button_type' keyword argument.
        """
        for button, button_type in self.add_page_add_push_buttons_dict.items():
            button.clicked.connect(lambda _, btn_type=button_type: handler(button_type=btn_type))

    def add_page_group_name_combobox_item_changed(self, handler) -> None:
        """Bind handler for group combobox text changes on Add tab."""
        self.ui.groups_comboBox.currentTextChanged.connect(handler)

    # === Delete tab ===

    def get_delete_option_page(self, button):
        """Return page widget for selected Delete option.

        Args:
            button: Radio button that defines delete option.

        Returns:
            Page widget corresponding to the button.
        """
        return self.delete_options_dict.get(button)

    def get_delete_page_comboboxes_datas(self) -> dict:
        """Return current states of comboboxes on Delete tab.

        Returns:
            Dict mapping combobox -> {'text': str, 'what_delete': str}.
        """
        comboboxes_datas: dict = {}
        for combobox in self.delete_page_comboboxes_dict.keys():
            text = combobox.currentText()
            what_delete = self.delete_page_comboboxes_dict.get(combobox)
            comboboxes_datas[combobox] = {"text": text, "what_delete": what_delete}
        return comboboxes_datas

    def get_delete_page_checkboxes_datas(self) -> dict:
        """Return current states of checkboxes on Delete tab.

        Returns:
            Dict mapping checkbox -> {'state': bool, 'what_delete': str}.
        """
        checkboxes_datas: dict = {}
        for checkbox in self.delete_page_checkboxes_dict.keys():
            checkbox_state = checkbox.isChecked()
            what_delete = self.delete_page_checkboxes_dict.get(checkbox)
            checkboxes_datas[checkbox] = {"state": checkbox_state, "what_delete": what_delete}
        return checkboxes_datas

    def get_delete_page_version_combobox_current_text(self) -> str:
        """Return current text of 'group to delete (file)' combobox on Delete tab."""
        return self.ui.choose_group_to_delete_comboBox.currentText()

    def get_delete_page_combobox_text(self, combobox) -> str:
        """Return current text for a given combobox on Delete tab."""
        return combobox.currentText()

    def set_delete_option_page(self, page) -> None:
        """Switch page inside Delete tab stacked widget.

        Args:
            page: Page widget to display.
        """
        self.ui.delete_stackedWidget.setCurrentWidget(page)

    def set_delete_button_state(self, state: bool, button_type: str) -> None:
        """Enable or disable 'Delete' buttons on Delete tab.

        Args:
            state: True to enable, False to disable.
            button_type: Type of delete action ('file' or 'group').
        """
        for button, b_type in self.delete_page_delete_push_buttons_dict.items():
            if b_type == button_type:
                button.setEnabled(state)

    def set_delete_checkboxes_state(self, type: str, state: bool) -> None:
        """Set state of checkboxes on Delete tab for a specific type.

        Args:
            type: Delete type ('file' or 'group').
            state: True to check, False to uncheck.
        """
        for checkbox, checkbox_type in self.delete_page_checkboxes_dict.items():
            if checkbox_type == type:
                checkbox.setChecked(state)

    def delete_page_radio_buttons_state_changed(self, handler) -> None:
        """Bind handler for radio button state changes on Delete tab."""
        for button in self.delete_options_dict.keys():
            button.toggled.connect(lambda _, btn=button: handler(button=btn))

    def delete_page_group_comboboxes_state_changed(self, handler) -> None:
        """Bind handler for combobox state changes on Delete tab.

        Args:
            handler: Callback accepting combobox as positional argument.
        """
        for combobox in self.delete_page_comboboxes_dict.keys():
            combobox.currentIndexChanged.connect(lambda _, cb=combobox: handler(cb))

    def delete_page_checkboxes_state_changed(self, handler) -> None:
        """Bind handler for checkbox state changes on Delete tab."""
        for checkbox in self.delete_page_checkboxes_dict.keys():
            checkbox.stateChanged.connect(handler)

    def delete_page_delete_push_buttons_clicked(self, handler) -> None:
        """Bind handler for 'Delete' button clicks on Delete tab.

        Args:
            handler: Callback accepting 'button_type' keyword argument.
        """
        for button, button_type in self.delete_page_delete_push_buttons_dict.items():
            button.clicked.connect(lambda _, btn_type=button_type: handler(button_type=btn_type))

    # === Progress bar ===

    def set_progress_bar_process_text(self, text: str, set_to_zero: bool = False) -> None:
        """Set process text near the progress bar.

        Args:
            text: Process description.
            set_to_zero: If True, reset label to default text.
        """
        self.ui.process_label.setText(
            f"Процесс: {text}" if not set_to_zero else "Процесс..."
        )

    def set_progress_bar_percents_text(self, percents: str) -> None:
        """Set percent text near the progress bar.

        Args:
            percents: Percentage text, e.g. '50%'.
        """
        self.ui.percent_label.setText(percents)

    def set_progress_bar_value(self, value: int) -> None:
        """Set numeric value of the progress bar.

        Args:
            value: Progress value between 0 and 100.
        """
        self.ui.progressBar.setValue(value)

    # === Notifications ===

    def show_notification(self, msg_type: str, title: str, text: str, button_text: str) -> None:
        """Show standard notification dialog.

        Args:
            msg_type: Notification type ('info', 'warning', 'error').
            title: Window title.
            text: Message text.
            button_text: Button caption.
        """
        Notification.show_notification(
            msg_type=msg_type,
            title=title,
            text=text,
            button_text=button_text,
        )

    def show_action_notification(
        self,
        msg_type: str,
        title: str,
        text: str,
        buttons_texts: list[str],
    ) -> int:
        """Show notification dialog with multiple action buttons.

        Args:
            msg_type: Notification type ('info', 'warning', 'error').
            title: Dialog title.
            text: Message text.
            buttons_texts: Button captions in display order.

        Returns:
            Index of the pressed button (0-based).
        """
        return Notification.show_actions_notification(
            msg_type=msg_type,
            title=title,
            text=text,
            buttons_texts=buttons_texts,
        )