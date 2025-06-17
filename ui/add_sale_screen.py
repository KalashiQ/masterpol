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
        self.products_data = []  # Будет содержать полные данные о продуктах
        self.init_ui()
        self.load_partner_products()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Заголовок
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

        # Контент
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout()

        form_title = QLabel("Добавление продажи")
        form_title.setObjectName("formTitle")
        content_layout.addWidget(form_title)

        form_subtitle = QLabel(f"Партнер: {self.partner_name}")
        form_subtitle.setObjectName("formSubtitle")
        content_layout.addWidget(form_subtitle)

        # Форма
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(25)
        form_layout.setHorizontalSpacing(20)

        # Выбор продукции
        self.product_combo = QComboBox()
        self.product_combo.setObjectName("inputField")
        self.product_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.product_combo.currentIndexChanged.connect(self.on_product_changed)
        form_layout.addRow("Продукция *", self.product_combo)

        # Количество
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 999999)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setSuffix(" шт.")
        self.quantity_spin.setObjectName("inputField")
        self.quantity_spin.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.quantity_spin.valueChanged.connect(self.update_total_sum)
        form_layout.addRow("Количество *", self.quantity_spin)

        # Цена за единицу
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0.01, 999999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setValue(0.00)
        self.price_spin.setSuffix(" ₽")
        self.price_spin.setObjectName("inputField")
        self.price_spin.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.price_spin.valueChanged.connect(self.update_total_sum)
        form_layout.addRow("Цена за единицу *", self.price_spin)

        # Общая сумма (только для отображения)
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
        self.save_btn.clicked.connect(self.save_sale)
        self.cancel_btn.clicked.connect(self.close)

    def load_partner_products(self):
        """Загружает продукцию партнера в выпадающий список"""
        try:
            print("=== ЗАГРУЗКА ПРОДУКЦИИ ПАРТНЕРА ===")
            self.products_data = self.db_manager.get_partner_products_for_sale(self.partner_inn)

            self.product_combo.clear()
            self.product_combo.addItem("Выберите продукцию", None)  # Пустой элемент

            if not self.products_data:
                self.product_combo.addItem("У партнера нет продукции", None)
                self.save_btn.setEnabled(False)
                QMessageBox.warning(self, "Внимание",
                                    f"У партнера '{self.partner_name}' нет добавленной продукции.\n"
                                    "Сначала добавьте продукцию в разделе 'Продукция'.")
                return

            # Добавляем продукты в комбобокс
            for i, product in enumerate(self.products_data):
                product_id, product_name, min_price = product

                # Преобразуем цену для отображения
                try:
                    price_float = float(str(min_price).replace(',', '.'))
                    display_text = f"{product_name} (мин. цена: {price_float:.2f} ₽)"
                except:
                    display_text = f"{product_name} (цена: {min_price})"

                # Сохраняем данные продукта в ComboBox
                # ИСПРАВЛЕНИЕ: убедимся что все ключи правильные
                product_data = {
                    'id': product_id,  # ID продукта
                    'name': product_name,  # Название продукта
                    'min_price': min_price  # Минимальная цена
                }

                self.product_combo.addItem(display_text, product_data)
                print(f"Добавлен продукт {i}: ID={product_id}, Название='{product_name}', Данные={product_data}")

            print(f"Загружено продуктов: {len(self.products_data)}")
            print(f"Элементов в комбобоксе: {self.product_combo.count()}")

            # Проверим данные в комбобоксе
            for i in range(self.product_combo.count()):
                item_text = self.product_combo.itemText(i)
                item_data = self.product_combo.itemData(i)
                print(f"Элемент {i}: '{item_text}' -> {item_data}")

        except Exception as e:
            print(f"Ошибка при загрузке продукции: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить продукцию: {str(e)}")

    def on_product_changed(self):
        """Обработчик изменения выбранного продукта"""
        product_data = self.product_combo.currentData()

        if product_data and product_data.get('min_price'):
            try:
                # Устанавливаем минимальную цену как цену по умолчанию
                min_price = float(str(product_data['min_price']).replace(',', '.'))
                self.price_spin.setValue(min_price)
                print(f"Установлена цена для '{product_data['name']}': {min_price}")
            except Exception as e:
                print(f"Ошибка при установке цены: {e}")
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
        except Exception as e:
            print(f"Ошибка при обновлении суммы: {e}")
            self.total_sum_label.setText("0.00 ₽")

    def save_sale(self):
        """Сохраняет новую продажу"""
        print("=== НАЧАЛО СОХРАНЕНИЯ ПРОДАЖИ ===")
        print(f"Текущий индекс комбобокса: {self.product_combo.currentIndex()}")
        print(f"Текущий текст: '{self.product_combo.currentText()}'")
        print(f"Данные: {self.product_combo.currentData()}")

        if not self.validate_fields():
            print("❌ Валидация не прошла")
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

            print("=== СОХРАНЕНИЕ ПРОДАЖИ ===")
            print("Данные продажи:", sale_data)
            print("Партнер:", self.partner_name)
            print("Продукт:", product_data['name'])
            print("Количество:", self.quantity_spin.value())
            print("Цена за единицу:", self.price_spin.value())
            print("Общая сумма:", self.quantity_spin.value() * self.price_spin.value())

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
            print(f"Ошибка при сохранении продажи: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")

    def validate_fields(self):
        """Валидация полей формы"""
        print("=== ВАЛИДАЦИЯ ПОЛЕЙ ===")

        # Проверяем выбранный продукт
        current_index = self.product_combo.currentIndex()
        product_data = self.product_combo.currentData()

        print(f"Текущий индекс: {current_index}")
        print(f"Данные продукта: {product_data}")
        print(f"Тип данных продукта: {type(product_data)}")
        print(f"Текст комбобокса: '{self.product_combo.currentText()}'")

        # Проверяем, что выбран реальный продукт (не первый пустой элемент)
        if current_index <= 0:
            QMessageBox.warning(self, "Ошибка", "Выберите продукцию")
            self.product_combo.setFocus()
            return False

        if not product_data:
            QMessageBox.warning(self, "Ошибка", "Данные выбранного продукта не найдены")
            self.product_combo.setFocus()
            return False

        # ДОПОЛНИТЕЛЬНАЯ ОТЛАДКА
        if isinstance(product_data, dict):
            print("Ключи в product_data:", list(product_data.keys()))
            for key, value in product_data.items():
                print(f"  {key}: {value} (тип: {type(value)})")

        # Проверяем наличие ID
        product_id = product_data.get('id')
        print(f"Извлеченный ID продукта: {product_id} (тип: {type(product_id)})")

        if not product_id:
            print("❌ ID продукта отсутствует или пустой")
            QMessageBox.warning(self, "Ошибка", f"ID продукта не найден. Данные: {product_data}")
            self.product_combo.setFocus()
            return False

        print(f"✅ Продукт выбран: ID={product_id}, Название={product_data.get('name')}")

        if self.quantity_spin.value() <= 0:
            QMessageBox.warning(self, "Ошибка", "Укажите количество больше 0")
            self.quantity_spin.setFocus()
            return False

        if self.price_spin.value() <= 0:
            QMessageBox.warning(self, "Ошибка", "Укажите цену больше 0")
            self.price_spin.setFocus()
            return False

        print("=== ВАЛИДАЦИЯ ПРОШЛА УСПЕШНО ===")
        return True