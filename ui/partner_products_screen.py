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

        partner_info = QLabel("Партнер: {} (ИНН: {})".format(self.partner_name, self.partner_inn))
        partner_info.setObjectName("partnerInfo")
        content_layout.addWidget(partner_info)

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

        self.products_table = QTableWidget()
        self.products_table.setColumnCount(4)
        self.products_table.setHorizontalHeaderLabels([
            "Наименование продукции", "Артикул", "Тип продукции", "Мин. стоимость"
        ])

        header = self.products_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setSortingEnabled(True)

        content_layout.addWidget(self.products_table)
        content_frame.setLayout(content_layout)
        main_layout.addWidget(content_frame)

        buttons_frame = QFrame()
        buttons_frame.setObjectName("buttonsFrame")
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.setContentsMargins(20, 10, 20, 20)

        buttons_layout.addStretch()

        self.add_btn = QPushButton("Добавить")
        self.add_btn.setObjectName("addBtn")

        self.edit_btn = QPushButton("Изменить")
        self.edit_btn.setObjectName("editBtn")

        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.setObjectName("deleteBtn")

        self.back_btn = QPushButton("Назад")
        self.back_btn.setObjectName("backBtn")

        buttons_layout.addWidget(self.add_btn)
        buttons_layout.addWidget(self.edit_btn)
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addWidget(self.back_btn)

        buttons_frame.setLayout(buttons_layout)
        main_layout.addWidget(buttons_frame)

        self.setLayout(main_layout)

        self.add_btn.clicked.connect(self.add_product)
        self.edit_btn.clicked.connect(self.edit_product)
        self.delete_btn.clicked.connect(self.delete_product)
        self.back_btn.clicked.connect(self.close)

    def load_products(self, search_text=""):
        try:
            products = self.db_manager.get_partner_products_by_partner_id(self.partner_inn, search_text)
            self.products_table.setRowCount(len(products))

            for row, product in enumerate(products):
                product_name, article_number, product_type, min_price = product

                name_item = QTableWidgetItem(str(product_name) if product_name else "")
                self.products_table.setItem(row, 0, name_item)

                article_item = QTableWidgetItem(str(article_number) if article_number else "")
                article_item.setTextAlignment(Qt.AlignCenter)
                self.products_table.setItem(row, 1, article_item)

                type_item = QTableWidgetItem(str(product_type) if product_type else "")
                type_item.setTextAlignment(Qt.AlignCenter)
                self.products_table.setItem(row, 2, type_item)

                if min_price is not None:
                    try:
                        if isinstance(min_price, str):
                            min_price = float(min_price.replace(',', '.'))
                        else:
                            min_price = float(min_price)
                        price_text = "{:,.2f} ₽".format(min_price)
                        price_item = QTableWidgetItem(price_text)
                        price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    except (ValueError, TypeError):
                        price_item = QTableWidgetItem(str(min_price))
                else:
                    price_item = QTableWidgetItem("")
                self.products_table.setItem(row, 3, price_item)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить продукцию: {}".format(str(e)))

    def on_search_text_changed(self):
        self.search_timer.stop()
        self.search_timer.start(300)

    def search_products(self):
        search_text = self.search_edit.text().strip()
        self.load_products(search_text)

    def get_selected_product_article(self):
        current_row = self.products_table.currentRow()
        if current_row >= 0:
            article_item = self.products_table.item(current_row, 1)
            return article_item.text() if article_item else None
        return None

    def add_product(self):
        try:
            from ui.add_product_screen import AddProductScreen
            self.add_product_window = AddProductScreen(self.partner_inn)
            self.add_product_window.product_added.connect(self.load_products)
            self.add_product_window.setWindowTitle("Добавление продукции")
            self.add_product_window.setFixedSize(600, 500)
            self.add_product_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Не удалось открыть окно добавления: {}".format(str(e)))

    def edit_product(self):
        article = self.get_selected_product_article()
        if not article:
            QMessageBox.warning(self, "Предупреждение", "Выберите продукт для редактирования")
            return

        try:
            product_data = self.db_manager.get_product_by_article(article)
            if not product_data:
                QMessageBox.warning(self, "Ошибка", "Не удалось найти данные продукта")
                return

            from ui.edit_product_screen import EditProductScreen
            self.edit_product_window = EditProductScreen(product_data, self.partner_inn)
            self.edit_product_window.product_updated.connect(self.load_products)
            self.edit_product_window.setWindowTitle("Редактирование продукции")
            self.edit_product_window.setFixedSize(600, 500)
            self.edit_product_window.show()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть окно редактирования: {str(e)}")

    def get_selected_product_data(self):
        current_row = self.products_table.currentRow()
        if current_row >= 0:
            try:
                name_item = self.products_table.item(current_row, 0)
                article_item = self.products_table.item(current_row, 1)
                type_item = self.products_table.item(current_row, 2)
                price_item = self.products_table.item(current_row, 3)

                price_text = price_item.text() if price_item else "0"
                price_clean = price_text.replace("₽", "").replace(" ", "").replace(",", ".")

                return {
                    'ProductName': name_item.text() if name_item else "",
                    'ArticleNumber': article_item.text() if article_item else "",
                    'ProductTypeID': type_item.text() if type_item else "",
                    'MinPartnerPrice': price_clean
                }
            except Exception:
                return None
        return None

    def delete_product(self):
        article = self.get_selected_product_article()
        if not article:
            QMessageBox.warning(self, "Предупреждение", "Выберите продукт для удаления")
            return

        current_row = self.products_table.currentRow()
        product_name = ""
        if current_row >= 0:
            name_item = self.products_table.item(current_row, 0)
            product_name = name_item.text() if name_item else ""

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить продукт:\n\n'{}' (Артикул: {})?".format(product_name, article),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                if self.db_manager.delete_product(article):
                    QMessageBox.information(self, "Успех", "Продукт успешно удален")
                    self.load_products()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить продукт")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", "Ошибка при удалении продукта: {}".format(str(e)))