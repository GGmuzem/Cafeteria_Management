from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(name)
# Настройка базы данных (например, sqlite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db
db = SQLAlchemy(app) # Загружаем бд в код
