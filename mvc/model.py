import os
import re
import sys
import yaml
import datetime


class Model:
    def __init__(self):
        self.config_data = self.__load_config() # Получаем данные из файла конфигурации
        self.in_group = False # Флаг нахождения таблицы в отображении всех версий группы
        self.search_all_versions = False # Флаг поиска всех версий

    def __load_config(self):
        """Функция загружает данные из файла конфигурации"""
        try:
            # Получаем путь к исполняемому файлу и проверяем существование
            exe_file_path = os.path.abspath(sys.argv[0])
            if not os.path.exists(exe_file_path):
                print(f"Произошла ошибка при получении пути к исполняемому файлу.\nПуть: {exe_file_path}")
                return 1
            
            # Получаем путь к файлу конфигурации и проверяем существование
            config_path = os.path.join(os.path.dirname(exe_file_path), "config.yaml")
            if not os.path.exists(config_path):
                print(f"Произошла ошибка при получении пути к файлу конфигурации.\nПуть: {config_path}")
                return 1
            
            try:
                # Загружаем данные из файла конфигурации
                with open(config_path, "r", encoding="utf-8") as file:
                    config_data = yaml.safe_load(file)

                return config_data
            except Exception as e:
                print(f"Произошла ошибка при загрузке данных из файла конфигурации.\nОшибка: {e}")
                return 1
            
        except Exception as e:
            print(f"Произошла непредвиденная ошибка.\nОшибка: {e}")

    def __parse_date(self, date_str):
        """Функция парсит дату в формате ДД.ММ.ГГГГ"""
        try:
            if date_str:
                return datetime.datetime.strptime(date_str, "%d.%m.%Y")
            else:
                return datetime.datetime.min
        except ValueError:
            return datetime.datetime.min

    def get_groups_names(self):
        """Функция возвращает список имен групп"""
        try:
            groups_names = []

            try:
                path_to_groups = self.config_data.get("versions_path")
            except Exception as e:
                print(f"Произошла ошибка при получении пути к группам из файла конфигурации.\nОшибка: {e}")
                return []
            
            if not os.path.exists(path_to_groups):
                print(f"Произошла ошибка при получении пути к группам.\nПуть: {path_to_groups}")
                return []
            try:
                groups_names = os.listdir(path_to_groups)

                return sorted(groups_names)
            
            except Exception as e:
                print(f"Произошла ошибка при получении списка имен групп.\nОшибка: {e}")
                return []
            
        except Exception as e:
            print(f"Произошла непредвиденная ошибка.\nОшибка: {e}")

    def get_group_versions(self, group_name):
        """Функция возвращает список версий группы"""
        try:
            try:
                path_to_group = os.path.join(self.config_data.get("versions_path"), group_name)
            except Exception as e:
                print(f"Произошла ошибка при получении пути к группе.\nОшибка: {e}")
                return []
            
            if not os.path.exists(path_to_group):
                print(f"Путь к выбранной группе не существует ли недоступен.\nПуть: {path_to_group}")
                return []

            try:
                versions = os.listdir(path_to_group)
                
                dates = []
                for ver in versions:
                    if not ver:
                        continue

                    match = re.search(r"\d{2}\.\d{2}\.\d{4}", ver)
                    dates.append([ver, match.group() if match else None])

                dates.sort(key=lambda x: self.__parse_date(x[1]), reverse=True)

                sorted_versions = [date[0] for date in dates]

                return sorted_versions
            
            except Exception as e:
                print(f"Произошла ошибка при получении списка версий группы.\nОшибка: {e}")
                return []
        except Exception as e:
            print(f"Произошла непредвиденная ошибка.\nОшибка: {e}")
            return []
        
    def get_actual_version(self, versions):
        """Функция возвращает актуальную версию"""    
        try:
            # Получаем даты для каждой верси
            dates = []
            for ver in versions:
                if not ver:
                    continue

                match = re.search(r"\d{2}\.\d{2}\.\d{4}", ver)
                dates.append([ver, match.group() if match else None])

            if not dates:
                print("Нет версий в группе.")
                return None

            # Определяем актуальную
            dates.sort(key=lambda x: self.__parse_date(x[1]), reverse=True)

            return dates[0][0]

        except Exception as e:
            print(f"Произошла непредвиденная ошибка в процессе получения актуальной версии.\nОшибка: {e}")
            return
        
    def search(self, text):
        """Функция выполняет поиск в таблице ПОСЛДЕНИЕ ВЕРСИИ ГРУПП"""
        try:
            if not text:
                return []
            
            # Получаем список групп
            try:
                groups = self.get_groups_names()
                if not groups:
                    return []
            except Exception as e:
                print(f"Произошла ошибка при получении списка групп.\nОшибка: {e}")
                return []
            
            # Получаем список списков, в виде [[группа, актуальная версия]]
            groups_versions = []
            try:
                for group in groups:
                    try:
                        versions = self.get_group_versions(group)

                    except Exception as e:
                        print(f"Произошла ошибка при получении списка версий группы.\nОшибка: {e}")
                        continue
                    
                    if not versions:
                        continue

                    try:
                        actual_version = self.get_actual_version(versions)
                        
                    except Exception as e:
                        print(f"Произошла ошибка при получении актуальной версии группы.\nОшибка: {e}")
                        continue
                    
                    if not actual_version:
                        continue

                    groups_versions.append([group, actual_version])

            except Exception as e:
                print(f"Произошла ошибка в процессе формирования списков групп и версий.\nОшибка: {e}")
                return []
            
            # Выполняем поиск
            try:
                result = []
                for group_version in groups_versions:
                    group_name = group_version[0].lower().strip()
                    version = group_version[1].lower().strip()
                    text = text.lower().strip()

                    if text in group_name or text in version and group_version not in result:
                        result.append(group_version)

                return result
            
            except Exception as e:
                print(f"Произошла ошибка в процессе поиска.\nОшибка: {e}")
                return []
            
        except Exception as e:
            print(f"Произошла непредвиденная ошибка.\nОшибка: {e}")
            return []
        
    def search_all(self, text):
        """Функция выполняет поиск в таблице ПО ВСЕМ ВЕРСИЯМ И ГРУППАМ"""
        try:
            if not text:
                return []
            
            # Получаем спсиок групп
            try:
                groups = self.get_groups_names()

            except Exception as e:
                print(f"Произошла ошибка при получении списка групп.\nОшибка: {e}")
                return []

            if not groups:
                return []
            
            # Получаем словарь, где ключ - группа, значение - список версий
            try:
                groups_versions = {}
                for group in groups:
                    groups_versions[group] = self.get_group_versions(group)

            except Exception as e:
                print(f"Произошла ошибка при получении списка версий групп.\nОшибка: {e}")
                return []
            
            # Выполняем поиск

            try:
                result = []
                for group in groups_versions.keys():
                    for version in groups_versions.get(group):
                        group_text = group.lower().strip()
                        version_text = version.lower().strip()
                        text = text.lower().strip()

                        if text in group_text or text in version_text and [group, version] not in result:
                            result.append([group, version])

                return result

            except Exception as e:
                print(f"Произошла ошибка в процессе поиска.\nОшибка: {e}")
                return []
                                
        except Exception as e:
            print(f"Произошла непредвиденная ошибка.\nОшибка: {e}")
            return []