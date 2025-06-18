from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFrame, QMessageBox, QMenuBar,
                             QAction, QStatusBar)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from ui.partners_screen import PartnersScreen


class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, user_type="user", username=""):
        super().__init__()
        self.user_type = user_type  # "admin" или "user"
        self.username = username
        self.current_screen = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Мастер-пол - {self.get_access_level_text()}")
        self.setGeometry(100, 100, 1200, 800)

        # Создаем меню
        self.create_menu()

        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Создаем верхнюю панель
        header_frame = self.create_header()
        layout.addWidget(header_frame)

        # Создаем основную область контента
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        content_frame.setLayout(self.content_layout)

        layout.addWidget(content_frame)

        central_widget.setLayout(layout)

        # Создаем статус бар
        self.create_status_bar()

        # Применяем стили
        self.apply_styles()

        # Показываем начальный экран
        self.show_welcome_screen()

    def create_menu(self):
        """Создает меню приложения"""
        menubar = self.menuBar()

        # Меню "Файл"
        file_menu = menubar.addMenu('Файл')

        logout_action = QAction('Выйти из аккаунта', self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)

        exit_action = QAction('Закрыть приложение', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню "Навигация"
        nav_menu = menubar.addMenu('Навигация')

        partners_action = QAction('Партнеры', self)
        partners_action.triggered.connect(self.show_partners)
        nav_menu.addAction(partners_action)

        # Меню "Справка"
        help_menu = menubar.addMenu('Справка')

        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_header(self):
        """Создает верхнюю панель приложения"""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setFixedHeight(80)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 10, 20, 10)

        # Логотип и название
        logo_layout = QHBoxLayout()
        logo_label = QLabel("🏢")
        logo_label.setStyleSheet("font-size: 32px; color: #606c38;")

        title_layout = QVBoxLayout()
        title_label = QLabel("Мастер-пол")
        title_label.setObjectName("appTitle")

        subtitle_label = QLabel("Система управления партнерами")
        subtitle_label.setObjectName("appSubtitle")

        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)

        logo_layout.addWidget(logo_label)
        logo_layout.addLayout(title_layout)

        # Информация о пользователе
        user_info_layout = QVBoxLayout()
        user_info_layout.setAlignment(Qt.AlignRight)

        user_label = QLabel(f"Пользователь: {self.username}")
        user_label.setObjectName("userLabel")

        access_label = QLabel(f"Уровень доступа: {self.get_access_level_text()}")
        access_label.setObjectName("accessLabel")

        # Цветовая индикация типа пользователя
        if self.user_type == "admin":
            access_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
        else:
            access_label.setStyleSheet("color: #1976d2; font-weight: bold;")

        logout_btn = QPushButton("Выйти")
        logout_btn.setObjectName("logoutBtn")
        logout_btn.clicked.connect(self.logout)

        user_info_layout.addWidget(user_label)
        user_info_layout.addWidget(access_label)
        user_info_layout.addWidget(logout_btn)

        header_layout.addLayout(logo_layout)
        header_layout.addStretch()
        header_layout.addLayout(user_info_layout)

        header_frame.setLayout(header_layout)
        return header_frame

    def create_status_bar(self):
        """Создает статус бар"""
        status_bar = QStatusBar()
        status_bar.showMessage(f"Готов к работе | {self.get_access_level_text()}")
        self.setStatusBar(status_bar)

    def get_access_level_text(self):
        """Возвращает текстовое описание уровня доступа"""
        return "Администратор" if self.user_type == "admin" else "Пользователь"

    def apply_styles(self):
        """Применяет стили к интерфейсу"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f4f3ee;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }

            QFrame#headerFrame {
                background-color: white;
                border-bottom: 2px solid #dda15e;
            }

            QFrame#contentFrame {
                background-color: #f4f3ee;
            }

            QLabel#appTitle {
                font-size: 24px;
                font-weight: bold;
                color: #606c38;
                margin: 0;
            }

            QLabel#appSubtitle {
                font-size: 12px;
                color: #666;
                margin: 0;
            }

            QLabel#userLabel {
                font-size: 14px;
                color: #333;
                font-weight: bold;
            }

            QLabel#accessLabel {
                font-size: 12px;
                margin-bottom: 5px;
            }

            QPushButton#logoutBtn {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
                font-size: 12px;
                font-weight: bold;
            }

            QPushButton#logoutBtn:hover {
                background-color: #c82333;
            }

            QPushButton#navBtn {
                background-color: #606c38;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 25px;
                font-size: 16px;
                font-weight: bold;
                margin: 10px;
                min-width: 200px;
                min-height: 50px;
            }

            QPushButton#navBtn:hover {
                background-color: #4a5228;
            }

            QLabel#welcomeTitle {
                font-size: 28px;
                font-weight: bold;
                color: #606c38;
                margin-bottom: 20px;
            }

            QLabel#welcomeText {
                font-size: 16px;
                color: #666;
                margin-bottom: 30px;
            }
        """)

    def show_welcome_screen(self):
        """Показывает приветственный экран"""
        self.clear_content()

        welcome_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # Приветственное сообщение
        welcome_title = QLabel(f"Добро пожаловать, {self.username}!")
        welcome_title.setObjectName("welcomeTitle")
        welcome_title.setAlignment(Qt.AlignCenter)

        welcome_text = QLabel(f"Вы вошли в систему как {self.get_access_level_text().lower()}")
        welcome_text.setObjectName("welcomeText")
        welcome_text.setAlignment(Qt.AlignCenter)

        # Кнопка для перехода к партнерам
        buttons_layout = QVBoxLayout()
        buttons_layout.setAlignment(Qt.AlignCenter)
        buttons_layout.setSpacing(15)

        partners_btn = QPushButton("Партнеры")
        partners_btn.setObjectName("navBtn")
        partners_btn.clicked.connect(self.show_partners)

        buttons_layout.addWidget(partners_btn)

        layout.addWidget(welcome_title)
        layout.addWidget(welcome_text)
        layout.addLayout(buttons_layout)

        welcome_widget.setLayout(layout)
        self.content_layout.addWidget(welcome_widget)
        self.current_screen = welcome_widget

    def clear_content(self):
        """Очищает область контента"""
        if self.current_screen:
            self.content_layout.removeWidget(self.current_screen)
            self.current_screen.deleteLater()
            self.current_screen = None

    def show_partners(self):
        """Показывает экран партнеров"""
        self.clear_content()
        self.current_screen = PartnersScreen(self.user_type, self.username)
        self.content_layout.addWidget(self.current_screen)
        self.statusBar().showMessage("Раздел: Партнеры")

    def show_about(self):
        """Показывает информацию о программе"""
        about_text = """
        Мастер-пол
        Система управления партнерами

        Версия: 1.0

        Разработано для управления партнерскими отношениями,
        учета продукции и анализа продаж.
        """
        QMessageBox.about(self, "О программе", about_text)

    def logout(self):
        """Выход из системы"""
        reply = QMessageBox.question(
            self,
            "Выход из системы",
            "Вы уверены, что хотите выйти из системы?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.logout_requested.emit()

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        reply = QMessageBox.question(
            self,
            "Закрытие приложения",
            "Вы уверены, что хотите закрыть приложение?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()