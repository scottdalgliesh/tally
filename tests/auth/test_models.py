# pylint: disable=[unused-argument, missing-function-docstring]
from tally import bcrypt
from tally.auth.models import User


def test_user_model(session):
    user = User.query.filter_by(username="scott").first()
    assert user.username == "scott"
    assert bcrypt.check_password_hash(user.password, "123")

    categories = [categ.name for categ in user.categories]
    bills = [bill.descr for bill in user.bills]
    assert sorted(categories) == sorted(["groceries", "gas", "misc"])
    assert sorted(bills) == sorted(["zehrs", "walmart", "ren's", "sobeys"])
