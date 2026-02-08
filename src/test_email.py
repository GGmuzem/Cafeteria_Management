
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_test_email():
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    if not sender_email or not sender_password:
        print("❌ Ошибка: SMTP_EMAIL или SMTP_PASSWORD не найдены в .env файле.")
        return

    print(f"📧 Попытка отправки с {sender_email} через {smtp_server}:{smtp_port}...")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = sender_email  # Send to self
    msg['Subject'] = "Test Email from Cafeteria App"
    msg.attach(MIMEText("Это тестовое сообщение для проверки настроек SMTP.", 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("✅ Успех! Тестовое письмо отправлено.")
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Ошибка аутентификации (535): {e}")
        print("💡 Совет: Если вы используете Gmail, вам нужно создать 'Пароль приложений'.")
        print("   1. Включите двухфакторную аутентификацию (2FA) в Google аккаунте.")
        print("   2. Перейдите в 'Безопасность' -> 'Двухэтапная аутентификация' -> 'Пароли приложений'.")
        print("   3. Создайте новый пароль (выберите 'Почта' и 'Компьютер Windows').")
        print("   4. Вставьте полученный 16-значный пароль в .env как SMTP_PASSWORD.")
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")

if __name__ == "__main__":
    send_test_email()
