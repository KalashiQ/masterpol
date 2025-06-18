from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QMessageBox,
                             QHeaderView, QLineEdit, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from database.db_manager import DatabaseManager
from datetime import datetime
from ui.add_sale_screen import AddSaleScreen
from ui.edit_sale_screen import EditSaleScreen


class SalesHistoryScreen(QWidget):
    def __init__(self, partner_inn, partner_name, user_type="user", username=""):
        super().__init__()
        self.partner_inn = partner_inn
        self.partner_name = partner_name
        self.user_type = user_type  # "admin" или "user"
        self.username = username
        self.db_manager = DatabaseManager()
        self.partner_discount = 0  # Текущая скидка партнера
        self.init_ui()
        self.load_sales_history()

    def calculate_partner_discount(self, total_quantity):
        """
        Рассчитывает скидку партнера на основе общего количества продукции
        до 10000 – 0%
        от 10000 – до 50000 – 5%
        от 50000 – до 300000 – 10%
        более 300000 – 15%
        """
        if total_quantity < 10000:
            return 0
        elif 10000 <= total_quantity < 50000:
            return 5
        elif 50000 <= total_quantity < 300000:
            return 10
        else:
            return 15

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("История продаж")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Информация о партнере и пользователе
        info_layout = QVBoxLayout()
        partner_info = QLabel(f"Партнер: {self.partner_name}")
        partner_info.setObjectName("partnerInfo")
        partner_info.setAlignment(Qt.AlignCenter)

        user_info = QLabel(f"Пользователь: {self.username} ({self.get_access_level_text()})")
        user_info.setObjectName("userInfo")
        user_info.setAlignment(Qt.AlignCenter)
        user_info.setStyleSheet("""
            QLabel#userInfo {
                font-size: 12px;
                color: #666;
                font-style: italic;
                margin-bottom: 10px;
            }
        """)

        info_layout.addWidget(partner_info)
        info_layout.addWidget(user_info)
        layout.addLayout(info_layout)

        search_layout = QHBoxLayout()
        search_label = QLabel("Поиск по наименованию:")
        search_label.setObjectName("searchLabel")

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Введите название продукции...")
        self.search_edit.setObjectName("searchEdit")
        self.search_edit.textChanged.connect(self.on_search_changed)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        search_layout.addStretch()
        layout.addLayout(search_layout)

        self.stats_frame = QFrame()
        self.stats_frame.setObjectName("statsFrame")
        stats_layout = QHBoxLayout()

        self.total_sales_label = QLabel("Всего продаж: 0")
        self.total_quantity_label = QLabel("Общее количество: 0")
        self.total_sum_label = QLabel("Общая сумма: 0.00 ₽")
        self.discount_label = QLabel("Скидка партнера: 0%")

        self.total_sales_label.setObjectName("statsLabel")
        self.total_quantity_label.setObjectName("statsLabel")
        self.total_sum_label.setObjectName("statsLabel")
        self.discount_label.setObjectName("statsLabel")

        stats_layout.addWidget(self.total_sales_label)
        stats_layout.addWidget(self.total_quantity_label)
        stats_layout.addWidget(self.total_sum_label)
        stats_layout.addWidget(self.discount_label)
        stats_layout.addStretch()

        self.stats_frame.setLayout(stats_layout)
        layout.addWidget(self.stats_frame)

        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels([
            "Дата продажи", "Наименование продукции", "Количество",
            "Цена за единицу", "Общая сумма"
        ])

        header = self.sales_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.sales_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.sales_table.setAlternatingRowColors(True)
        self.sales_table.setSortingEnabled(True)

        # Двойной клик доступен только для админов
        if self.user_type == "admin":
            self.sales_table.doubleClicked.connect(self.edit_sale)

        layout.addWidget(self.sales_table)

        # Добавляем информацию о скидке под таблицей
        discount_frame = QFrame()
        discount_frame.setObjectName("discountFrame")
        discount_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        discount_layout = QHBoxLayout()

        self.discount_info_label = QLabel("Скидка партнера: 0% (общее количество: 0 шт.)")
        self.discount_info_label.setObjectName("discountInfoLabel")
        self.discount_info_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
            }
        """)

        discount_layout.addWidget(self.discount_info_label)
        discount_layout.addStretch()
        discount_frame.setLayout(discount_layout)
        layout.addWidget(discount_frame)

        # Если пользователь не админ, показываем информационное сообщение
        if self.user_type != "admin":
            info_label = QLabel("ℹ️ Режим просмотра: редактирование и удаление записей недоступно")
            info_label.setObjectName("infoLabel")
            info_label.setStyleSheet("""
                QLabel#infoLabel {
                    background-color: #e3f2fd;
                    border: 1px solid #bbdefb;
                    border-radius: 5px;
                    padding: 8px;
                    color: #1976d2;
                    font-size: 12px;
                    margin: 5px 0;
                }
            """)
            layout.addWidget(info_label)

        buttons_layout = QHBoxLayout()

        # Кнопки, доступные только администраторам
        if self.user_type == "admin":
            self.add_btn = QPushButton("Добавить")
            self.edit_btn = QPushButton("Изменить")
            self.delete_btn = QPushButton("Удалить")

            self.add_btn.setObjectName("addBtn")
            self.edit_btn.setObjectName("editBtn")
            self.delete_btn.setObjectName("deleteBtn")

            buttons_layout.addWidget(self.add_btn)
            buttons_layout.addWidget(self.edit_btn)
            buttons_layout.addWidget(self.delete_btn)

            # Подключаем события для административных кнопок
            self.add_btn.clicked.connect(self.add_sale)
            self.edit_btn.clicked.connect(self.edit_sale)
            self.delete_btn.clicked.connect(self.delete_sale)

        # Кнопка "Назад" доступна всем
        self.back_btn = QPushButton("Назад")
        self.back_btn.setObjectName("backBtn")

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.back_btn)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        # Применяем стили для кнопок
        self.apply_button_styles()

        # Подключаем событие для кнопки "Назад"
        self.back_btn.clicked.connect(self.close)

    def apply_button_styles(self):
        """Применяет стили для кнопок"""
        button_style = """
            QPushButton {
                background-color: #f0f0f0;
                color: black;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                min-width: 80px;
            }

            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #999;
                color: black;
            }

            QPushButton:pressed {
                background-color: #d0d0d0;
                color: black;
            }
        """

        delete_button_style = """
            QPushButton#deleteBtn {
                background-color: #ffebee;
                color: black;
                border: 1px solid #f44336;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                min-width: 80px;
            }

            QPushButton#deleteBtn:hover {
                background-color: #ffcdd2;
                border-color: #d32f2f;
                color: black;
            }

            QPushButton#deleteBtn:pressed {
                background-color: #ffb3ba;
                color: black;
            }
        """

        # Применяем стили ко всем кнопкам
        all_buttons = [self.back_btn]

        if self.user_type == "admin":
            all_buttons.extend([self.add_btn, self.edit_btn])

        for button in all_buttons:
            button.setStyleSheet(button_style)

        # Отдельный стиль для кнопки удаления
        if self.user_type == "admin":
            self.delete_btn.setStyleSheet(delete_button_style)

    def get_access_level_text(self):
        """Возвращает текстовое описание уровня доступа"""
        return "Администратор" if self.user_type == "admin" else "Пользователь"

    def load_sales_history(self, search_text=""):
        try:
            sales = self.db_manager.get_partner_sales_history(self.partner_inn, search_text)
            self.sales_table.setRowCount(len(sales))
            total_sum = 0

            # Получаем статистику для расчета скидки
            stats = self.db_manager.get_sales_statistics(self.partner_inn)
            total_quantity = stats['total_quantity'] if stats else 0
            self.partner_discount = self.calculate_partner_discount(total_quantity)

            for row, sale in enumerate(sales):
                sale_date, product_name, quantity, unit_price, total_price, sale_id = sale

                if isinstance(sale_date, str):
                    for fmt in ['%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y']:
                        try:
                            date_obj = datetime.strptime(sale_date, fmt)
                            formatted_date = date_obj.strftime('%d.%m.%Y')
                            break
                        except:
                            continue
                    else:
                        formatted_date = sale_date
                else:
                    formatted_date = sale_date.strftime('%d.%m.%Y') if sale_date else ""

                items = [
                    QTableWidgetItem(formatted_date),
                    QTableWidgetItem(str(product_name) if product_name else ""),
                    QTableWidgetItem(str(quantity) if quantity else "0"),
                    QTableWidgetItem(f"{float(str(unit_price).replace(',', '.')):.2f} ₽" if unit_price else "0.00 ₽"),
                    QTableWidgetItem(f"{float(total_price):.2f} ₽" if total_price else "0.00 ₽")
                ]

                items[0].setTextAlignment(Qt.AlignCenter)
                items[2].setTextAlignment(Qt.AlignCenter)
                items[3].setTextAlignment(Qt.AlignRight)
                items[4].setTextAlignment(Qt.AlignRight)

                for item in items:
                    item.setData(Qt.UserRole, sale_id)

                for col, item in enumerate(items):
                    self.sales_table.setItem(row, col, item)

                if total_price:
                    total_sum += float(total_price)

            # Обновляем информацию о скидке под таблицей
            self.update_discount_info()
            self.update_statistics()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить историю продаж: {str(e)}")

    def update_statistics(self):
        try:
            stats = self.db_manager.get_sales_statistics(self.partner_inn)

            if stats:
                total_quantity = stats['total_quantity']
                discount = self.calculate_partner_discount(total_quantity)

                self.total_sales_label.setText(f"Всего продаж: {stats['total_sales']}")
                self.total_quantity_label.setText(f"Общее количество: {total_quantity}")
                self.total_sum_label.setText(f"Общая сумма: {stats['total_sum']:.2f} ₽")
                self.discount_label.setText(f"Скидка партнера: {discount}%")
            else:
                self.total_sales_label.setText("Всего продаж: 0")
                self.total_quantity_label.setText("Общее количество: 0")
                self.total_sum_label.setText("Общая сумма: 0.00 ₽")
                self.discount_label.setText("Скидка партнера: 0%")

        except Exception as e:
            pass

    def update_discount_info(self):
        """Обновляет информацию о скидке под таблицей"""
        try:
            stats = self.db_manager.get_sales_statistics(self.partner_inn)

            if stats:
                total_quantity = stats['total_quantity']
                discount = self.calculate_partner_discount(total_quantity)

                # Определяем диапазон для текущей скидки
                if total_quantity < 10000:
                    range_text = "до 10 000"
                elif 10000 <= total_quantity < 50000:
                    range_text = "от 10 000 до 50 000"
                elif 50000 <= total_quantity < 300000:
                    range_text = "от 50 000 до 300 000"
                else:
                    range_text = "свыше 300 000"

                self.discount_info_label.setText(
                    f"Скидка партнера: {discount}% "
                    f"(общее количество: {total_quantity:,} шт., диапазон: {range_text})"
                )
            else:
                self.discount_info_label.setText("Скидка партнера: 0% (общее количество: 0 шт., диапазон: до 10 000)")

        except Exception as e:
            self.discount_info_label.setText("Скидка партнера: 0% (ошибка расчета)")

    def on_search_changed(self):
        search_text = self.search_edit.text().strip()
        self.load_sales_history(search_text)

    def get_selected_sale_id(self):
        current_row = self.sales_table.currentRow()
        if current_row < 0:
            return None

        for col in range(self.sales_table.columnCount()):
            item = self.sales_table.item(current_row, col)
            if item:
                sale_id = item.data(Qt.UserRole)
                if sale_id is not None:
                    return sale_id

        return None

    def get_selected_sale_info(self):
        current_row = self.sales_table.currentRow()
        if current_row < 0:
            return None, None, None, None, None

        date_item = self.sales_table.item(current_row, 0)
        product_item = self.sales_table.item(current_row, 1)
        quantity_item = self.sales_table.item(current_row, 2)
        sum_item = self.sales_table.item(current_row, 4)

        date_text = date_item.text() if date_item else "неизвестно"
        product_text = product_item.text() if product_item else "неизвестно"
        quantity_text = quantity_item.text() if quantity_item else "неизвестно"
        sum_text = sum_item.text() if sum_item else "неизвестно"
        sale_id = self.get_selected_sale_id()

        return sale_id, date_text, product_text, quantity_text, sum_text

    def edit_sale(self):
        """Редактирование продажи (только для администраторов)"""
        if self.user_type != "admin":
            QMessageBox.warning(self, "Доступ запрещен",
                                "У вас нет прав для выполнения этого действия")
            return

        sale_id, date_text, product_text, quantity_text, sum_text = self.get_selected_sale_info()

        if not sale_id:
            QMessageBox.warning(self, "Предупреждение",
                                "Выберите продажу для редактирования.\n\n"
                                "Убедитесь, что вы кликнули на строку в таблице.")
            return

        try:
            self.edit_sale_window = EditSaleScreen(self.partner_inn, self.partner_name, sale_id)
            self.edit_sale_window.sale_updated.connect(lambda: self.load_sales_history(self.search_edit.text().strip()))
            self.edit_sale_window.setWindowTitle(f"Редактирование продажи - {product_text} от {date_text}")
            self.edit_sale_window.setFixedSize(500, 450)
            self.edit_sale_window.show()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть окно редактирования продажи: {str(e)}")

    def delete_sale(self):
        """Удаление продажи (только для администраторов)"""
        if self.user_type != "admin":
            QMessageBox.warning(self, "Доступ запрещен",
                                "У вас нет прав для выполнения этого действия")
            return

        sale_id, date_text, product_text, quantity_text, sum_text = self.get_selected_sale_info()

        if not sale_id:
            QMessageBox.warning(self, "Предупреждение",
                                "Выберите продажу для удаления.\n\n"
                                "Убедитесь, что вы кликнули на строку в таблице.")
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить продажу?\n\n"
            f"Дата: {date_text}\n"
            f"Продукт: {product_text}\n"
            f"Количество: {quantity_text}\n"
            f"Сумма: {sum_text}",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                if self.db_manager.delete_sale(sale_id):
                    QMessageBox.information(self, "Успех", "Продажа успешно удалена")
                    self.load_sales_history(self.search_edit.text().strip())
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить продажу")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении продажи: {str(e)}")

    def add_sale(self):
        """Добавление продажи (только для администраторов)"""
        if self.user_type != "admin":
            QMessageBox.warning(self, "Доступ запрещен",
                                "У вас нет прав для выполнения этого действия")
            return

        try:
            self.add_sale_window = AddSaleScreen(self.partner_inn, self.partner_name)
            self.add_sale_window.sale_added.connect(lambda: self.load_sales_history(self.search_edit.text().strip()))
            self.add_sale_window.setWindowTitle(f"Добавление продажи - {self.partner_name}")
            self.add_sale_window.setFixedSize(500, 400)
            self.add_sale_window.show()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть окно добавления продажи: {str(e)}")