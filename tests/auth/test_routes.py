# pylint:disable=unused-argument
import pytest
from tally.auth.models import User

valid = True
invalid = False

test_input = [
    pytest.param(
        {
            'username': 'new_user',
            'password': '123',
            'confirm_password': '123',
        },
        valid,
        id='valid input'
    ),
    pytest.param(
        {
            'username': 'new_user',
            'password': '123',
            'confirm_password': '1234',
        },
        invalid,
        id='invalid input'
    ),
]


@pytest.mark.parametrize('data, is_valid', test_input)
def test_register(session, client, data, is_valid):
    response = client.post('/auth/register', data=data, follow_redirects=True)
    msg_flashed = f'{data["username"]} created'.\
        encode('utf-8') in response.data
    user_created = bool(
        User.query.filter_by(username=data['username']).first()
    )
    assert msg_flashed is is_valid
    assert user_created is is_valid
