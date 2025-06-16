from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QMessageBox,
                             QHeaderView)
from PyQt5.QtCore import Qt
from database.db_manager import DatabaseManager
from ui.add_partner_screen import AddPartnerScreen
from ui.edit_partner_screen import EditPartnerScreen
from ui.partner_products_screen import PartnerProductsScreen



class PartnersScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.init_ui()
        self.load_partners()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Партнеры")
        title.setObjectName("title")
        layout.addWidget(title)

        self.partners_table = QTableWidget()
        self.partners_table.setColumnCount(8)
        self.partners_table.setHorizontalHeaderLabels([
            "Тип", "Наименование", "Директор", "Телефон",
            "Email", "Адрес", "ИНН", "Рейтинг"
        ])

        header = self.partners_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Stretch)

        self.partners_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.partners_table.setAlternatingRowColors(True)

        layout.addWidget(self.partners_table)

        buttons_layout = QHBoxLayout()

        self.add_btn = QPushButton("Добавить")
        self.edit_btn = QPushButton("Редактировать")
        self.products_btn = QPushButton("Продукция")
        self.history_btn = QPushButton("История продаж")
        self.delete_btn = QPushButton("Удалить")
        self.update_btn = QPushButton("Обновить")

        self.delete_btn.setObjectName("deleteBtn")

        buttons_layout.addWidget(self.add_btn)
        buttons_layout.addWidget(self.edit_btn)
        buttons_layout.addWidget(self.products_btn)
        buttons_layout.addWidget(self.history_btn)
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addWidget(self.update_btn)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        self.add_btn.clicked.connect(self.add_partner)
        self.edit_btn.clicked.connect(self.edit_partner)
        self.products_btn.clicked.connect(self.show_products)
        self.history_btn.clicked.connect(self.show_history)
        self.delete_btn.clicked.connect(self.delete_partner)
        self.update_btn.clicked.connect(self.load_partners)

    def load_partners(self):
        try:
            partners = self.db_manager.get_all_partners()
            self.partners_table.setRowCount(len(partners))

            for row, partner in enumerate(partners):
                for col, value in enumerate(partner):
                    item = QTableWidgetItem(str(value) if value else "")
                    if col == 7:
                        item.setTextAlignment(Qt.AlignCenter)
                    self.partners_table.setItem(row, col, item)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {str(e)}")

    def get_selected_partner_inn(self):
        current_row = self.partners_table.currentRow()
        if current_row >= 0:
            inn_item = self.partners_table.item(current_row, 6)
            return inn_item.text() if inn_item else None
        return None

    def delete_partner(self):
        inn = self.get_selected_partner_inn()
        if not inn:
            QMessageBox.warning(self, "Предупреждение", "Выберите партнера для удаления")
            return

        reply = QMessageBox.question(self, "Подтверждение",
                                     "Вы уверены, что хотите удалить выбранного партнера?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                if self.db_manager.delete_partner(inn):
                    QMessageBox.information(self, "Успех", "Партнер успешно удален")
                    self.load_partners()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить партнера")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {str(e)}")

    def add_partner(self):
        self.add_partner_window = AddPartnerScreen()
        self.add_partner_window.partner_added.connect(self.load_partners)
        self.add_partner_window.setWindowTitle("Добавление партнера")
        self.add_partner_window.setFixedSize(800, 600)
        self.add_partner_window.show()

    def edit_partner(self):
        inn = self.get_selected_partner_inn()
        if not inn:
            QMessageBox.warning(self, "Предупреждение", "Выберите партнера для редактирования")
            return

        self.edit_partner_window = EditPartnerScreen(inn)
        self.edit_partner_window.partner_updated.connect(self.load_partners)
        self.edit_partner_window.setWindowTitle("Редактирование партнера")
        self.edit_partner_window.setFixedSize(800, 600)
        self.edit_partner_window.show()

    def show_products(self):
        """Показывает продукцию выбранного партнера"""
        inn = self.get_selected_partner_inn()
        if not inn:
            QMessageBox.warning(self, "Предупреждение", "Выберите партнера для просмотра продукции")
            return

        try:
            # Получаем название партнера для отображения в заголовке
            partner_name = self.db_manager.get_partner_name_by_inn(inn)

            # Импортируем и создаем окно продукции
            from ui.partner_products_screen import PartnerProductsScreen

            self.products_window = PartnerProductsScreen(inn, partner_name)
            self.products_window.setWindowTitle(f"Продукция - {partner_name}")
            self.products_window.setFixedSize(1000, 700)
            self.products_window.show()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть экран продукции: {str(e)}")
            print(f"Подробная ошибка: {e}")

    def show_history(self):
        QMessageBox.information(self, "Информация", "Экран истории продаж будет реализован позже")