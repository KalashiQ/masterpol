from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QLabel, QLineEdit, QMessageBox,
                             QHeaderView, QFrame, QPushButton)
from PyQt5.QtCore import Qt, QTimer
from database.db_manager import DatabaseManager


class PartnerProductsScreen(QWidget):
    def __init__(self, partner_inn, partner_name):
        super().__init__()
        self.partner_inn = partner_inn
        self.partner_name = partner_name
        self.db_manager = DatabaseManager()
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.search_products)
        self.init_ui()
        self.load_products()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Заголовок
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

        # Контент
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout()

        # Информация о партнере
        partner_info = QLabel(f"Партнер: {self.partner_name}")
        partner_info.setObjectName("partnerInfo")
        content_layout.addWidget(partner_info)

        # Поиск
        search_layout = QHBoxLayout()
        search_label = QLabel("Поиск:")
        search_label.setObjectName("searchLabel")

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Введите название продукции для поиска...")
        self.search_edit.setObjectName("searchField")
        self.search_edit.textChanged.connect(self.on_search_text_changed)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        content_layout.addLayout(search_layout)

        # Таблица продукции
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(4)
        self.products_table.setHorizontalHeaderLabels([
            "Наименование продукции", "Артикул", "Тип продукции", "Мин. стоимость"
        ])

        # Настройка заголовков таблицы
        header = self.products_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Наименование растягивается
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Артикул по содержимому
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Тип по содержимому
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Стоимость по содержимому

        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setSortingEnabled(True)

        content_layout.addWidget(self.products_table)
        content_frame.setLayout(content_layout)
        main_layout.addWidget(content_frame)

        # Кнопки управления
        buttons_frame = QFrame()
        buttons_frame.setObjectName("buttonsFrame")
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.setContentsMargins(20, 10, 20, 20)

        # Добавляем растяжку слева
        buttons_layout.addStretch()

        # Кнопки
        self.add_btn = QPushButton("➕ Добавить")
        self.add_btn.setObjectName("addBtn")

        self.edit_btn = QPushButton("✏️ Изменить")
        self.edit_btn.setObjectName("editBtn")

        self.delete_btn = QPushButton("🗑️ Удалить")
        self.delete_btn.setObjectName("deleteBtn")

        self.back_btn = QPushButton("⬅️ Назад")
        self.back_btn.setObjectName("backBtn")

        # Добавляем кнопки в layout
        buttons_layout.addWidget(self.add_btn)
        buttons_layout.addWidget(self.edit_btn)
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addWidget(self.back_btn)

        buttons_frame.setLayout(buttons_layout)
        main_layout.addWidget(buttons_frame)

        self.setLayout(main_layout)

        # Подключение сигналов кнопок
        self.add_btn.clicked.connect(self.add_product)
        self.edit_btn.clicked.connect(self.edit_product)
        self.delete_btn.clicked.connect(self.delete_product)
        self.back_btn.clicked.connect(self.close)

    def load_products(self, search_text=""):
        """Загружает продукцию партнера"""
        try:
            # Сначала пробуем получить продукцию конкретного партнера
            products = self.db_manager.get_partner_products_by_inn(self.partner_inn, search_text)

            # Если продукции нет, получаем все продукты
            if not products:
                products = self.db_manager.get_partner_products("", search_text)

            self.products_table.setRowCount(len(products))

            for row, product in enumerate(products):
                # product содержит: (ProductName, ArticleNumber, ProductType, MinPartnerPrice)
                product_name, article_number, product_type, min_price = product

                # Наименование продукции
                name_item = QTableWidgetItem(str(product_name) if product_name else "")
                self.products_table.setItem(row, 0, name_item)

                # Артикул
                article_item = QTableWidgetItem(str(article_number) if article_number else "")
                article_item.setTextAlignment(Qt.AlignCenter)
                self.products_table.setItem(row, 1, article_item)

                # Тип продукции
                type_item = QTableWidgetItem(str(product_type) if product_type else "")
                type_item.setTextAlignment(Qt.AlignCenter)
                self.products_table.setItem(row, 2, type_item)

                # Минимальная стоимость
                if min_price is not None:
                    price_text = f"{min_price:,.2f} ₽"
                    price_item = QTableWidgetItem(price_text)
                    price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    price_item = QTableWidgetItem("")
                self.products_table.setItem(row, 3, price_item)

            # Обновляем информацию о количестве найденных товаров
            count_text = f"Найдено товаров: {len(products)}"
            if hasattr(self, 'count_label'):
                self.count_label.setText(count_text)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить продукцию: {str(e)}")

    def on_search_text_changed(self):
        """Обработчик изменения текста поиска с задержкой"""
        self.search_timer.stop()
        self.search_timer.start(300)  # Задержка 300мс для оптимизации

    def search_products(self):
        """Выполняет поиск продукции"""
        search_text = self.search_edit.text().strip()
        self.load_products(search_text)

    def get_selected_product_article(self):
        """Получает артикул выбранного продукта"""
        current_row = self.products_table.currentRow()
        if current_row >= 0:
            article_item = self.products_table.item(current_row, 1)  # Колонка "Артикул"
            return article_item.text() if article_item else None
        return None

    def add_product(self):
        """Добавляет новый продукт"""
        QMessageBox.information(self, "Информация", "Функция добавления продукта будет реализована позже")

    def edit_product(self):
        """Редактирует выбранный продукт"""
        article = self.get_selected_product_article()
        if not article:
            QMessageBox.warning(self, "Предупреждение", "Выберите продукт для редактирования")
            return

        QMessageBox.information(self, "Информация",
                                f"Функция редактирования продукта '{article}' будет реализована позже")

    def delete_product(self):
        """Удаляет выбранный продукт"""
        article = self.get_selected_product_article()
        if not article:
            QMessageBox.warning(self, "Предупреждение", "Выберите продукт для удаления")
            return

        # Получаем название продукта для подтверждения
        current_row = self.products_table.currentRow()
        product_name = ""
        if current_row >= 0:
            name_item = self.products_table.item(current_row, 0)
            product_name = name_item.text() if name_item else ""

        # Подтверждение удаления
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить продукт:\n\n'{product_name}' (Артикул: {article})?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                if self.db_manager.delete_product(article):
                    QMessageBox.information(self, "Успех", "Продукт успешно удален")
                    self.load_products()  # Обновляем таблицу
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить продукт")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении продукта: {str(e)}")