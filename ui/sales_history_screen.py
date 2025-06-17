from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QMessageBox,
                             QHeaderView, QLineEdit, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from database.db_manager import DatabaseManager
from datetime import datetime


class SalesHistoryScreen(QWidget):
    def __init__(self, partner_inn, partner_name):
        super().__init__()
        self.partner_inn = partner_inn
        self.partner_name = partner_name
        self.db_manager = DatabaseManager()
        self.init_ui()
        self.load_sales_history()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Заголовок
        title = QLabel("История продаж")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Информация о партнере
        partner_info = QLabel(f"Партнер: {self.partner_name}")
        partner_info.setObjectName("partnerInfo")
        partner_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(partner_info)

        # Поиск
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

        # Статистика
        self.stats_frame = QFrame()
        self.stats_frame.setObjectName("statsFrame")
        stats_layout = QHBoxLayout()

        self.total_sales_label = QLabel("Всего продаж: 0")
        self.total_quantity_label = QLabel("Общее количество: 0")
        self.total_sum_label = QLabel("Общая сумма: 0.00 ₽")

        self.total_sales_label.setObjectName("statsLabel")
        self.total_quantity_label.setObjectName("statsLabel")
        self.total_sum_label.setObjectName("statsLabel")

        stats_layout.addWidget(self.total_sales_label)
        stats_layout.addWidget(self.total_quantity_label)
        stats_layout.addWidget(self.total_sum_label)
        stats_layout.addStretch()

        self.stats_frame.setLayout(stats_layout)
        layout.addWidget(self.stats_frame)

        # Таблица истории продаж
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels([
            "Дата продажи", "Наименование продукции", "Количество",
            "Цена за единицу", "Общая сумма"
        ])

        # Настройка таблицы
        header = self.sales_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Дата
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Наименование
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Количество
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Цена
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Сумма

        self.sales_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.sales_table.setAlternatingRowColors(True)
        self.sales_table.setSortingEnabled(True)

        layout.addWidget(self.sales_table)

        # Кнопки
        buttons_layout = QHBoxLayout()

        self.add_btn = QPushButton("Добавить")
        self.edit_btn = QPushButton("Изменить")
        self.delete_btn = QPushButton("Удалить")
        self.back_btn = QPushButton(" Назад")

        self.add_btn.setObjectName("addBtn")
        self.edit_btn.setObjectName("editBtn")
        self.delete_btn.setObjectName("deleteBtn")
        self.back_btn.setObjectName("backBtn")

        # Отключаем кнопки добавления и изменения (будут реализованы позже)
        self.add_btn.setEnabled(False)
        self.edit_btn.setEnabled(False)

        buttons_layout.addWidget(self.add_btn)
        buttons_layout.addWidget(self.edit_btn)
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.back_btn)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        # Подключение сигналов
        self.delete_btn.clicked.connect(self.delete_sale)
        self.back_btn.clicked.connect(self.close)

    def load_sales_history(self, search_text=""):
        """Загружает историю продаж партнера"""
        try:
            print("=== ЗАГРУЗКА ИСТОРИИ ПРОДАЖ ===")
            print(f"Партнер: {self.partner_name} (ИНН: {self.partner_inn})")
            print(f"Поиск: '{search_text}'")

            sales = self.db_manager.get_partner_sales_history(self.partner_inn, search_text)
            self.sales_table.setRowCount(len(sales))

            total_sum = 0

            for row, sale in enumerate(sales):
                # sale содержит: (SaleDate, ProductName, Quantity, MinPartnerPrice, TotalSum, SaleID)
                sale_date, product_name, quantity, unit_price, total_price, sale_id = sale

                # Форматируем дату
                if isinstance(sale_date, str):
                    try:
                        # Пробуем разные форматы даты
                        for fmt in ['%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y']:
                            try:
                                date_obj = datetime.strptime(sale_date, fmt)
                                formatted_date = date_obj.strftime('%d.%m.%Y')
                                break
                            except:
                                continue
                        else:
                            formatted_date = sale_date
                    except:
                        formatted_date = sale_date
                else:
                    formatted_date = sale_date.strftime('%d.%m.%Y') if sale_date else ""

                # Заполняем таблицу
                items = [
                    QTableWidgetItem(formatted_date),
                    QTableWidgetItem(str(product_name) if product_name else ""),
                    QTableWidgetItem(str(quantity) if quantity else "0"),
                    QTableWidgetItem(f"{float(str(unit_price).replace(',', '.')):.2f} ₽" if unit_price else "0.00 ₽"),
                    QTableWidgetItem(f"{float(total_price):.2f} ₽" if total_price else "0.00 ₽")
                ]

                # Выравнивание
                items[0].setTextAlignment(Qt.AlignCenter)  # Дата
                items[2].setTextAlignment(Qt.AlignCenter)  # Количество
                items[3].setTextAlignment(Qt.AlignRight)  # Цена
                items[4].setTextAlignment(Qt.AlignRight)  # Сумма

                # Сохраняем SaleID в первом элементе для удаления
                items[0].setData(Qt.UserRole, sale_id)

                for col, item in enumerate(items):
                    self.sales_table.setItem(row, col, item)

                # Считаем общую сумму
                if total_price:
                    total_sum += float(total_price)

            # Обновляем статистику
            self.update_statistics()

            print(f"Загружено продаж: {len(sales)}")
            print("=== ЗАГРУЗКА ЗАВЕРШЕНА ===")

        except Exception as e:
            print(f"Ошибка при загрузке истории продаж: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить историю продаж: {str(e)}")

    def update_statistics(self):
        """Обновляет статистику продаж"""
        try:
            stats = self.db_manager.get_sales_statistics(self.partner_inn)

            if stats:
                self.total_sales_label.setText(f"Всего продаж: {stats['total_sales']}")
                self.total_quantity_label.setText(f"Общее количество: {stats['total_quantity']}")
                self.total_sum_label.setText(f"Общая сумма: {stats['total_sum']:.2f} ₽")
            else:
                self.total_sales_label.setText("Всего продаж: 0")
                self.total_quantity_label.setText("Общее количество: 0")
                self.total_sum_label.setText("Общая сумма: 0.00 ₽")

        except Exception as e:
            print(f"Ошибка при обновлении статистики: {e}")

    def on_search_changed(self):
        """Обработчик изменения поискового запроса"""
        search_text = self.search_edit.text().strip()
        self.load_sales_history(search_text)

    def get_selected_sale_id(self):
        """Получает ID выбранной продажи"""
        current_row = self.sales_table.currentRow()
        if current_row >= 0:
            date_item = self.sales_table.item(current_row, 0)
            if date_item:
                return date_item.data(Qt.UserRole)
        return None

    def delete_sale(self):
        """Удаляет выбранную продажу"""
        sale_id = self.get_selected_sale_id()
        if not sale_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите продажу для удаления")
            return

        # Получаем информацию о продаже для подтверждения
        current_row = self.sales_table.currentRow()
        date_item = self.sales_table.item(current_row, 0)
        product_item = self.sales_table.item(current_row, 1)

        date_text = date_item.text() if date_item else "неизвестно"
        product_text = product_item.text() if product_item else "неизвестно"

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить продажу?\n\n"
            f"Дата: {date_text}\n"
            f"Продукт: {product_text}",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                if self.db_manager.delete_sale(sale_id):
                    QMessageBox.information(self, "Успех", "Продажа успешно удалена")
                    # Перезагружаем данные
                    search_text = self.search_edit.text().strip()
                    self.load_sales_history(search_text)
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить продажу")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении продажи: {str(e)}")