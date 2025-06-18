from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QDoubleSpinBox, QPushButton, QLabel,
    QMessageBox, QFrame, QSizePolicy
)
from PyQt5.QtCore import pyqtSignal
from database.db_manager import DatabaseManager


class AddProductScreen(QWidget):
    product_added = pyqtSignal()

    def __init__(self, partner_inn=None):
        super().__init__()
        self.partner_inn = partner_inn
        self.db_manager = DatabaseManager()

        self.product_types = {
            "Ламинат": "1",
            "Массивная доска": "2",
            "Паркетная доска": "3",
            "Пробковое покрытие": "4"
        }

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout()

        icon_label = QLabel("📦")
        icon_label.setObjectName("iconLabel")
        title_label = QLabel("Продукция")
        title_label.setObjectName("headerTitle")

        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_frame.setLayout(header_layout)

        main_layout.addWidget(header_frame)

        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout()

        form_title = QLabel("Продукция")
        form_title.setObjectName("formTitle")
        content_layout.addWidget(form_title)

        form_subtitle = QLabel("Добавление информации о продукции")
        form_subtitle.setObjectName("formSubtitle")
        content_layout.addWidget(form_subtitle)

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(25)
        form_layout.setHorizontalSpacing(20)

        self.product_name_edit = QLineEdit()
        self.product_name_edit.setPlaceholderText("Введите название продукции")
        self.product_name_edit.setObjectName("inputField")
        self.product_name_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addRow("Название продукции *", self.product_name_edit)

        self.product_type_combo = QComboBox()
        self.product_type_combo.addItem("Выберите тип продукции", "")
        for type_name, type_id in self.product_types.items():
            self.product_type_combo.addItem(f"{type_name} (ID: {type_id})", type_id)
        self.product_type_combo.setObjectName("inputField")
        self.product_type_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addRow("Тип продукции *", self.product_type_combo)

        self.article_edit = QLineEdit()
        self.article_edit.setPlaceholderText("Введите артикул")
        self.article_edit.setObjectName("inputField")
        self.article_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addRow("Артикул *", self.article_edit)

        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0.00, 999999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setValue(0.00)
        self.price_spin.setSuffix(" ₽")
        self.price_spin.setObjectName("inputField")
        self.price_spin.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addRow("Минимальная стоимость *", self.price_spin)

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

        self.save_btn.clicked.connect(self.save_product)
        self.cancel_btn.clicked.connect(self.close)

    def save_product(self):
        if not self.validate_fields():
            return

        try:
            selected_type_id = self.product_type_combo.currentData()
            product_data = {
                'ProductName': self.product_name_edit.text().strip(),
                'ProductTypeID': selected_type_id,
                'ArticleNumber': self.article_edit.text().strip(),
                'MinPartnerPrice': self.price_spin.value()
            }

            # Добавляем отладочную информацию
            print(f"Добавляем продукт для партнера с ИНН: {self.partner_inn}")
            print(f"Данные продукта: {product_data}")

            result = self.db_manager.add_product_with_partner_id(product_data, self.partner_inn)
            print(f"Результат добавления: {result}")

            if result:
                QMessageBox.information(self, "Успех", "Продукт успешно добавлен!")
                # Очищаем поля после успешного добавления
                self.clear_fields()
                self.product_added.emit()
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить продукт")

        except Exception as e:
            print(f"Ошибка при сохранении: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")

    def clear_fields(self):
        """Очищает все поля формы"""
        self.product_name_edit.clear()
        self.product_type_combo.setCurrentIndex(0)
        self.article_edit.clear()
        self.price_spin.setValue(0.00)

    def validate_fields(self):
        if not self.product_name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название продукции")
            self.product_name_edit.setFocus()
            return False

        if not self.product_type_combo.currentData():
            QMessageBox.warning(self, "Ошибка", "Выберите тип продукции")
            self.product_type_combo.setFocus()
            return False

        if not self.article_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите артикул")
            self.article_edit.setFocus()
            return False

        if self.price_spin.value() <= 0:
            QMessageBox.warning(self, "Ошибка", "Введите корректную стоимость")
            self.price_spin.setFocus()
            return False

        return True