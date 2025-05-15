import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(email, subject, attachments, user):
    addr_from = os.getenv("FROM")
    password = os.getenv("PASSWORD")
    host = os.getenv("HOST")
    port = os.getenv("PORT")

    if not addr_from or not password or not host or not port:
        raise Exception("Не заданы необходимые переменные окружения (FROM, PASSWORD, HOST, PORT)")
    
    msg = MIMEMultipart()
    msg['From'] = addr_from
    msg['To'] = email
    msg['Subject'] = subject

    body = '<p>В вашем магазине были заказаны следующие товары:</p><ul>'
    final = 0

    for js in attachments:
        product_link = f"<a href='http://localhost:8080/product/{js['id']}'>{js['name']}</a>"
        body += f"<li>{product_link} в количестве {js['quantity']} по цене {js['price']} ₽</li>"
        final += js['quantity'] * js['price']

    body += f"</ul><p>Итоговая сумма заказа: {final} ₽</p>"
    body += (f"<p>Данные заказчика"
             f": {user.name} {user.surname}, номер телефона: {user.phone_number}, адрес: {user.address}</p>")
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP_SSL(host, int(port))
        server.login(addr_from, password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Не удалось отправить письмо: {e}")
        return False
    
    return True