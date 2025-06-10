MAIN_STYLE = """
QMainWindow {
    background-color: #fefae0;
    font-family: 'Segoe UI', Arial, sans-serif;
}

QLabel#title {
    font-size: 18px;
    font-weight: bold;
    color: #283618;
    padding: 10px;
}

QTableWidget {
    background-color: #fefae0;
    border: 1px solid #dda15e;
    gridline-color: #dda15e;
    selection-background-color: #606c38;
    font-size: 11px;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #dda15e;
    color: #283618;
    background-color: #fefae0;
    border: none;
    margin: 0px;
}

QTableWidget::item:selected {
    background-color: #606c38;
    color: #fefae0;
    border: none;
    margin: 0px;
}

QTableWidget::item:alternate {
    padding: 8px;
    background-color: #dda15e;
    color: #283618;
    border: none;
    margin: 0px;
}

QTableWidget::item:alternate:selected {
    padding: 8px;
    background-color: #606c38;
    color: #fefae0;
    border: none;
    margin: 0px;
}

QHeaderView::section {
    background-color: #283618;
    color: #fefae0;
    font-weight: bold;
    padding: 10px;
    border: none;
    font-size: 11px;
}

QPushButton {
    background-color: #606c38;
    color: #fefae0;
    border: none;
    padding: 12px 20px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: bold;
    min-width: 100px;
}

QPushButton:hover {
    background-color: #dda15e;
    color: #283618;
}

QPushButton:pressed {
    background-color: #283618;
    color: #fefae0;
}

QPushButton#deleteBtn {
    background-color: #bc6c25;
    color: #fefae0;
}

QPushButton#deleteBtn:hover {
    background-color: #283618;
    color: #fefae0;
}

QPushButton#deleteBtn:pressed {
    background-color: #606c38;
    color: #fefae0;
}

QHBoxLayout {
    spacing: 10px;
}

QVBoxLayout {
    spacing: 10px;
}
"""