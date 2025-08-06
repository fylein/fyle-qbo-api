import logging

from django.conf import settings
from rest_framework.serializers import ValidationError
from rest_framework.views import Response

from apps.fyle.helpers import patch_request
from apps.workspaces.models import FyleCredential, LastExportDetail, QBOCredential

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def assert_valid(condition: bool, message: str) -> Response or None:
    """
    Assert conditions
    :param condition: Boolean condition
    :param message: Bad request message
    :return: Response or None
    """
    if not condition:
        raise ValidationError(detail={'message': message})


class LookupFieldMixin:
    lookup_field = 'workspace_id'

    def filter_queryset(self, queryset):
        if self.lookup_field in self.kwargs:
            lookup_value = self.kwargs[self.lookup_field]
            filter_kwargs = {self.lookup_field: lookup_value}
            queryset = queryset.filter(**filter_kwargs)
        return super().filter_queryset(queryset)


def patch_integration_settings(workspace_id: int, errors: int = None, is_token_expired = None, unmapped_card_count: int = None):
    """
    Patch integration settings
    """

    fyle_credential = FyleCredential.objects.get(workspace_id=workspace_id)
    refresh_token = fyle_credential.refresh_token
    url = '{}/integrations/'.format(settings.INTEGRATIONS_SETTINGS_API)
    payload = {
        'tpa_name': 'Fyle Quickbooks Integration',
    }

    if errors is not None:
        payload['errors_count'] = errors

    if is_token_expired is not None:
        payload['is_token_expired'] = is_token_expired

    if unmapped_card_count is not None:
        payload['unmapped_card_count'] = unmapped_card_count

    try:
        if fyle_credential.workspace.onboarding_state == 'COMPLETE':
            patch_request(url, payload, refresh_token)
            return True
        return False
    except Exception as error:
        logger.error(error, exc_info=True)
        return False


def patch_integration_settings_for_unmapped_cards(workspace_id: int, unmapped_card_count: int) -> None:
    """
    Patch integration settings for unmapped cards
    :param workspace_id: Workspace id
    :param unmapped_card_count: Unmapped card count
    return: None
    """
    last_export_detail = LastExportDetail.objects.get(workspace_id=workspace_id)
    if unmapped_card_count != last_export_detail.unmapped_card_count:
        is_patched = patch_integration_settings(workspace_id=workspace_id, unmapped_card_count=unmapped_card_count)
        if is_patched:
            last_export_detail.unmapped_card_count = unmapped_card_count
            last_export_detail.save(update_fields=['unmapped_card_count', 'updated_at'])


def invalidate_qbo_credentials(workspace_id, qbo_credentials=None):
    if not qbo_credentials:
        qbo_credentials = QBOCredential.objects.filter(workspace_id=workspace_id, is_expired=False, refresh_token__isnull=False).first()

    if qbo_credentials:
        if not qbo_credentials.is_expired:
            patch_integration_settings(workspace_id, is_token_expired=True)
        qbo_credentials.refresh_token = None
        qbo_credentials.is_expired = True
        qbo_credentials.save()
