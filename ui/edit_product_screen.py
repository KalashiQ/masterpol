from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QComboBox, QDoubleSpinBox, QPushButton, QLabel,
                             QMessageBox, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from database.db_manager import DatabaseManager


class EditProductScreen(QWidget):
    product_updated = pyqtSignal()

    def __init__(self, product_data, partner_inn=None):
        super().__init__()
        self.partner_inn = partner_inn
        self.original_article = product_data['ArticleNumber']  # Сохраняем оригинальный артикул для поиска
        self.product_data = product_data
        self.db_manager = DatabaseManager()

        # Словарь типов продукции: название -> ID
        self.product_types = {
            "Ламинат": "1",
            "Массивная доска": "2",
            "Паркетная доска": "3",
            "Пробковое покрытие": "4"
        }

        # Обратный словарь: ID -> название
        self.id_to_type = {v: k for k, v in self.product_types.items()}

        self.init_ui()
        self.load_product_data()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Заголовок
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout()

        icon_label = QLabel("✏️")
        icon_label.setObjectName("iconLabel")
        title_label = QLabel("Редактирование продукции")
        title_label.setObjectName("headerTitle")

        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_frame.setLayout(header_layout)

        main_layout.addWidget(header_frame)

        # Контент
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout()

        form_title = QLabel("Редактирование продукции")
        form_title.setObjectName("formTitle")
        content_layout.addWidget(form_title)

        form_subtitle = QLabel("Изменение информации о продукции")
        form_subtitle.setObjectName("formSubtitle")
        content_layout.addWidget(form_subtitle)

        # Форма
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(25)
        form_layout.setHorizontalSpacing(20)

        # Наименование продукции
        self.product_name_edit = QLineEdit()
        self.product_name_edit.setPlaceholderText("Введите название продукции")
        self.product_name_edit.setObjectName("inputField")
        self.product_name_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addRow("Название продукции *", self.product_name_edit)

        # Тип продукции - ComboBox
        self.product_type_combo = QComboBox()
        self.product_type_combo.addItem("Выберите тип продукции", "")

        # Добавляем типы продукции из словаря
        for type_name, type_id in self.product_types.items():
            self.product_type_combo.addItem(f"{type_name} (ID: {type_id})", type_id)

        self.product_type_combo.setObjectName("inputField")
        self.product_type_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addRow("Тип продукции *", self.product_type_combo)

        # Артикул
        self.article_edit = QLineEdit()
        self.article_edit.setPlaceholderText("Введите артикул")
        self.article_edit.setObjectName("inputField")
        self.article_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addRow("Артикул *", self.article_edit)

        # Минимальная стоимость
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

        # Кнопки
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

        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_product)
        self.cancel_btn.clicked.connect(self.close)

    def load_product_data(self):
        """Загружает данные продукта в форму"""
        try:
            print("=== ЗАГРУЗКА ДАННЫХ ПРОДУКТА ===")
            print("product_data:", self.product_data)

            # Заполняем поля данными продукта
            self.product_name_edit.setText(self.product_data.get('ProductName', ''))
            self.article_edit.setText(self.product_data.get('ArticleNumber', ''))

            # Устанавливаем тип продукции в ComboBox
            product_type_id = str(self.product_data.get('ProductTypeID', ''))
            print("Ищем тип с ID:", product_type_id)

            # Ищем нужный элемент в ComboBox по ID
            for i in range(self.product_type_combo.count()):
                if self.product_type_combo.itemData(i) == product_type_id:
                    self.product_type_combo.setCurrentIndex(i)
                    print(f"Установлен тип: {self.product_type_combo.itemText(i)}")
                    break

            # Устанавливаем цену
            min_price = self.product_data.get('MinPartnerPrice', 0)
            if isinstance(min_price, str):
                try:
                    min_price = float(min_price.replace(',', '.'))
                except (ValueError, AttributeError):
                    min_price = 0.0

            self.price_spin.setValue(float(min_price))

            print("=== ДАННЫЕ ЗАГРУЖЕНЫ ===")

        except Exception as e:
            print("Ошибка загрузки данных:", e)
            QMessageBox.warning(self, "Ошибка", f"Ошибка при загрузке данных: {str(e)}")

    def save_product(self):
        """Сохраняет изменения в продукте"""
        if not self.validate_fields():
            return

        try:
            # Получаем ID типа продукции из выбранного элемента ComboBox
            selected_type_id = self.product_type_combo.currentData()

            updated_data = {
                'ProductName': self.product_name_edit.text().strip(),
                'ProductTypeID': selected_type_id,
                'ArticleNumber': self.article_edit.text().strip(),
                'MinPartnerPrice': self.price_spin.value()
            }

            print("=== СОХРАНЕНИЕ ИЗМЕНЕНИЙ ===")
            print("original_article:", self.original_article)
            print("updated_data:", updated_data)

            # Используем метод update_product для обновления
            if self.db_manager.update_product(self.original_article, updated_data):
                QMessageBox.information(self, "Успех", "Продукт успешно обновлен!")
                self.product_updated.emit()
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось обновить продукт")

        except Exception as e:
            print("Ошибка сохранения:", e)
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")

    def validate_fields(self):
        """Валидация полей формы"""
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