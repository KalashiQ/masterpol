import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from database.db_manager import DatabaseManager
from ui.auth_screen import AuthScreen
from ui.main_window import MainWindow


def get_resource_path(relative_path):
    """Получает абсолютный путь к ресурсу, работает для dev и для PyInstaller"""
    try:
        # PyInstaller создает временную папку и сохраняет путь в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_data_path():
    """Получает путь для сохранения данных приложения"""
    if getattr(sys, 'frozen', False):
        # Если запущено как exe файл
        # Используем папку рядом с exe файлом для базы данных
        exe_dir = os.path.dirname(sys.executable)
        data_dir = os.path.join(exe_dir, 'data')
    else:
        # Если запущено как Python скрипт
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database')

    # Создаем папку, если её нет
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    return data_dir


class MasterPolApp:
    def __init__(self):
        # Инициализируем базу данных с правильным путем
        self.init_database()

        self.auth_screen = None
        self.main_window = None
        self.current_user = None
        self.current_user_type = None

        # Показываем экран авторизации
        self.show_auth_screen()

    def init_database(self):
        """Инициализирует базу данных с правильным путем для exe"""
        try:
            # Получаем путь для базы данных
            data_path = get_data_path()
            db_path = os.path.join(data_path, 'masterpol.db')

            print(f"Путь к базе данных: {db_path}")

            # Инициализируем менеджер базы данных с правильным путем
            db_manager = DatabaseManager(db_path)
            db_manager.fix_partner_table_structure()
            db_manager.add_partner_id_to_products_table()

        except Exception as e:
            print(f"Ошибка инициализации базы данных: {e}")

    def show_auth_screen(self):
        """Показывает экран авторизации"""
        self.auth_screen = AuthScreen()
        self.auth_screen.authentication_successful.connect(self.on_authentication_success)
        self.auth_screen.setWindowTitle("Мастер-пол - Авторизация")
        self.auth_screen.setFixedSize(520, 670)
        self.auth_screen.show()

    def on_authentication_success(self, user_type, username):
        """Обработчик успешной авторизации"""
        self.current_user_type = user_type
        self.current_user = username

        # Закрываем экран авторизации
        if self.auth_screen:
            self.auth_screen.close()
            self.auth_screen = None

        # Показываем главное окно с передачей типа пользователя
        self.show_main_window()

    def show_main_window(self):
        """Показывает главное окно приложения"""
        self.main_window = MainWindow(self.current_user_type, self.current_user)
        self.main_window.logout_requested.connect(self.on_logout_requested)
        self.main_window.show()

    def on_logout_requested(self):
        """Обработчик запроса выхода из системы"""
        # Закрываем главное окно
        if self.main_window:
            self.main_window.close()
            self.main_window = None

        # Сбрасываем информацию о пользователе
        self.current_user = None
        self.current_user_type = None

        # Показываем экран авторизации
        self.show_auth_screen()


def main():
    app = QApplication(sys.argv)

    # Настройка шрифтов для разных ОС
    app.setStyleSheet("""
        QApplication {
            font-family: -apple-system, BlinkMacSystemFont, Arial, Helvetica, sans-serif;
        }
    """)

    # Создаем приложение с системой авторизации
    master_pol_app = MasterPolApp()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()