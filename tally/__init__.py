from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .config import Config

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app(test_config=None):
    app = Flask(__name__)
    if test_config:
        app.config.from_object(test_config)
    else:
        app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'

    @app.shell_context_processor
    def make_shell_context():  # pylint:disable=unused-variable
        from .models import Bill, Category, User  # nopep8
        return {
            'db': db,
            'User': User,
            'Category': Category,
            'Bill': Bill,
        }

    return app
