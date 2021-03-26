# pylint:disable=unused-argument
import pytest
from tally.auth.forms import UserRegisterForm

valid = True
invalid = False

test_input = [
    pytest.param('new_user', '123', '123', valid, id='valid input'),
    pytest.param('new_user', '123', '1234', invalid,
                 id='mismatched passwords'),
    pytest.param('scott', '123', '123', invalid, id='duplicate user'),
    pytest.param('this_is_a_really_really_long_name', '123',
                 '123', invalid, id='duplicate user'),
]


@pytest.mark.parametrize('username,password,confirm,result', test_input)
def test_UserRegisterForm_validation(username, password, confirm, result, session):
    form = UserRegisterForm()
    form.username.data = username
    form.password.data = password
    form.confirm_password.data = confirm
    assert form.validate() is result
