import sqlite3
import os


class DatabaseManager:
    def __init__(self, db_path="database/masterpol.db"):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def create_test_table(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Partners_Import (
            PartnerID INTEGER PRIMARY KEY,
            PartnerType TEXT,
            PartnerName TEXT,
            Director TEXT,
            Phone TEXT,
            Email TEXT,
            LegalAddress TEXT,
            INN TEXT,
            Rating REAL
        )
        ''')

        # Добавим тестовые данные
        test_data = [
            ('ЗАО', 'База Строитель', 'Иванова Александра', '493 123 45 67', 'aleksandraivan...', '652050, Кемеро...',
             '2222455179', 7.00),
            ('ЗАО', 'МонтажПро', 'Степанов Степан', '912 888 33 33', 'stepanov@step...', '309500, Белгор...',
             '5552431140', 10.00),
            ('ООО', 'Паркет 29', 'Петров Василий', '987 123 56 78', 'vpetrov@vl.ru', '164500, Арханг...', '3333888520',
             7.00)
        ]

        cursor.executemany('''
        INSERT OR REPLACE INTO Partners_Import 
        (PartnerType, PartnerName, Director, Phone, Email, LegalAddress, INN, Rating)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', test_data)

        conn.commit()
        conn.close()

    def add_partner(self, partner_data):
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO Partners_Import 
        (PartnerType, PartnerName, Director, Phone, Email, LegalAddress, INN, Rating)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        values = (
            partner_data['PartnerType'],
            partner_data['PartnerName'],
            partner_data['Director'],
            partner_data['Phone'],
            partner_data['Email'],
            partner_data['LegalAddress'],
            partner_data['INN'],
            partner_data['Rating']
        )

        cursor.execute(query, values)
        conn.commit()
        conn.close()

        return cursor.rowcount > 0

    def get_all_partners(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
        SELECT PartnerType, PartnerName, Director, Phone, 
               Email, LegalAddress, INN, Rating 
        FROM Partners_Import
        ORDER BY PartnerName
        """

        cursor.execute(query)
        partners = cursor.fetchall()
        conn.close()

        return partners

    def delete_partner(self, inn):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM Partners_Import WHERE INN = ?", (inn,))
        conn.commit()
        conn.close()

        return cursor.rowcount > 0

    def get_partner_by_inn(self, inn):
        """Получает данные партнера по ИНН"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT PartnerType, PartnerName, Director, Phone, Email, 
                       LegalAddress, INN, Rating 
                FROM Partners_Import 
                WHERE INN = ?
            """, (inn,))

            result = cursor.fetchone()
            conn.close()
            return result

        except Exception as e:
            print(f"Ошибка при получении партнера: {e}")
            return None

    def update_partner(self, inn, partner_data):
        """Обновляет данные партнера"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Partners_Import 
                SET PartnerType = ?, PartnerName = ?, Director = ?, 
                    Phone = ?, Email = ?, LegalAddress = ?, Rating = ?
                WHERE INN = ?
            """, (
                partner_data['PartnerType'],
                partner_data['PartnerName'],
                partner_data['Director'],
                partner_data['Phone'],
                partner_data['Email'],
                partner_data['LegalAddress'],
                partner_data['Rating'],
                inn
            ))

            conn.commit()
            rowcount = cursor.rowcount
            conn.close()
            return rowcount > 0


        except Exception as e:
            print(f"Ошибка при обновлении партнера: {e}")
            return False

    def get_partner_products(self, partner_inn, search_text=""):
        """Получает продукцию партнера с возможностью поиска"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Запрос для получения продукции партнера на основе вашей структуры БД
            # Поскольку у вас ProductTypeID содержит название типа, а не ID
            base_query = """
            SELECT DISTINCT p.ProductName, p.ArticleNumber, p.ProductTypeID as ProductType, p.MinPartnerPrice
            FROM Products_Import p
            WHERE 1=1
            """

            params = []

            # Добавляем условие поиска если задан поисковый текст
            if search_text:
                base_query += " AND LOWER(p.ProductName) LIKE LOWER(?)"
                params.append(f"%{search_text}%")

            base_query += " ORDER BY p.ProductName"

            cursor.execute(base_query, params)
            products = cursor.fetchall()
            conn.close()

            return products

        except Exception as e:
            print(f"Ошибка при получении продукции партнера: {e}")
            return []

    def get_partner_name_by_inn(self, inn):
        """Получает название партнера по ИНН"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT PartnerName FROM Partners_Import WHERE INN = ?", (inn,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else "Неизвестный партнер"
        except Exception as e:
            print(f"Ошибка при получении названия партнера: {e}")
            return "Неизвестный партнер"

    def get_partner_products_by_inn(self, partner_inn, search_text=""):
        """Получает продукцию конкретного партнера по ИНН (если есть связь)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Сначала проверим, есть ли таблица связи партнеров и продукции
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%Partner%Product%'")
            partner_product_tables = cursor.fetchall()

            if partner_product_tables:
                # Если есть таблица связи, используем её
                table_name = partner_product_tables[0][0]
                base_query = f"""
                SELECT DISTINCT p.ProductName, p.ArticleNumber, p.ProductTypeID, p.MinPartnerPrice
                FROM Products_Import p
                JOIN {table_name} pp ON p.ProductID = pp.ProductID
                JOIN Partners_Import pi ON pp.PartnerID = pi.PartnerID
                WHERE pi.INN = ?
                """
                params = [partner_inn]
            else:
                # Если таблицы связи нет, показываем все продукты
                print("Таблица связи партнеров и продукции не найдена, показываем все продукты")
                base_query = """
                SELECT DISTINCT ProductName, ArticleNumber, ProductTypeID, MinPartnerPrice
                FROM Products_Import
                WHERE 1=1
                """
                params = []

            # Добавляем условие поиска если задан поисковый текст
            if search_text:
                base_query += " AND LOWER(ProductName) LIKE LOWER(?)" if "Products_Import" in base_query else " AND LOWER(p.ProductName) LIKE LOWER(?)"
                params.append(f"%{search_text}%")

            base_query += " ORDER BY ProductName" if "Products_Import" in base_query else " ORDER BY p.ProductName"

            cursor.execute(base_query, params)
            products = cursor.fetchall()
            conn.close()

            return products

        except Exception as e:
            print(f"Ошибка при получении продукции партнера: {e}")
            return []

    def delete_product(self, article_number):
        """Удаляет продукт по артикулу"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM Products_Import WHERE ArticleNumber = ?", (article_number,))
            conn.commit()
            rowcount = cursor.rowcount
            conn.close()

            return rowcount > 0

        except Exception as e:
            print("Ошибка при удалении продукта: {}".format(e))
            return False
