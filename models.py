from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Advertisement(db.Model):
    __tablename__ = 'advertisements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Поле created_at
    owner = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'owner': self.owner
        }
