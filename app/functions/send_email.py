import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formataddr
from email.header import Header
from loguru import logger


def send_email(user_tg_id, subject, from_name, body, to_email, file_path, smtp_server, smtp_port, smtp_user, smtp_password):
    # Кодируем имя отправителя, если оно на кириллице
    from_header = formataddr((str(Header(from_name, 'utf-8')), smtp_user))
    # Создаем сообщение
    msg = MIMEMultipart()
    # msg['From'] = f'{from_name} <{smtp_user}>'
    msg['From'] = from_header
    msg['To'] = to_email
    msg['Subject'] = subject

    # Добавляем тело сообщения
    msg.attach(MIMEText(body, 'plain'))

    # Добавляем вложение
    with open(file_path, 'rb') as attachment:
        part = MIMEApplication(attachment.read(), Name='Распечатай-Заработай.pdf')
    part['Content-Disposition'] = f'attachment; filename="Распечатай-Заработай.pdf"'
    msg.attach(part)

    # Подключаемся к SMTP серверу и отправляем сообщение
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        # print("Email sent successfully!")
        logger.debug(f"TG ID: {user_tg_id}, Email sent successfully!")

# # Пример вызова функции
# send_email(
#     subject='Ваш отчет',
#     body='Прикреплен ваш отчет в формате PDF.',
#     to_email=user_email,
#     file_path='/path/to/your/pdf_file.pdf',
#     smtp_server=SMTP_SERVER,
#     smtp_port=SMTP_PORT,
#     smtp_user=SMTP_USER,
#     smtp_password=SMTP_PASSWORD
# )
