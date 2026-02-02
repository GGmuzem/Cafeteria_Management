from config import db
from datetime import datetime
# Здесь мы инициализируем и проверяем таблицу history
class history_operation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    operation_type = db.Column(db.String(20), nullable=False)
    how_many = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id, operation_type, how_many):
        self.user_id = user_id
        self.operation_type = operation_type
        self.how_many = how_many

    def __repr__(self):
        return f'<History {self.id}>'



