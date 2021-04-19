# pylint:disable=unused-argument
import pytest

from tally.auth.models import User
from tally.tally.forms import CategoryForm
from tally.tally.models import Category

pytestmark = pytest.mark.usefixtures("session", "logged_in")

valid = True
invalid = False

test_input = [
    pytest.param({"name": "new_cat", "hidden": False}, valid, id="valid input"),
    pytest.param({"name": "groceries", "hidden": False}, invalid, id="duplicate"),
]


@pytest.mark.parametrize("categ_data,result", test_input)
def test_UserRegisterForm(categ_data, result):
    form = CategoryForm(data=categ_data)
    assert form.validate() is result


def test_UserRegisterForm_update_unchanged_name():
    existing_category = (
        Category.query.filter_by(name="groceries").join(User).filter_by(username="scott").one()
    )
    form = CategoryForm(obj=existing_category)
    assert form.validate() is True
