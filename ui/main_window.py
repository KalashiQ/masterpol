from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt
from ui.partners_screen import PartnersScreen
from styles.styles import MAIN_STYLE


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Мастер-пол")
        self.setGeometry(100, 100, 1200, 700)

        self.setStyleSheet(MAIN_STYLE)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.partners_screen = PartnersScreen()
        self.stacked_widget.addWidget(self.partners_screen)

        self.stacked_widget.setCurrentWidget(self.partners_screen)