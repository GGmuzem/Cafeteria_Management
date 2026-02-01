from config import db
from cryptography.fernet import Fernet
import os
import secrets
import string
from flask_login import UserMixin

# Здесь мы инициализируем и проверяем таблицу users

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    wallet = db.Column(db.String(255), nullable=False, unique=True)
    key = db.Column(db.String(255), nullable=False)
    
    def __init__(self, login, password, role="student", wallet=None):
        self.login = login
        self.password = password
        self.role = role
        self.key = Fernet.generate_key().decode()
        if wallet is None:
            wallet = ''.join(secrets.choice(string.digits) for _ in range(16))
        self.set_wallet(wallet)
    
    def set_wallet(self, wallet_value): # Шифровка кошелька
        cipher_suite = Fernet(self.key.encode())
        encrypted_text = cipher_suite.encrypt(str(wallet_value).encode('utf-8'))
        self.wallet = encrypted_text.decode('utf-8')

    def get_wallet(self): # Расшифровка кошелька
        try:
            cipher_suite = Fernet(self.key.encode())
            decrypted_text = cipher_suite.decrypt(self.wallet.encode('utf-8'))
            return decrypted_text.decode('utf-8')
        except Exception as e:
            return f"Error decoding: {e}"