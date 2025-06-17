from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QMessageBox,
                             QHeaderView)
from PyQt5.QtCore import Qt
from database.db_manager import DatabaseManager
from ui.add_partner_screen import AddPartnerScreen
from ui.edit_partner_screen import EditPartnerScreen
from ui.partner_products_screen import PartnerProductsScreen
from ui.sales_history_screen import SalesHistoryScreen


class PartnersScreen(QWidget):
    def __init__(self, user_type="user", username=""):
        super().__init__()
        self.user_type = user_type  # "admin" или "user"
        self.username = username
        self.db_manager = DatabaseManager()
        self.init_ui()
        self.load_partners()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок с информацией о пользователе
        title_layout = QVBoxLayout()
        title = QLabel("Партнеры")
        title.setObjectName("title")
        title.setStyleSheet("""
            QLabel#title {
                font-size: 28px;
                font-weight: bold;
                color: black;
                margin-bottom: 10px;
                padding: 10px 0px;
            }
        """)
        title_layout.addWidget(title)

        # Показываем тип доступа
        access_info = QLabel(f"Пользователь: {self.username} ({self.get_access_level_text()})")
        access_info.setObjectName("accessInfo")
        access_info.setStyleSheet("""
            QLabel#accessInfo {
                font-size: 12px;
                color: #666;
                font-style: italic;
                margin-bottom: 20px;
                padding: 15px 20px;
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 5px;
                min-height: 40px;
                line-height: 1.5;
            }
        """)
        title_layout.addWidget(access_info)

        layout.addLayout(title_layout)

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

        # Кнопки, доступные всем пользователям
        self.products_btn = QPushButton("Продукция")
        self.history_btn = QPushButton("История продаж")
        self.update_btn = QPushButton("Обновить")

        # Кнопки, доступные только администраторам
        self.add_btn = QPushButton("Добавить")
        self.edit_btn = QPushButton("Редактировать")
        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.setObjectName("deleteBtn")

        # Добавляем кнопки в зависимости от типа пользователя
        if self.user_type == "admin":
            buttons_layout.addWidget(self.add_btn)
            buttons_layout.addWidget(self.edit_btn)
            buttons_layout.addWidget(self.delete_btn)

        buttons_layout.addWidget(self.products_btn)
        buttons_layout.addWidget(self.history_btn)
        buttons_layout.addWidget(self.update_btn)

        # Если пользователь не админ, показываем информационное сообщение
        if self.user_type != "admin":
            info_label = QLabel("ℹ️ Режим просмотра: доступны только функции просмотра данных")
            info_label.setObjectName("infoLabel")
            info_label.setStyleSheet("""
                QLabel#infoLabel {
                    background-color: #e3f2fd;
                    border: 1px solid #bbdefb;
                    border-radius: 5px;
                    padding: 8px;
                    color: #1976d2;
                    font-size: 12px;
                    margin: 5px;
                }
            """)
            layout.addWidget(info_label)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        # Применяем стили для черного цвета текста кнопок
        self.apply_button_styles()

        # Подключаем события для кнопок, доступных администраторам
        if self.user_type == "admin":
            self.add_btn.clicked.connect(self.add_partner)
            self.edit_btn.clicked.connect(self.edit_partner)
            self.delete_btn.clicked.connect(self.delete_partner)

        # Подключаем события для кнопок, доступных всем
        self.products_btn.clicked.connect(self.show_products)
        self.history_btn.clicked.connect(self.show_history)
        self.update_btn.clicked.connect(self.load_partners)

    def apply_button_styles(self):
        """Применяет стили с черным цветом текста для всех кнопок"""
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
        all_buttons = [self.products_btn, self.history_btn, self.update_btn]

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
        """Удаление партнера (только для администраторов)"""
        if self.user_type != "admin":
            QMessageBox.warning(self, "Доступ запрещен",
                                "У вас нет прав для выполнения этого действия")
            return

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
        """Добавление партнера (только для администраторов)"""
        if self.user_type != "admin":
            QMessageBox.warning(self, "Доступ запрещен",
                                "У вас нет прав для выполнения этого действия")
            return

        self.add_partner_window = AddPartnerScreen()
        self.add_partner_window.partner_added.connect(self.load_partners)
        self.add_partner_window.setWindowTitle("Добавление партнера")
        self.add_partner_window.setFixedSize(800, 600)
        self.add_partner_window.show()

    def edit_partner(self):
        """Редактирование партнера (только для администраторов)"""
        if self.user_type != "admin":
            QMessageBox.warning(self, "Доступ запрещен",
                                "У вас нет прав для выполнения этого действия")
            return

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
        """Просмотр продукции партнера (доступно всем)"""
        inn = self.get_selected_partner_inn()
        if not inn:
            QMessageBox.warning(self, "Предупреждение", "Выберите партнера для просмотра продукции")
            return

        try:
            partner_name = self.db_manager.get_partner_name_by_inn(inn)
            # Исправленный вызов конструктора - только необходимые аргументы
            self.products_window = PartnerProductsScreen(inn, partner_name)
            self.products_window.setWindowTitle(f"Продукция - {partner_name}")
            self.products_window.setFixedSize(1000, 700)
            self.products_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть экран продукции: {str(e)}")

    def show_history(self):
        """Просмотр истории продаж (доступно всем)"""
        inn = self.get_selected_partner_inn()
        if not inn:
            QMessageBox.warning(self, "Предупреждение", "Выберите партнера для просмотра истории продаж")
            return

        try:
            partner_name = self.db_manager.get_partner_name_by_inn(inn)
            # Исправленный вызов конструктора - только необходимые аргументы
            self.history_window = SalesHistoryScreen(inn, partner_name)
            self.history_window.setWindowTitle(f"История продаж - {partner_name}")
            self.history_window.setFixedSize(1200, 800)
            self.history_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть экран истории продаж: {str(e)}")