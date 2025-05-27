import asyncpg
import os

import pytz
from dotenv import load_dotenv
from datetime import datetime, timedelta
from loguru import logger

load_dotenv()

db_host = "91.132.224.176"
async def select_user_id(user_tg_id):
    connection = None
    try:
        connection = await asyncpg.connect(
            host=db_host,
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB')
        )
        # print("Connected to the database")
        logger.debug(f"TG ID: {user_tg_id}, DB - users table = connected")

        query = "SELECT * FROM users WHERE tg_id = $1"
        user = await connection.fetchrow(query, int(user_tg_id))

        return user

    except Exception as e:
        # print(f"Error occurred: {e}")
        logger.error(f"TG ID: {user_tg_id}, Error occurred: {e}")

    finally:
        if connection:
            await connection.close()
            # print("Connection closed.")
            logger.debug(f"TG ID: {user_tg_id}, DB - users table = connection closed.")


# async def add_user(
#         user_name,
#         user_email,
#         user_tel_number,
#         user_tg_id):
#     connection = None
#     try:
#         connection = await asyncpg.connect(
#             # host="46.30.42.146",
#             host=db_host,
#             user=os.getenv('POSTGRES_USER'),
#             password=os.getenv('POSTGRES_PASSWORD'),
#             database=os.getenv('POSTGRES_DB')
#         )
#         # print("Connected to the database")
#         logger.debug(f"TG ID: {user_tg_id}, DB - users table = connected")
#
#         # SQL-запрос для добавления пользователя
#         query = """
#                 INSERT INTO users(name, email, tel_number, tg_id)
#                 VALUES($1, $2, $3, $4)
#                 """
#         await connection.execute(query, user_name, user_email, user_tel_number, user_tg_id)
#         # print(f"User {user_name} added successfully.")
#         logger.debug(f"TG ID: {user_tg_id} added to DB - users table = successfully.")
#
#     except Exception as e:
#         # print(f"Error occurred: {e}")
#         logger.error(f"TG ID: {user_tg_id}, Error occurred: {e}")
#
#     finally:
#         if connection:
#             await connection.close()
#             # print("Connection closed.")
#             logger.debug(f"TG ID: {user_tg_id}, DB - users table = connection closed.")
async def add_user(
        user_name,
        user_email,
        user_tel_number,
        user_tg_id,
        tg_first_name=None,
        tg_last_name=None,
        tg_username=None,
        tg_language_code=None,
        tg_is_premium=False):
    connection = None
    try:
        connection = await asyncpg.connect(
            host=db_host,
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB')
        )
        logger.debug(f"TG ID: {user_tg_id}, DB - users table = connected")

        # SQL-запрос для добавления пользователя с новыми колонками
        query = """
                INSERT INTO users(name, email, tel_number, tg_id, tg_first_name, tg_last_name, tg_username, tg_language_code, tg_is_premium)
                VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """
        await connection.execute(query,
                                 user_name,
                                 user_email,
                                 user_tel_number,
                                 user_tg_id,
                                 tg_first_name,
                                 tg_last_name,
                                 tg_username,
                                 tg_language_code,
                                 tg_is_premium,)
        logger.debug(f"TG ID: {user_tg_id} added to DB - users table = successfully.")

    except Exception as e:
        logger.error(f"TG ID: {user_tg_id}, Error occurred: {e}")

    finally:
        if connection:
            await connection.close()
            logger.debug(f"TG ID: {user_tg_id}, DB - users table = connection closed.")


# async def add_violation(
#         tg_id: object,
#         main_category: object,
#         violation_type: object,
#         address: object,
#         violation_url: object,
#         violation_URI_full: object):
#     connection = None
#     try:
#         connection = await asyncpg.connect(
#             host="46.30.42.146",
#             user=os.getenv('POSTGRES_USER'),
#             password=os.getenv('POSTGRES_PASSWORD'),
#             database=os.getenv('POSTGRES_DB')
#         )
#         print("Connected to the database")
#
#         # SQL-запрос для добавления нарушения с текущей датой
#         query = """
#                 INSERT INTO violation(tg_id, main_category, violation_type, address, violation_url, violation_URI_full, addition_date)
#                 VALUES($1, $2, $3, $4, $5, $6, CURRENT_DATE)  -- Добавление текущей даты в колонку addition_date
#                 """
#         await connection.execute(query, str(tg_id), main_category, violation_type, address, violation_url, violation_URI_full)
#         print(f"Violation added successfully for TG ID: {tg_id}.")
#
#     except Exception as e:
#         print(f"An error occurred while adding the violation: {e}")
#
#     finally:
#         if connection is not None:
#             await connection.close()
#             print("Database connection closed.")


# async def number_of_violations(user_tg_id):
#     connection = None
#     try:
#         connection = await asyncpg.connect(
#             host="46.30.42.146",
#             user=os.getenv('POSTGRES_USER'),
#             password=os.getenv('POSTGRES_PASSWORD'),
#             database=os.getenv('POSTGRES_DB')
#         )
#         print("Connected to the database")
#
#         query = "SELECT count(tg_id) FROM violation WHERE tg_id = $1 AND status = $2"
#         value = await connection.fetchrow(query, str(user_tg_id))
#         return value['count']
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         if connection:
#             await connection.close()
# async def add_violation(tg_id,
#                         main_category,
#                         violation_type,
#                         address,
#                         violation_url,
#                         violation_URI_full):
#     connection = None
#     try:
#         connection = await asyncpg.connect(
#             # host="46.30.42.146",
#             host=db_host,
#             user=os.getenv('POSTGRES_USER'),
#             password=os.getenv('POSTGRES_PASSWORD'),
#             database=os.getenv('POSTGRES_DB')
#         )
#         print("Connected to the database")
#
#         # SQL-запрос для добавления нарушения с возвратом нового id
#         query = """
#             INSERT INTO violation(tg_id, main_category, violation_type, address, violation_url, violation_URI_full, addition_date)
#             VALUES($1, $2, $3, $4, $5, $6, CURRENT_DATE)
#             RETURNING id;  -- Возвращает id новой записи
#         """
#         new_id = await connection.fetchval(
#             query,
#             str(tg_id),
#             main_category,
#             violation_type,
#             address,
#             violation_url,
#             violation_URI_full
#         )
#         print(f"Violation added successfully for TG ID: {tg_id}. New ID: {new_id}")
#
#         return new_id
#
#     except Exception as e:
#         print(f"An error occurred while adding the violation: {e}")
#         return None
#
#     finally:
#         if connection is not None:
#             await connection.close()
#             print("Database connection closed.")

# async def number_of_violations(user_tg_id, status=1):
#     connection = None
#     try:
#         connection = await asyncpg.connect(
#             host="46.30.42.146",
#             user=os.getenv('POSTGRES_USER'),
#             password=os.getenv('POSTGRES_PASSWORD'),
#             database=os.getenv('POSTGRES_DB')
#         )
#         print("Connected to the database")
#
#         query = "SELECT count(tg_id) AS count FROM violation WHERE tg_id = $1 AND status = $2"
#         value = await connection.fetchrow(query, str(user_tg_id), status)
#
#         if value is None:
#             return 0  # Или другое значение, которое вы считаете подходящим
#         return value['count']
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         if connection:
#             await connection.close()

# Ниже вариант со сбором не нужной инфы о месте хранения изображения на серверах ТГ
# async def add_violation(tg_id,
#                         main_category,
#                         violation_type,
#                         address,
#                         violation_url,
#                         violation_URI_full):
# async def add_violation(tg_id,
#                         main_category,
#                         violation_type,
#                         address,):
#     connection = None
#     try:
#         connection = await asyncpg.connect(
#             host=db_host,
#             user=os.getenv('POSTGRES_USER'),
#             password=os.getenv('POSTGRES_PASSWORD'),
#             database=os.getenv('POSTGRES_DB')
#         )
#         # print("Connected to the database")
#         logger.debug(f"TG ID: {tg_id}, DB - violation table = connected")
#
#         # Установка московского времени
#         moscow_timezone = pytz.timezone('Europe/Moscow')
#         addition_date = datetime.now(moscow_timezone)  # Текущая дата и время в московском часовом поясе
#
#         # SQL-запрос для добавления нарушения с возвратом нового id
#         query = """
#             INSERT INTO violation(tg_id, main_category, violation_type, address, addition_date)
#             VALUES($1, $2, $3, $4, $5)
#             RETURNING id;  -- Возвращает id новой записи
#         """
#         new_id = await connection.fetchval(
#             query,
#             tg_id,
#             main_category,
#             violation_type,
#             address,
#             addition_date  # Передаём московскую дату и время как параметр
#         )
#         # print(f"Violation added successfully for TG ID: {tg_id}. New ID: {new_id}")
#         logger.debug(f"TG ID: {tg_id}, Violation ID: {new_id} added successfully")
#
#         return new_id
#
#     except Exception as e:
#         # print(f"An error occurred while adding the violation: {e}")
#         logger.error(f"TG ID: {tg_id}, An error occurred while adding new violation: {e}")
#         return None
#
#     finally:
#         if connection is not None:
#             await connection.close()
#             # print("Database connection closed.")
#             logger.debug(f"TG ID: {tg_id}, DB - violation table = connection closed.")
##
# Вариант добавления нарушения в таблицу с новыми колонками подъезд и этаж
async def add_violation(tg_id,
                        main_category,
                        violation_type,
                        address,
                        floor=None,
                        entrance=None):
    connection = None
    try:
        connection = await asyncpg.connect(
            host=db_host,
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB')
        )
        logger.debug(f"TG ID: {tg_id}, DB - violation table = connected")

        # Установка московского времени
        moscow_timezone = pytz.timezone('Europe/Moscow')
        addition_date = datetime.now(moscow_timezone)

        # Преобразуем строковые числа в int (если переданы)
        floor = int(floor) if isinstance(floor, str) and floor.isdigit() else None
        entrance = int(entrance) if isinstance(entrance, str) and entrance.isdigit() else None

        # SQL-запрос
        query = """
            INSERT INTO violation(tg_id, main_category, violation_type, address, addition_date, floor, entrance)
            VALUES($1, $2, $3, $4, $5, $6, $7)
            RETURNING id;
        """
        new_id = await connection.fetchval(
            query,
            tg_id,
            main_category,
            violation_type,
            address,
            addition_date,
            floor,
            entrance
        )
        logger.debug(f"TG ID: {tg_id}, Violation ID: {new_id} added successfully")

        return new_id

    except Exception as e:
        logger.error(f"TG ID: {tg_id}, An error occurred while adding new violation: {e}")
        return None

    finally:
        if connection is not None:
            await connection.close()
            logger.debug(f"TG ID: {tg_id}, DB - violation table = connection closed.")



# async def number_of_violations(user_tg_id, status=None):
#     connection = None
#     try:
#         connection = await asyncpg.connect(
#             host=db_host,
#             user=os.getenv('POSTGRES_USER'),
#             password=os.getenv('POSTGRES_PASSWORD'),
#             database=os.getenv('POSTGRES_DB')
#         )
#         # print("Connected to the database")
#         logger.debug(f"TG ID: {user_tg_id}, DB - violation table = connected")
#
#         if status is None:
#             # Если статус не указан, считаем для всех статусов
#             query = "SELECT count(tg_id) AS count FROM violation WHERE tg_id = $1"
#             value = await connection.fetchrow(query, user_tg_id)
#             logger.debug(f"TG ID: {user_tg_id}, Посчитали для всех статусов: {value}")
#         else:
#             # Если статус указан, считаем только для этого статуса
#             query = "SELECT count(tg_id) AS count FROM violation WHERE tg_id = $1 AND status = $2"
#             value = await connection.fetchrow(query, user_tg_id, status)
#             logger.debug(f"TG ID: {user_tg_id}, Посчитали только для статуса {status}: {value}")
#
#         if value is None:
#             logger.warning(f"TG ID: {user_tg_id}, для пользователя записей не найдено")
#             return 0  # Если записи не найдены, возвращаем 0
#         logger.debug(f"TG ID: {user_tg_id}, Количество записей: {value['count']}")
#         return value['count']  # Возвращаем найденное количество записей
#     except Exception as e:
#         # print(f"Error: {e}")
#         logger.error(f"TG ID: {user_tg_id}, Error: {e}")
#         return 0  # Возвращаем 0 в случае ошибки
#     finally:
#         if connection:
#             await connection.close()  # Закрываем соединение
#             logger.debug(f"TG ID: {user_tg_id}, DB - violation table = connection closed.")

#этот вариант функции возвращает список с суммой записей для статуса 1, 2 и общим количеством.
async def number_of_violations(user_tg_id):
    connection = None
    try:
        connection = await asyncpg.connect(
            host=db_host,
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB')
        )
        logger.debug(f"TG ID: {user_tg_id}, DB - violation table = connected")

        # Один запрос для подсчёта всех данных
        query = """
            SELECT
                COUNT(CASE WHEN status = 1 THEN 1 END) AS count_status_1,
                COUNT(CASE WHEN status = 2 THEN 1 END) AS count_status_2,
                COUNT(CASE WHEN status IN (1, 2) THEN 1 END) AS total_count
            FROM violation
            WHERE tg_id = $1
        """
        result = await connection.fetchrow(query, user_tg_id)

        if result is None:
            logger.warning(f"TG ID: {user_tg_id}, для пользователя записей не найдено")
            return [0, 0, 0]

        count_status_1 = result['count_status_1']
        count_status_2 = result['count_status_2']
        total_count = result['total_count']

        logger.debug(f"TG ID: {user_tg_id}, Статус 1: {count_status_1}, Статус 2: {count_status_2}, Общее: {total_count}")
        return [count_status_1, count_status_2, total_count]

    except Exception as e:
        logger.error(f"TG ID: {user_tg_id}, Error: {e}")
        return [0, 0, 0]  # Возвращаем [0, 0, 0] в случае ошибки
    finally:
        if connection:
            await connection.close()
            logger.debug(f"TG ID: {user_tg_id}, DB - violation table = connection closed.")


async def get_user_violations_list(user_tg_id, status=1):
    connection = None
    try:
        # Подключаемся к базе данных
        connection = await asyncpg.connect(
            # host="46.30.42.146",
            host=db_host,
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB')
        )
        # print("Connected to the database")
        logger.debug(f"TG ID: {user_tg_id}, DB - violation table = connected")

        # Строим SQL-запрос с фильтром по статусу, если статус указан
        query = """
            SELECT id, violation_type, addition_date,
                   CASE
                       WHEN LENGTH(address) > 40 THEN CONCAT(LEFT(address, 37), '...')
                       ELSE address
                   END AS short_address,
                   status
            FROM violation
            WHERE tg_id = $1 AND status = $2
        """

        # Если параметр status передан, добавляем условие в запрос
        if status is not None:
            query += " AND status = $2"
            params = (user_tg_id, status)
            logger.debug(f"TG ID: {user_tg_id}, параметр status передан: {status}")
        else:
            params = (user_tg_id,)
            logger.debug(f"TG ID: {user_tg_id}, параметр status не передан")

        query += " ORDER BY id"

        # Выполняем запрос и передаем параметры
        rows = await connection.fetch(query, *params)

        # Преобразуем результат в список кортежей
        result = []
        for row in rows:
            result.append((row['id'],
                           row['violation_type'],
                           row['addition_date'],
                           row['short_address'],
                           row['status']))

        return result

    except Exception as e:
        # print(f"Error: {e}")
        logger.error(f"TG ID: {user_tg_id}, Error: {e}")
        return []

    finally:
        if connection:
            await connection.close()
            # print("Database connection closed")
            logger.debug(f"TG ID: {user_tg_id}, DB - violation table = connection closed.")


async def get_violations_info_by_id(user_tg_id, violation_id):
    connection = None
    try:
        # Подключаемся к базе данных
        connection = await asyncpg.connect(
            host=db_host,
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB')
        )
        # print("Connected to the database")
        logger.debug(f"TG ID: {user_tg_id}, DB - violation table = connected")

        # SQL-запрос для получения информации о нарушении
        query = """
                SELECT id, violation_type, addition_date, 
                       CASE 
                           WHEN LENGTH(address) > 50 THEN CONCAT(LEFT(address, 47), '...')
                           ELSE address
                       END AS short_address,
                       status
                FROM violation
                WHERE id = $1
                ORDER BY addition_date DESC, id
            """

        # Выполняем запрос и получаем одну строку (fetchrow возвращает один результат)
        row = await connection.fetchrow(query, int(violation_id))

        # Проверяем, что результат не пустой
        if row:
            # Возвращаем результат в виде кортежа
            return (row['id'],
                    row['violation_type'],
                    row['addition_date'],
                    row['short_address'],
                    row['status'])
        else:
            # print(f"Violation with ID {violation_id} not found.")
            logger.error(f"TG ID: {user_tg_id}, violation ID: {violation_id} not found.")
            return None

    except Exception as e:
        import traceback
        # print(f"Error: {e}")
        logger.error(f"TG ID: {user_tg_id}, Error: {e}")
        # print(traceback.format_exc())  # Печатает полный стектрейс ошибки
        logger.error(traceback.format_exc())
        return None

    finally:
        if connection:
            await connection.close()
            # print("Database connection closed")
            logger.debug(f"TG ID: {user_tg_id}, DB - violation table = connection closed.")


# async def update_violation_status(violation_id, new_status):
#     connection = None
#     try:
#         # Подключаемся к базе данных
#         connection = await asyncpg.connect(
#             host="46.30.42.146",
#             user=os.getenv('POSTGRES_USER'),
#             password=os.getenv('POSTGRES_PASSWORD'),
#             database=os.getenv('POSTGRES_DB')
#         )
#         print("Connected to the database")
#
#         # Строим SQL-запрос для обновления статуса
#         query = """
#             UPDATE violation
#             SET status = $1
#             WHERE id = $2
#         """
#
#         # Выполняем запрос и передаем параметры
#         await connection.execute(query, new_status, violation_id)
#         print(f"Status for violation ID {violation_id} updated to {new_status}")
#
#     except Exception as e:
#         print(f"Error: {e}")
#
#     finally:
#         if connection:
#             await connection.close()
#             print("Database connection closed")
async def update_violation_status(user_tg_id, violation_id, status):
    connection = None
    try:
        connection = await asyncpg.connect(
            host=db_host,
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB')
        )
        # print("Connected to the database")
        logger.debug(f"TG ID: {user_tg_id}, DB - violation table = connected")

        # Проверка: если статус равен 2, устанавливаем дополнительно notice_date и expiry_date
        if status == 2:
            logger.debug(f"TG ID: {user_tg_id}, status is 2, updating notice_date and expiry_date for violation ID {violation_id}")
            moscow_timezone = pytz.timezone('Europe/Moscow')
            current_date = datetime.now(moscow_timezone).date()  # Текущая дата как объект date
            expiry_date = (datetime.now(moscow_timezone) + timedelta(days=10)).date()  # Текущая дата + 10 дней как объект date

            # SQL запрос обновляет status, notice_date, expiry_date при status=2
            query = """
                UPDATE violation
                SET status = $1,
                    notice_date = $2,
                    expiry_date = $3
                WHERE id = $4
            """
            await connection.execute(query, status, current_date, expiry_date, violation_id)

        else:
            # Обновление только status, если он не равен 2
            query = """
                UPDATE violation
                SET status = $1
                WHERE id = $2
            """
            await connection.execute(query, status, violation_id)

        # print(f"Status updated to {status} for violation ID {violation_id}")
        logger.debug(f"TG ID: {user_tg_id}, violation ID: {violation_id}, status updated to {status}")

    except Exception as e:
        # print(f"Error: {e}")
        logger.error(f"TG ID: {user_tg_id}, Error: {e}")
    finally:
        if connection:
            # await connection.close()
            logger.debug(f"TG ID: {user_tg_id}, DB - violation table = connection closed.")


async def get_last_id_in_violation(tg_id: int):
    connection = None
    try:
        connection = await asyncpg.connect(
            host=db_host,
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB')
        )
        # print("Connected to the database")
        logger.debug(f"TG ID: {tg_id}, DB - violation table = connected")

        # SQL-запрос для получения последнего id для указанного tg_id
        query = """
            SELECT id FROM violation WHERE tg_id = $1 ORDER BY id DESC LIMIT 1;
        """
        last_id = await connection.fetchval(query, tg_id)
        return last_id

    except Exception as e:
        # print(f"An error occurred while retrieving the last violation ID: {e}")
        logger.error(f"TG ID: {tg_id}, An error occurred while retrieving the last violation ID: {e}")

    finally:
        if connection is not None:
            await connection.close()
            # print("Database connection closed.")
            logger.debug(f"TG ID: {tg_id}, DB - violation table = connection closed.")


async def get_name_in_db(user_tg_id):
    connection = None
    try:
        connection = await asyncpg.connect(
            host=db_host,
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB')
        )
        logger.debug(f"TG ID: {user_tg_id}, DB - users table = connected")

        query = "SELECT name FROM users WHERE tg_id = $1"
        name = await connection.fetchval(query, user_tg_id)

        if name is None:
            logger.warning(f"TG ID: {user_tg_id}, user not found in the database.")
            return None  # Пользователь не найден

        logger.debug(f"TG ID: {user_tg_id}, user \"{name}\" found in the database.")  # Имя пользователя найдено
        return name

    except Exception as e:
        logger.error(f"TG ID: {user_tg_id}, Error occurred: {e}")
        return None  # В случае ошибки вернём None

    finally:
        if connection:
            await connection.close()
            logger.debug(f"TG ID: {user_tg_id}, DB - users table = connection closed.")
