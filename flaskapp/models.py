from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flaskapp import db, login_manager
from flask_login import UserMixin
import datetime as dt
from flask import current_app
from flaskapp.user.utils import get_random_string


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(db.Model, UserMixin):
    # __tablename__ = "user"    # By this line you can choose custom names of database tables.
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), default=None)
    current_profession = db.Column(db.String(200), default=None)
    about = db.Column(db.String(1000), default=None)
    last_active = db.Column(db.DateTime, nullable=False, default=dt.datetime.now())
    profile_image = db.Column(db.String(500), nullable=False, default='default.jpg')
    profile_identicon_unique_string = db.Column(db.String(64), unique=True, nullable=False)
    date_joined = db.Column(db.DateTime, nullable=False, default=dt.datetime.now())
    is_email_verified = db.Column(db.Boolean(), nullable=False, default=False)
    is_account_active = db.Column(db.Boolean(), nullable=False, default=True)

    posts = db.relationship('Post', backref=db.backref('author', lazy=True))

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    @staticmethod
    def generate_random_identicon_image():
        got_string = False
        while not got_string:
            random_identicon_string = get_random_string()
            identicon_string_user = User.query.filter_by(
                profile_identicon_unique_string=random_identicon_string).first()
            if not identicon_string_user:
                got_string = True
        return random_identicon_string

    def get_mail_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_mail_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"""User(Username : {self.username}, Email : {self.email}, Date Joined : {self.date_joined})"""


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=dt.datetime.now())
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"""Post(Title : {self.title}, Date Posted : {self.date_posted})"""

