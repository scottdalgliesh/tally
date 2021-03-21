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
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app(config=Config):
    '''App factory.'''
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from . import auth  # nopep8
    app.register_blueprint(auth.bp)

    from . import tally  # nopep8
    app.register_blueprint(tally.bp)

    @app.shell_context_processor
    def make_shell_context():   # pylint:disable=unused-variable
        '''Create context for "flask shell" CLI tool.'''
        from .auth.models import User
        from .tally.models import Bill, Category
        return {
            'db': db,
            'User': User,
            'Category': Category,
            'Bill': Bill,
        }

    return app
