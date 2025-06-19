import sqlite3
import hashlib
import os


class AuthManager:
    def __init__(self, db_path=None):
        if db_path is None:
            # Если путь не передан, используем стандартный путь
            self.db_path = "database/masterpol.db"
        else:
            self.db_path = db_path

        # Создаем директорию, если её нет
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        self.init_users_table()
        self.create_default_users()

    def get_connection(self):
        """Получает соединение с базой данных"""
        return sqlite3.connect(self.db_path)

    def hash_password(self, password):
        """Хеширует пароль с использованием SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def init_users_table(self):
        """Создает таблицу пользователей, если она не существует"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Users (
                    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Username TEXT UNIQUE NOT NULL,
                    Password TEXT NOT NULL,
                    UserType TEXT NOT NULL CHECK (UserType IN ('admin', 'user')),
                    FullName TEXT,
                    Email TEXT,
                    CreatedDate TEXT DEFAULT CURRENT_TIMESTAMP,
                    IsActive INTEGER DEFAULT 1
                )
            ''')

            conn.commit()
            conn.close()
            print("Таблица пользователей успешно создана/проверена")
            return True

        except Exception as e:
            print(f"Ошибка создания таблицы пользователей: {e}")
            return False

    def create_default_users(self):
        """Создает пользователей по умолчанию"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Проверяем, есть ли уже пользователи
            cursor.execute("SELECT COUNT(*) FROM Users")
            count = cursor.fetchone()[0]

            if count == 0:
                # Создаем администратора по умолчанию
                admin_password = self.hash_password("admin123")
                cursor.execute('''
                    INSERT INTO Users (Username, Password, UserType, FullName, Email)
                    VALUES (?, ?, ?, ?, ?)
                ''', ("admin", admin_password, "admin", "Администратор системы", "admin@masterpol.ru"))

                # Создаем пользователя по умолчанию
                user_password = self.hash_password("user123")
                cursor.execute('''
                    INSERT INTO Users (Username, Password, UserType, FullName, Email)
                    VALUES (?, ?, ?, ?, ?)
                ''', ("user", user_password, "user", "Пользователь системы", "user@masterpol.ru"))

                conn.commit()
                print("Созданы пользователи по умолчанию")
            else:
                print("Пользователи уже существуют в базе данных")

            conn.close()
            return True

        except Exception as e:
            print(f"Ошибка создания пользователей по умолчанию: {e}")
            return False

    def authenticate_user(self, username, password, user_type):
        """Аутентифицирует пользователя"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            hashed_password = self.hash_password(password)

            cursor.execute('''
                SELECT UserID, Username, UserType, FullName, IsActive 
                FROM Users 
                WHERE Username = ? AND Password = ? AND UserType = ? AND IsActive = 1
            ''', (username, hashed_password, user_type))

            user_data = cursor.fetchone()
            conn.close()

            return user_data is not None

        except Exception as e:
            print(f"Ошибка аутентификации: {e}")
            return False

    def register_user(self, username, password, user_type, full_name="", email=""):
        """Регистрирует нового пользователя"""
        try:
            if self.user_exists(username):
                return False, "Пользователь с таким логином уже существует"

            conn = self.get_connection()
            cursor = conn.cursor()

            hashed_password = self.hash_password(password)

            cursor.execute('''
                INSERT INTO Users (Username, Password, UserType, FullName, Email)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, hashed_password, user_type, full_name, email))

            conn.commit()
            conn.close()

            return True, "Пользователь успешно зарегистрирован"

        except Exception as e:
            return False, f"Ошибка регистрации: {str(e)}"

    def user_exists(self, username):
        """Проверяет, существует ли пользователь с таким логином"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM Users WHERE Username = ?", (username,))
            count = cursor.fetchone()[0]
            conn.close()

            return count > 0

        except Exception as e:
            return False

    def get_user_info(self, username):
        """Получает информацию о пользователе"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT UserID, Username, UserType, FullName, Email, CreatedDate
                FROM Users 
                WHERE Username = ? AND IsActive = 1
            ''', (username,))

            user_data = cursor.fetchone()
            conn.close()

            if user_data:
                return {
                    'user_id': user_data[0],
                    'username': user_data[1],
                    'user_type': user_data[2],
                    'full_name': user_data[3],
                    'email': user_data[4],
                    'created_date': user_data[5]
                }
            return None

        except Exception as e:
            return None

    def change_password(self, username, old_password, new_password):
        """Изменяет пароль пользователя"""
        try:
            # Сначала проверяем старый пароль
            conn = self.get_connection()
            cursor = conn.cursor()

            old_hashed = self.hash_password(old_password)
            cursor.execute('''
                SELECT UserID FROM Users 
                WHERE Username = ? AND Password = ? AND IsActive = 1
            ''', (username, old_hashed))

            if not cursor.fetchone():
                conn.close()
                return False, "Неверный текущий пароль"

            # Обновляем пароль
            new_hashed = self.hash_password(new_password)
            cursor.execute('''
                UPDATE Users 
                SET Password = ? 
                WHERE Username = ? AND IsActive = 1
            ''', (new_hashed, username))

            conn.commit()
            conn.close()

            return True, "Пароль успешно изменен"

        except Exception as e:
            return False, f"Ошибка изменения пароля: {str(e)}"

    def get_all_users(self):
        """Получает список всех пользователей (только для админов)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT UserID, Username, UserType, FullName, Email, CreatedDate, IsActive
                FROM Users 
                ORDER BY CreatedDate DESC
            ''')

            users = cursor.fetchall()
            conn.close()

            return users

        except Exception as e:
            return []

    def deactivate_user(self, username):
        """Деактивирует пользователя"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE Users 
                SET IsActive = 0 
                WHERE Username = ?
            ''', (username,))

            conn.commit()
            rowcount = cursor.rowcount
            conn.close()

            return rowcount > 0

        except Exception as e:
            return False

    def activate_user(self, username):
        """Активирует пользователя"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE Users 
                SET IsActive = 1 
                WHERE Username = ?
            ''', (username,))

            conn.commit()
            rowcount = cursor.rowcount
            conn.close()

            return rowcount > 0

        except Exception as e:
            return False