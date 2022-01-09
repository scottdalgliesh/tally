from flask import Flask

from . import auth, tally
from .config import Config
from .extensions import bcrypt, db, login_manager, migrate


def create_app(config: Config = Config()) -> Flask:
    """App factory."""
    # create app
    app = Flask(__name__)
    app.config.from_object(config)

    # initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # register blueprints
    app.register_blueprint(auth.routes.bp)
    app.register_blueprint(tally.routes.bp)

    @app.shell_context_processor
    def make_shell_context() -> dict:  # pylint:disable=unused-variable
        """Create context for "flask shell" CLI tool."""
        from .auth.models import User
        from .tally.models import Bill, Category

        return {"db": db, "User": User, "Category": Category, "Bill": Bill}

    return app
