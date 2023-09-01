import pytest

from apps.workspaces.actions import post_to_integration_settings


@pytest.mark.django_db(databases=['default'])
def test_post_to_integration_settings(mocker):
    mocker.patch(
        'apps.fyle.helpers.post_request',
        return_value=''
    )

    no_exception = True
    post_to_integration_settings(1, True)

    # If exception is raised, this test will fail
    assert no_exception
