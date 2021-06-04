from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flaskapp import db, login_manager
from flask_login import UserMixin
import datetime as dt
from flask import current_app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    # __tablename__ = "user"    # By this line you can choose custom names of database tables.
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    profile_image = db.Column(db.String(250), nullable=False, default='default.jpg')
    is_email_verified = db.Column(db.Boolean(), nullable=False, default=False)
    date_joined = db.Column(db.DateTime, nullable=False, default=dt.datetime.now())
    posts = db.relationship('Post', backref=db.backref('author', lazy=True))

    def get_reset_password_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def get_verify_email_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    @staticmethod
    def verify_verify_email_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"""User(Username : {self.username}, Email : {self.email}, Image : {self.profile_image})"""


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=dt.datetime.now())
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"""Post(Title : {self.title}, Date Posted : {self.date_posted})"""
