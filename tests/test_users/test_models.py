# import pytest
# from apps.users.models import User

# @pytest.mark.django_db
# def test_user_creation():
#     '''
#     Test 
#     '''

#     assert 1 == 1

#     # user = UserManager.create_user(email='nilesh.p@fyle.in', full_name='', password='hello')

#     # assert user.email=='nilesh.p@fyle.in'


import pytest
from datetime import datetime, timezone
from fyle_rest_auth.models import User

@pytest.mark.django_db
def test_user_creation():
    '''
    Test Post of User Profile
    '''
    user = User(password='', last_login=datetime.now(tz=timezone.utc), email='nilesh.p@fyle.in',
                         user_id='ust5Gda9HC3qc', full_name='', active='t', staff='f', admin='t')

    user.save()

    assert user.email=='nilesh.p@fyle.in'

