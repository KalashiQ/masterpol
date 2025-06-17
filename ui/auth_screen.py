from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QPushButton, QLabel, QMessageBox,
                             QFrame, QSizePolicy, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPainter, QBrush, QColor
from database.auth_manager import AuthManager


class AuthScreen(QWidget):
    authentication_successful = pyqtSignal(str, str)  # user_type, username

    def __init__(self):
        super().__init__()
        self.auth_manager = AuthManager()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignCenter)

        # Основной контейнер
        auth_container = QFrame()
        auth_container.setObjectName("authContainer")
        auth_container.setFixedSize(480, 650)  # Немного увеличена высота
        auth_container.setStyleSheet("""
            QFrame#authContainer {
                background-color: white;
                border: 2px solid #dda15e;
                border-radius: 15px;
            }
        """)

        container_layout = QVBoxLayout()
        container_layout.setSpacing(15)  # Увеличен отступ между секциями
        container_layout.setContentsMargins(50, 30, 50, 30)

        # Заголовок приложения
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignCenter)  # ЭТА СТРОКА БЫЛА ПРОПУЩЕНА!
        title_layout.setSpacing(10)

        # Логотип - дополнительное центрирование
        logo_wrapper = QHBoxLayout()
        logo_wrapper.setAlignment(Qt.AlignCenter)

        app_icon = QLabel()
        app_icon.setAlignment(Qt.AlignCenter)
        app_icon.setFixedSize(60, 80)  # Широкий контейнер для логотипа
        app_icon.setScaledContents(True)  # Автоматическое масштабирование содержимого

        # Пытаемся загрузить логотип из файла
        try:
            pixmap = QPixmap("assets/masterpol.png")
            if not pixmap.isNull():
                # Масштабируем изображение на всю ширину контейнера
                scaled_pixmap = pixmap.scaled(100, 60, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                app_icon.setPixmap(scaled_pixmap)
                app_icon.setStyleSheet("""
                    QLabel {
                        background: transparent;
                        border: none;
                        padding: 10px;
                        margin: 0 auto;
                        min-width: 180px;
                    }
                """)
            else:
                # Если файл не найден, используем эмодзи
                app_icon.setText("🏢")
                app_icon.setStyleSheet("""
                    QLabel {
                        font-size: 48px;
                        color: #606c38;
                        background: transparent;
                        border: none;
                        margin: 0 auto;
                    }
                """)
        except:
            # Если произошла ошибка, используем эмодзи
            app_icon.setText("🏢")
            app_icon.setStyleSheet("""
                QLabel {
                    font-size: 48px;
                    color: #606c38;
                    background: transparent;
                    border: none;
                    margin: 0 auto;
                }
            """)

        logo_wrapper.addWidget(app_icon)

        app_title = QLabel("Мастер-пол")
        app_title.setAlignment(Qt.AlignCenter)
        app_title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #606c38;
                background: transparent;
                border: none;
                margin-top: 5px;
                margin-bottom: 5px;
            }
        """)

        app_subtitle = QLabel("Система управления партнерами")
        app_subtitle.setAlignment(Qt.AlignCenter)
        app_subtitle.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666;
                background: transparent;
                border: none;
                margin-bottom: 15px;
                line-height: 1.4;
                padding: 0px 10px;
            }
        """)

        title_layout.addLayout(logo_wrapper)  # Добавляем обертку вместо прямого виджета
        title_layout.addWidget(app_title)
        title_layout.addWidget(app_subtitle)

        container_layout.addLayout(title_layout)

        # Форма авторизации
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(25)  # Отступ между полями
        form_layout.setHorizontalSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft)

        # Поле логина
        login_label = QLabel("Логин:")
        login_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-weight: bold;
                font-size: 14px;
                background: transparent;
                border: none;
                margin-bottom: 5px;
                padding: 0px;
            }
        """)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Введите логин")
        self.username_edit.setObjectName("authField")
        self.username_edit.setFixedHeight(65)

        form_layout.addRow(login_label, self.username_edit)

        # Поле пароля
        password_label = QLabel("Пароль:")
        password_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-weight: bold;
                font-size: 14px;
                background: transparent;
                border: none;
                margin-bottom: 5px;
                padding: 0px;
            }
        """)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Введите пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setObjectName("authField")
        self.password_edit.setFixedHeight(65)

        form_layout.addRow(password_label, self.password_edit)

        # Тип пользователя
        type_label = QLabel("Тип доступа:")
        type_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-weight: bold;
                font-size: 14px;
                background: transparent;
                border: none;
                margin-bottom: 5px;
                padding: 0px;
            }
        """)

        self.user_type_combo = QComboBox()
        self.user_type_combo.addItems(["Пользователь", "Администратор"])
        self.user_type_combo.setObjectName("authField")
        self.user_type_combo.setFixedHeight(65)

        form_layout.addRow(type_label, self.user_type_combo)

        container_layout.addLayout(form_layout)

        # Добавляем дополнительный отступ перед кнопками
        container_layout.addSpacing(20)

        # Кнопки
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(15)

        self.login_btn = QPushButton("Войти в систему")
        self.login_btn.setObjectName("loginBtn")
        self.login_btn.setFixedHeight(50)

        self.register_btn = QPushButton("Регистрация")
        self.register_btn.setObjectName("registerBtn")
        self.register_btn.setFixedHeight(40)

        buttons_layout.addWidget(self.login_btn)
        buttons_layout.addWidget(self.register_btn)

        container_layout.addLayout(buttons_layout)

        # Информация о тестовых аккаунтах
        info_label = QLabel("""
Тестовые аккаунты:
Админ: admin / admin123
Пользователь: user / user123
        """.strip())
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #888;
                background: transparent;
                border: 1px solid #e9ecef;
                border-radius: 5px;
                padding: 10px;
                margin-top: 15px;
            }
        """)
        container_layout.addWidget(info_label)

        auth_container.setLayout(container_layout)
        main_layout.addWidget(auth_container)

        self.setLayout(main_layout)

        # Применяем стили
        self.apply_styles()

        # Подключаем события
        self.login_btn.clicked.connect(self.authenticate_user)
        self.register_btn.clicked.connect(self.show_register_dialog)
        self.password_edit.returnPressed.connect(self.authenticate_user)

    def apply_styles(self):
        """Применяет стили к элементам формы"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f3ee;
                font-family: Arial, Helvetica, sans-serif;
            }

            QLineEdit#authField, QComboBox#authField {
                border: 2px solid #dda15e;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 14px;
                background-color: white;
                color: #333;
                margin-top: 5px;
                margin-bottom: 10px;
                min-width: 200px;
            }

            QLineEdit#authField:focus, QComboBox#authField:focus {
                border-color: #606c38;
                outline: none;
            }

            QComboBox#authField::drop-down {
                border: none;
                width: 30px;
            }

            QComboBox#authField::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666;
                margin-right: 10px;
            }

            QPushButton#loginBtn {
                background-color: #606c38;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
            }

            QPushButton#loginBtn:hover {
                background-color: #4a5228;
            }

            QPushButton#loginBtn:pressed {
                background-color: #3d441f;
            }

            QPushButton#registerBtn {
                background-color: transparent;
                color: #606c38;
                border: 2px solid #606c38;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }

            QPushButton#registerBtn:hover {
                background-color: #606c38;
                color: white;
            }

            QLabel {
                color: #333;
                font-weight: bold;
                font-size: 14px;
                background: transparent;
                border: none;
                margin: 0px;
                padding: 2px;
            }

            QFormLayout QLabel {
                background: transparent;
                border: none;
                margin-bottom: 5px;
                margin-top: 5px;
            }
        """)

    def authenticate_user(self):
        """Аутентификация пользователя"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        user_type = "admin" if self.user_type_combo.currentText() == "Администратор" else "user"

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        if self.auth_manager.authenticate_user(username, password, user_type):
            QMessageBox.information(self, "Успех", f"Добро пожаловать, {username}!")
            self.authentication_successful.emit(user_type, username)
        else:
            QMessageBox.warning(self, "Ошибка",
                                "Неверный логин, пароль или тип доступа!\n\n"
                                "Попробуйте тестовые аккаунты:\n"
                                "Админ: admin / admin123\n"
                                "Пользователь: user / user123")

    def show_register_dialog(self):
        """Показывает диалог регистрации"""
        from ui.register_screen import RegisterScreen
        self.register_dialog = RegisterScreen()
        self.register_dialog.user_registered.connect(self.on_user_registered)
        self.register_dialog.setWindowTitle("Регистрация пользователя")
        self.register_dialog.setFixedSize(400, 350)
        self.register_dialog.show()

    def on_user_registered(self, username):
        """Обработчик успешной регистрации"""
        QMessageBox.information(self, "Успех", f"Пользователь {username} успешно зарегистрирован!")
        self.username_edit.setText(username)
        self.user_type_combo.setCurrentText("Пользователь")