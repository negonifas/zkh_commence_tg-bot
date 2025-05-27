import asyncio
import os

import aiogram
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from loguru import logger


async def delete_messages(state: FSMContext, chat_id: int, bot: Bot):
    """Функция для удаления сообщений с указанными ID."""
    data = await state.get_data()
    registered_msg_id = data.get("registered_msg_id")  # сообщение msg из user_reg
    success_reg_msg_id = data.get("success_reg_msg_id")  # сообщение success_reg_msg из user_reg
    greeting_message = data.get("greeting_message")  # сообщение greeting_message из user_reg
    wrong_input_after_dashboard_msg_id = data.get("wrong_input_after_dashboard_msg_id")

    # Список ID сообщений для удаления
    message_ids = [registered_msg_id,
                   success_reg_msg_id,
                   greeting_message,
                   wrong_input_after_dashboard_msg_id, ]

    for msg_id in message_ids:
        if msg_id:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=msg_id)
                print(f"Сообщение с ID {msg_id} успешно удалено.")
            except TelegramBadRequest as e:
                print(f"Ошибка при удалении сообщения с ID {msg_id}: {e}")


async def delete_messages_by_names(state: FSMContext, *message_names):
    async with Bot(token=os.getenv('TOKEN')) as bot:
        data = await state.get_data()
        current_chat_id = data.get('current_chat_id')

        # if current_chat_id is None:
        #     print("Chat ID не найден в состоянии.")
        #     return

        for message_name in message_names:
            message_id = data.get(message_name)  # Получаем ID сообщения по имени

            if message_id is None:
                print(f"ID сообщения '{message_name}' не найдено в состоянии.")
                continue

            try:
                await bot.delete_message(chat_id=current_chat_id, message_id=message_id)
                print(f"Сообщение с ID {message_id} успешно удалено.")
            except TelegramBadRequest as e:
                print(f"Ошибка при удалении сообщения с ID {message_id}: {e}")


async def delete_messages_by_id(state: FSMContext, message_id: int):
    async with Bot(token=os.getenv('TOKEN')) as bot:
        data = await state.get_data()
        current_chat_id = data.get('current_chat_id')

        if current_chat_id is None:
            print("Chat ID не найден в состоянии.")
            return

        if message_id is None:
            print(f"ID сообщения не найдено в состоянии.")

        try:
            await bot.delete_message(chat_id=current_chat_id, message_id=message_id)
            print(f"Сообщение с ID {message_id} успешно удалено.")
        except TelegramBadRequest as e:
            print(f"Ошибка при удалении сообщения с ID {message_id}: {e}")


# Асинхронная функция для удаления сообщения с задержкой
async def delete_message_after_delay(user_tg_id, msg, delay: int):
    async def task():
        await asyncio.sleep(delay)
        try:
            await msg.delete()
            logger.debug(f"TG ID: {user_tg_id}, сообщение с ID {msg.message_id} удалено через {delay} секунд.")
        except Exception as e:
            logger.error(f"TG ID: {user_tg_id}, ошибка при удалении сообщения с ID {msg.message_id}: {e}")

    asyncio.create_task(task())

