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

QLabel#headerTitle {
    font-size: 20px;
    font-weight: bold;
    color: #283618;
    padding: 15px 10px;
}

QLabel#iconLabel {
    font-size: 18px;
    padding: 15px 5px;
}

QFrame#headerFrame {
    background-color: #fefae0;
    border-bottom: 2px solid #dda15e;
    padding: 5px;
}

QFrame#contentFrame {
    background-color: #fefae0;
    padding: 20px;
}

/* Информация о партнере */
QLabel#partnerInfo {
    font-size: 14px;
    font-weight: bold;
    color: #606c38;
    padding: 10px 0px;
    background-color: #f4f3ee;
    border: 1px solid #dda15e;
    border-radius: 4px;
    padding-left: 10px;
}

/* Поле поиска */
QLabel#searchLabel {
    font-size: 12px;
    font-weight: bold;
    color: #283618;
    min-width: 50px;
}

QLineEdit#searchField {
    background-color: #fefae0;
    border: 2px solid #dda15e;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
    color: #283618;
}

QLineEdit#searchField:focus {
    border-color: #606c38;
    background-color: #f4f3ee;
}

QLineEdit#searchField::placeholder {
    color: #8b8680;
    font-style: italic;
}

QFrame#buttonsFrame {
    background-color: #fefae0;
    border-top: 1px solid #dda15e;
}

/* Кнопки управления продукцией */
QPushButton#addBtn {
    background-color: #606c38;
    color: #fefae0;
    border: none;
    padding: 10px 15px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: bold;
    min-width: 100px;
}

QPushButton#addBtn:hover {
    background-color: #dda15e;
    color: #283618;
}

QPushButton#editBtn {
    background-color: #bc6c25;
    color: #fefae0;
    border: none;
    padding: 10px 15px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: bold;
    min-width: 100px;
}

QPushButton#editBtn:hover {
    background-color: #dda15e;
    color: #283618;
}

QPushButton#deleteBtn {
    background-color: #dc2626;
    color: #fefae0;
    border: none;
    padding: 10px 15px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: bold;
    min-width: 100px;
}

QPushButton#deleteBtn:hover {
    background-color: #b91c1c;
    color: #fefae0;
}

QPushButton#backBtn {
    background-color: #6b7280;
    color: #fefae0;
    border: none;
    padding: 10px 15px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: bold;
    min-width: 100px;
}

QPushButton#backBtn:hover {
    background-color: #4b5563;
    color: #fefae0;
}

QLabel#formTitle {
    font-size: 18px;
    font-weight: bold;
    color: #283618;
    padding: 10px 0px 5px 0px;
}

QLabel#formSubtitle {
    font-size: 14px;
    color: #606c38;
    padding: 0px 0px 20px 0px;
    font-style: italic;
}

/* Поля ввода */
QLineEdit#inputField {
    background-color: #fefae0;
    border: 2px solid #dda15e;
    border-radius: 6px;
    padding: 10px 12px;
    font-size: 12px;
    color: #283618;
    min-height: 20px;
}

QLineEdit#inputField:focus {
    border-color: #606c38;
    background-color: #f4f3ee;
}

QLineEdit#inputField::placeholder {
    color: #8b8680;
    font-style: italic;
}

/* Поле для цены */
QDoubleSpinBox#inputField {
    background-color: #fefae0;
    border: 2px solid #dda15e;
    border-radius: 6px;
    padding: 10px 12px;
    font-size: 12px;
    color: #283618;
    min-height: 20px;
}

QDoubleSpinBox#inputField:focus {
    border-color: #606c38;
    background-color: #f4f3ee;
}

/* Кнопки формы */
QPushButton#saveBtn {
    background-color: #606c38;
    color: #fefae0;
    border: none;
    padding: 12px 20px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: bold;
    min-width: 120px;
}

QPushButton#saveBtn:hover {
    background-color: #dda15e;
    color: #283618;
}

QPushButton#saveBtn:pressed {
    background-color: #283618;
    color: #fefae0;
}

QPushButton#cancelBtn {
    background-color: #bc6c25;
    color: #fefae0;
    border: none;
    padding: 12px 20px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: bold;
    min-width: 120px;
}

QPushButton#cancelBtn:hover {
    background-color: #283618;
    color: #fefae0;
}

QPushButton#cancelBtn:pressed {
    background-color: #606c38;
    color: #fefae0;
}

QComboBox#inputField {
    background-color: #fefae0;
    border: 2px solid #dda15e;
    border-radius: 6px;
    padding: 10px 12px;
    font-size: 12px;
    color: #283618;
    min-height: 20px;
}

QComboBox#inputField:focus {
    border-color: #606c38;
    background-color: #f4f3ee;
}

QComboBox#inputField::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 25px;
    border-left-width: 1px;
    border-left-color: #dda15e;
    border-left-style: solid;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
    background-color: #dda15e;
}

QComboBox#inputField::down-arrow {
    image: none;
    border: none;
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #283618;
    margin: 5px;
}

QComboBox#inputField QAbstractItemView {
    background-color: #fefae0;
    border: 2px solid #dda15e;
    selection-background-color: #606c38;
    selection-color: #fefae0;
    color: #283618;
    font-size: 12px;
}

QComboBox#inputField QAbstractItemView::item {
    padding: 8px;
    border-bottom: 1px solid #dda15e;
}

QComboBox#inputField QAbstractItemView::item:hover {
    background-color: #f4f3ee;
}

QComboBox#inputField QAbstractItemView::item:selected {
    background-color: #606c38;
    color: #fefae0;
}
"""