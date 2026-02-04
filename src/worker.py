import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from config import app, db
from database.users import User
from database.notifications import Notification

# Загружаем переменные окружения
load_dotenv()

def send_email_notification(user_email, subject, message):
    """
    Отправляет email пользователю.
    Требует настройки SMTP_EMAIL и SMTP_PASSWORD в .env файле.
    """
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    if not sender_email or not sender_password:
        print("SMTP настройки не найдены. Письмо не отправлено.")
        return False

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = user_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"Уведомление отправлено на {user_email}")
        return True
    except Exception as e:
        print(f"Ошибка отправки email: {e}")
        return False

def check_incoming_notifications():
    """
    Функция проверки новых записей в БД (уведомлений).
    """
    with app.app_context():
        notifications = Notification.query.filter_by(status='pending').all()
        
        if notifications:
            print(f"[{time.strftime('%H:%M:%S')}] Найдено {len(notifications)} новых уведомлений.")
            
            for notification in notifications:
                print(f"Отправка письма на {notification.email}...")
                if send_email_notification(notification.email, notification.subject, notification.message):
                    notification.status = 'sent'
                else:
                    notification.status = 'failed'
            db.session.commit()

def run_worker():
    """
    Запуск цикла обработки.
    """
    print("Worker запущен...")
    while True:
        check_incoming_notifications()
        time.sleep(60)

if __name__ == "__main__":
    run_worker()