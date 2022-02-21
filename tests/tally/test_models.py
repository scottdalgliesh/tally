# pylint: disable=[unused-argument, missing-function-docstring]
from datetime import date

from flask_login import current_user
from sqlalchemy import select

from tally.auth.models import User
from tally.tally.models import Bill, Category


def test_category_model(session):
    categ = (
        Category.query.filter_by(name="groceries").join(User).filter_by(username="scott").one()
    )
    bills = [bill.descr for bill in categ.bills]
    assert categ.name == "groceries"
    assert categ.user.username == "scott"
    assert sorted(bills) == ["sobeys", "zehrs"]


def test_Bill_generate_filters(session, logged_in, review_db):
    def get_num_results(filters):
        query = select(Bill).join(Bill.category).where(*filters)
        result = session.execute(query).scalars().all()
        return len(result)

    assert get_num_results([]) == 13

    user_id = current_user.id
    filters = Bill.generate_filters(user_id=user_id)
    assert get_num_results(filters) == 8

    filters = Bill.generate_filters(
        user_id=user_id, start_date=date(2020, 1, 27), end_date=date(2020, 1, 29)
    )
    assert get_num_results(filters) == 3

    filters = Bill.generate_filters(user_id=user_id, description="sobeys")
    assert get_num_results(filters) == 1

    filters = Bill.generate_filters(user_id=user_id, categories=[1])
    assert get_num_results(filters) == 2

    filters = Bill.generate_filters(user_id=user_id, exclude_hidden=False)
    assert get_num_results(filters) == 9

    filters = Bill.generate_filters(user_id=user_id, min_value=200, max_value=300)
    assert get_num_results(filters) == 2
