# pylint: disable=[unused-argument, missing-function-docstring]
import io
from datetime import date

import pytest
from bs4 import BeautifulSoup
from flask_login import current_user

from tally.auth.models import User
from tally.tally.models import Bill, Category

from .test_parse import sample_statement_1

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


@pytest.mark.parametrize(
    "mock_tika", [sample_statement_1.statement_text], indirect=True, ids=["sample_statement1"]
)
def test_new_statement(mock_tika, client):
    # clear existing data
    Bill.query.delete()

    # simulate file upload
    file_upload = (io.BytesIO(bytes("file contents", "utf8")), "sample.pdf")
    client.post("/new_statement", data={"file": file_upload}, content_type="multipart/form-data")

    sample_trans = sample_statement_1.transactions
    bills = Bill.query.all()
    assert len(bills) == len(sample_trans)
    assert bills[0].date == sample_trans[0].Date
    assert bills[0].descr == sample_trans[0].Description
    assert bills[0].value == sample_trans[0].Value
    assert bills[0].category_id is None


def test_categorize(client, session):
    # make 3 bills uncategorized
    # pylint: disable=singleton-comparison
    bills = Bill.query.all()
    for bill in bills[:3]:
        bill.category_id = None
    session.commit()
    uncategorized_bills = Bill.query.filter(Bill.category_id == None).all()

    response = client.get("/categorize")
    html = BeautifulSoup(response.data, features="html.parser")

    # check output
    table_body = html.find("tbody")
    assert len(table_body.find_all("tr")) == 3  # type: ignore
    assert all(
        val in table_body.getText() for val in ["2020-01-28", "ren's", "300"]  # type: ignore
    )

    # apply new categories to first two and check they are applied
    form_data = {
        "categories-0-category": 1,
        "categories-1-category": 1,
        "categories-2-category": -1,
    }
    client.post("/categorize", data=form_data)
    new_categories = [bill.category_id for bill in uncategorized_bills]
    assert new_categories == [None, 1, 1]


def test_review_all(client):
    bills = Bill.query.join(User).filter_by(username="scott").all()
    response = client.get("/review_all")
    soup = BeautifulSoup(response.data, features="html.parser")
    table_body = soup.find("tbody")
    assert len(table_body.find_all("tr")) == len(bills)  # type: ignore
    assert all(
        val in table_body.getText() for val in ["2020-01-28", "ren's", "300"]  # type: ignore
    )


def test_edit_bill(client):
    bill = Bill.query.get(1)
    assert bill.descr == "zehrs"

    client.post(
        "/edit_bill/1",
        data={
            "date": date(2000, 1, 1),
            "description": "Updated description",
            "value": 1000,
            "category": 2,
        },
    )
    assert bill.date == date(2000, 1, 1)
    assert bill.descr == "Updated description"
    assert bill.value == 1000
    assert bill.category_id == 2


def test_new_bill(client):
    count = Bill.query.count()
    client.post(
        "/new_bill",
        data={
            "date": date(3000, 1, 1),
            "description": "New Bill!",
            "value": 46,
            "category": 1,
        },
    )

    bill = Bill.query.filter_by(descr="New Bill!").one()
    assert Bill.query.count() == count + 1
    assert bill.date == date(3000, 1, 1)
    assert bill.descr == "New Bill!"
    assert bill.value == 46
    assert bill.category_id == 1


def test_delete_bill(client):
    count = Bill.query.count()
    client.post("delete_bill/1")
    assert Bill.query.count() == count - 1
    assert Bill.query.get(1) is None
