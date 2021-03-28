# pylint:disable=unused-argument
import pytest

from tally.auth.forms import UserRegisterForm, UserUpdateForm

valid = True
invalid = False

test_input = [
    pytest.param("new_user", "123", "123", valid, id="valid input"),
    pytest.param("new_user", "123", "1234", invalid, id="mismatched passwords"),
    pytest.param("scott", "123", "123", invalid, id="duplicate user"),
    pytest.param("this_is_a_really_really_long_name", "123", "123", invalid, id="duplicate user"),
]


@pytest.mark.parametrize("username,password,confirm,result", test_input)
def test_UserRegisterForm(username, password, confirm, result, session):
    form = UserRegisterForm()
    form.username.data = username
    form.password.data = password
    form.confirm_password.data = confirm
    assert form.validate() is result


test_input = [
    pytest.param("new_user", valid, id="valid new username"),
    pytest.param("scott", valid, id="same username"),
    pytest.param("sarah", invalid, id="duplicate username"),
]


@pytest.mark.parametrize("username,result", test_input)
def test_UserUpdateForm(username, result, session, logged_in):
    form = UserUpdateForm()
    form.username.data = username
    assert form.validate() is result
