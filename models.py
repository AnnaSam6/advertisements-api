from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Advertisement(db.Model):
    """Модель объявления"""
    __tablename__ = 'advertisements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Исправлено: created_at вместо created_date
    owner = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        """Преобразует объект в словарь для JSON ответа"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,  # Исправлено
            'owner': self.owner
        }

    def update_from_dict(self, data):
        """Обновляет объект из словаря"""
        if 'title' in data and data['title']:
            self.title = data['title']
        if 'description' in data and data['description']:
            self.description = data['description']
        if 'owner' in data and data['owner']:
            self.owner = data['owner']
