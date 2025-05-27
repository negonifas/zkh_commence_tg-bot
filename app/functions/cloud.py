from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.http import MediaFileUpload
from loguru import logger

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'
PARENT_FOLDER_ID = "1zBnLYWMSH917C_wtGM5yb6t2sksnE0XB"


def file_stream_to_cloud(user_tg_id, file_stream, folder_name, file_name):
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)

    # Поиск существующей папки с тем же именем в родительской папке PARENT_FOLDER_ID
    # folder_id = None
    query = f"'{PARENT_FOLDER_ID}' in parents and name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get('files', [])

    if folders:
        folder_id = folders[0]['id']
        # print(f"Найдена существующая папка '{folder_name}' с ID: {folder_id}")
        logger.debug(f"TG ID: {user_tg_id}, найдена существующая папка '{folder_name}' с ID: {folder_id}")
    else:
        # Создание новой папки, если она не найдена
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [PARENT_FOLDER_ID]  # Обязательно указываем родительскую папку
        }
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder.get('id')
        # print(f"Папка '{folder_name}' создана с ID: {folder_id}")
        logger.debug(f"TG ID: {user_tg_id}, папка '{folder_name}' создана с ID: {folder_id}")

    # Загрузка изображения в найденную или новую папку
    media = MediaIoBaseUpload(file_stream, mimetype='image/jpeg', resumable=True)
    file_metadata = {
        'name': f"{file_name}",
        'parents': [folder_id]
    }

    try:
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        file_id = file.get('id')
        # print(f"TG ID: {user_tg_id}, файл загружен с ID: {file_id}")
        logger.debug(f"TG ID: {user_tg_id}, файл загружен с ID: {file_id}")

        # # Настройка прав доступа без передачи собственности
        # permission = {
        #     'type': 'user',
        #     'role': 'writer',
        #     'emailAddress': 'revizorzkh@gmail.com',
        # }
        # service.permissions().create(
        #     fileId=file_id,
        #     body=permission
        # ).execute()
        #
        # # Формирование расшаренной ссылки
        # shared_url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
        # print(f"Ссылка для общего доступа: {shared_url}")
        # return shared_url

    except Exception as e:
        # print(f"TG ID: {user_tg_id}, ошибка при загрузке файла: {e}")
        logger.error(f"TG ID: {user_tg_id}, ошибка при загрузке файла в G-облако: {e}")


def file_to_cloud(user_tg_id, file, folder_name, file_name):
    # Аутентификация
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)

    # Поиск существующей папки с тем же именем в указанной родительской папке
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false and '{PARENT_FOLDER_ID}' in parents"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get('files', [])

    if folders:
        folder_id = folders[0]['id']
        # print(f"TG ID: {user_tg_id}, найдена существующая папка '{folder_name}' с ID: {folder_id}")
        logger.debug(f"TG ID: {user_tg_id}, найдена существующая папка '{folder_name}' с ID: {folder_id}")
    else:
        # Создание новой папки, если она не найдена
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [PARENT_FOLDER_ID]
        }

        folder = service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder.get('id')
        # print(f"Папка '{folder_name}' создана с ID: {folder_id}")
        logger.debug(f"TG ID: {user_tg_id}, папка '{folder_name}' создана с ID: {folder_id}")

    # Загрузка файла в найденную или новую папку
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }

    try:
        file = service.files().create(
            body=file_metadata,
            media_body=file
        ).execute()
        file_id = file.get('id')
        # print(f"Файл '{file_name}' загружен с ID: {file_id}")
        logger.debug(f"TG ID: {user_tg_id}, файл '{file_name}' загружен с ID: {file_id}")

        # # Настройка прав доступа
        # permission = {
        #     'type': 'user',  # Указываем, что даем доступ конкретному пользователю
        #     'role': 'writer',  # Передаем полное владение
        #     'emailAddress': 'revizorzkh@gmail.com'  # Ваш email для добавления прав
        # }
        # service.permissions().create(
        #     fileId=file_id,
        #     body=permission,
        #     # transferOwnership=True  # Передаем право владельца
        # ).execute()
        #
        # # Формирование расшаренной ссылки
        # shared_url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
        # print(f"Ссылка для общего доступа: {shared_url}")
        # return shared_url

    except Exception as e:
        # print(f"Ошибка при загрузке файла: {e}")
        logger.error(f"TG ID: {user_tg_id}, ошибка при загрузке файла: {e}")


def pdf_to_cloud(user_tg_id, pdf_file, folder_name, file_name):
    # Аутентификация
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)

    # Поиск существующей папки с тем же именем в указанной родительской папке
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false and '{PARENT_FOLDER_ID}' in parents"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get('files', [])

    if folders:
        folder_id = folders[0]['id']
        # print(f"Найдена существующая папка '{folder_name}' с ID: {folder_id}")
        logger.debug(f"TG ID: {user_tg_id}, найдена существующая папка '{folder_name}' with ID: {folder_id}")
    else:
        # Создание новой папки, если она не найдена
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [PARENT_FOLDER_ID]
        }

        folder = service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder.get('id')
        # print(f"Папка '{folder_name}' создана с ID: {folder_id}")
        logger.debug(f"TG ID: {user_tg_id}, папка '{folder_name}' создана с ID: {folder_id}")

    # Загрузка файла в найденную или новую папку
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    # Указание MIME-типа файла для загрузки
    pdf_file = MediaFileUpload(pdf_file, mimetype='application/pdf')

    try:
        file = service.files().create(
            body=file_metadata,
            media_body=pdf_file
        ).execute()
        file_id = file.get('id')
        # print(f"Файл '{file_name}' загружен с ID: {file_id}")
        logger.debug(f"TG ID: {user_tg_id}, файл {file_name} загружен с ID: {file_id}")

    except Exception as e:
        print(f"Ошибка при загрузке файла: {e}")
        logger.error(f"TG ID: {user_tg_id}, ошибка при загрузке PDF файла в облако: {e}")
