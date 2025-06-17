import sqlite3
import os
from datetime import datetime


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

        test_data = [
            ('ЗАО', 'База Строитель', 'Иванова Александра', '493 123 45 67', 'aleksandraivan...', '652050, Кемеро...', '2222455179', 7.00),
            ('ЗАО', 'МонтажПро', 'Степанов Степан', '912 888 33 33', 'stepanov@step...', '309500, Белгор...', '5552431140', 10.00),
            ('ООО', 'Паркет 29', 'Петров Василий', '987 123 56 78', 'vpetrov@vl.ru', '164500, Арханг...', '3333888520', 7.00)
        ]

        cursor.executemany('''
        INSERT OR REPLACE INTO Partners_Import 
        (PartnerType, PartnerName, Director, Phone, Email, LegalAddress, INN, Rating)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', test_data)

        conn.commit()
        conn.close()

    def is_inn_exists(self, inn):
        """Проверяет, существует ли партнер с таким ИНН"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Partners_Import WHERE INN = ?", (inn,))
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except Exception as e:
            return False

    def add_partner(self, partner_data):
        """Добавляет нового партнера с проверкой уникальности ИНН"""
        try:
            inn = partner_data['INN']
            if self.is_inn_exists(inn):
                return False, f"Партнер с ИНН {inn} уже существует в базе данных"

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
            partner_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return True, "Партнер успешно добавлен"

        except Exception as e:
            return False, f"Ошибка при добавлении партнера: {str(e)}"

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
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0

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
            return False

    def get_partner_products(self, partner_inn, search_text=""):
        """Получает продукцию партнера с возможностью поиска"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            base_query = """
            SELECT DISTINCT p.ProductName, p.ArticleNumber, p.ProductTypeID as ProductType, p.MinPartnerPrice
            FROM Products_Import p
            WHERE 1=1
            """

            params = []

            if search_text:
                base_query += " AND LOWER(p.ProductName) LIKE LOWER(?)"
                params.append(f"%{search_text}%")

            base_query += " ORDER BY p.ProductName"

            cursor.execute(base_query, params)
            products = cursor.fetchall()
            conn.close()
            return products

        except Exception as e:
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
            return "Неизвестный партнер"

    def add_product(self, product_data, partner_inn=None):
        """Добавляет новый продукт в базу данных"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
            INSERT INTO Products_Import 
            (ProductName, ProductTypeID, ArticleNumber, MinPartnerPrice)
            VALUES (?, ?, ?, ?)
            """

            price = product_data['MinPartnerPrice']
            if isinstance(price, (int, float)):
                price_str = str(price).replace('.', ',')
            else:
                price_str = str(price)

            values = (
                product_data['ProductName'],
                product_data['ProductTypeID'],
                product_data['ArticleNumber'],
                price_str
            )

            cursor.execute(query, values)
            product_id = cursor.lastrowid
            conn.commit()
            rowcount = cursor.rowcount
            conn.close()

            return rowcount > 0

        except Exception as e:
            return False

    def get_partner_products_by_inn(self, partner_inn, search_text=""):
        """Получает продукцию - показывает все продукты из Products_Import"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            base_query = """
            SELECT DISTINCT ProductName, ArticleNumber, ProductTypeID, MinPartnerPrice
            FROM Products_Import
            WHERE 1=1
            """
            params = []

            if search_text:
                base_query += " AND LOWER(ProductName) LIKE LOWER(?)"
                params.append(f"%{search_text}%")

            base_query += " ORDER BY ProductName"

            cursor.execute(base_query, params)
            products = cursor.fetchall()
            conn.close()
            return products

        except Exception as e:
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
            return False

    def add_partner_id_to_products_table(self):
        """Добавляет поле PartnerID в таблицу Products_Import"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("PRAGMA table_info(Products_Import)")
            columns = [col[1] for col in cursor.fetchall()]

            if 'PartnerID' not in columns:
                cursor.execute("ALTER TABLE Products_Import ADD COLUMN PartnerID INTEGER")

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            return False

    def add_product_with_partner_id(self, product_data, partner_inn=None):
        """Добавляет новый продукт с указанием партнера"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            partner_id = None
            if partner_inn:
                cursor.execute("SELECT PartnerID FROM Partners_Import WHERE INN = ?", (partner_inn,))
                partner_result = cursor.fetchone()
                if partner_result:
                    partner_id = partner_result[0]

            query = """
            INSERT INTO Products_Import 
            (ProductName, ProductTypeID, ArticleNumber, MinPartnerPrice, PartnerID)
            VALUES (?, ?, ?, ?, ?)
            """

            price = product_data['MinPartnerPrice']
            if isinstance(price, (int, float)):
                price_str = str(price).replace('.', ',')
            else:
                price_str = str(price)

            values = (
                product_data['ProductName'],
                product_data['ProductTypeID'],
                product_data['ArticleNumber'],
                price_str,
                partner_id
            )

            cursor.execute(query, values)
            product_id = cursor.lastrowid
            conn.commit()
            rowcount = cursor.rowcount
            conn.close()

            return rowcount > 0

        except Exception as e:
            return False

    def get_partner_products_by_partner_id(self, partner_inn, search_text=""):
        """Получает продукцию конкретного партнера по PartnerID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT PartnerID FROM Partners_Import WHERE INN = ?", (partner_inn,))
            partner_result = cursor.fetchone()

            if not partner_result:
                base_query = """
                SELECT DISTINCT ProductName, ArticleNumber, ProductTypeID, MinPartnerPrice
                FROM Products_Import
                WHERE PartnerID IS NULL
                """
                params = []

                if search_text:
                    base_query += " AND LOWER(ProductName) LIKE LOWER(?)"
                    params.append(f"%{search_text}%")

                base_query += " ORDER BY ProductName"

                cursor.execute(base_query, params)
                products = cursor.fetchall()
                conn.close()
                return products

            partner_id = partner_result[0]

            base_query = """
            SELECT DISTINCT ProductName, ArticleNumber, ProductTypeID, MinPartnerPrice
            FROM Products_Import
            WHERE PartnerID = ?
            """
            params = [partner_id]

            if search_text:
                base_query += " AND LOWER(ProductName) LIKE LOWER(?)"
                params.append(f"%{search_text}%")

            base_query += " ORDER BY ProductName"

            cursor.execute(base_query, params)
            products = cursor.fetchall()
            conn.close()
            return products

        except Exception as e:
            return []

    def update_product(self, original_article, product_data):
        """Обновляет данные продукта по артикулу"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            price = product_data['MinPartnerPrice']
            if isinstance(price, (int, float)):
                price_str = str(price).replace('.', ',')
            else:
                price_str = str(price)

            query = """
            UPDATE Products_Import 
            SET ProductName = ?, ProductTypeID = ?, ArticleNumber = ?, MinPartnerPrice = ?
            WHERE ArticleNumber = ?
            """

            values = (
                product_data['ProductName'],
                product_data['ProductTypeID'],
                product_data['ArticleNumber'],
                price_str,
                original_article
            )

            cursor.execute(query, values)
            conn.commit()
            rowcount = cursor.rowcount
            conn.close()

            return rowcount > 0

        except Exception as e:
            return False

    def get_product_by_article(self, article_number):
        """Получает данные продукта по артикулу"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
            SELECT ProductName, ArticleNumber, ProductTypeID, MinPartnerPrice
            FROM Products_Import 
            WHERE ArticleNumber = ?
            """

            cursor.execute(query, (article_number,))
            result = cursor.fetchone()
            conn.close()

            if result:
                return {
                    'ProductName': result[0],
                    'ArticleNumber': result[1],
                    'ProductTypeID': result[2],
                    'MinPartnerPrice': result[3]
                }
            return None

        except Exception as e:
            return None

    def fix_partner_table_structure(self):
        """Исправляет структуру таблицы Partners_Import"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM Partners_Import WHERE PartnerID IS NULL")
            partners_with_null_id = cursor.fetchall()

            if partners_with_null_id:
                cursor.execute("SELECT MAX(PartnerID) FROM Partners_Import WHERE PartnerID IS NOT NULL")
                max_id_result = cursor.fetchone()
                max_id = max_id_result[0] if max_id_result[0] is not None else 0

                for i, partner in enumerate(partners_with_null_id):
                    new_id = max_id + i + 1
                    partner_inn = partner[7]
                    cursor.execute("UPDATE Partners_Import SET PartnerID = ? WHERE INN = ?", (new_id, partner_inn))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            return False

    def update_products_with_null_partner_id(self, partner_inn):
        """Обновляет продукты с NULL PartnerID для конкретного партнера"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT PartnerID FROM Partners_Import WHERE INN = ?", (partner_inn,))
            partner_result = cursor.fetchone()

            if not partner_result:
                return False

            partner_id = partner_result[0]

            cursor.execute("SELECT ProductID FROM Products_Import WHERE PartnerID IS NULL")
            null_products = cursor.fetchall()

            if null_products:
                for product in null_products:
                    product_id = product[0]
                    cursor.execute("UPDATE Products_Import SET PartnerID = ? WHERE ProductID = ?", (partner_id, product_id))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            return False

    def get_partner_sales_history(self, partner_inn, search_text=""):
        """Получает историю продаж партнера с названиями продуктов"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT PartnerID FROM Partners_Import WHERE INN = ?", (partner_inn,))
            partner_result = cursor.fetchone()

            if not partner_result:
                return []

            partner_id = partner_result[0]

            base_query = """
            SELECT 
                pps.SaleDate,
                pi.ProductName,
                pps.Quantity,
                pi.MinPartnerPrice,
                (pps.Quantity * CAST(REPLACE(pi.MinPartnerPrice, ',', '.') AS FLOAT)) AS TotalSum,
                pps.ROWID as SaleID
            FROM Partner_Products_Import pps
            JOIN Products_Import pi ON pps.ProductID = pi.ROWID
            WHERE pps.PartnerID = ?
            """

            params = [partner_id]

            if search_text:
                base_query += " AND LOWER(pi.ProductName) LIKE LOWER(?)"
                params.append(f"%{search_text}%")

            base_query += " ORDER BY pps.SaleDate DESC"

            cursor.execute(base_query, params)
            sales = cursor.fetchall()

            if not sales:
                alt_query = """
                SELECT 
                    pps.SaleDate,
                    pi.ProductName,
                    pps.Quantity,
                    pi.MinPartnerPrice,
                    (pps.Quantity * CAST(REPLACE(pi.MinPartnerPrice, ',', '.') AS FLOAT)) AS TotalSum,
                    pps.ROWID as SaleID
                FROM Partner_Products_Import pps, Products_Import pi
                WHERE pps.PartnerID = ? 
                AND pps.ProductID = pi.ROWID
                """

                if search_text:
                    alt_query += " AND LOWER(pi.ProductName) LIKE LOWER(?)"
                    params = [partner_id, f"%{search_text}%"]
                else:
                    params = [partner_id]

                alt_query += " ORDER BY pps.SaleDate DESC"

                cursor.execute(alt_query, params)
                sales = cursor.fetchall()

            conn.close()
            return sales

        except Exception as e:
            return []

    def delete_sale(self, sale_id):
        """Удаляет запись о продаже по ROWID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM Partner_Products_Import WHERE ROWID = ?", (sale_id,))
            conn.commit()
            rowcount = cursor.rowcount
            conn.close()

            return rowcount > 0

        except Exception as e:
            return False

    def get_sales_statistics(self, partner_inn):
        """Получает статистику продаж партнера"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT PartnerID FROM Partners_Import WHERE INN = ?", (partner_inn,))
            partner_result = cursor.fetchone()

            if not partner_result:
                return None

            partner_id = partner_result[0]

            query = """
            SELECT 
                COUNT(*) as total_sales,
                SUM(pps.Quantity) as total_quantity,
                SUM(pps.Quantity * CAST(REPLACE(pi.MinPartnerPrice, ',', '.') AS FLOAT)) as total_sum
            FROM Partner_Products_Import pps
            JOIN Products_Import pi ON pps.ProductID = pi.ROWID
            WHERE pps.PartnerID = ?
            """

            cursor.execute(query, (partner_id,))
            stats = cursor.fetchone()

            if not stats or stats[0] == 0:
                manual_query = """
                SELECT 
                    COUNT(*) as total_sales,
                    SUM(pps.Quantity) as total_quantity,
                    SUM(pps.Quantity * CAST(REPLACE(pi.MinPartnerPrice, ',', '.') AS FLOAT)) as total_sum
                FROM Partner_Products_Import pps, Products_Import pi
                WHERE pps.PartnerID = ? 
                AND pps.ProductID = pi.ROWID
                """

                cursor.execute(manual_query, (partner_id,))
                stats = cursor.fetchone()

            conn.close()

            if stats:
                return {
                    'total_sales': stats[0] if stats[0] else 0,
                    'total_quantity': stats[1] if stats[1] else 0,
                    'total_sum': stats[2] if stats[2] else 0
                }
            else:
                return {
                    'total_sales': 0,
                    'total_quantity': 0,
                    'total_sum': 0
                }

        except Exception as e:
            return None

    def get_partner_products_for_sale(self, partner_inn):
        """Получает продукцию партнера для добавления в продажу"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT PartnerID FROM Partners_Import WHERE INN = ?", (partner_inn,))
            partner_result = cursor.fetchone()

            if not partner_result:
                return []

            partner_id = partner_result[0]

            query = """
            SELECT 
                ROWID as ProductID,
                ProductName, 
                MinPartnerPrice
            FROM Products_Import
            WHERE PartnerID = ?
            ORDER BY ProductName
            """

            cursor.execute(query, (partner_id,))
            raw_products = cursor.fetchall()

            products = []
            for product in raw_products:
                if len(product) >= 3:
                    product_id = product[0]
                    product_name = product[1]
                    min_price = product[2]

                    if product_name and min_price is not None:
                        products.append((product_id, product_name, min_price))

            conn.close()
            return products

        except Exception as e:
            return []

    def add_sale(self, sale_data):
        """Добавляет новую продажу"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            current_date = datetime.now().strftime('%d.%m.%Y')

            query = """
            INSERT INTO Partner_Products_Import 
            (ProductID, PartnerID, Quantity, SaleDate)
            VALUES (?, ?, ?, ?)
            """

            values = (
                sale_data['ProductID'],
                sale_data['PartnerID'],
                sale_data['Quantity'],
                current_date
            )

            cursor.execute(query, values)
            sale_id = cursor.lastrowid
            conn.commit()
            rowcount = cursor.rowcount
            conn.close()

            return rowcount > 0

        except Exception as e:
            return False

    def get_partner_id_by_inn(self, inn):
        """Получает ID партнера по ИНН"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT PartnerID FROM Partners_Import WHERE INN = ?", (inn,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except Exception as e:
            return None

    def get_sale_by_id(self, sale_id):
        """Получает данные продажи по ROWID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
            SELECT 
                pps.ROWID as SaleID,
                pps.ProductID,
                pps.PartnerID,
                pps.Quantity,
                pps.SaleDate,
                pi.ProductName,
                pi.MinPartnerPrice,
                (pps.Quantity * CAST(REPLACE(pi.MinPartnerPrice, ',', '.') AS FLOAT)) AS TotalSum
            FROM Partner_Products_Import pps
            JOIN Products_Import pi ON pps.ProductID = pi.ROWID
            WHERE pps.ROWID = ?
            """

            cursor.execute(query, (sale_id,))
            sale_data = cursor.fetchone()

            if not sale_data:
                alt_query = """
                SELECT 
                    pps.ROWID as SaleID,
                    pps.ProductID,
                    pps.PartnerID,
                    pps.Quantity,
                    pps.SaleDate,
                    pi.ProductName,
                    pi.MinPartnerPrice,
                    (pps.Quantity * CAST(REPLACE(pi.MinPartnerPrice, ',', '.') AS FLOAT)) AS TotalSum
                FROM Partner_Products_Import pps, Products_Import pi
                WHERE pps.ROWID = ?
                AND pps.ProductID = pi.ROWID
                """

                cursor.execute(alt_query, (sale_id,))
                sale_data = cursor.fetchone()

                if not sale_data:
                    conn.close()
                    return None

            result = {
                'SaleID': sale_data[0],
                'ProductID': sale_data[1],
                'PartnerID': sale_data[2],
                'Quantity': sale_data[3],
                'SaleDate': sale_data[4],
                'ProductName': sale_data[5],
                'MinPartnerPrice': sale_data[6],
                'TotalSum': sale_data[7]
            }

            conn.close()
            return result

        except Exception as e:
            return None

    def update_sale(self, sale_data):
        """Обновляет существующую продажу по ROWID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT ROWID, * FROM Partner_Products_Import WHERE ROWID = ?", (sale_data['SaleID'],))
            existing_sale = cursor.fetchone()

            if not existing_sale:
                conn.close()
                return False

            current_date = datetime.now().strftime('%d.%m.%Y')

            query = """
            UPDATE Partner_Products_Import 
            SET ProductID = ?, 
                PartnerID = ?, 
                Quantity = ?,
                SaleDate = ?
            WHERE ROWID = ?
            """

            values = (
                sale_data['ProductID'],
                sale_data['PartnerID'],
                sale_data['Quantity'],
                current_date,
                sale_data['SaleID']
            )

            cursor.execute(query, values)
            conn.commit()
            rowcount = cursor.rowcount
            conn.close()

            return rowcount > 0

        except Exception as e:
            return False