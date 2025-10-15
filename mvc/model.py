import os
import sys
import yaml


class Model:
    def __init__(self):
        self.config_data = self.load_config() # Получаем данные из файла конфигурации
        # Проверяем что данные получены
        if not type(self.config_data) == dict:
            return

    def load_config(self):
        """Функция загружает данные из файла конфигурации"""
        try:
            # Получаем путь к исполняемому файлу и проверяем существование
            exe_file_path = os.path.abspath(sys.argv[0])
            if not os.path.exists(exe_file_path):
                print(f"Произошла ошибка при получении пути к исполняемому файлу. Путь: {exe_file_path}")
                return 1
            
            # Получаем путь к файлу конфигурации и проверяем существование
            config_path = os.path.join(os.path.dirname(exe_file_path), "config.yaml")
            if not os.path.exists(config_path):
                print(f"Произошла ошибка при получении пути к файлу конфигурации. Путь: {config_path}")
                return 1
            
            try:
                # Загружаем данные из файла конфигурации
                with open(config_path, "r", encoding="utf-8") as file:
                    config_data = yaml.safe_load(file)

                return config_data
            except Exception as e:
                print(f"Произошла ошибка при загрузке данных из файла конфигурации: {e}")
                return 1
            
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")