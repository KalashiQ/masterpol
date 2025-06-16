import sys
from PyQt5.QtWidgets import QApplication
from database.db_manager import DatabaseManager
from ui.main_window import MainWindow


def main():
    db_manager = DatabaseManager()
    db_manager.fix_partner_table_structure()
    db_manager.add_partner_id_to_products_table()
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()