from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import tempfile
import os
import shutil
import qrcode
from PIL import Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from app.functions.expiry_date import expiry_date
from reportlab.lib.styles import ParagraphStyle
from loguru import logger


def create_pdf_body(
                    user_tg_id,
                    pdf_title,
                    main_menu_text,
                    violation_details,
                    address,
                    image,
                    qr_code_img,
                    font_path_regular,
                    font_path_bold,
                    logo_img,
):
    # Создаем временную директорию
    temp_dir = tempfile.mkdtemp()

    # Имя PDF-файла
    pdf_file_name = os.path.join(temp_dir, "Распечатай-Заработай.pdf")

    # Создаем PDF-файл
    with open(pdf_file_name, "wb") as pdf_file:
        pdf = canvas.Canvas(pdf_file, pagesize=A4)

        # page_width, page_height = A4

        # Регистрируем шрифты Times New Roman
        pdfmetrics.registerFont(TTFont('Times-Regular', font_path_regular))
        pdfmetrics.registerFont(TTFont('Times-Bold', font_path_bold))

        # Размеры страницы A4
        page_width, page_height = A4

        # Параметры для логотипа
        logo_width = 89.3
        logo_height = 49.8
        x_logo_position = (page_width - logo_width) / 2  # Горизонтально по центру
        y_logo_position = page_height - 10 - logo_height  # Отступ сверху 10pt

        # Рисуем логотип
        pdf.drawInlineImage(logo_img, x_logo_position, y_logo_position, width=logo_width, height=logo_height)

        # Отступ для заголовка
        title_y_position = y_logo_position - 55

        # Заголовок (Times New Roman, 65pt, жирный)
        pdf.setFont("Times-Bold", 60)
        pdf.drawCentredString(page_width / 2, title_y_position, pdf_title)

        # Отступаем на 20pt вниз после заголовка
        line_y_position = title_y_position - 20

        # Устанавливаем толщину линии
        pdf.setLineWidth(1.5)

        # Рисуем горизонтальную линию с отступами 36pt слева и справа
        pdf.line(36, line_y_position, page_width - 36, line_y_position)

        # Отступаем вниз на 10pt после линии
        text_y_position = line_y_position - 10

        # Устанавливаем стиль текста
        styles = getSampleStyleSheet()
        style = styles['Normal']
        style.fontName = 'Times-Regular'
        style.fontSize = 14
        style.leading = 18
        style.alignment = 1  # По центру
        style.leftIndent = 36  # Отступ слева
        style.rightIndent = 36  # Отступ справа

        # Формируем текст
        # text = f"В квартире по адресу: {address},<br/>обнаружено нарушение - {main_menu_text} - {violation_details}."
        text = f"В квартире по адресу: {address},<br/>обнаружено нарушение: {violation_details}"

        # Создаем объект Paragraph для автоматического переноса
        paragraph = Paragraph(text, style)

        # Рисуем текст с учетом отступов
        text_block_width = page_width - 2 * 36  # Ширина текста с учетом отступов
        text_block_height = paragraph.wrap(text_block_width, 0)[1]  # Высота блока текста

        # Рисуем текст, отступая на высоту от линии
        pdf.setFont("Times-Regular", 14)
        paragraph.drawOn(pdf, 36, text_y_position - text_block_height)

        # Вычисляем доступное место для изображения
        available_width = page_width - 2 * 36  # Ширина минус отступы
        # available_height = text_y_position - text_block_height - 36  # Нижний отступ 36pt
        available_height = text_y_position - text_block_height - 325 # не ниже этой точки

        img_width, img_height = image.size

        # Определяем масштабирование
        width_scale = available_width / img_width
        height_scale = available_height / img_height

        # Выбираем меньший масштаб для сохранения пропорций
        scale = min(width_scale, height_scale)

        # Вычисляем новые размеры изображения
        new_width = img_width * scale
        new_height = img_height * scale

        # Определяем позицию для размещения изображения
        x_image_position = (page_width - new_width) / 2  # Центрирование по горизонтали
        y_image_position = text_y_position - text_block_height - new_height - 5  # Отступ снизу 5pt

        # Рисуем изображение
        pdf.drawInlineImage(
            image,
            x_image_position,
            y_image_position,
            width=new_width,
            height=new_height,
        )

        # Отступ вниз на 5pt после изображения
        text_y_position_after_image = y_image_position - 5

        # Устанавливаем одинаковый межстрочный интервал для всех блоков
        common_leading = 18

        # Стиль для обычного текста (Times-Regular 14pt)
        style_regular = ParagraphStyle(
            'Regular',
            fontName='Times-Regular',
            fontSize=14,
            leading=common_leading,  # Устанавливаем одинаковый межстрочный интервал
            alignment=1  # По центру
        )

        # Стиль для жирного текста (Times-Bold 14pt)
        style_bold = ParagraphStyle(
            'Bold',
            fontName='Times-Bold',
            fontSize=14,
            leading=common_leading,  # Устанавливаем одинаковый межстрочный интервал
            alignment=1  # По центру
        )

        # Формируем текстовый блок с обычным и жирным шрифтами
        text = (
            f"До <font name='Times-Bold'>{expiry_date(10)}</font> "
            "вам необходимо устранить нарушение либо предоставить разрешительную документацию на электронную почту:<br/>"
            "info@ozpprevizor.ru<br/><br/>"
            "В случае непредставления разрешительной документации будет инициировано обращение в суд для принудительного"
            " устранения нарушения и взыскания судебных расходов.<br/>"
            f"<font name='Times-Bold'>Чтобы избежать демонтажа при отсутствии разрешительной документации перейдите по ссылке в QR коде:</font>"
        )

        # Создаем объект Paragraph с текстом и стилем
        paragraph = Paragraph(text, style_regular)

        # Высчитываем высоту блока текста
        text_block_height = paragraph.wrap(page_width - 72, 0)[1]

        # Рисуем текстовый блок с учетом отступа 5pt после изображения
        paragraph.drawOn(pdf, 36, text_y_position_after_image - text_block_height)

        qr_code_width, qr_code_height = qr_code_img.size
        max_qr_height = int(page_height * 0.15)  # Уменьшил высоту QR
        aspect_ratio_qr = qr_code_width / qr_code_height

        if qr_code_height > max_qr_height:
            # Масштабируем QR-код, сохраняя пропорции
            new_qr_height = max_qr_height
            new_qr_width = aspect_ratio_qr * new_qr_height
            qr_code_img = qr_code_img.resize((int(new_qr_width), int(new_qr_height)))
        else:
            new_qr_width, new_qr_height = qr_code_width, qr_code_height

        # Позиционируем QR-код в нижней части страницы
        qr_code_x_position = (page_width - new_qr_width) / 2
        qr_code_y_position = 20  # Отступ от нижнего края

        # Рисуем QR-код
        pdf.drawInlineImage(qr_code_img, qr_code_x_position, qr_code_y_position, width=new_qr_width,
                            height=new_qr_height)

        # Сохраняем PDF
        pdf.save()

        logger.debug(f"TG ID: {user_tg_id}, PDF file saved: '{pdf_file_name}' in temp directory.")

    return pdf_file_name, temp_dir


def delete_temp_directory(user_tg_id, dir_path: str) -> None:
    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path)
        # print(f'Temporary directory deleted: {dir_path}')
        logger.debug(f"TG ID: {user_tg_id}, Temporary directory deleted: {dir_path}")
    else:
        # print(f'Directory does not exist: {dir_path}')
        logger.error(f"TG ID: {user_tg_id}, Directory does not exist: {dir_path}")


def generate_qr_code(data: str) -> Image.Image:
    """
    Генерирует QR-код на основе предоставленных данных.

    :param data: Данные для кодирования в QR-коде.
    :return: Изображение QR-кода.
    """
    # Создаем QR-код
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=20,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Создаем изображение QR-кода
    img = qr.make_image(fill='black', back_color='white')

    # Если нужно сохранить изображение для отладки
    # img.save("qr_code.png")
    img.save("test_qr_code.png")

    return img


def get_full_violation_composition(violations_list, short_description):
    for violation in violations_list:
        # Разделяем на короткую и длинную части
        short, long = violation.split(" - ")
        # Если короткая формулировка совпадает, возвращаем:
        if short == short_description:
            # return f"{short} — {long}"  # полную версию
            return f"{long}"  # длинную версию

    # Если не нашли совпадений, возвращаем сообщение об ошибке
    return "Нарушение не найдено"
