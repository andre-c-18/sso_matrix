from extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id                = db.Column(db.Integer, primary_key=True)
    username          = db.Column(db.String(100), unique=True, nullable=False)
    email             = db.Column(db.String(255), unique=True, nullable=False)
    password_hash     = db.Column(db.String(255), nullable=False)
    full_name         = db.Column(db.String(255), nullable=False)
    role_id           = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False, default=4)
    is_active         = db.Column(db.SmallInteger, default=1)
    is_email_verified = db.Column(db.SmallInteger, default=0)
    avatar_url        = db.Column(db.String(500))
    last_login        = db.Column(db.DateTime)
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at        = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id':        self.id,
            'username':  self.username,
            'email':     self.email,
            'full_name': self.full_name,
            'role_id':   self.role_id,
            'role_name': self.role.name if self.role else None,
            'is_active': self.is_active,
            'last_login': str(self.last_login) if self.last_login else None,
        }
