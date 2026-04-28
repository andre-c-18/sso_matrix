from extensions import db
from datetime import datetime

# 6 aksi fixed untuk standard_access
STANDARD_ACTIONS = [
    {'key': 'view',    'label': 'View',    'icon': 'bi-eye',            'color': 'primary',   'desc': 'Lihat data'},
    {'key': 'edit',    'label': 'Edit',    'icon': 'bi-pencil',         'color': 'warning',   'desc': 'Ubah data'},
    {'key': 'export',  'label': 'Export',  'icon': 'bi-download',       'color': 'success',   'desc': 'Export/unduh'},
    {'key': 'approve', 'label': 'Approve', 'icon': 'bi-check-circle',   'color': 'info',      'desc': 'Setujui data'},
    {'key': 'upload',  'label': 'Upload',  'icon': 'bi-upload',         'color': 'secondary', 'desc': 'Upload file'},
    {'key': 'delete',  'label': 'Delete',  'icon': 'bi-trash',          'color': 'danger',    'desc': 'Hapus data'},
]

class AccessMatrix(db.Model):
    __tablename__ = 'access_matrix'

    id              = db.Column(db.Integer, primary_key=True)
    role_id         = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    app_id          = db.Column(db.String(100), db.ForeignKey('applications.app_id'), nullable=False)
    standard_access = db.Column(db.JSON, nullable=False, default=list)
    # ['view', 'edit', 'export', 'approve', 'upload', 'delete']
    right_config    = db.Column(db.JSON, default=None)
    # { "paths": ["/", "/dashboard"], "key1": val1, ... }
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('role_id', 'app_id', name='uq_role_app'),
    )

    role        = db.relationship('Role', backref='access_matrices')
    application = db.relationship('Application', backref='access_matrices')

    def to_dict(self):
        return {
            'id':              self.id,
            'role_id':         self.role_id,
            'role_name':       self.role.name if self.role else None,
            'app_id':          self.app_id,
            'standard_access': self.standard_access or [],
            'right_config':    self.right_config or {},
        }
