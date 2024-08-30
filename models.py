from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    files = db.relationship('File', backref='owner', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    public = db.Column(db.Boolean, default=False)
    size = db.Column(db.Integer)  # File size in bytes
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<File {self.filename}>'
