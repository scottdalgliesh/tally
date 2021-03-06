#pylint:disable=[missing-function-docstring, redefined-outer-name, unused-argument]

from datetime import date

import pytest
from tally import create_app
from tally import db as _db
from tally.config import Config
from tally.models import Bill, Category, User


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = None
    TESTING = True


@pytest.fixture(scope='session')
def app(tmp_path_factory, worker_id):
    """Instantiate app instance for testing."""
    # create worker-bound temp directory to facilitate use of pytest-xdist
    tmp_path = tmp_path_factory.getbasetemp() / worker_id
    tmp_db = tmp_path / 'test.db'
    tmp_path.mkdir()

    # instantiate app
    TestConfig.SQLALCHEMY_DATABASE_URI = f'sqlite:///{tmp_db}'
    app = create_app(TestConfig)
    return app


def populate_test_db(db):
    """Populate test database with sample data."""
    users = [
        User(username='scott', password='123'),
        User(username='sarah', password='123'),
    ]
    db.session.add_all(users)
    db.session.commit()

    categs = [
        Category(name='groceries', username='scott'),
        Category(name='gas', username='scott'),
        Category(name='misc', username='scott'),
        Category(name='groceries', username='sarah'),
        Category(name='gas', username='sarah'),
        Category(name='misc', username='sarah'),
    ]
    db.session.add_all(categs)
    db.session.commit()

    bills = [
        Bill.from_name(date(2020, 1, 26), 'zehrs', 100, 'scott', 'groceries'),
        Bill.from_name(date(2020, 1, 27), 'walmart', 200, 'scott', 'misc'),
        Bill.from_name(date(2020, 1, 28), 'ren\'s', 300, 'scott', 'misc'),
        Bill.from_name(date(2020, 1, 29), 'sobeys', 400, 'scott', 'groceries'),
        Bill.from_name(date(2020, 1, 26), 'petro', 500, 'sarah', 'gas'),
        Bill.from_name(date(2020, 1, 27), 'canadian tire',
                       600, 'sarah', 'misc'),
        Bill.from_name(date(2020, 1, 28), 'shell', 700, 'sarah', 'gas'),
        Bill.from_name(date(2020, 1, 29), 'no frills',
                       800, 'sarah', 'groceries'),
    ]
    db.session.add_all(bills)
    db.session.commit()


@pytest.fixture(scope='session')
def db(app):
    """Create & populate test database."""
    _db.app = app
    _db.create_all()
    populate_test_db(_db)
    yield _db
    _db.drop_all()


@pytest.fixture(scope='function')
def session(db):
    """Configure test database for transactional testing."""
    connection = db.engine.connect()
    transaction = connection.begin()
    options = {'bind': connection, 'binds': {}}
    session = db.create_scoped_session(options=options)
    db.session = session
    yield session

    transaction.rollback()
    connection.close()
    session.remove()
