import os
import re
import sys
import yaml
import shutil
import datetime
import threading
import subprocess

from pathlib import Path
from packaging import version
from cryptography.fernet import Fernet, InvalidToken

from PyQt5.QtCore import QObject, pyqtSignal


class Model(QObject):
    """Main application model.

    Encapsulates business logic, file operations, encryption/decryption,
    version management, and communication with the UI through signals.
    """

    # Signals
    progress_chehged = pyqtSignal(str, int)  # Progress bar state changed (text, value)
    show_notification = pyqtSignal(str, str)  # Show notification (type, text)
    operation_finished = pyqtSignal(str, int)  # Background operation finished (name, status code)

    def __init__(self) -> None:
        """Initialize the model and load configuration."""
        super().__init__()

        # Determine base path for script or frozen executable
        if getattr(sys, "frozen", False):
            self.base_path = Path(sys.executable).parent
        else:
            # Path to project root folder (e.g., File Archive/)
            self.base_path = Path(__file__).parent.parent

        # Configuration and state
        self.config_data = self._load_config()  # Configuration data from config.yaml
        self.in_group: bool = False  # Flag: table currently shows all versions of one group
        self.search_all_versions: bool = False  # Flag: search across all versions
        self.new_group_name = None  # Name of newly created group
        self.is_temp_folder_created = False # Flag: temp folder was created
        self.temp_folder_path = None  # Path to temp folder

        # Encryption-related paths
        self.keyfile_path: str = self.base_path / "_internal" / "keyfile.key"  # Encryption key file
        self.password_file_path: str = self.base_path / "_internal" / "password.key"  # Encrypted password file

        # Progress bar step settings
        self.DOWNLOAD_PROGRESS_BAR_STEP: int = 3
        self.CREATE_NEW_GROUP_PROGRESS_BAR_STEP: int = 3
        self.ADD_PROGRESS_BAR_STEP: int = 2
        self.DELETE_PROGRESS_BAR_STEP: int = 2

    # === Version checking & updating ===

    def check_program_version(self) -> bool | None:
        """Check if a new program version is available on the server.

        Returns:
            True if a newer version is available,
            False if current version is up to date,
            None if a check error occurred.
        """
        program_server_path = Path(self.config_data.get("server_program_path"))

        if not program_server_path.exists():
            return None

        program_server_files = [p.name for p in program_server_path.iterdir()]
        for file_name in program_server_files:
            # Look for file that starts with "config" and ends with ".yaml"
            if file_name.startswith("config") and file_name.endswith(".yaml"):
                try:
                    with open(program_server_path / file_name, "r", encoding="utf-8") as f:
                        config_data = yaml.safe_load(f)

                    local_version = str(self.config_data.get("program_version_number"))
                    program_server_version = str(config_data.get("program_version_number"))

                    if not program_server_version:
                        return None

                    if version.parse(program_server_version) > version.parse(local_version):
                        return True
                    return False

                except IndexError:
                    # If filename format is unexpected, skip it
                    continue

        return None

    def update_program(self) -> None:
        """Run external updater to update the program."""
        updater_path = Path.cwd() / "updater.exe"

        # Ensure updater.exe exists
        if not updater_path.exists():
            self.show_notification.emit(
                "error",
                f"Не найдена программа автоматического обновления: {updater_path}",
            )
            return

        # Start updater.exe
        try:
            os.startfile(updater_path)
        except OSError as e:
            self.show_notification.emit(
                "error",
                f"Не удалось запустить программу обновления: {e}",
            )

    # === Group and version management ===

    def get_groups_names(self) -> list[str]:
        """Return list of group names from versions directory.

        Returns:
            Sorted list of group names, or empty list on error.
        """
        try:
            path_to_groups = Path(self.config_data.get("versions_path"))
            if not path_to_groups.exists():
                self.show_notification.emit(
                    "error",
                    "Путь к группам не существует или недоступен.\n"
                    f"Путь: {path_to_groups}",
                )
                return []

            groups_names = [p.name for p in path_to_groups.iterdir()]
            return sorted(groups_names)

        except FileNotFoundError:
            self.show_notification.emit(
                "error",
                f"Путь к группам не найден: {path_to_groups}",
            )
            return []
        except PermissionError:
            self.show_notification.emit(
                "error",
                f"Отсутствуют права доступа к папке с группами: {path_to_groups}",
            )
            return []
        except Exception as e:
            self.show_notification.emit(
                "error",
                "Произошла непредвиденная ошибка при получении списка групп.\n"
                f"Ошибка: {e}",
            )
            return []

    def get_group_versions(self, group_name: str) -> list[str]:
        """Return list of versions for a specific group.

        Args:
            group_name: Name of the group.

        Returns:
            Sorted list of version names, newest first, or empty list on error.
        """
        try:
            versions_path = Path(self.config_data.get("versions_path"))
            path_to_group = versions_path / group_name
            if not path_to_group.exists():
                self.show_notification.emit(
                    "error",
                    "Путь к выбранной группе не существует или недоступен.\n"
                    f"Путь: {path_to_group}",
                )
                return []

            versions = [p.name for p in path_to_group.iterdir()]

            dates: list[list[str | None]] = []
            for ver in versions:
                if not ver or ver.startswith("~"):
                    continue

                match = re.search(r"\d{2}\.\d{2}\.\d{4}", ver)
                dates.append([ver, match.group() if match else None])

            dates.sort(key=lambda x: self._parse_date(x[1]), reverse=True)

            sorted_versions = [date[0] for date in dates]
            return sorted_versions

        except FileNotFoundError:
            self.show_notification.emit(
                "error",
                f"Путь к группе не найден: {path_to_group}",
            )
            return []
        except PermissionError:
            self.show_notification.emit(
                "error",
                f"Отсутствуют права доступа к папке группы: {path_to_group}",
            )
            return []
        except Exception as e:
            self.show_notification.emit(
                "error",
                "Произошла непредвиденная ошибка при получении версий группы.\n"
                f"Ошибка: {e}",
            )
            return []

    def get_actual_version(self, versions: list[str]) -> str | None:
        """Return the actual (most relevant) version name from a list.

        Logic:
        - Extract dates from version names when possible.
        - Detect whether items are folders or files.
        - Prefer newest by date; if no dates, fall back to name ordering.

        Args:
            versions: List of version names.

        Returns:
            Name of the most relevant version, or None on error/empty list.
        """
        base_path = Path(self.config_data.get("versions_path"))

        def extract_date(name: str) -> datetime.datetime | None:
            match = re.search(r"\d{2}\.\d{2}\.\d{4}", name)
            return self._parse_date(match.group()) if match else None

        try:
            # Filter and parse versions
            items: list[tuple[str, datetime.datetime | None]] = [
                (v, extract_date(v)) for v in versions if v
            ]
            if not items:
                return None

            # Determine what exists in filesystem
            folders = [x for x in items if (base_path / x[0]).is_dir()]
            files = [x for x in items if (base_path / x[0]).is_file()]

            # Fallback: if no FS data, use all items
            target = folders or files or items
            is_folder = bool(folders or (not files and target is items))

            # Check if any dates exist
            has_dates = any(date for _, date in target)

            if has_dates:
                # Sort by date desc, then by name asc
                target.sort(
                    key=lambda x: (
                        x[1] or datetime.datetime.min,
                        x[0].lower(),
                    ),
                    reverse=True,
                )
            else:
                # Without dates, sort by name depending on type
                target.sort(key=lambda x: x[0].lower(), reverse=is_folder)

            return target[0][0]

        except Exception as e:
            self.show_notification.emit(
                "error",
                f"Ошибка при получении актуальной версии: {e}",
            )
            return None

    def get_desktop_path(self) -> Path | None:
        """Return path to Desktop folder, preferring OneDrive if present.

        Returns:
            Path to Desktop folder or None on error.
        """
        try:
            # Try OneDrive desktop with Russian name
            onedrive_desktop_path = Path.home() / "OneDrive" / "Рабочий стол"
            if onedrive_desktop_path.exists():
                return onedrive_desktop_path

            # Try OneDrive desktop with English name
            onedrive_desktop_path = Path.home() / "OneDrive" / "Desktop"
            if onedrive_desktop_path.exists():
                return onedrive_desktop_path

            # Fallback to default Desktop path
            desktop_path = Path.home() / "Desktop"
            return desktop_path

        except Exception as e:
            self.show_notification.emit(
                "error",
                "Произошла ошибка при получении пути к папке Desktop.\n"
                f"Ошибка: {e}",
            )
            return None

    # === Search ===

    def search(self, text: str) -> list[list[str | None]]:
        """Search in last versions table (groups and their actual versions).

        Args:
            text: Search query string.

        Returns:
            List of [group_name, version_name] pairs that match the query.
        """
        try:
            if not text:
                return []

            groups = self.get_groups_names()
            if not groups:
                return []

            groups_versions: list[list[str | None]] = []
            for group in groups:
                versions = self.get_group_versions(group)
                actual_version = self.get_actual_version(versions)
                groups_versions.append([group, actual_version])

            result: list[list[str | None]] = []
            search_text = text.lower().strip()
            for group_version in groups_versions:
                group_name = group_version[0].lower().strip()

                if group_version[1] is None:
                    if search_text in group_name and group_version not in result:
                        result.append(group_version)
                    continue

                version_name = str(group_version[1]).lower().strip()

                if (search_text in group_name or search_text in version_name) and group_version not in result:
                    result.append(group_version)

            return result

        except Exception as e:
            self.show_notification.emit(
                "error",
                "Произошла непредвиденная ошибка при поиске.\n"
                f"Ошибка: {e}",
            )
            return []

    def search_all(self, text: str) -> list[list[str | None]]:
        """Search across all versions and all groups.

        Args:
            text: Search query string.

        Returns:
            List of [group_name, version_name] pairs matching the query.
            If a group has no versions, version_name is None.
        """
        try:
            if not text:
                return []

            groups = self.get_groups_names()
            if not groups:
                return []

            groups_versions: dict[str, list[str]] = {}
            for group in groups:
                groups_versions[group] = self.get_group_versions(group)

            result: list[list[str | None]] = []
            search_text = text.lower().strip()
            for group, versions in groups_versions.items():
                group_text = group.lower().strip()

                if not versions:
                    if search_text in group_text and [group, None] not in result:
                        result.append([group, None])
                else:
                    for version_name in versions:
                        version_text = version_name.lower().strip() if version_name else ""

                        if (search_text in group_text or search_text in version_text) and [
                            group,
                            version_name,
                        ] not in result:
                            result.append([group, version_name])

            return result

        except Exception as e:
            self.show_notification.emit(
                "error",
                "Произошла непредвиденная ошибка при поиске по всем версиям.\n"
                f"Ошибка: {e}",
            )
            return []

    # === Group / file operations ===

    def create_new_group(self, group_name: str) -> int:
        """Create a new group directory.

        Args:
            group_name: Name of the group to create.

        Returns:
            0 on success, 1 on error.
        """
        try:
            if not group_name:
                return 1

            progress_step_size = 100 // self.CREATE_NEW_GROUP_PROGRESS_BAR_STEP
            current_step = 0

            self.progress_chehged.emit("Формируем путь к группе...", current_step)
            group_path = Path(self.config_data.get("versions_path")) / group_name

            current_step += progress_step_size
            self.progress_chehged.emit("Проверяем существование группы...", current_step)
            if group_path.exists():
                self.show_notification.emit(
                    "error",
                    f"Группа с именем {group_name} уже существует.",
                )
                return 1

            current_step += progress_step_size
            self.progress_chehged.emit("Создаём группу...", current_step)
            group_path.mkdir(parents=True, exist_ok=True)

            self.progress_chehged.emit("Группа создана.", 100)
            self.show_notification.emit(
                "info",
                f"Группа {group_name} успешно создана.",
            )
            return 0

        except Exception as e:
            self.show_notification.emit(
                "error",
                "Произошла ошибка при создании новой группы.\n"
                f"Ошибка: {e}",
            )
            return 1

    def delete_group(self, group_name: str) -> int:
        """Delete a group directory and all its contents.

        Args:
            group_name: Name of the group to delete.

        Returns:
            0 on success, 1 on error.
        """
        try:
            if not group_name:
                return 1

            progress_step_size = 100 // self.DELETE_PROGRESS_BAR_STEP
            current_step = 0

            self.progress_chehged.emit("Формируем путь к группе...", current_step)
            group_path = Path(self.config_data.get("versions_path")) / group_name

            if not group_path.exists():
                self.show_notification.emit(
                    "error",
                    f"Группа с именем {group_name} не существует.",
                )
                return 1

            current_step += progress_step_size
            self.progress_chehged.emit("Удаляем группу...", current_step)
            shutil.rmtree(group_path)

            self.progress_chehged.emit("Группа удалена.", 100)
            self.show_notification.emit(
                "info",
                f"Группа {group_name} успешно удалена.",
            )
            return 0

        except Exception as e:
            self.show_notification.emit(
                "error",
                "Произошла ошибка при удалении группы.\n"
                f"Ошибка: {e}",
            )
            return 1

    def delete_file(self, data: list[str]) -> int:
        """Delete a file or directory for a given group and version.

        Args:
            data: List where data[0] is group name and data[1] is file/version name.

        Returns:
            0 on success, 1 on error.
        """
        try:
            if not data or len(data) < 2:
                return 1

            progress_step_size = 100 // self.DELETE_PROGRESS_BAR_STEP
            current_step = 0

            self.progress_chehged.emit("Формируем путь к файлу...", current_step)
            file_path = Path(self.config_data.get("versions_path")) / data[0] / data[1]

            if not file_path.exists():
                self.show_notification.emit(
                    "error",
                    f"Файл не существует. Путь: {file_path}",
                )
                return 1

            current_step += progress_step_size
            self.progress_chehged.emit("Удаляем файл...", current_step)
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir():
                shutil.rmtree(file_path)

            self.progress_chehged.emit("Файл удалён.", 100)
            self.show_notification.emit(
                "info",
                f"Файл {file_path} успешно удалён.",
            )
            return 0

        except Exception as e:
            self.show_notification.emit(
                "error",
                "Произошла ошибка при удалении файла.\n"
                f"Ошибка: {e}",
            )
            return 1

    def add_version(self, version_path: str, group_name: str) -> int:
        """Add a new version (folder) to a group with encryption of its files.

        Args:
            version_path: Source directory of the new version.
            group_name: Name of the target group.

        Returns:
            0 on success, 1 on error.
        """
        try:
            if not version_path or not group_name:
                return 1

            progress_step_size = 100 // self.ADD_PROGRESS_BAR_STEP
            current_step = 0

            self.progress_chehged.emit("Формируем путь к папке новой версии...", current_step)
            src_path = Path(version_path)
            dst_root = Path(self.config_data.get("versions_path")) / group_name / src_path.name

            if dst_root.exists():
                self.show_notification.emit("error", f"Папка {dst_root} уже существует.")
                return 1

            dst_root.mkdir(parents=True, exist_ok=True)

            current_step += progress_step_size
            self.progress_chehged.emit("Копируем и шифруем файлы...", current_step)

            for root, dirs, files in os.walk(version_path):
                root_path = Path(root)
                rel = root_path.relative_to(version_path)
                dst_dir = dst_root / rel
                dst_dir.mkdir(parents=True, exist_ok=True)

                for filename in files:
                    src_file = root_path / filename
                    dst_file = dst_dir / filename
                    self._encrypt_file(str(src_file), str(dst_file))

            self.progress_chehged.emit("Версия добавлена.", 100)
            self.show_notification.emit("info", "Папка успешно скопирована и зашифрована.")
            return 0

        except Exception as e:
            self.show_notification.emit(
                "error",
                "Произошла ошибка при добавлении версии.\n"
                f"Ошибка: {e}",
            )
            return 1

    def add_instruction(self, instruction_path: str, group_name: str) -> int:
        """Add an instruction file to a group with encryption.

        Args:
            instruction_path: Path to the instruction file.
            group_name: Target group name.

        Returns:
            0 on success, 1 on error.
        """
        try:
            if not instruction_path or not group_name:
                return 1
            
            if not instruction_path.endswith((".pdf", ".doc", ".docx")):
                self.show_notification.emit("error", f"Не поддерживаемый тип файла.\nПоддерживаемые типы: .pdf, .doc, .docx")
                return 1

            progress_step_size = 100 // self.ADD_PROGRESS_BAR_STEP
            current_step = 0

            self.progress_chehged.emit("Формируем путь к файлу...", current_step)
            instruction_path_obj = Path(instruction_path)
            dst_path = Path(self.config_data.get("versions_path")) / group_name / instruction_path_obj.name

            if dst_path.exists():
                self.show_notification.emit("error", f"Файл {dst_path} уже существует.")
                return 1

            current_step += progress_step_size
            self.progress_chehged.emit("Копируем и шифруем файл...", current_step)
            self._encrypt_file(src_path=instruction_path, dst_path=str(dst_path))

            self.progress_chehged.emit("Инструкция добавлена.", 100)
            self.show_notification.emit("info", "Инструкция успешно скопирована и зашифрована.")
            return 0

        except Exception as e:
            self.show_notification.emit(
                "error",
                "Произошла ошибка при добавлении инструкции.\n"
                f"Ошибка: {e}",
            )
            return 1

    def download(self, group: str, file: str, save_path: str | Path | None) -> int:
        """Download and decrypt a version folder or instruction file.

        Args:
            group: Group name.
            file: Version or file name.
            save_path: Destination directory for downloaded content.
                If not set, Desktop is used.

        Returns:
            0 on success, 1 on error.
        """
        try:
            file_path = Path(self.config_data.get("versions_path")) / group / file

            if not save_path:
                save_path = self.get_desktop_path()
                if not save_path or not Path(save_path).exists():
                    return 1
            elif not Path(save_path).exists():
                self.show_notification.emit(
                    "error",
                    f"Директория {save_path} не существует.",
                )
                return 1

            if file_path.is_dir():
                progress_step_size = 100 // self.DOWNLOAD_PROGRESS_BAR_STEP
                current_step = 0

                self.progress_chehged.emit("Создаём путь исходной папки...", current_step)
                src_path = file_path
                if not src_path.exists():
                    self.show_notification.emit(
                        "error",
                        f"Директория {src_path} не существует.",
                    )
                    return 1

                current_step += progress_step_size
                self.progress_chehged.emit("Создаём путь сохранения...", current_step)
                dst_path = Path(save_path) / f"{group} {file}"
                if dst_path.exists():
                    self.show_notification.emit(
                        "error",
                        f"Директория {dst_path} уже существует.",
                    )
                    return 1

                dst_path.mkdir(parents=True, exist_ok=True)

                current_step += progress_step_size
                self.progress_chehged.emit("Скачиаваем файлы...", current_step)
                for root, dirs, files in os.walk(src_path):
                    root_path = Path(root)
                    rel = root_path.relative_to(src_path)
                    dst_dir = dst_path / rel
                    dst_dir.mkdir(parents=True, exist_ok=True)

                    for filename in files:
                        if not filename.endswith(".enc"):
                            continue

                        src_file = root_path / filename
                        dst_file = dst_dir / filename[:-4]
                        self._decryprt_file(str(src_file), str(dst_file))

            else:
                progress_step_size = 100 // self.DOWNLOAD_PROGRESS_BAR_STEP
                current_step = 0

                self.progress_chehged.emit(f"Скачивание файла {file}...", current_step)
                src_path = Path(self.config_data.get("versions_path")) / group / f"{file}.enc"

                current_step += progress_step_size
                self.progress_chehged.emit(f"Скачивание файла {file}...", current_step)
                dst_path = Path(save_path) / file

                current_step += progress_step_size
                self.progress_chehged.emit(f"Скачивание файла {file}...", current_step)
                self._decryprt_file(str(src_path), str(dst_path))

            self.progress_chehged.emit("Скачивание завершено.", 100)
            self.show_notification.emit("info", "Файл успешно скачан.")
            return 0

        except Exception as e:
            self.show_notification.emit(
                "error",
                "Произошла ошибка при скачивании файла.\n"
                f"Ошибка: {e}",
            )
            return 1
        
    def open_file(self, group: str, file: str) -> None:
        """"""
        try:
            file_path = Path(self.config_data.get("versions_path")) / group / f"{file}.enc"

            if not file_path.exists():
                self.show_notification.emit("error", "Выбранный файл не существует на сервере.")
                return

            # Create a temp folder
            temp_folder_path = self._create_temp_folder() / file_path.name
            
            # Decrypt and download the instruction file to the temp folder
            shutil.copy(file_path, temp_folder_path)
            self._decryprt_file(temp_folder_path, temp_folder_path.with_suffix(""))
            
            # Open file
            subprocess.Popen(['start', '', temp_folder_path.with_suffix("")], shell=True)
        
        except Exception as e:
            self.show_notification.emit("error", f"Произошла ошибка при открытии файла.\nОшибка: {e}")
            return
        
    def delete_temp_folder(self, path: Path) -> None:
        """"""
        try:
            shutil.rmtree(path)

        except Exception as e:
            print("Ошибка: ", e)

    # === Password management ===

    def get_decrypted_password(self) -> str | None:
        """Get and decrypt password from password.key.

        Returns:
            Decrypted password string or None if not available.
        """
        if not self.password_file_path.exists():
            return None

        try:
            with open(self.password_file_path, "r", encoding="utf-8") as f:
                encrypted_password = f.read().strip()

            if not encrypted_password:
                return None

            return self._decrypt_string(encrypted_password)
        except Exception:
            return None

    def set_password(self, new_password: str) -> int:
        """Set new password in password.key using encryption.

        Args:
            new_password: Plain text password to store.

        Returns:
            0 on success, 1 on error.
        """
        try:
            encrypted_password = self._encrypt_string(new_password)

            with open(self.password_file_path, "w", encoding="utf-8") as f:
                f.write(encrypted_password)

            return 0

        except Exception as e:
            self.show_notification.emit(
                "error",
                "Произошла ошибка при смене пароля.\n"
                f"Ошибка: {e}",
            )
            return 1

    # === Threaded operations ===

    def download_in_thread(self, group: str, file: str, save_path: str | Path | None) -> None:
        """Run download operation in a separate thread."""
        thread = threading.Thread(target=self._wrapper_download, args=(group, file, save_path))
        thread.daemon = True
        thread.start()

    def create_group_in_thread(self, group_name: str) -> None:
        """Run create_new_group operation in a separate thread."""
        thread = threading.Thread(target=self._wrapper_create_new_group, args=(group_name,))
        thread.daemon = True
        thread.start()

    def add_version_in_thread(self, version_path: str, group_name: str) -> None:
        """Run add_version operation in a separate thread."""
        thread = threading.Thread(target=self._wrapper_add_version, args=(version_path, group_name))
        thread.daemon = True
        thread.start()

    def add_instruction_in_thread(self, instruction_path: str, group_name: str) -> None:
        """Run add_instruction operation in a separate thread."""
        thread = threading.Thread(target=self._wrapper_add_instruction, args=(instruction_path, group_name))
        thread.daemon = True
        thread.start()

    def delete_group_in_thread(self, group_name: str) -> None:
        """Run delete_group operation in a separate thread."""
        thread = threading.Thread(target=self._wrapper_delete_group, args=(group_name,))
        thread.daemon = True
        thread.start()

    def delete_file_in_thread(self, data: list[str]) -> None:
        """Run delete_file operation in a separate thread."""
        thread = threading.Thread(target=self._wrapper_delete_file, args=(data,))
        thread.daemon = True
        thread.start()

    # === Internal helpers ===

    def _load_config(self) -> dict | None:
        """Load configuration data from config.yaml in the base path.

        Returns:
            Parsed configuration dictionary or None if loading failed.
        """
        try:
            config_path = self.base_path / "config.yaml"
            if not config_path.exists():
                self.show_notification.emit(
                    "error",
                    f"Файл конфигурации не найден.\nПуть: {config_path}",
                )
                return None

            with open(config_path, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)

                # Remove password key if still present (no longer used)
                if config and "password" in config:
                    del config["password"]

                return config

        except Exception as e:
            self.show_notification.emit(
                "error",
                "Произошла непредвиденная ошибка при чтении файла конфигурации.\n"
                f"Ошибка: {e}",
            )
            return None

    def _parse_date(self, date_str: str | None) -> datetime.datetime:
        """Parse date string in DD.MM.YYYY format into datetime.

        Args:
            date_str: Date string in format DD.MM.YYYY.

        Returns:
            Parsed datetime or datetime.min on error/empty input.
        """
        try:
            if date_str:
                return datetime.datetime.strptime(date_str, "%d.%m.%Y")
            return datetime.datetime.min
        except ValueError:
            return datetime.datetime.min

    def _encrypt_file(self, src_path: str, dst_path: str) -> None:
        """Encrypt a single file and save encrypted copy with .enc extension.

        Args:
            src_path: Path to the source file.
            dst_path: Path to the destination file without .enc extension.
        """
        # Add .enc extension to the destination file
        dst_path_obj = Path(str(dst_path) + ".enc")

        # Read encryption key
        with open(self.keyfile_path, "rb") as kf:
            key = kf.read().strip()

        fernet = Fernet(key)

        # Read source data
        with open(src_path, "rb") as f:
            data = f.read()

        # Encrypt data
        encrypted_data = fernet.encrypt(data)

        # Ensure destination directory exists
        dst_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Write encrypted file
        with open(dst_path_obj, "wb") as f:
            f.write(encrypted_data)

    def _decryprt_file(self, src_path: str, dst_path: str) -> None:
        """Decrypt a single file and save decrypted copy to the given path.

        Args:
            src_path: Path to encrypted .enc file.
            dst_path: Path to the destination decrypted file.
        """
        try:
            with open(self.keyfile_path, "rb") as kf:
                key = kf.read().strip()

            fernet = Fernet(key)

            with open(src_path, "rb") as f:
                encrypted_data = f.read()

            decrypted_data = fernet.decrypt(encrypted_data)

            Path(dst_path).parent.mkdir(parents=True, exist_ok=True)

            with open(dst_path, "wb") as f:
                f.write(decrypted_data)

        except FileNotFoundError:
            self.show_notification.emit(
                "error",
                "Ошибка: Не найден файл ключа или исходный файл для дешифрования.",
            )
            return
        except InvalidToken:
            self.show_notification.emit(
                "error",
                "Ошибка дешифрования: ключ недействителен или данные повреждены.",
            )
            return
        except Exception as e:
            self.show_notification.emit(
                "error",
                "Произошла непредвиденная ошибка при дешифровании файла.\n"
                f"Ошибка: {e}",
            )
            return

    def _get_fernet(self) -> Fernet:
        """Read encryption key from keyfile and return Fernet instance.

        Returns:
            Configured Fernet instance.
        """
        with open(self.keyfile_path, "rb") as kf:
            key = kf.read().strip()
        return Fernet(key)

    def _encrypt_string(self, plaintext: str) -> str:
        """Encrypt plain text string and return base64-encoded value.

        Args:
            plaintext: Plain text string to encrypt.

        Returns:
            Base64-encoded encrypted string or empty string for empty input.
        """
        if not plaintext:
            return ""

        fernet = self._get_fernet()
        encrypted_bytes = fernet.encrypt(plaintext.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")

    def _decrypt_string(self, encrypted_text: str) -> str:
        """Decrypt string, with backward compatibility for plain text.

        Args:
            encrypted_text: Base64-encoded encrypted string or plain text.

        Returns:
            Decrypted string, original text if token invalid, or empty string on error.
        """
        if not encrypted_text:
            return ""

        try:
            fernet = self._get_fernet()
            decrypted_bytes = fernet.decrypt(encrypted_text.encode("utf-8"))
            return decrypted_bytes.decode("utf-8")
        except InvalidToken:
            # Backward compatibility: return original text if not encrypted
            return encrypted_text
        except Exception:
            return ""
        
    def _create_temp_folder(self) -> Path:
        """"""
        user_profile = Path.home()
        desktop_path = user_profile / "AppData" / "Local" / "Temp" / "filearchive_temp"

        if desktop_path.exists():
            return desktop_path
        
        os.mkdir(path=desktop_path)

        self.is_temp_folder_created = True
        self.temp_folder_path = desktop_path

        return desktop_path

    # === Thread wrapper helpers ===

    def _wrapper_download(self, group: str, file: str, save_path: str | Path | None) -> None:
        """Wrapper for download() to emit operation_finished signal."""
        status_code = self.download(group, file, save_path)
        self.operation_finished.emit("download", status_code)

    def _wrapper_create_new_group(self, group_name: str) -> None:
        """Wrapper for create_new_group() to emit operation_finished signal."""
        status_code = self.create_new_group(group_name)
        self.operation_finished.emit("create_group", status_code)

    def _wrapper_add_version(self, version_path: str, group_name: str) -> None:
        """Wrapper for add_version() to emit operation_finished signal."""
        status_code = self.add_version(version_path, group_name)
        self.operation_finished.emit("add_version", status_code)

    def _wrapper_add_instruction(self, instruction_path: str, group_name: str) -> None:
        """Wrapper for add_instruction() to emit operation_finished signal."""
        status_code = self.add_instruction(instruction_path, group_name)
        self.operation_finished.emit("add_instruction", status_code)

    def _wrapper_delete_group(self, group_name: str) -> None:
        """Wrapper for delete_group() to emit operation_finished signal."""
        status_code = self.delete_group(group_name)
        self.operation_finished.emit("delete_group", status_code)

    def _wrapper_delete_file(self, data: list[str]) -> None:
        """Wrapper for delete_file() to emit operation_finished signal."""
        status_code = self.delete_file(data)
        self.operation_finished.emit("delete_file", status_code)