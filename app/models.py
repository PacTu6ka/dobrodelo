from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='volunteer')  # volunteer, coordinator, admin
    phone = db.Column(db.String(30), nullable=True)
    city = db.Column(db.String(60), nullable=True, default='Москва')
    birth_date = db.Column(db.Date, nullable=True)
    skills = db.Column(db.String(255), nullable=True)
    interests = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    organizations = db.relationship('Organization', backref='coordinator', lazy=True)
    applications = db.relationship('Application', backref='volunteer', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def age(self):
        if not self.birth_date:
            return 25  # default if not set
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    @property
    def is_minor(self):
        return self.age < 18

    @property
    def total_hours(self):
        # Суммируем часы за подтвержденную явку
        return sum(app.hours_awarded or 0 for app in self.applications if app.status == 'attended')


class Organization(db.Model):
    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(60), nullable=False, default='Москва')
    contact_email = db.Column(db.String(120), nullable=True)
    contact_phone = db.Column(db.String(30), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)  # Подтверждена ли модератором (FR-03, FR-37)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    projects = db.relationship('Project', backref='organization', lazy=True, cascade="all, delete-orphan")


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(60), nullable=False)  # Животные, Экология, Социальное, Дети, Спорт
    city = db.Column(db.String(60), nullable=False, default='Москва')
    address = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(30), default='open')  # draft, open, closed, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    shifts = db.relationship('Shift', backref='project', lazy=True, cascade="all, delete-orphan")


class Shift(db.Model):
    __tablename__ = 'shifts'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(10), nullable=False, default='10:00')
    end_time = db.Column(db.String(10), nullable=False, default='14:00')
    location = db.Column(db.String(255), nullable=True)
    max_volunteers = db.Column(db.Integer, nullable=False, default=10)
    hours = db.Column(db.Float, nullable=False, default=4.0)  # Количество начисляемых волонтерских часов
    min_age = db.Column(db.Integer, default=14)  # Минимальный возраст
    parent_consent_required = db.Column(db.Boolean, default=True)  # Согласие родителей для несовершеннолетних (FR-21)

    # Relationships
    applications = db.relationship('Application', backref='shift', lazy=True, cascade="all, delete-orphan")

    @property
    def approved_count(self):
        return sum(1 for a in self.applications if a.status in ['approved', 'attended'])

    @property
    def available_places(self):
        return max(0, self.max_volunteers - self.approved_count)


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    shift_id = db.Column(db.Integer, db.ForeignKey('shifts.id'), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(30), default='pending')  # pending, approved, rejected, attended, no_show, cancelled
    parent_consent_given = db.Column(db.Boolean, default=False)  # Подтверждено родителем (FR-21)
    hours_awarded = db.Column(db.Float, default=0.0)  # Автоматический учет часов (FR-28)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.String(255), nullable=True)


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=5)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
