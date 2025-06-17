from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QComboBox, QSpinBox, QPushButton, QLabel,
                             QMessageBox, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from database.db_manager import DatabaseManager


class AddPartnerScreen(QWidget):
    partner_added = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout()

        icon_label = QLabel("🏢")
        icon_label.setObjectName("iconLabel")
        title_label = QLabel("Добавление партнера")
        title_label.setObjectName("headerTitle")

        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_frame.setLayout(header_layout)

        main_layout.addWidget(header_frame)

        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout()

        form_title = QLabel("Партнер")
        form_title.setObjectName("formTitle")
        content_layout.addWidget(form_title)

        form_subtitle = QLabel("Добавление информации о партнере")
        form_subtitle.setObjectName("formSubtitle")
        content_layout.addWidget(form_subtitle)

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(25)
        form_layout.setHorizontalSpacing(20)

        self.partner_type_combo = QComboBox()
        self.partner_type_combo.addItems(["ЗАО", "ООО", "ПАО", "ИП", "ТОО"])
        self.partner_type_combo.setObjectName("inputField")
        self.partner_type_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addRow("Тип организации *", self.partner_type_combo)

        self.partner_name_edit = QLineEdit()
        self.partner_name_edit.setPlaceholderText("Введите название организации")
        self.partner_name_edit.setObjectName("inputField")
        self.partner_name_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addRow("Наименование организации *", self.partner_name_edit)

        self.director_edit = QLineEdit()
        self.director_edit.setPlaceholderText("Введите ФИО директора")
        self.director_edit.setObjectName("inputField")
        self.director_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addRow("ФИО директора *", self.director_edit)

        contact_row_layout = QHBoxLayout()
        contact_row_layout.setSpacing(15)

        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("+7 (XXX) XXX-XX-XX")
        self.phone_edit.setObjectName("inputField")

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("example@domain.com")
        self.email_edit.setObjectName("inputField")

        contact_row_layout.addWidget(self.phone_edit)
        contact_row_layout.addWidget(self.email_edit)

        contact_label = QLabel("Телефон * / Email *")
        contact_label.setObjectName("fieldLabel")
        form_layout.addRow(contact_label, contact_row_layout)

        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("Введите юридический адрес")
        self.address_edit.setObjectName("inputField")
        self.address_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addRow("Юридический адрес *", self.address_edit)

        self.inn_edit = QLineEdit()
        self.inn_edit.setPlaceholderText("Введите 10 цифр ИНН")
        self.inn_edit.setObjectName("inputField")
        self.inn_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addRow("ИНН *", self.inn_edit)

        rating_frame = QFrame()
        rating_frame.setObjectName("ratingFrame")
        rating_layout = QVBoxLayout()

        rating_title = QLabel("Рейтинг")
        rating_title.setObjectName("ratingTitle")
        rating_layout.addWidget(rating_title)

        rating_subtitle = QLabel("Выберите рейтинг партнера от 0 до 10")
        rating_subtitle.setObjectName("ratingSubtitle")
        rating_layout.addWidget(rating_subtitle)

        self.rating_spin = QSpinBox()
        self.rating_spin.setRange(0, 10)
        self.rating_spin.setValue(0)
        self.rating_spin.setObjectName("ratingSpinBox")
        self.rating_spin.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        rating_layout.addWidget(self.rating_spin)

        rating_frame.setLayout(rating_layout)
        form_layout.addRow("", rating_frame)

        content_layout.addLayout(form_layout)
        content_frame.setLayout(content_layout)
        main_layout.addWidget(content_frame)

        main_layout.addStretch()

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.save_btn = QPushButton("💾 Сохранить")
        self.save_btn.setObjectName("saveBtn")
        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.setObjectName("cancelBtn")

        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

        self.save_btn.clicked.connect(self.save_partner)
        self.cancel_btn.clicked.connect(self.close)

    def save_partner(self):
        if not self.validate_fields():
            return

        try:
            partner_data = {
                'PartnerType': self.partner_type_combo.currentText(),
                'PartnerName': self.partner_name_edit.text().strip(),
                'Director': self.director_edit.text().strip(),
                'Phone': self.phone_edit.text().strip(),
                'Email': self.email_edit.text().strip(),
                'LegalAddress': self.address_edit.text().strip(),
                'INN': self.inn_edit.text().strip(),
                'Rating': self.rating_spin.value()
            }

            success, message = self.db_manager.add_partner(partner_data)

            if success:
                QMessageBox.information(self, "Успех", message)
                self.partner_added.emit()
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", message)
                if "ИНН" in message:
                    self.inn_edit.setFocus()
                    self.inn_edit.selectAll()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Непредвиденная ошибка: {str(e)}")

    def validate_fields(self):
        if not self.partner_name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите наименование партнера")
            self.partner_name_edit.setFocus()
            return False

        if not self.director_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите ФИО директора")
            self.director_edit.setFocus()
            return False

        inn = self.inn_edit.text().strip()
        if not inn:
            QMessageBox.warning(self, "Ошибка", "Введите ИНН")
            self.inn_edit.setFocus()
            return False

        if not inn.isdigit():
            QMessageBox.warning(self, "Ошибка", "ИНН должен содержать только цифры")
            self.inn_edit.setFocus()
            self.inn_edit.selectAll()
            return False

        if len(inn) not in [10, 12]:
            QMessageBox.warning(self, "Ошибка", "ИНН должен содержать 10 или 12 цифр")
            self.inn_edit.setFocus()
            self.inn_edit.selectAll()
            return False

        if not self.phone_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите телефон")
            self.phone_edit.setFocus()
            return False

        if not self.email_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите email")
            self.email_edit.setFocus()
            return False

        if not self.address_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите юридический адрес")
            self.address_edit.setFocus()
            return False

        return True

    def clear_fields(self):
        self.partner_type_combo.setCurrentIndex(0)
        self.partner_name_edit.clear()
        self.director_edit.clear()
        self.phone_edit.clear()
        self.email_edit.clear()
        self.address_edit.clear()
        self.inn_edit.clear()
        self.rating_spin.setValue(0)