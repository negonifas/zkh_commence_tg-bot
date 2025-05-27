import asyncio
import os
# from dadata import Dadata
# from dadata import DadataAsync
from dotenv import load_dotenv

# # Ваш API-ключ и секрет || https://dadata.ru/api/suggest/fias/
# API_KEY = "fcf9cd798dee7e897d3ac6b819839b829eaa0cda"
# SECRET_KEY = "c0547053b122d903e4759f1d60c683f7eff73d34"

# # Создаем экземпляр Dadata
# dadata = Dadata(API_KEY, SECRET_KEY)

# # Очистка адреса
# result = dadata.clean("address", "Москва, пирерва 2 13")
# print(result)

load_dotenv()

async def address_cleaner(address_string):
    # async with DadataAsync(os.getenv('ADDRESS_API_KEY'),
                           # os.getenv('ADDRESS_SECRET_KEY')
                           # ) as dadata:
        # clean_address_data = await dadata.clean("address", address_string)
        # return clean_address_data["result"]
        # ниже Это временный вариант
        clean_address_data = address_string
        return clean_address_data

# Пример использования
# print(asyncio.run(address_cleaner("Москва, цимлянская 30, кВ 165. Подъезд 2, этаж 22")))
