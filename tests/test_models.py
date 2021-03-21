# pylint:disable=unused-argument

from tally.auth.models import User


def test_sample_test(session):
    user_names = [user.username for user in session.query(User).all()]
    assert user_names == ['scott', 'sarah']


def test_sample_test2(session):
    user_names = [user.username for user in User.query.all()]
    assert user_names == ['scott', 'sarah']


def test_sample_test3(session):
    user_names = [user.username for user in User.query.all()]
    assert user_names == ['scott', 'sarah']


def test_sample_test4(session):
    user_names = [user.username for user in User.query.all()]
    assert user_names == ['scott', 'sarah']


def test_sample_test5(session):
    user_names = [user.username for user in User.query.all()]
    assert user_names == ['scott', 'sarah']


def test_sample_test6(session):
    user_names = [user.username for user in User.query.all()]
    assert user_names == ['scott', 'sarah']


def test_sample_test7(session):
    user_names = [user.username for user in User.query.all()]
    assert user_names == ['scott', 'sarah']


def test_sample_test8(session):
    user_names = [user.username for user in User.query.all()]
    assert user_names == ['scott', 'sarah']
