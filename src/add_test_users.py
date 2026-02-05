from dotenv import load_dotenv
# Загружаем переменные окружения (в том числе KEY) перед импортом остальных модулей
load_dotenv()

from config import app, db
from database.users import User
from werkzeug.security import generate_password_hash

def create_users():
    with app.app_context():
        # Список пользователей: (логин, пароль, роль)
        users_data = [
            ("student_test", "123", "student"),
            ("cook_test", "123", "cook"),
            ("admin_test", "123", "admin")
        ]

        for login, password, role in users_data:
            # Проверяем, существует ли уже такой пользователь, чтобы не создавать дубликаты
            if User.query.filter_by(login=login).first():
                print(f"Пользователь {login} уже существует.")
                continue

            # Хешируем пароль (обязательно для безопасности и работы входа)
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            
            # Создаем пользователя. Кошелек сгенерируется автоматически в __init__
            new_user = User(login=login, password=hashed_password, role=role)
            
            db.session.add(new_user)
            print(f"Добавлен пользователь: {login} (Роль: {role})")

        db.session.commit()
        print("Все пользователи успешно добавлены в базу данных!")

if __name__ == "__main__":
    create_users()
