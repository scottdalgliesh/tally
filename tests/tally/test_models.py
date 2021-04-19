# pylint: disable=unused-argument
from tally.auth.models import User
from tally.tally.models import Category


def test_category_model(session):
    categ = (
        Category.query.filter_by(name="groceries").join(User).filter_by(username="scott").one()
    )
    bills = [bill.descr for bill in categ.bills]
    assert categ.name == "groceries"
    assert categ.user.username == "scott"
    assert sorted(bills) == ["sobeys", "zehrs"]
