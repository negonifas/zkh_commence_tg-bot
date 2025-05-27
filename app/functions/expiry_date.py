from datetime import datetime, timedelta


# Функция для расчета expiry_date от текущей даты
def expiry_date(days):
    # Получаем текущую дату
    current_date = datetime.now()

    # Прибавляем к текущей дате количество дней
    future_date = current_date + timedelta(days=days)

    # Возвращаем дату в формате день.месяц.год
    return future_date.strftime("%d.%m.%Y")
