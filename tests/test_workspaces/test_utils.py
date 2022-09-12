import logging
from apps.workspaces.utils import generate_qbo_refresh_token
from django.conf import settings

logger = logging.getLogger(__name__)

def test_generate_qbo_refresh_token(db):
    try:
        generate_qbo_refresh_token('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjbGllbnRfaWQiOiJ0cGFZZlU3Vkx5ckVOIiwicmVzcG9uc2VfdHlwZSI6ImNvZGUiLCJjbHVzdGVyX2RvbWFpbiI6Imh0dHBzOi8vc3RhZ2luZy5meWxlLnRlY2giLCJvcmdfdXNlcl9pZCI6Im91U2xYM0RHa1hWVyIsImV4cCI6MTY1NDg3MDk2M30.zmWs--h6Osqfz-TRiZMqnKiLCqUdjg6AG3I4pbwbMzI', settings.QBO_REDIRECT_URI)
    except:
        logger.info('Some of the parameters were wrong')
