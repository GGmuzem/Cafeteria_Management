from config import db
from cryptography.fernet import Fernet
from datetime import datetime
import secrets
import string
import os
from flask_login import UserMixin
from .wallets import Wallet
from .history import history_operation
# Здесь мы инициализируем и проверяем таблицу users

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    role = db.Column(db.String(10), nullable=False)
    wallet = db.Column(db.String(255), nullable=False, unique=True)
    allergen = db.Column(db.String(255), nullable=True)
    preferences = db.Column(db.String(255), nullable=True)
    subscription = db.Column(db.DateTime(), nullable=True)
    
    def __init__(self, login, password, role="student", wallet=None, health=None):
        self.login = login
        self.password = password
        self.role = role
        if wallet is None: # Если нет кошелька или создали человека то создаем ему кошелек
            generated_wallet = ''.join(secrets.choice(string.digits) for _ in range(16))
            self.set_wallet(generated_wallet)
        else:
            self.set_wallet(wallet)
        self.health = health

    key = os.getenv("KEY") # Это ключ который храниться в .env
    def set_wallet(self, wallet_value): # Шифровка кошелька
        cipher_suite = Fernet(self.key)
        encrypted_text = cipher_suite.encrypt(str(wallet_value).encode('utf-8'))
        self.wallet = encrypted_text.decode('utf-8')

    def get_wallet(self): # Расшифровка кошелька
        try:
            cipher_suite = Fernet(self.key)
            decrypted_text = cipher_suite.decrypt(self.wallet.encode('utf-8'))
            return decrypted_text.decode('utf-8')
        except Exception as e:
            return f"Error decoding: {e}"

    def get_balance(self):  # Баланс
        wallet_number = self.wallet
        wallet = Wallet.query.filter_by(wallet_number=wallet_number).first()
        if wallet is None:
            wallet = Wallet(wallet_number=wallet_number, money=0)
            db.session.add(wallet)
            db.session.commit()
        return wallet.money

    def add_money(self, how_many_on): # Начисление денег
        self.get_balance() # Гарантируем, что запись кошелька существует
        wallet_number = self.wallet # Используем зашифрованный номер, как в БД
        wallet = Wallet.query.filter_by(wallet_number=wallet_number).first()
        hmo = float(how_many_on)
        if hmo <= 0:
            return
        wallet.money += hmo
        history = history_operation(
                    user=self.id,
                    type_of_transaction='Начисление',
                    amount=how_many_on,
                )
        db.session.add(history)
        db.session.commit()


    def rem_money(self, how_many_off): # Снятие денег
        self.get_balance() # Гарантируем, что запись кошелька существует
        wallet_number = self.wallet # Используем зашифрованный номер, как в БД
        wallet = Wallet.query.filter_by(wallet_number=wallet_number).first()
        hmo = float(how_many_off)
        if hmo <= 0:
            return False
        if wallet.money < hmo:
            return False
        wallet.money -= hmo
        history = history_operation(
            user=self.id,
            type_of_transaction='Снятие',
            amount=how_many_off,
        )
        db.session.add(history)
        db.session.commit()
        return True

    def get_history_operation(self): # Получаем историю опреаций (недавних)
        return history_operation.query.filter_by(user=self.id).order_by(history_operation.date.desc()).all()

    def get_subscription_expiration(self):
        if self.subscription:
            from datetime import timedelta
            return self.subscription + timedelta(days=30)
        return None
