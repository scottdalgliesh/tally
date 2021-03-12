#pylint:disable=[missing-function-docstring, redefined-outer-name, unused-argument]

from datetime import date

import pytest
from tally import create_app, db
from tally.config import TestConfig
from tally.models import Bill, Category, User


@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)
    return app


@pytest.fixture
def clear_test_db(app):
    """Reset database & session state before/after tests."""
    db.drop_all()
    db.session.close()
    db.create_all()
    yield db.session.rollback()


@pytest.fixture
def sample_db(clear_test_db):
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
