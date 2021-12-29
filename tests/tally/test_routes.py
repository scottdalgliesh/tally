# pylint: disable=[unused-argument, missing-function-docstring]
import pytest
from flask_login import current_user

from tally.auth.models import User
from tally.tally.models import Category

pytestmark = pytest.mark.usefixtures("session", "logged_in")


def test_categories_existing(client):
    response = client.get("/categories")
    categories = ["groceries", "gas", "misc"]
    assert all(categ.encode() in response.data for categ in categories)


def test_categories_add(client):
    client.post("/categories", data={"name": "new_cat", "hidden": False})
    categ_created = bool(
        Category.query.filter_by(name="new_cat").join(User).filter_by(username="scott").one()
    )
    assert categ_created is True


def test_edit_category(client):
    old_categ = (
        Category.query.filter_by(name="groceries").join(User).filter_by(username="scott").one()
    )
    client.post(f"/edit_category/{old_categ.id}", data={"name": "renamed_categ", "hidden": False})
    assert old_categ.name == "renamed_categ"
    assert not "groceries" in current_user.categories


def test_delete_category(client):
    old_categ = (
        Category.query.filter_by(name="groceries").join(User).filter_by(username="scott").one()
    )
    client.post(f"/delete_category/{old_categ.id}")
    assert not "groceries" in current_user.categories
