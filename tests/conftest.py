#pylint:disable=[missing-function-docstring, redefined-outer-name, unused-argument]

from datetime import date

import pytest

from tally import create_app, db as _db
from tally.config import TestConfig
from tally.models import Bill, Category, User


@pytest.fixture(scope='session')
def app():
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
    _db.app = app
    _db.create_all()
    populate_test_db(_db)
    yield _db
    _db.drop_all()


@pytest.fixture(scope='function')
def session(db):
    connection = db.engine.connect()
    transaction = connection.begin()
    options = {'bind': connection, 'binds': {}}
    session = db.create_scoped_session(options=options)
    db.session = session
    yield session

    transaction.rollback()
    connection.close()
    session.remove()
