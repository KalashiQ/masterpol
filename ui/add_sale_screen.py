from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QComboBox, QSpinBox, QDoubleSpinBox, QPushButton, QLabel,
                             QMessageBox, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from database.db_manager import DatabaseManager


class AddSaleScreen(QWidget):
    sale_added = pyqtSignal()

    def __init__(self, partner_inn, partner_name):
        super().__init__()
        self.partner_inn = partner_inn
        self.partner_name = partner_name
        self.db_manager = DatabaseManager()
        self.products_data = []
        self.init_ui()
        self.load_partner_products()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout()

        icon_label = QLabel("💰")
        icon_label.setObjectName("iconLabel")
        title_label = QLabel("Добавление продажи")
        title_label.setObjectName("headerTitle")

        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_frame.setLayout(header_layout)

        main_layout.addWidget(header_frame)

        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout()

        form_title = QLabel("Добавление продажи")
        form_title.setObjectName("formTitle")
        content_layout.addWidget(form_title)

        form_subtitle = QLabel(f"Партнер: {self.partner_name}")
        form_subtitle.setObjectName("formSubtitle")
        content_layout.addWidget(form_subtitle)

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(25)
        form_layout.setHorizontalSpacing(20)

        self.product_combo = QComboBox()
        self.product_combo.setObjectName("inputField")
        self.product_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.product_combo.currentIndexChanged.connect(self.on_product_changed)
        form_layout.addRow("Продукция *", self.product_combo)

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 999999)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setSuffix(" шт.")
        self.quantity_spin.setObjectName("inputField")
        self.quantity_spin.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.quantity_spin.valueChanged.connect(self.update_total_sum)
        form_layout.addRow("Количество *", self.quantity_spin)

        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0.01, 999999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setValue(0.00)
        self.price_spin.setSuffix(" ₽")
        self.price_spin.setObjectName("inputField")
        self.price_spin.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.price_spin.valueChanged.connect(self.update_total_sum)
        form_layout.addRow("Цена за единицу *", self.price_spin)

        self.total_sum_label = QLabel("0.00 ₽")
        self.total_sum_label.setObjectName("totalSumLabel")
        self.total_sum_label.setStyleSheet("""
            QLabel#totalSumLabel {
                font-size: 16px;
                font-weight: bold;
                color: #606c38;
                background-color: #f4f3ee;
                border: 2px solid #dda15e;
                border-radius: 6px;
                padding: 10px;
                text-align: center;
            }
        """)
        form_layout.addRow("Общая сумма:", self.total_sum_label)

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

        self.save_btn.clicked.connect(self.save_sale)
        self.cancel_btn.clicked.connect(self.close)

    def load_partner_products(self):
        """Загружает продукцию партнера в выпадающий список"""
        try:
            self.products_data = self.db_manager.get_partner_products_for_sale(self.partner_inn)
            self.product_combo.clear()
            self.product_combo.addItem("Выберите продукцию", None)

            if not self.products_data:
                self.product_combo.addItem("У партнера нет продукции", None)
                self.save_btn.setEnabled(False)
                QMessageBox.warning(self, "Внимание",
                                    f"У партнера '{self.partner_name}' нет добавленной продукции.\n"
                                    "Сначала добавьте продукцию в разделе 'Продукция'.")
                return

            for product_id, product_name, min_price in self.products_data:
                try:
                    price_float = float(str(min_price).replace(',', '.'))
                    display_text = f"{product_name} (мин. цена: {price_float:.2f} ₽)"
                except:
                    display_text = f"{product_name} (цена: {min_price})"

                product_data = {
                    'id': product_id,
                    'name': product_name,
                    'min_price': min_price
                }

                self.product_combo.addItem(display_text, product_data)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить продукцию: {str(e)}")

    def on_product_changed(self):
        """Обработчик изменения выбранного продукта"""
        product_data = self.product_combo.currentData()

        if product_data and product_data.get('min_price'):
            try:
                min_price = float(str(product_data['min_price']).replace(',', '.'))
                self.price_spin.setValue(min_price)
            except:
                self.price_spin.setValue(0.00)
        else:
            self.price_spin.setValue(0.00)

        self.update_total_sum()

    def update_total_sum(self):
        """Обновляет общую сумму"""
        try:
            quantity = self.quantity_spin.value()
            price = self.price_spin.value()
            total = quantity * price
            self.total_sum_label.setText(f"{total:.2f} ₽")
        except:
            self.total_sum_label.setText("0.00 ₽")

    def save_sale(self):
        """Сохраняет новую продажу"""
        if not self.validate_fields():
            return

        try:
            product_data = self.product_combo.currentData()
            partner_id = self.db_manager.get_partner_id_by_inn(self.partner_inn)

            if not partner_id:
                QMessageBox.critical(self, "Ошибка", "Не удалось найти ID партнера")
                return

            sale_data = {
                'ProductID': product_data['id'],
                'PartnerID': partner_id,
                'Quantity': self.quantity_spin.value()
            }

            if self.db_manager.add_sale(sale_data):
                QMessageBox.information(self, "Успех",
                                        f"Продажа успешно добавлена!\n\n"
                                        f"Продукт: {product_data['name']}\n"
                                        f"Количество: {self.quantity_spin.value()} шт.\n"
                                        f"Сумма: {self.quantity_spin.value() * self.price_spin.value():.2f} ₽")
                self.sale_added.emit()
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить продажу")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")

    def validate_fields(self):
        """Валидация полей формы"""
        current_index = self.product_combo.currentIndex()
        product_data = self.product_combo.currentData()

        if current_index <= 0 or not product_data:
            QMessageBox.warning(self, "Ошибка", "Выберите продукцию")
            self.product_combo.setFocus()
            return False

        if not product_data.get('id'):
            QMessageBox.warning(self, "Ошибка", "ID продукта не найден")
            self.product_combo.setFocus()
            return False

        if self.quantity_spin.value() <= 0:
            QMessageBox.warning(self, "Ошибка", "Укажите количество больше 0")
            self.quantity_spin.setFocus()
            return False

        if self.price_spin.value() <= 0:
            QMessageBox.warning(self, "Ошибка", "Укажите цену больше 0")
            self.price_spin.setFocus()
            return False

        return True