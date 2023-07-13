import pytest
from datetime import datetime, timezone
from fyle_rest_auth.models import User

@pytest.mark.django_db
def test_user_creation():
    '''
    Test Post of User Profile
    '''
    user = User(password='', last_login=datetime.now(tz=timezone.utc), email='labhvam.s@fyle.in',
                         user_id='usqywo0f3nLY', full_name='', active='t', staff='f', admin='t')

    user.save()

    assert user.email == 'labhvam.s@fyle.in'


@pytest.mark.django_db
def test_get_of_user(add_users_to_database):
    '''
    Test Get of User Profile
    '''
    user = User.objects.filter(email='labhvam.s@fyle.in').first()

    assert user.user_id == 'usqywo0f3nLY'
