from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flaskapp.config import Config
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask import Flask
import os


UPLOAD_FOLDER = ""
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


db = SQLAlchemy()

migrate = Migrate()

bcrypt = Bcrypt()

login_manager = LoginManager()
login_manager.login_view = 'user_blueprint.login'
# login_manager.login_message = 'Login Required.'
login_manager.login_message_category = 'warning'

mail = Mail()


def create_app(config_class=Config):
    global UPLOAD_FOLDER
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    UPLOAD_FOLDER = os.path.join(app.root_path, 'static/MEDIA').replace("\\", "/")

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000  # uploaded file can be up to 16 MB in size.

    from flaskapp.user.routes import user_blueprint
    from flaskapp.post.routes import post_blueprint
    from flaskapp.main.routes import main_blueprint
    from flaskapp.error.handlers import error_blueprint

    app.register_blueprint(user_blueprint)
    app.register_blueprint(post_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(error_blueprint)

    return app

