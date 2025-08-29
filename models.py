from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class EnumType:
    pass


class TaskStatus(Enum):
    WAITING = 'Bekliyor'
    IN_PROGRESS = 'Devam Ediyor'
    COMPLETED = 'Tamamlandi'

class TaskPriority(Enum):
    LOW = 'Düşük'
    MEDIUM = 'Orta'
    HIGH = 'Yüksek'

class UserRole(Enum):
    VIEWER = 'viewer'
    EDITOR = 'editor'
    ADMIN = 'admin'

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    tasks = db.relationship('Task', backref='user', lazy=True)
    role = db.Column(db.String(20), default=UserRole.VIEWER.value)

    def __init__(self, username, email, password, is_admin=False, role=UserRole.VIEWER.value):
        self.username = username
        self.email = email
        self.password = password
        self.created_on = datetime.now()
        self.is_admin = is_admin
        self.role = role

task_category = db.Table(
    'task_category',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)

class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default=TaskStatus.WAITING.value)
    priority = db.Column(db.String(20), default=TaskPriority.MEDIUM.value)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    categories = db.relationship('Category',secondary=task_category,backref=db.backref('tasks', lazy='dynamic'))
    start_date = db.Column(db.DateTime, nullable=True)
    finish_date = db.Column(db.DateTime, nullable=True)
    history = db.relationship('TaskHistory', backref='task', lazy=True, order_by="desc(TaskHistory.changed_at)")

class TaskHistory(db.Model):
    __tablename__ = "taskshistory"
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    changed_at = db.Column(db.DateTime, default=datetime.now)
    field_name = db.Column(db.String(50))
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    changed_by_user = db.relationship('User', foreign_keys=[changed_by])

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"))



class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(100), nullable=False)