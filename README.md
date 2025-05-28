# 🚨 Telegram-бот для фиксации нарушений

## 📝 Описание

Telegram-бот на базе [aiogram 3](https://docs.aiogram.dev/en/latest/), предназначенный для фиксации и обработки нарушений (например, в ЖКХ), автоматизации уведомлений, генерации PDF-документов с QR-кодами, отправки email и хранения данных пользователей и нарушений в базе данных (PostgreSQL).

---

## 💡 Основные возможности

- Регистрация пользователей с валидацией имени, email и телефона
- Фиксация нарушений: пошаговый сценарий с вводом адреса, подъезда, этажа, типа нарушения, фото и комментария
- Генерация PDF-уведомлений с фото, QR-кодом и логотипом
- Отправка уведомлений по email
- Загрузка файлов в Google Drive
- Хранение данных о пользователях и нарушениях в PostgreSQL
- Поддержка FSM (Finite State Machine) для сценариев взаимодействия
- Логирование событий через loguru
- Кастомные клавиатуры и inline-кнопки для удобства

---

## ⚙️ Установка

1. **Клонируйте репозиторий:**

```bash
git clone <repo_url>
cd <repo_dir>
```

2. **Создайте и активируйте виртуальное окружение:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. **Установите зависимости:**

```bash
pip install -r requirements.txt
```

4. **Создайте файл `.env` в корне проекта и укажите переменные:**

```
TOKEN=ваш_telegram_bot_token
ADMIN_TG_ID=telegram_id_администратора
POSTGRES_USER=пользователь_бд
POSTGRES_PASSWORD=пароль_бд
POSTGRES_DB=имя_бд
SMTP_USER=логин_почты
SMTP_PASSWORD=пароль_почты
```

5. **(Опционально) Настройте Google Drive:**
- Поместите файл `service_account.json` с сервисным аккаунтом Google в корень проекта.

---

## 🚀 Запуск

```bash
python run.py
```

---

## 🏗️ Архитектура проекта

- `run.py` — точка входа, запуск Telegram-бота
- `requirements.txt` — зависимости
- `app/handlers/` — обработчики команд и сценариев (регистрация, фиксация нарушений и др.)
- `app/db/` — работа с базой данных (PostgreSQL, SQLite)
- `app/functions/` — вспомогательные функции (работа с PDF, email, Google Drive, адресами и др.)
- `app/kb/` — клавиатуры для Telegram-бота
- `app/pagination/` — логика постраничного вывода
- `app/etc/` — константы, FSM-состояния, списки нарушений
- `app/pdf_elements/` — ресурсы для PDF (шрифты, логотипы)
- `bot_logs/` — логи работы бота

---

## 🗂️ Структура проекта

```text
.
├── run.py
├── requirements.txt
├── README.md
├── .env (создайте самостоятельно)
├── service_account.json (Google API, опционально)
├── app/
│   ├── handlers/         # Обработчики команд и сценариев
│   ├── db/               # Работа с базой данных
│   ├── functions/        # Вспомогательные функции (PDF, email, облако и др.)
│   ├── kb/               # Клавиатуры для Telegram-бота
│   ├── pagination/       # Постраничный вывод оформленных нарушений
│   ├── etc/              # Константы, FSM, списки нарушений
│   ├── pdf_elements/     # Шрифты, логотипы для PDF
│   └── ...
├── bot_logs/             # Логи работы бота
├── .venv/                # Виртуальное окружение
```
---

## 🗄️ Структура базы данных (PostgreSQL)

### Таблица `users`

| Поле            | Тип данных   | Описание                        |
|-----------------|-------------|---------------------------------|
| id              | SERIAL      | Первичный ключ                  |
| name            | TEXT        | Имя пользователя                |
| email           | TEXT        | Email пользователя              |
| tel_number      | TEXT        | Телефон пользователя            |
| tg_id           | BIGINT      | Telegram ID пользователя        |
| tg_first_name   | TEXT        | Имя в Telegram                  |
| tg_last_name    | TEXT        | Фамилия в Telegram              |
| tg_username     | TEXT        | Username в Telegram             |
| tg_language_code| TEXT        | Язык Telegram                   |
| tg_is_premium   | BOOLEAN     | Признак Telegram Premium        |

### Таблица `violation`

| Поле         | Тип данных   | Описание                                      |
|--------------|-------------|-----------------------------------------------|
| id           | SERIAL      | Первичный ключ                                |
| tg_id        | BIGINT      | Telegram ID пользователя                      |
| main_category| TEXT        | Основная категория нарушения                  |
| violation_type| TEXT       | Тип нарушения                                 |
| address      | TEXT        | Адрес нарушения                               |
| addition_date| TIMESTAMP   | Дата и время добавления                       |
| floor        | INTEGER     | Этаж (опционально)                            |
| entrance     | INTEGER     | Подъезд (опционально)                         |
| status       | INTEGER     | Статус нарушения (например, 1 — новое, 2 — подтверждено) |
| notice_date  | DATE        | Дата уведомления (опционально)                |
| expiry_date  | DATE        | Дата истечения срока (опционально)            |

---


## 🔄 Основные сценарии работы

### 1. 👤 Регистрация пользователя
- Ввод имени, email, телефона
- Данные сохраняются в PostgreSQL

### 2. 📸 Фиксация нарушения
- Ввод адреса, подъезда, этажа
- Выбор типа нарушения
- Загрузка фото и комментария
- Генерация PDF-уведомления с QR-кодом
- Отправка PDF на email и/или в Google Drive

### 3. 🗃️ Управление нарушениями
- Просмотр, подтверждение, редактирование нарушений

---

## 🛠️ Переменные окружения

- `TOKEN` — токен Telegram-бота
- `ADMIN_TG_ID` — Telegram ID администратора
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` — доступ к PostgreSQL
- `SMTP_USER`, `SMTP_PASSWORD` — доступ к SMTP для отправки email
- (опционально) переменные для Google Drive API

---

## 📄 Пример .env

```text
TOKEN=123456789:ABCDEF...
ADMIN_TG_ID=123456789
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=yourdb
SMTP_USER=your@mail.ru
SMTP_PASSWORD=yourpassword
```

---

## 📦 Зависимости

Все зависимости указаны в `requirements.txt`. Основные:
- aiogram
- loguru
- python-dotenv
- asyncpg
- reportlab, pillow, qrcode (PDF и изображения)
- google-api-python-client (Google Drive)

---

## 📬 Контакты и поддержка

По вопросам и предложениям — пишите на negonifas@gmail.com  
