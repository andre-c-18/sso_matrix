from extensions import db
from datetime import datetime

class Role(db.Model):
    __tablename__ = 'roles'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship('User', backref='role', lazy=True)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'description': self.description}
