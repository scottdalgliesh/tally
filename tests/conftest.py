# pylint:disable=[missing-function-docstring, redefined-outer-name, unused-argument]

from datetime import date
from pathlib import Path

import pytest

from tally.app import create_app
from tally.auth.models import User
from tally.config import Config
from tally.extensions import bcrypt
from tally.extensions import db as _db
from tally.tally import parse
from tally.tally.models import Bill, Category


class TestConfig(Config):
    """App config class for tests."""

    SQLALCHEMY_DATABASE_URI = ""  # to be overridden with temp directory
    UPLOAD_FOLDER = Path("")  # to be overridden with temp directory
    TESTING = True
    WTF_CSRF_ENABLED = False


@pytest.fixture(scope="session")
def app(tmp_path_factory, worker_id):
    """Instantiate app instance for testing."""
    # create worker-bound temp directory to facilitate use of pytest-xdist
    tmp_path = tmp_path_factory.getbasetemp() / worker_id
    tmp_db = tmp_path / "test.db"
    tmp_path.mkdir()

    # use temp directory for testing app config
    # IMPORTANT: DATABASE_URI & UPLOAD_FOLDER modified from production values
    test_config = TestConfig(
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{tmp_db}",
        UPLOAD_FOLDER=tmp_path,
    )

    # instantiate app
    app = create_app(test_config)
    return app


def populate_test_db(db):
    """Populate test database with sample data."""
    users = [
        User(
            username="scott",
            password=bcrypt.generate_password_hash("123").decode("utf-8"),
        ),
        User(
            username="sarah",
            password=bcrypt.generate_password_hash("123").decode("utf-8"),
        ),
    ]
    db.session.add_all(users)
    db.session.commit()

    categs = [
        Category.from_name(name="groceries", username="scott"),
        Category.from_name(name="gas", username="scott"),
        Category.from_name(name="misc", username="scott"),
        Category.from_name(name="groceries", username="sarah"),
        Category.from_name(name="gas", username="sarah"),
        Category.from_name(name="misc", username="sarah"),
    ]
    db.session.add_all(categs)
    db.session.commit()

    bills = [
        Bill.from_name(date(2020, 1, 26), "zehrs", 100, "scott", "groceries"),
        Bill.from_name(date(2020, 1, 27), "walmart", 200, "scott", "misc"),
        Bill.from_name(date(2020, 1, 28), "ren's", 300, "scott", "misc"),
        Bill.from_name(date(2020, 1, 29), "sobeys", 400, "scott", "groceries"),
        Bill.from_name(date(2020, 1, 26), "petro", 500, "sarah", "gas"),
        Bill.from_name(date(2020, 1, 27), "canadian tire", 600, "sarah", "misc"),
        Bill.from_name(date(2020, 1, 28), "shell", 700, "sarah", "gas"),
        Bill.from_name(date(2020, 1, 29), "no frills", 800, "sarah", "groceries"),
    ]
    db.session.add_all(bills)
    db.session.commit()


@pytest.fixture(scope="session")
def db(app):
    """Create & populate test database."""
    _db.app = app
    _db.create_all()
    populate_test_db(_db)
    yield _db
    _db.drop_all()


@pytest.fixture(scope="function")
def session(db):
    """Configure test database for transactional testing."""
    connection = db.engine.connect()
    transaction = connection.begin()
    options = {"bind": connection, "binds": {}}
    session = db.create_scoped_session(options=options)
    db.session = session
    yield session

    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture
def logged_in(client, session):
    client.post(
        "/auth/login",
        data={"username": "scott", "password": "123"},
        follow_redirects=True,
    )


@pytest.fixture
def review_db(session):
    """Add additional data for the purpose of testing review module capabilities."""
    session.add_all(
        [
            Bill.from_name(date(2019, 12, 31), "Previous month", 1, "scott", "misc"),
            Bill.from_name(date(2020, 1, 1), "Start of current month", 1, "scott", "misc"),
            Bill.from_name(date(2020, 1, 31), "End of current month", 1, "scott", "misc"),
            Bill.from_name(date(2020, 2, 1), "Next month", 1, "scott", "misc"),
        ]
    )
    session.add(Category.from_name(name="sample_hidden", username="scott", hidden=True))
    session.add(Bill.from_name(date(2000, 1, 1), "hidden", 100, "scott", "sample_hidden"))
    session.commit()


@pytest.fixture
def mock_tika(request, monkeypatch):
    class MockTika:
        """Mock Tika.parser response with provided text.

        This must be called by pytest with the indirect=True option.
        """

        @staticmethod
        def from_file(url: str) -> dict[str, str]:  # pylint: disable=unused-argument
            return {"content": request.param}

    monkeypatch.setattr(parse, "parser", MockTika)
