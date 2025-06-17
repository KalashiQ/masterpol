from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QPushButton, QLabel, QMessageBox,
                             QFrame, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal
from database.auth_manager import AuthManager


class RegisterScreen(QWidget):
    user_registered = pyqtSignal(str)  # username

    def __init__(self):
        super().__init__()
        self.auth_manager = AuthManager()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Заголовок
        title_label = QLabel("Регистрация пользователя")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #606c38;
                margin-bottom: 20px;
            }
        """)
        main_layout.addWidget(title_label)

        # Форма регистрации
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(10)

        # Поля формы
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Введите логин")
        self.username_edit.setObjectName("registerField")
        form_layout.addRow("Логин:", self.username_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Введите пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setObjectName("registerField")
        form_layout.addRow("Пароль:", self.password_edit)

        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setPlaceholderText("Подтвердите пароль")
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_password_edit.setObjectName("registerField")
        form_layout.addRow("Подтвердить пароль:", self.confirm_password_edit)

        self.full_name_edit = QLineEdit()
        self.full_name_edit.setPlaceholderText("Введите ФИО")
        self.full_name_edit.setObjectName("registerField")
        form_layout.addRow("ФИО:", self.full_name_edit)

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("example@domain.com")
        self.email_edit.setObjectName("registerField")
        form_layout.addRow("Email:", self.email_edit)

        self.user_type_combo = QComboBox()
        self.user_type_combo.addItems(["Пользователь", "Администратор"])
        self.user_type_combo.setObjectName("registerField")
        form_layout.addRow("Тип доступа:", self.user_type_combo)

        main_layout.addLayout(form_layout)

        # Кнопки
        buttons_layout = QHBoxLayout()

        self.register_btn = QPushButton("Зарегистрировать")
        self.register_btn.setObjectName("primaryBtn")

        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.setObjectName("secondaryBtn")

        buttons_layout.addWidget(self.register_btn)
        buttons_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

        # Применяем стили
        self.apply_styles()

        # Подключаем события
        self.register_btn.clicked.connect(self.register_user)
        self.cancel_btn.clicked.connect(self.close)

    def apply_styles(self):
        """Применяет стили к элементам формы"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f3ee;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }

            QLineEdit#registerField, QComboBox#registerField {
                border: 2px solid #dda15e;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                background-color: white;
                min-height: 20px;
            }

            QLineEdit#registerField:focus, QComboBox#registerField:focus {
                border-color: #606c38;
            }

            QComboBox#registerField::drop-down {
                border: none;
                width: 25px;
            }

            QComboBox#registerField::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #666;
                margin-right: 8px;
            }

            QPushButton#primaryBtn {
                background-color: #606c38;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 20px;
                min-height: 20px;
            }

            QPushButton#primaryBtn:hover {
                background-color: #4a5228;
            }

            QPushButton#secondaryBtn {
                background-color: transparent;
                color: #606c38;
                border: 2px solid #606c38;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                min-height: 20px;
            }

            QPushButton#secondaryBtn:hover {
                background-color: #606c38;
                color: white;
            }

            QLabel {
                color: #333;
                font-weight: bold;
                font-size: 14px;
            }
        """)

    def validate_fields(self):
        """Валидация полей формы"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        confirm_password = self.confirm_password_edit.text().strip()
        full_name = self.full_name_edit.text().strip()

        if not username:
            QMessageBox.warning(self, "Ошибка", "Введите логин")
            self.username_edit.setFocus()
            return False

        if len(username) < 3:
            QMessageBox.warning(self, "Ошибка", "Логин должен содержать минимум 3 символа")
            self.username_edit.setFocus()
            return False

        if not password:
            QMessageBox.warning(self, "Ошибка", "Введите пароль")
            self.password_edit.setFocus()
            return False

        if len(password) < 6:
            QMessageBox.warning(self, "Ошибка", "Пароль должен содержать минимум 6 символов")
            self.password_edit.setFocus()
            return False

        if password != confirm_password:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            self.confirm_password_edit.setFocus()
            return False

        if not full_name:
            QMessageBox.warning(self, "Ошибка", "Введите ФИО")
            self.full_name_edit.setFocus()
            return False

        return True

    def register_user(self):
        """Регистрирует нового пользователя"""
        if not self.validate_fields():
            return

        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        full_name = self.full_name_edit.text().strip()
        email = self.email_edit.text().strip()
        user_type = "admin" if self.user_type_combo.currentText() == "Администратор" else "user"

        try:
            success, message = self.auth_manager.register_user(
                username=username,
                password=password,
                user_type=user_type,
                full_name=full_name,
                email=email
            )

            if success:
                QMessageBox.information(self, "Успех", message)
                self.user_registered.emit(username)
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", message)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Непредвиденная ошибка: {str(e)}")