import sqlite3


class Database:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_db()

    def create_db(self):
        try:
            query = ("CREATE TABLE IF NOT EXISTS users("
                     "id INTEGER PRIMARY KEY,"
                     "name TEXT,"
                     "email TEXT,"
                     "tel_number TEXT,"
                     "tg_id TEXT);")
            self.cursor.execute(query)
            self.connection.commit()
        except sqlite3.Error as Error:
            print("Ошибка при создании:", Error)

    def add_user(self, user_name,
                 user_email,
                 user_tel_number,
                 user_tg_id):
        self.cursor.execute(f"INSERT INTO users(name, email, tel_number, tg_id) VALUES (?, ?, ?, ?)", (user_name,
                                                                                                       user_email,
                                                                                                       user_tel_number,
                                                                                                       user_tg_id))
        self.connection.commit()

    def select_user_id(self, user_tg_id):
        users = self.cursor.execute("SELECT * FROM users WHERE tg_id = ?", (user_tg_id,))
        return users.fetchone()

    def __del__(self):
        self.cursor.close()
        self.connection.close()

