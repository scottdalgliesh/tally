# pylint: disable=[unused-argument, missing-function-docstring]
import pytest
from flask import request
from flask_login import current_user

from tally.auth.models import User

valid = True
invalid = False

test_input = [
    pytest.param(
        {"username": "new_user", "password": "123", "confirm_password": "123"},
        valid,
        id="valid input",
    ),
    pytest.param(
        {"username": "new_user", "password": "123", "confirm_password": "1234"},
        invalid,
        id="invalid input",
    ),
]


@pytest.mark.parametrize("data, is_valid", test_input)
def test_register(session, client, data, is_valid):
    response = client.post("/auth/register", data=data, follow_redirects=True)
    msg_flashed = f'{data["username"]} created'.encode("utf-8") in response.data
    user_created = bool(User.query.filter_by(username=data["username"]).first())
    assert msg_flashed is is_valid
    assert user_created is is_valid


test_input = [
    pytest.param({"username": "scott", "password": "123"}, valid, id="valid input"),
    pytest.param({"username": "scott", "password": "wrong pass"}, invalid, id="invalid password"),
    pytest.param(
        {"username": "wrong username", "password": "123"}, invalid, id="invalid username"
    ),
]


@pytest.mark.parametrize("data, is_valid", test_input)
def test_login(session, client, data, is_valid):
    client.post(r"/auth/login?next=%2Fauth%2Faccount", data=data, follow_redirects=True)
    if is_valid:
        assert current_user.username == data["username"]
        assert request.url_rule and request.url_rule.rule == "/auth/account"
    else:
        assert current_user.is_anonymous


def test_logout(session, client, logged_in):
    client.get("/auth/logout")
    assert current_user.is_anonymous


test_input = [
    pytest.param({"username": "new_username"}, valid, id="valid input"),
    pytest.param({"username": "sarah"}, invalid, id="invalid input"),
]


@pytest.mark.parametrize("data, is_valid", test_input)
def test_account(session, client, logged_in, data, is_valid):
    client.post("/auth/account", data=data)
    if is_valid:
        assert not User.query.filter_by(username="scott").first()
        assert User.query.filter_by(username=data["username"]).first()
    else:
        assert User.query.filter_by(username="scott").first()
