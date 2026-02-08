from config import db
from database.users import User
from database.notifications import Notification
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user

# Вход в аккаунт
def login_user_db(login, password):
    user = User.query.filter_by(login=login).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        
        # Отправка уведомления о входе
        if user.email:
            notif = Notification(
                email=user.email,
                subject="Вход в аккаунт",
                message="Выполнен вход в ваш аккаунт в системе столовой."
            )
            db.session.add(notif)
            db.session.commit()
            
        return True
    return False

# Регстрация аккаунта
def register_user(login, password, password_repeat):
    existing_user = User.query.filter_by(login=login).first()
    if existing_user:
        return None, 'Имя пользователя уже занято'
    elif password != password_repeat:
        return None, 'Пароли не совпадают'
    else:
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(login=login, password=hashed_password, role="student", wallet=None)

        try:
            db.session.add(new_user)
            db.session.commit()
            return new_user, None
        except Exception as e:
            db.session.rollback()
            print(f'Error saving to database: {e}')
            return None, 'Ошибка сохранения в базу данных'
