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