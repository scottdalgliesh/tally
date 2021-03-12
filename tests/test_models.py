from tally.models import User


def test_sample_test(sample_db):
    user_names = [user.username for user in User.query.all()]
    assert user_names == ['scott', 'sarah']
