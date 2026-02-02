"""
Какие функции реализуются здесь:

    Создание и изменения меню
    Просмотр рецепта блюда
    Просмотр склада и создания заявки для закупки продуктов
    Просмотр истории заказов
    
"""
from flask import render_template, redirect, url_for, flash, request
from config import app, db
from database.store import Storage
from database.menu import Menu
from database.history import History
from flask_login import login_required