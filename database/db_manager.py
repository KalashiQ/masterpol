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
            print("Ошибка при проверке ИНН:", e)
            return False

    def add_partner(self, partner_data):
        """Добавляет нового партнера с проверкой уникальности ИНН"""
        try:
            print("=== ДОБАВЛЕНИЕ ПАРТНЕРА ===")
            print("Данные для добавления:", partner_data)

            # Проверяем уникальность ИНН
            inn = partner_data['INN']
            if self.is_inn_exists(inn):
                print(f"⚠️ ОШИБКА: Партнер с ИНН {inn} уже существует!")
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

            print("SQL запрос:", query)
            print("Значения:", values)

            cursor.execute(query, values)

            # Получаем ID добавленного партнера
            partner_id = cursor.lastrowid
            print("ID добавленного партнера:", partner_id)

            conn.commit()
            rowcount = cursor.rowcount

            # Проверяем, добавился ли партнер
            cursor.execute("SELECT * FROM Partners_Import WHERE PartnerID = ?", (partner_id,))
            added_partner = cursor.fetchone()
            print("Добавленный партнер:", added_partner)

            conn.close()

            print("=== ДОБАВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО ===")
            return True, "Партнер успешно добавлен"

        except Exception as e:
            print("Ошибка при добавлении партнера:", e)
            import traceback
            traceback.print_exc()
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
            print("Ошибка при получении партнера: {}".format(e))
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
            print("Ошибка при обновлении партнера: {}".format(e))
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
                params.append("{}{}{}".format("%", search_text, "%"))

            base_query += " ORDER BY p.ProductName"

            cursor.execute(base_query, params)
            products = cursor.fetchall()
            conn.close()

            return products

        except Exception as e:
            print("Ошибка при получении продукции партнера: {}".format(e))
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
            print("Ошибка при получении названия партнера: {}".format(e))
            return "Неизвестный партнер"

    def add_product(self, product_data, partner_inn=None):
        """Добавляет новый продукт в базу данных"""
        try:
            print("=== ДОБАВЛЕНИЕ ПРОДУКТА ===")
            print("Данные для добавления:", product_data)

            conn = self.get_connection()
            cursor = conn.cursor()

            # Добавляем продукт
            query = """
            INSERT INTO Products_Import 
            (ProductName, ProductTypeID, ArticleNumber, MinPartnerPrice)
            VALUES (?, ?, ?, ?)
            """

            # Преобразуем цену в строку с запятой как в существующих данных
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

            print("SQL запрос для продукта:", query)
            print("Значения:", values)

            cursor.execute(query, values)

            # Получаем ID добавленного продукта
            product_id = cursor.lastrowid
            print("ID добавленного продукта:", product_id)

            conn.commit()
            rowcount = cursor.rowcount

            # Проверим, добавился ли наш продукт
            cursor.execute("SELECT * FROM Products_Import WHERE ProductID = ?", (product_id,))
            added_product = cursor.fetchone()
            print("Добавленный продукт:", added_product)

            conn.close()

            print("=== КОНЕЦ ДОБАВЛЕНИЯ ===")
            return rowcount > 0

        except Exception as e:
            print("Ошибка при добавлении продукта: {}".format(e))
            import traceback
            traceback.print_exc()
            return False

    def get_partner_products_by_inn(self, partner_inn, search_text=""):
        """Получает продукцию - показывает все продукты из Products_Import"""
        try:
            print("=== ПОЛУЧЕНИЕ ПРОДУКЦИИ ===")
            print("partner_inn:", partner_inn)
            print("search_text:", search_text)

            conn = self.get_connection()
            cursor = conn.cursor()

            # Сначала проверим общее количество продуктов
            cursor.execute("SELECT COUNT(*) FROM Products_Import")
            total_products = cursor.fetchone()[0]
            print("Всего продуктов в Products_Import:", total_products)

            # Показываем все продукты из Products_Import
            print("Показываем все продукты из Products_Import")
            base_query = """
            SELECT DISTINCT ProductName, ArticleNumber, ProductTypeID, MinPartnerPrice
            FROM Products_Import
            WHERE 1=1
            """
            params = []

            # Добавляем условие поиска если задан поисковый текст
            if search_text:
                base_query += " AND LOWER(ProductName) LIKE LOWER(?)"
                params.append("{}{}{}".format("%", search_text, "%"))

            # Добавляем сортировку
            base_query += " ORDER BY ProductName"

            print("Итоговый SQL запрос:", base_query)
            print("Параметры запроса:", params)

            cursor.execute(base_query, params)
            products = cursor.fetchall()
            conn.close()

            print("Результат запроса - количество продуктов:", len(products))
            for i, product in enumerate(products):
                print("Продукт {}: {}".format(i, product))
            print("=== КОНЕЦ ПОЛУЧЕНИЯ ===")

            return products

        except Exception as e:
            print("Ошибка при получении продукции партнера: {}".format(e))
            import traceback
            traceback.print_exc()

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

    def add_partner_id_to_products_table(self):
        """Добавляет поле PartnerID в таблицу Products_Import"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Проверяем, есть ли уже поле PartnerID
            cursor.execute("PRAGMA table_info(Products_Import)")
            columns = [col[1] for col in cursor.fetchall()]

            if 'PartnerID' not in columns:
                # Добавляем поле PartnerID
                cursor.execute("ALTER TABLE Products_Import ADD COLUMN PartnerID INTEGER")
                print("Поле PartnerID добавлено в таблицу Products_Import")
            else:
                print("Поле PartnerID уже существует в таблице Products_Import")

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print("Ошибка при добавлении поля PartnerID: {}".format(e))
            return False

    def add_product_with_partner_id(self, product_data, partner_inn=None):
        """Добавляет новый продукт с указанием партнера"""
        try:
            print("=== ДОБАВЛЕНИЕ ПРОДУКТА С ПАРТНЕРОМ ===")
            print("Данные для добавления:", product_data)
            print("ИНН партнера:", partner_inn)

            conn = self.get_connection()
            cursor = conn.cursor()

            # Проверяем, есть ли партнер в базе
            if partner_inn:
                print("Ищем партнера с ИНН:", partner_inn)
                cursor.execute("SELECT PartnerID, PartnerName FROM Partners_Import WHERE INN = ?", (partner_inn,))
                partner_result = cursor.fetchone()
                print("Результат поиска партнера:", partner_result)

                if partner_result:
                    partner_id = partner_result[0]
                    partner_name = partner_result[1]
                    print(f"Найден партнер: ID={partner_id}, Название={partner_name}")
                else:
                    print("⚠️ ВНИМАНИЕ: Партнер с ИНН", partner_inn, "не найден в базе данных!")
                    print("Проверим всех партнеров в базе:")
                    cursor.execute("SELECT PartnerID, PartnerName, INN FROM Partners_Import")
                    all_partners = cursor.fetchall()
                    for p in all_partners:
                        print(f"  ID: {p[0]}, Название: {p[1]}, ИНН: {p[2]}")
                    partner_id = None
            else:
                print("ИНН партнера не передан")
                partner_id = None

            print("Итоговый ID партнера для добавления:", partner_id)

            # Добавляем продукт с PartnerID
            query = """
            INSERT INTO Products_Import 
            (ProductName, ProductTypeID, ArticleNumber, MinPartnerPrice, PartnerID)
            VALUES (?, ?, ?, ?, ?)
            """

            # Преобразуем цену в строку с запятой как в существующих данных
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
                partner_id  # Может быть None, если партнер не найден
            )

            print("SQL запрос для продукта:", query)
            print("Значения:", values)

            cursor.execute(query, values)

            # Получаем ID добавленного продукта
            product_id = cursor.lastrowid
            print("ID добавленного продукта:", product_id)

            conn.commit()
            rowcount = cursor.rowcount

            # Проверим, добавился ли наш продукт
            cursor.execute("SELECT * FROM Products_Import WHERE ProductID = ?", (product_id,))
            added_product = cursor.fetchone()
            print("Добавленный продукт (полная запись):", added_product)

            conn.close()

            print("=== КОНЕЦ ДОБАВЛЕНИЯ ===")
            return rowcount > 0

        except Exception as e:
            print("Ошибка при добавлении продукта:", e)
            import traceback
            traceback.print_exc()
            return False

    def get_partner_products_by_partner_id(self, partner_inn, search_text=""):
        """Получает продукцию конкретного партнера по PartnerID"""
        try:
            print("=== ПОЛУЧЕНИЕ ПРОДУКЦИИ ПО PARTNER_ID ===")
            print("partner_inn:", partner_inn)

            conn = self.get_connection()
            cursor = conn.cursor()

            # Проверяем всех партнеров
            print("Все партнеры в базе:")
            cursor.execute("SELECT PartnerID, PartnerName, INN FROM Partners_Import")
            all_partners = cursor.fetchall()
            for p in all_partners:
                print(f"  ID: {p[0]}, Название: {p[1]}, ИНН: {p[2]}")

            # Находим ID партнера по ИНН
            cursor.execute("SELECT PartnerID FROM Partners_Import WHERE INN = ?", (partner_inn,))
            partner_result = cursor.fetchone()

            if not partner_result:
                print(f"⚠️ Партнер с ИНН {partner_inn} не найден")
                print("Попробуем найти продукты без привязки к партнеру...")

                # Если партнер не найден, показываем продукты с NULL PartnerID
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

                print(f"Найдено продуктов без партнера: {len(products)}")
                return products

            partner_id = partner_result[0]
            print("ID партнера:", partner_id)

            # Запрос продукции этого партнера
            base_query = """
            SELECT DISTINCT ProductName, ArticleNumber, ProductTypeID, MinPartnerPrice
            FROM Products_Import
            WHERE PartnerID = ?
            """
            params = [partner_id]

            # Добавляем условие поиска если задан поисковый текст
            if search_text:
                base_query += " AND LOWER(ProductName) LIKE LOWER(?)"
                params.append(f"%{search_text}%")

            base_query += " ORDER BY ProductName"

            print("SQL запрос:", base_query)
            print("Параметры:", params)

            cursor.execute(base_query, params)
            products = cursor.fetchall()
            conn.close()

            print("Найдено продуктов:", len(products))
            for i, product in enumerate(products):
                print(f"Продукт {i}: {product}")

            return products

        except Exception as e:
            print("Ошибка при получении продукции партнера:", e)
            import traceback
            traceback.print_exc()
            return []

    def update_product(self, original_article, product_data):
        """Обновляет данные продукта по артикулу"""
        try:
            print("=== ОБНОВЛЕНИЕ ПРОДУКТА ===")
            print("original_article:", original_article)
            print("product_data:", product_data)

            conn = self.get_connection()
            cursor = conn.cursor()

            # Преобразуем цену в строку с запятой как в существующих данных
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
                original_article  # Ищем по оригинальному артикулу
            )

            print("SQL запрос:", query)
            print("Значения:", values)

            cursor.execute(query, values)
            conn.commit()
            rowcount = cursor.rowcount
            conn.close()

            print("Количество обновленных строк:", rowcount)
            print("=== КОНЕЦ ОБНОВЛЕНИЯ ===")

            return rowcount > 0

        except Exception as e:
            print("Ошибка при обновлении продукта:", e)
            import traceback
            traceback.print_exc()
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
            print("Ошибка при получении продукта:", e)
            return None

    def fix_partner_table_structure(self):
        """Исправляет структуру таблицы Partners_Import"""
        try:
            print("=== ИСПРАВЛЕНИЕ СТРУКТУРЫ ТАБЛИЦЫ ПАРТНЕРОВ ===")
            conn = self.get_connection()
            cursor = conn.cursor()

            # Проверяем текущую структуру таблицы
            cursor.execute("PRAGMA table_info(Partners_Import)")
            columns_info = cursor.fetchall()
            print("Текущая структура таблицы Partners_Import:")
            for col in columns_info:
                print(f"  {col}")

            # Получаем всех партнеров с NULL PartnerID
            cursor.execute("SELECT * FROM Partners_Import WHERE PartnerID IS NULL")
            partners_with_null_id = cursor.fetchall()
            print(f"Партнеры с NULL PartnerID: {len(partners_with_null_id)}")

            if partners_with_null_id:
                # Находим максимальный PartnerID
                cursor.execute("SELECT MAX(PartnerID) FROM Partners_Import WHERE PartnerID IS NOT NULL")
                max_id_result = cursor.fetchone()
                max_id = max_id_result[0] if max_id_result[0] is not None else 0
                print(f"Максимальный существующий PartnerID: {max_id}")

                # Присваиваем ID партнерам с NULL
                for i, partner in enumerate(partners_with_null_id):
                    new_id = max_id + i + 1
                    partner_inn = partner[7]  # INN находится на 7-й позиции
                    partner_name = partner[2]  # PartnerName на 2-й позиции

                    print(f"Обновляем партнера '{partner_name}' (ИНН: {partner_inn}) -> ID: {new_id}")
                    cursor.execute("UPDATE Partners_Import SET PartnerID = ? WHERE INN = ?", (new_id, partner_inn))

            conn.commit()

            # Проверяем результат
            cursor.execute("SELECT PartnerID, PartnerName, INN FROM Partners_Import ORDER BY PartnerID")
            all_partners = cursor.fetchall()
            print("Результат исправления:")
            for p in all_partners:
                print(f"  ID: {p[0]}, Название: {p[1]}, ИНН: {p[2]}")

            conn.close()
            print("=== ИСПРАВЛЕНИЕ ЗАВЕРШЕНО ===")
            return True

        except Exception as e:
            print(f"Ошибка при исправлении структуры таблицы: {e}")
            import traceback
            traceback.print_exc()
            return False

    def update_products_with_null_partner_id(self, partner_inn):
        """Обновляет продукты с NULL PartnerID для конкретного партнера"""
        try:
            print("=== ОБНОВЛЕНИЕ ПРОДУКТОВ С NULL PARTNER_ID ===")
            conn = self.get_connection()
            cursor = conn.cursor()

            # Получаем PartnerID для переданного ИНН
            cursor.execute("SELECT PartnerID FROM Partners_Import WHERE INN = ?", (partner_inn,))
            partner_result = cursor.fetchone()

            if not partner_result:
                print(f"Партнер с ИНН {partner_inn} не найден")
                return False

            partner_id = partner_result[0]
            print(f"PartnerID для ИНН {partner_inn}: {partner_id}")

            # Получаем все продукты с NULL PartnerID
            cursor.execute("SELECT ProductID, ProductName, ArticleNumber FROM Products_Import WHERE PartnerID IS NULL")
            null_products = cursor.fetchall()
            print(f"Продуктов с NULL PartnerID: {len(null_products)}")

            if null_products:
                print("Обновляем продукты:")
                for product in null_products:
                    product_id, product_name, article = product
                    print(f"  Продукт ID: {product_id}, Название: {product_name}, Артикул: {article}")
                    cursor.execute("UPDATE Products_Import SET PartnerID = ? WHERE ProductID = ?",
                                   (partner_id, product_id))

            conn.commit()

            # Проверяем результат
            cursor.execute("SELECT COUNT(*) FROM Products_Import WHERE PartnerID = ?", (partner_id,))
            updated_count = cursor.fetchone()[0]
            print(f"Теперь у партнера {partner_id} продуктов: {updated_count}")

            conn.close()
            print("=== ОБНОВЛЕНИЕ ЗАВЕРШЕНО ===")
            return True

        except Exception as e:
            print(f"Ошибка при обновлении продуктов: {e}")
            return False

    def get_partner_sales_history(self, partner_inn, search_text=""):
        """Получает историю продаж партнера с названиями продуктов"""
        try:
            print("=== ПОЛУЧЕНИЕ ИСТОРИИ ПРОДАЖ ===")
            print("partner_inn:", partner_inn)
            print("search_text:", search_text)

            conn = self.get_connection()
            cursor = conn.cursor()

            # Находим ID партнера по ИНН
            cursor.execute("SELECT PartnerID FROM Partners_Import WHERE INN = ?", (partner_inn,))
            partner_result = cursor.fetchone()

            if not partner_result:
                print(f"⚠️ Партнер с ИНН {partner_inn} не найден")
                return []

            partner_id = partner_result[0]
            print("ID партнера:", partner_id)

            # ИСПРАВЛЕННЫЙ ЗАПРОС: используем ROWID для связи с Products_Import
            base_query = """
            SELECT 
                pps.SaleDate,
                pi.ProductName,
                pps.Quantity,
                pi.MinPartnerPrice,
                (pps.Quantity * CAST(REPLACE(pi.MinPartnerPrice, ',', '.') AS FLOAT)) AS TotalSum,
                pps.SaleID
            FROM Partner_Products_Import pps
            JOIN Products_Import pi ON pps.ProductID = pi.ROWID
            WHERE pps.PartnerID = ?
            """

            params = [partner_id]

            # Добавляем условие поиска если задан поисковый текст
            if search_text:
                base_query += " AND LOWER(pi.ProductName) LIKE LOWER(?)"
                params.append(f"%{search_text}%")

            base_query += " ORDER BY pps.SaleDate DESC"

            print("SQL запрос:", base_query)
            print("Параметры:", params)

            cursor.execute(base_query, params)
            sales = cursor.fetchall()

            print("Найдено продаж:", len(sales))
            for i, sale in enumerate(sales):
                print(f"Продажа {i}: {sale}")

            # Если JOIN не работает, попробуем альтернативный подход
            if not sales:
                print("=== JOIN НЕ ДАЕТ РЕЗУЛЬТАТОВ, ПРОБУЕМ АЛЬТЕРНАТИВНЫЙ ПОДХОД ===")

                # Сначала получаем все продажи партнера
                cursor.execute("SELECT * FROM Partner_Products_Import WHERE PartnerID = ?", (partner_id,))
                raw_sales = cursor.fetchall()
                print(f"Прямой запрос продаж: {len(raw_sales)}")
                for sale in raw_sales:
                    print(f"  Продажа: {sale}")

                # Получаем продажи с ручным соединением
                manual_query = """
                SELECT 
                    pps.SaleDate,
                    pps.ProductID,
                    pps.Quantity,
                    pps.SaleID,
                    pi.ProductName,
                    pi.MinPartnerPrice
                FROM Partner_Products_Import pps, Products_Import pi
                WHERE pps.PartnerID = ? 
                AND pps.ProductID = pi.ROWID
                """

                if search_text:
                    manual_query += " AND LOWER(pi.ProductName) LIKE LOWER(?)"
                    params = [partner_id, f"%{search_text}%"]
                else:
                    params = [partner_id]

                manual_query += " ORDER BY pps.SaleDate DESC"

                print("Альтернативный SQL запрос:", manual_query)
                print("Параметры:", params)

                cursor.execute(manual_query, params)
                manual_sales = cursor.fetchall()

                print(f"Альтернативный запрос нашел: {len(manual_sales)}")

                # Преобразуем к нужному формату
                sales = []
                for sale in manual_sales:
                    sale_date = sale[0]
                    product_id = sale[1]
                    quantity = sale[2]
                    sale_id = sale[3]
                    product_name = sale[4]
                    min_price = sale[5]

                    total_sum = quantity * float(str(min_price).replace(',', '.'))

                    sales.append((sale_date, product_name, quantity, min_price, total_sum, sale_id))
                    print(f"Преобразованная продажа: {sales[-1]}")

            conn.close()
            print("Итого найдено продаж:", len(sales))
            print("=== ПОЛУЧЕНИЕ ИСТОРИИ ПРОДАЖ ЗАВЕРШЕНО ===")

            return sales

        except Exception as e:
            print("Ошибка при получении истории продаж:", e)
            import traceback
            traceback.print_exc()
            return []

    def delete_sale(self, sale_id):
        """Удаляет запись о продаже"""
        try:
            print(f"=== УДАЛЕНИЕ ПРОДАЖИ ID: {sale_id} ===")

            conn = self.get_connection()
            cursor = conn.cursor()

            # Проверяем, существует ли продажа
            cursor.execute("SELECT * FROM Partner_Products_Import WHERE SaleID = ?", (sale_id,))
            sale = cursor.fetchone()

            if not sale:
                print(f"⚠️ Продажа с ID {sale_id} не найдена")
                return False

            print("Удаляемая продажа:", sale)

            # Удаляем продажу
            cursor.execute("DELETE FROM Partner_Products_Import WHERE SaleID = ?", (sale_id,))

            conn.commit()
            rowcount = cursor.rowcount
            conn.close()

            print(f"Удалено записей: {rowcount}")
            print("=== УДАЛЕНИЕ ЗАВЕРШЕНО ===")

            return rowcount > 0

        except Exception as e:
            print("Ошибка при удалении продажи:", e)
            import traceback
            traceback.print_exc()
            return False

    def get_sales_statistics(self, partner_inn):
        """Получает статистику продаж партнера"""
        try:
            print("=== ПОЛУЧЕНИЕ СТАТИСТИКИ ПРОДАЖ ===")
            conn = self.get_connection()
            cursor = conn.cursor()

            # Находим ID партнера по ИНН
            cursor.execute("SELECT PartnerID FROM Partners_Import WHERE INN = ?", (partner_inn,))
            partner_result = cursor.fetchone()

            if not partner_result:
                print(f"⚠️ Партнер с ИНН {partner_inn} не найден")
                return None

            partner_id = partner_result[0]
            print("ID партнера для статистики:", partner_id)

            # ИСПРАВЛЕННЫЙ ЗАПРОС: используем ROWID для связи
            query = """
            SELECT 
                COUNT(*) as total_sales,
                SUM(pps.Quantity) as total_quantity,
                SUM(pps.Quantity * CAST(REPLACE(pi.MinPartnerPrice, ',', '.') AS FLOAT)) as total_sum
            FROM Partner_Products_Import pps
            JOIN Products_Import pi ON pps.ProductID = pi.ROWID
            WHERE pps.PartnerID = ?
            """

            print("SQL запрос статистики:", query)
            cursor.execute(query, (partner_id,))
            stats = cursor.fetchone()

            print("Результат статистики:", stats)

            # Если JOIN не работает, используем альтернативный подход
            if not stats or stats[0] == 0:
                print("=== JOIN НЕ ДАЕТ РЕЗУЛЬТАТОВ ДЛЯ СТАТИСТИКИ, ПРОБУЕМ АЛЬТЕРНАТИВНЫЙ ПОДХОД ===")

                # Получаем статистику с ручным соединением
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
                print("Альтернативный результат статистики:", stats)

            conn.close()

            if stats:
                result = {
                    'total_sales': stats[0] if stats[0] else 0,
                    'total_quantity': stats[1] if stats[1] else 0,
                    'total_sum': stats[2] if stats[2] else 0
                }
                print("Итоговая статистика:", result)
                return result
            else:
                return {
                    'total_sales': 0,
                    'total_quantity': 0,
                    'total_sum': 0
                }

        except Exception as e:
            print("Ошибка при получении статистики:", e)
            import traceback
            traceback.print_exc()
            return None

    def get_partner_products_for_sale(self, partner_inn):
        """Получает продукцию партнера для добавления в продажу"""
        try:
            print("=== ПОЛУЧЕНИЕ ПРОДУКЦИИ ДЛЯ ПРОДАЖИ ===")
            print("partner_inn:", partner_inn)

            conn = self.get_connection()
            cursor = conn.cursor()

            # Находим ID партнера по ИНН
            cursor.execute("SELECT PartnerID FROM Partners_Import WHERE INN = ?", (partner_inn,))
            partner_result = cursor.fetchone()

            if not partner_result:
                print(f"⚠️ Партнер с ИНН {partner_inn} не найден")
                return []

            partner_id = partner_result[0]
            print("ID партнера:", partner_id)

            # ИСПРАВЛЕННЫЙ ЗАПРОС: используем ROWID для получения реального ID
            query = """
            SELECT 
                ROWID as ProductID,
                ProductName, 
                MinPartnerPrice
            FROM Products_Import
            WHERE PartnerID = ?
            ORDER BY ProductName
            """

            print("SQL запрос:", query)
            print("Параметры:", [partner_id])

            cursor.execute(query, (partner_id,))
            raw_products = cursor.fetchall()

            print("Найдено записей:", len(raw_products))
            for i, product in enumerate(raw_products):
                print(f"  Запись {i}: {product}")

            # Преобразуем в нужный формат (ProductID, ProductName, MinPartnerPrice)
            products = []
            for product in raw_products:
                if len(product) >= 3:
                    product_id = product[0]  # ROWID
                    product_name = product[1]  # ProductName
                    min_price = product[2]  # MinPartnerPrice

                    # ROWID всегда существует, проверяем только название и цену
                    if product_name and min_price is not None:
                        products.append((product_id, product_name, min_price))
                        print(f"  ✅ Обработано: ID={product_id}, Название={product_name}, Цена={min_price}")
                    else:
                        print(
                            f"  ⚠️ Пропущено - некорректные данные: ID={product_id}, Название={product_name}, Цена={min_price}")
                else:
                    print(f"  ⚠️ Неполная запись: {product}")

            print("Итого продуктов для продажи:", len(products))
            conn.close()

            # ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА
            print("=== ФИНАЛЬНАЯ ПРОВЕРКА ДАННЫХ ===")
            for i, (product_id, product_name, min_price) in enumerate(products):
                print(
                    f"Продукт {i}: ID={product_id} (тип: {type(product_id)}), Название={product_name}, Цена={min_price}")

            return products

        except Exception as e:
            print("Ошибка при получении продукции для продажи:", e)
            import traceback
            traceback.print_exc()
            return []

    def add_sale(self, sale_data):
        """Добавляет новую продажу"""
        try:
            print("=== ДОБАВЛЕНИЕ ПРОДАЖИ ===")
            print("Данные продажи:", sale_data)

            conn = self.get_connection()
            cursor = conn.cursor()

            # Получаем текущую дату и время
            from datetime import datetime
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

            print("SQL запрос:", query)
            print("Значения:", values)

            cursor.execute(query, values)

            # Получаем ID добавленной продажи
            sale_id = cursor.lastrowid
            print("ID добавленной продажи:", sale_id)

            conn.commit()
            rowcount = cursor.rowcount

            # Проверяем, добавилась ли продажа
            cursor.execute("SELECT * FROM Partner_Products_Import WHERE SaleID = ?", (sale_id,))
            added_sale = cursor.fetchone()
            print("Добавленная продажа:", added_sale)

            conn.close()

            print("=== ДОБАВЛЕНИЕ ПРОДАЖИ ЗАВЕРШЕНО ===")
            return rowcount > 0

        except Exception as e:
            print("Ошибка при добавлении продажи:", e)
            import traceback
            traceback.print_exc()
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
            print("Ошибка при получении ID партнера:", e)
            return None


