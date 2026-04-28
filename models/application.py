from extensions import db
from datetime import datetime

class Application(db.Model):
    __tablename__ = 'applications'

    id              = db.Column(db.Integer, primary_key=True)
    app_id          = db.Column(db.String(100), unique=True, nullable=False)
    app_secret      = db.Column(db.String(255), nullable=False)
    app_name        = db.Column(db.String(255), nullable=False)
    description     = db.Column(db.Text)
    callback_url    = db.Column(db.String(500), nullable=False)
    allowed_origins = db.Column(db.Text)
    auto_redirect   = db.Column(db.SmallInteger, default=0)
    is_active       = db.Column(db.SmallInteger, default=1)
    created_by      = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = db.relationship('User', foreign_keys=[created_by], backref='applications')

    def to_dict(self):
        return {
            'app_id':        self.app_id,
            'app_name':      self.app_name,
            'description':   self.description,
            'callback_url':  self.callback_url,
            'auto_redirect': self.auto_redirect,
            'is_active':     self.is_active,
        }
