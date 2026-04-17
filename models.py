from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Advertisement(db.Model):
    """Модель объявления"""
    __tablename__ = 'advertisements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    owner = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        """Преобразует объект в словарь для JSON ответа"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'owner': self.owner
        }

    def update_from_dict(self, data):
        """Обновляет объект из словаря"""
        if 'title' in data:
            self.title = data['title']
        if 'description' in data:
            self.description = data['description']
        if 'owner' in data:
            self.owner = data['owner']
