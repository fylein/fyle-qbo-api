import base64
import hashlib
import hmac
import logging

from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import permissions

from apps.workspaces.models import Workspace

User = get_user_model()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class WorkspacePermissions(permissions.BasePermission):
    """
    Permission check for users <> workspaces
    """

    def validate_and_cache(self, workspace_users, user: User, workspace_id: str, payload: dict, cache_users: bool = False):
        if user.id in workspace_users:
            if cache_users:
                cache.set(workspace_id, workspace_users, 172800)
            return True

        logger.error(f'User {user.id} is not allowed to access workspace {workspace_id}')
        logger.info(f'Permission was cached earlier: {not cache_users}')
        logger.info(f'Allowed users: {workspace_users}')
        logger.info(f'Payload: {payload}')
        cache.delete(str(workspace_id))
        return False

    def has_permission(self, request, view):
        workspace_id = str(view.kwargs.get('workspace_id'))
        user = request.user
        workspace_users = cache.get(workspace_id)
        logger.info(f'User: {user}')
        logger.info(f'Workspace users: {workspace_users}')

        if workspace_users:
            return self.validate_and_cache(workspace_users, user, workspace_id, request.data)
        else:
            workspace_users = Workspace.objects.filter(pk=workspace_id).values_list('user', flat=True)
            return self.validate_and_cache(workspace_users, user, workspace_id, request.data, True)


class IsAuthenticatedForInternalAPI(permissions.BasePermission):
    """
    Custom auth for internal APIs
    """

    def has_permission(self, request, view):
        # Client sends a token in the header, which we decrypt and compare with the Client Secret
        cipher_suite = Fernet(settings.ENCRYPTION_KEY)
        try:
            decrypted_password = cipher_suite.decrypt(request.headers['X-Internal-API-Client-ID'].encode('utf-8')).decode('utf-8')
            if decrypted_password == settings.E2E_TESTS_CLIENT_SECRET:
                return True
        except Exception:
            return False

        return False


class IsAuthenticatedForQuickbooksWebhook(permissions.BasePermission):
    """
    Custom auth for Quickbooks webhook APIs using signature validation
    """

    def has_permission(self, request, view):
        try:
            signature = request.headers.get('intuit-signature')
            payload = request.body
            qbo_webhook_token = settings.QBO_WEBHOOK_TOKEN
            expected = base64.b64encode(
                hmac.new(
                    qbo_webhook_token.encode('utf-8'),
                    payload,
                    hashlib.sha256
                ).digest()
            ).decode('utf-8')

            if not hmac.compare_digest(signature, expected):
                logger.error("Invalid signature")
                return False

            return True
        except Exception as e:
            logger.error(f"Webhook authentication error: {str(e)}")
            return False
