import re
import sys

from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QObject, QEvent


class Controller(QObject):
    """The main controller of the application.

    Responsible for communication between the model and the view, signal processing,
    updating the interface and running background operations.
    """

    def __init__(self, model: object, view: object) -> None:
        """Initializes the controller and adjusts the initial state of the application.

        Args:
            model: An instance of a model that implements business logic.
            view: An instance of the view (UI) responsible for displaying.
        """
        super().__init__()

        self.model = model
        self.view = view

        # Checking the current version of the program at startup
        self.__check_program_version()

        # Flag to prevent recursive version updates
        self._is_updating_versions = False

        # Initial interface configuration
        self.update_layer_one_table_data()  # Uploading data to the group table
        # Uploading groups to comboboxes
        self.view.set_groups_comboboxes_data(self.model.get_groups_names())
        self.update_version_combobox_data()  # Uploading versions to comboboxes

        # Setting the event filter for the search field
        self.view.ui.search_lineEdit.installEventFilter(self)

        # === Handlers ===
        # Buttons
        self.view.tab_button_clicked(self.on_tab_button_clicked)
        self.view.download_page_choose_push_button_clicked(self.on_download_page_choose_folder_path_button_clicked)
        self.view.add_page_choose_folder_path_push_buttons_clicked(self.on_add_page_choose_folder_path_button_clicked)
        self.view.add_page_choose_file_path_push_buttons_clicked(self.on_add_page_choose_file_path_button_clicked)
        self.view.add_page_create_push_buttons_clicked(self.on_add_page_create_push_button_clicked)
        self.view.add_page_add_push_buttons_clicked(self.on_add_page_add_push_button_clicked)
        self.view.delete_page_delete_push_buttons_clicked(self.on_delete_page_delete_push_button_clicked)
        self.view.download_page_back_push_button_clicked(self.on_download_page_back_push_button_clicked)
        self.view.download_page_download_push_buttons_clicked(self.on_download_page_download_push_button_clicked)
        self.view.download_page_open_push_button_clicked(self.on_download_page_open_push_button_clicked)

        # Radio-Buttons
        self.view.add_page_radio_buttons_state_changed(self.on_add_options_button_clicked)
        self.view.delete_page_radio_buttons_state_changed(self.on_delete_options_button_clicked)

        # Input Fields
        self.view.add_page_new_group_name_lineedit_text_changed(self.on_add_page_new_group_name_lineedit_text_changed)
        self.view.add_page_paths_lineedits_text_changed(self.on_add_page_paths_lineedits_text_changed)
        self.view.download_page_search_lineedit_text_changed(self.on_download_page_search_lineedit_text_changed)

        # Comboboxes
        self.view.add_page_group_name_combobox_item_changed(self.on_add_page_group_name_combobox_item_changed)
        self.view.delete_page_group_comboboxes_state_changed(self.on_delete_page_group_comboboxes_state_changed)

        # Checkboxes
        self.view.delete_page_checkboxes_state_changed(self.on_delete_page_checkboxes_state_changed)
        self.view.download_page_search_all_versions_checkbox_state_changed(
            self.on_download_page_search_all_versions_checkbox_state_changed
        )

        # Table
        self.view.download_page_table_row_clicked(self.on_download_page_table_row_clicked)
        self.view.download_page_table_row_double_clicked(self.on_download_page_table_row_double_clicked)

        # Model Signals
        self.model.progress_chehged.connect(self.on_progress_bar_changed)
        self.model.show_notification.connect(self.on_show_notification)
        self.model.operation_finished.connect(self.on_operation_finished)

    # === Main functions ===

    def update_layer_one_table_data(self, data: list = None) -> None:
        """Updates the data in the group table on the first tab.

        Args:
            data: Ready-made data for the table. If not transmitted, the data
                They are formed based on the list of groups and their current versions.
        """
        if data is None:
            groups_names = self.model.get_groups_names()  # Getting a list of all the groups

            layer_one_data = []
            for group_name in groups_names:
                versions = self.model.get_group_versions(group_name)  # All versions of the group
                actual_version = self.model.get_actual_version(versions)  # Current version
                layer_one_data.append([group_name, actual_version])  # Row for the table

            # Filling in the group table
            self.view.set_layer_one_table_data(layer_one_data)
        else:
            self.view.set_layer_one_table_data(data)

    def update_version_combobox_data(self) -> None:
        """Updates the list of versions in the combo box on the deletions tab."""
        if self._is_updating_versions:
            return

        self._is_updating_versions = True
        try:
            group_name = self.view.get_delete_page_version_combobox_current_text()
            versions = self.model.get_group_versions(group_name)
            self.view.set_version_combobox_data(versions)
        finally:
            self._is_updating_versions = False

    # === Icons and Events filter ===

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Processes events for the search field and changes the icon depending on the focus.

        Args:
            obj: The object for which the event was triggered.
            event: A Qt event.

        Returns:
            True if the event has been processed, otherwise False.
        """
        if obj is self.view.ui.search_lineEdit:
            if event.type() == QEvent.FocusIn:
                self.view.set_search_icon_state(state=True)
            elif event.type() == QEvent.FocusOut:
                self.view.set_search_icon_state(state=False)

        return super().eventFilter(obj, event)

    # === Navigation Bar ===

    def on_tab_button_clicked(self, button: object) -> None:
        """ Handles clicking on the tab selection button.

        Args:
            button: The tab button that the user clicked on.
        """
        self.view.set_tab_page(button)

    # === Download tab ===

    def update_back_push_button_state(self, state: bool = None) -> None:
        """Updates the status of the Back button on the Download tab.

        Args:
            state: The explicit state of the button. If not specified, it is calculated
                based on the model.in_group flag.
        """
        if state is None:
            self.view.set_back_button_state(state=self.model.in_group)
        else:
            self.view.set_back_button_state(state=state)

    def update_download_button_state(self) -> None:
        """Updates the status of the "Download" button on the "Download" tab."""
        label_text = self.view.get_choosen_label_text().strip()
        if label_text != "Выбрано изделие:" and not label_text.endswith("Версия:"):
            self.view.set_download_button_state(state=True)
        else:
            self.view.set_download_button_state(state=False)

    def update_open_button_state(self) -> None:
        """"""
        label_text = self.view.get_choosen_label_text().strip()
        if label_text.split("Версия: ")[1].endswith((".pdf", ".doc", ".docx")):
            self.view.set_open_button_visible_state(True)
        else:
            self.view.set_open_button_visible_state(False)

    def on_download_page_search_lineedit_text_changed(self) -> None:
        """Handles changing the text in the search bar on the Download tab."""
        search_text = self.view.get_search_lineedit_text()
        if search_text:
            if not self.model.search_all_versions:
                # Regular search by groups and current versions
                search_results = self.model.search(text=search_text)
                self.update_layer_one_table_data(data=search_results)
            else:
                # Search through all files of all versions
                search_results = self.model.search_all(text=search_text)
                self.update_layer_one_table_data(data=search_results)
        else:
            # If the search bar is empty, we show all the groups
            self.update_layer_one_table_data()

    def on_download_page_search_all_versions_checkbox_state_changed(self, state: int) -> None:
        """Handles changing the state of the "Search for all versions" checkbox.

        Args:
            state: The status of the checkbox (Qt state).
        """
        self.model.search_all_versions = state

        # We simulate changing the text in the search bar to update the table
        self.on_download_page_search_lineedit_text_changed()

    def on_download_page_choose_folder_path_button_clicked(self) -> None:
        """Processes the selection of a folder to save files on the "Download" tab."""
        folder_path = QFileDialog.getExistingDirectory()
        self.view.set_download_save_path(folder_path)

    def on_download_page_table_row_clicked(self, row: int) -> None:
        """ Handles a single click on a table row on the Download tab.

        Args:
            row: The index of the selected row in the table.
        """
        row_data = self.view.get_table_row_data(row=row)
        self.view.set_choosen_label_text(data=row_data, in_group_flag=self.model.in_group)
        self.update_download_button_state()
        self.update_open_button_state()

    def on_download_page_table_row_double_clicked(self, row: int) -> None:
        """Handles a double click on a row of the table on the "Download" tab.

        Double-clicking on a group opens a list of versions of that group.
        Args:
            row: The index of the selected row in the table.
        """
        if not self.model.in_group:
            row_data = self.view.get_table_row_data(row=row)

            # Get the versions of the group and set the data in the table
            layer_two_data = self.model.get_group_versions(group_name=row_data[0])
            self.view.set_layer_two_table_data(layer_two_data)

            # Setting the flag for being inside the group
            self.model.in_group = True

            # Updating the status of the Back button
            self.update_back_push_button_state()

    def on_download_page_back_push_button_clicked(self) -> None:
        """Handles clicking on the "Back" button on the "Download" tab."""
        # Going back to the list of groups
        self.model.in_group = False
        self.update_layer_one_table_data()
        self.update_back_push_button_state(state=False)
        self.view.set_choosen_label_text(data=None, in_group_flag=None)
        self.update_download_button_state()

    def on_download_page_download_push_button_clicked(self) -> None:
        """Handles clicking on the "Download" button on the "Download" tab.

        Parses the selected text, determines the group, file, and path.
        saves, then initiates the download.
        """
        text = self.view.get_choosen_label_text()

        group_match = re.search(
            r"Выбран[ао]\s+(?:изделие|группа)\s*:\s*(.*?)\s*(?:,|\n)\s*Версия",
            text,
            re.IGNORECASE
        )

        file_match = re.search(
            r"Версия\s*:\s*(.*)$",
            text,
            re.IGNORECASE
        )

        if not group_match or not file_match:
            return

        group = group_match.group(1)
        file = file_match.group(1)
        save_path = self.view.get_download_save_path()

        # Disabling the page for the download time
        self.view.update_page_enabled_state(page="download", state=False)

        # Start the download in a separate stream
        self.model.download_in_thread(group=group, file=file, save_path=save_path)

    def on_download_page_open_push_button_clicked(self) -> None:
        """"""
        text = self.view.get_choosen_label_text()

        group_match = re.search(
            r"Выбран[ао]\s+(?:изделие|группа)\s*:\s*(.*?)\s*(?:,|\n)\s*Версия",
            text,
            re.IGNORECASE
        )

        file_match = re.search(
            r"Версия\s*:\s*(.*)$",
            text,
            re.IGNORECASE
        )

        if not group_match or not file_match:
            return

        group = group_match.group(1)
        file = file_match.group(1)

        # Open the file
        self.model.open_file(group=group, file=file)

    # === Add tab ===

    def update_add_push_buttons_state(self) -> None:
        """Updates the status of the "Add" buttons on the "Add" tab."""
        group_name = self.view.get_add_page_combobox_current_group_name()
        lineedits_texts = self.view.get_add_page_paths_lineedits_datas()

        for value in lineedits_texts.values():
            text = value.get("text")
            button = value.get("button")
            self.view.set_add_button_state(state=bool(group_name and text), button=button)

    def on_add_options_button_clicked(self, button: object) -> None:
        """Handles the selection of the add option on the "Add" tab.

        Args:
            button: The radio button that is pressed is the option to add it.
        """
        page = self.view.get_add_option_page(button)
        self.view.set_add_option_page(page)

    def on_add_page_choose_folder_path_button_clicked(self, button: object) -> None:
        """Handles the folder selection on the "Add" tab.

        Args:
            button: The button for which the folder path is selected.
        """
        lineedit = self.view.get_path_lineedit(button=button)
        folder_path = QFileDialog.getExistingDirectory()
        self.view.set_lineedit_path(lineedit=lineedit, path=folder_path)

    def on_add_page_choose_file_path_button_clicked(self, button: object) -> None:
        """Processes the file selection on the "Add" tab.

        Args:
            button: The button for which the file path is selected.
        """
        lineedit = self.view.get_path_lineedit(button=button)
        path, _ = QFileDialog.getOpenFileName(
            None,
            "Выбрать файл",
            "",
            "Докумен Word (*.pdf *.doc *.docx);",
        )
        self.view.set_lineedit_path(lineedit=lineedit, path=path)

    def on_add_page_create_push_button_clicked(self) -> None:
        """Handles the creation of a new group on the "Add" tab."""
        new_group_name = self.view.get_new_group_name_lineedit_text()
        self.model.new_group_name = new_group_name

        # Disabling the page while the group is being created
        self.view.update_page_enabled_state(page="add", state=False)

        # Creating a group in a separate thread
        self.model.create_group_in_thread(group_name=new_group_name)

    def on_add_page_new_group_name_lineedit_text_changed(self, text: str) -> None:
        """Handles changing the name of a new group on the "Add" tab.

        Args:
            text: The current text in the group name input field.
        """
        group_name = self.view.get_new_group_name_lineedit_text()
        self.view.update_add_page_create_push_button_state(state=bool(group_name))

    def on_add_page_paths_lineedits_text_changed(self) -> None:
        """Handles changing the text in the path fields on the "Add" tab."""
        self.update_add_push_buttons_state()

    def on_add_page_group_name_combobox_item_changed(self) -> None:
        """Handles changing the selected group in the combo box on the "Add" tab."""
        self.update_add_push_buttons_state()

    def on_add_page_add_push_button_clicked(self, button_type: str) -> None:
        """Handles clicking on the "Add" button on the "Add" tab.

        Args:
            button_type: The type of addition: 'version' or 'instruction'.
        """
        group_name = self.view.get_add_page_combobox_current_group_name()

        if button_type == "version":
            # Adding a version
            version_path = self.view.get_version_path_lineedit_text()
            self.view.update_page_enabled_state(page="add", state=False)
            self.model.add_version_in_thread(version_path=version_path, 
                                             group_name=group_name)

        elif button_type == "instruction":
            # Adding instructions
            instruction_path = self.view.get_instruction_path_lineedit_text()
            self.view.update_page_enabled_state(page="add", state=False)
            self.model.add_instruction_in_thread(instruction_path=instruction_path, 
                                                 group_name=group_name)

    # === Delete tab ===

    def update_delete_push_buttons_state(self) -> None:
        """Updates the status of the "Delete" buttons on the "Delete" tab."""
        comboboxes_data = self.view.get_delete_page_comboboxes_datas()
        checkboxes_data = self.view.get_delete_page_checkboxes_datas()

        for checkbox_data in checkboxes_data.values():
            checkbox_state = checkbox_data.get("state")
            what_delete = checkbox_data.get("what_delete")

            button_state = False
            if checkbox_state:
                relevant_comboboxes = [
                    cb for cb in comboboxes_data.values() if cb.get("what_delete") == what_delete
                ]
                button_state = all(cb.get("text") for cb in relevant_comboboxes)

            self.view.set_delete_button_state(state=button_state, button_type=what_delete)

    def on_delete_options_button_clicked(self, button: object) -> None:
        """Handles changing combo box values on the "Delete" tab.

        Args:
            combobox: A combo box whose value has changed.
        """
        page = self.view.get_delete_option_page(button)
        self.view.set_delete_option_page(page)

    def on_delete_page_group_comboboxes_state_changed(self, combobox: object) -> None:
        """Обрабатывает изменение значений комбобоксов на вкладке «Удалить».

        Args:
            combobox: Комбобокс, значение которого изменилось.
        """
        # We update the list of versions only when changing the combo box of the group
        if combobox is self.view.ui.choose_group_to_delete_comboBox:
            self.update_version_combobox_data()

        self.update_delete_push_buttons_state()

    def on_delete_page_checkboxes_state_changed(self) -> None:
        """Handles changing the status of the checkboxes on the "Delete" tab."""
        self.update_delete_push_buttons_state()

    def on_delete_page_delete_push_button_clicked(self, button_type: str) -> None:
        """Handles clicking on the delete buttons on the "Delete" tab.

        Args:
            button_type: Deletion type: 'file' or 'group'.
        """
        if not button_type:
            return

        comboboxes_datas = self.view.get_delete_page_comboboxes_datas()

        if button_type == "file":
            file_page_data = []

            # We are looking for combo boxes for the file deletion page
            for combobox in comboboxes_datas.keys():
                if comboboxes_datas[combobox].get("what_delete") == "file":
                    # Getting selected items from comboboxes
                    file_page_data.append(self.view.get_delete_page_combobox_text(combobox=combobox))

            if file_page_data:
                # Disabling the page while deleting files
                self.view.update_page_enabled_state(page="delete", state=False)
                self.model.delete_file_in_thread(data=file_page_data)

        elif button_type == "group":
            group_name = None

            # We are looking for a combo box for the group deletion page
            for combobox in comboboxes_datas.keys():
                if comboboxes_datas[combobox].get("what_delete") == "group":
                    # Getting the selected item from the combo box
                    group_name = self.view.get_delete_page_combobox_text(combobox=combobox)
                    break

            if group_name:
                # Disabling the page while deleting the group
                self.view.update_page_enabled_state(page="delete", state=False)
                self.model.delete_group_in_thread(group_name=group_name)

    # === Signals and completion of operations ===

    def on_progress_bar_changed(self, process_text: str, value: int) -> None:
        """Handles changing the status of the progress bar.

        Args:
            process_text: The text of the operation status.
            value: The current value of the progress bar (0-100).
        """
        self.view.set_progress_bar_process_text(text=process_text)
        self.view.set_progress_bar_percents_text(percents=f"{value}%")
        self.view.set_progress_bar_value(value=value)

    def on_show_notification(self, msg_type: str, text: str) -> None:
        """Processes the display of a standard notification.

        Args:
            msg_type: Notification type: 'info', 'warning' or 'error'.
            text: The text of the message.
        """
        if msg_type == "info":
            self.view.show_notification(msg_type=msg_type, 
            title="Информация", 
            text=text, 
            button_text="Ок")
            
        elif msg_type == "warning":
            self.view.show_notification(msg_type=msg_type, 
            title="Предупреждение", 
            text=text, 
            button_text="Ок")
            
        elif msg_type == "error":
            self.view.show_notification(msg_type=msg_type, 
            title="Ошибка", 
            text=text, 
            button_text="Закрыть")

        # Reset the progress bar after the message
        self.view.set_progress_bar_process_text(text="", set_to_zero=True)
        self.view.set_progress_bar_percents_text(percents="0%")
        self.view.set_progress_bar_value(value=0)

    def on_show_action_notification(self, msg_type: str, title: str, text: str, buttons_texts: list[str]) -> int:
        """Handles the display of notifications with action buttons.

        Args:
            msg_type: Notification type: 'info', 'warning' or 'error'.
            title: The title of the notification window.
            text: The main text of the message.
            buttons_texts: A list of captions for buttons.

        Returns:
            The index of the pressed button (0-based).
        """
        notification = self.view.show_action_notification(
            msg_type=msg_type,
            title=title,
            text=text,
            buttons_texts=buttons_texts,
        )
        return notification

    def on_operation_finished(self, operation_name: str, status_code: int) -> None:
        """Handles the completion of a background operation.

        Args:
            operation_name: Operation name (create_group, add_version, delete_file, etc.).
            status_code: Operation completion code (0 — success).
        """
        # If the operation failed, we don't update anything
        if status_code != 0:
            return

        if operation_name == "create_group":
            self.update_layer_one_table_data()
            self.view.set_groups_comboboxes_data(self.model.get_groups_names())
            self.view.set_new_group_to_combobox(new_group_name=self.model.new_group_name)
            self.update_version_combobox_data()

        elif operation_name in ["add_version", "add_instruction"]:
            self.update_layer_one_table_data()
            self.view.set_groups_comboboxes_data(self.model.get_groups_names())
            self.update_version_combobox_data()

        elif operation_name == "delete_file":
            self.update_layer_one_table_data()
            self.view.set_groups_comboboxes_data(self.model.get_groups_names())
            self.update_version_combobox_data()
            self.view.set_delete_checkboxes_state(type="file", state=False)
            self.view.set_choosen_label_text(data=None, in_group_flag=None)

        elif operation_name == "delete_group":
            self.update_layer_one_table_data()
            self.view.set_groups_comboboxes_data(self.model.get_groups_names())
            self.update_version_combobox_data()
            self.view.set_delete_checkboxes_state(type="group", state=False)
            self.view.set_choosen_label_text(data=None, in_group_flag=None)

        # After a successful operation, we turn on all the pages again.
        self.view.update_page_enabled_state(state=True, check_all=True)

    def __check_program_version(self) -> None:
        """Checks the relevance of the program version and, if necessary, launches an update.

        If the version is outdated, the user is prompted to update the program.
        If the verification fails or the update fails, the application is terminated.
        """
        # Checking the program version
        is_version = self.model.check_program_version()

        # If an error occurred during the version check
        if is_version is None:
            self.on_show_notification(
                msg_type="error",
                text=(
                    "Во время проверки версии произошла ошибка!\n"
                    "Ошибка связана с путём к файлу конфигурации."
                ),
            )
            sys.exit()

        # If the version does not match (an update is required)
        if is_version:
            action = self.on_show_action_notification(
                msg_type="warning",
                title="Обновление",
                text=(
                    "Обнаружена новая версия программы.\n"
                    "Продолжить работу без обновления невозможно.\n"
                    "Желаете обновить?"
                ),
                buttons_texts=["Обновить", "Закрыть"],
            )

            if action == 1:
                self.model.update_program()
                sys.exit()  # Closing the main application after launching the update
            else:
                sys.exit()