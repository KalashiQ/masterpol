import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from database.db_manager import DatabaseManager
from ui.auth_screen import AuthScreen
from ui.main_window import MainWindow


class MasterPolApp:
    def __init__(self):
        # Инициализируем базу данных (ваш существующий код)
        self.init_database()

        self.auth_screen = None
        self.main_window = None
        self.current_user = None
        self.current_user_type = None

        # Показываем экран авторизации
        self.show_auth_screen()

    def init_database(self):
        """Инициализирует базу данных (ваш существующий код)"""
        db_manager = DatabaseManager()
        db_manager.fix_partner_table_structure()
        db_manager.add_partner_id_to_products_table()

    def show_auth_screen(self):
        """Показывает экран авторизации"""
        self.auth_screen = AuthScreen()
        self.auth_screen.authentication_successful.connect(self.on_authentication_success)
        self.auth_screen.setWindowTitle("Мастер-пол - Авторизация")
        self.auth_screen.setFixedSize(520, 670)  # Увеличен размер окна
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