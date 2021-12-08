import pytest
from datetime import datetime, timezone
from fyle_rest_auth.models import User

@pytest.mark.django_db
def test_user_creation():
    '''
    Test Post of User Profile
    '''
    user = User(password='', last_login=datetime.now(tz=timezone.utc), email='ashwin.t@fyle.in',
                         user_id='usqywo0f3nBY', full_name='', active='t', staff='f', admin='t')

    user.save()

    assert user.email=='ashwin.t@fyle.in'

    # assert 'ashwin.t@fyle.in'=='ashwin.t@fyle.in'

