import json
import base64
from typing import Dict
import requests

from django.conf import settings

from future.moves.urllib.parse import urlencode
from qbosdk import (
    UnauthorizedClientError,
    NotFoundClientError,
    WrongParamsError,
    InternalServerError,
)

from fyle_accounting_mappings.models import MappingSetting


from fyle_qbo_api.utils import assert_valid
from .models import WorkspaceGeneralSettings
from ..fyle.models import ExpenseGroupSettings
from apps.quickbooks_online.queue import (
    schedule_qbo_objects_status_sync,
    schedule_reimbursements_sync,
)
from apps.mappings.queue import (
    schedule_auto_map_ccc_employees,
    schedule_bill_payment_creation,
    schedule_tax_groups_creation,
    schedule_auto_map_employees,
)


def generate_qbo_refresh_token(authorization_code: str, redirect_uri: str) -> str:
    """
    Generate QBO refresh token from authorization code
    """
    api_data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': redirect_uri,
    }

    auth = '{0}:{1}'.format(settings.QBO_CLIENT_ID, settings.QBO_CLIENT_SECRET)
    auth = base64.b64encode(auth.encode('utf-8'))

    request_header = {
        'Accept': 'application/json',
        'Content-type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic {0}'.format(str(auth.decode())),
    }

    token_url = settings.QBO_TOKEN_URI
    response = requests.post(
        url=token_url, data=urlencode(api_data), headers=request_header
    )

    if response.status_code == 200:
        return json.loads(response.text)['refresh_token']

    elif response.status_code == 401:
        raise UnauthorizedClientError(
            'Wrong client secret or/and refresh token', response.text
        )

    elif response.status_code == 404:
        raise NotFoundClientError('Client ID doesn\'t exist', response.text)

    elif response.status_code == 400:
        raise WrongParamsError('Some of the parameters were wrong', response.text)

    elif response.status_code == 500:
        raise InternalServerError('Internal server error', response.text)


def create_or_update_general_settings(general_settings_payload: Dict, workspace_id):
    """
    Create or update general settings
    :param workspace_id:
    :param general_settings_payload: general settings payload
    :return:
    """
    assert_valid(
        'reimbursable_expenses_object' in general_settings_payload
        and general_settings_payload['reimbursable_expenses_object'],
        'reimbursable_expenses_object field is blank',
    )

    assert_valid(
        'employee_field_mapping' in general_settings_payload
        and general_settings_payload['employee_field_mapping'],
        'employee_field_mapping field is blank',
    )

    if (
        'auto_map_employees' in general_settings_payload
        and general_settings_payload['auto_map_employees']
    ):
        assert_valid(
            general_settings_payload['auto_map_employees']
            in ['EMAIL', 'NAME', 'EMPLOYEE_CODE'],
            'auto_map_employees can have only EMAIL / NAME / EMPLOYEE_CODE',
        )

    if general_settings_payload['auto_create_destination_entity']:
        assert_valid(
            general_settings_payload['auto_map_employees']
            and general_settings_payload['employee_field_mapping'] == 'VENDOR',
            'auto_create_destination_entity can be set only if auto map is enabled and employee mapped to vendor',
        )

    if general_settings_payload['je_single_credit_line']:
        assert_valid(
            general_settings_payload['reimbursable_expenses_object'] == 'JOURNAL ENTRY'
            or general_settings_payload['corporate_credit_card_expenses_object']
            == 'JOURNAL ENTRY',
            'je_single_credit_line can be set only if reimbursable_expenses_object or \
                corporate_credit_card_expenses_object is JOURNAL ENTRY',
        )

    if (
        general_settings_payload['sync_fyle_to_qbo_payments']
        or general_settings_payload['sync_qbo_to_fyle_payments']
    ):
        assert_valid(
            general_settings_payload['reimbursable_expenses_object'] == 'BILL',
            'sync_fyle_to_qbo_payments / sync_qbo_to_fyle_payments can be set \
                only if reimbursable_expenses_object is BILL',
        )

    workspace_general_settings = WorkspaceGeneralSettings.objects.filter(
        workspace_id=workspace_id
    ).first()

    map_merchant_to_vendor = True

    if workspace_general_settings:
        map_merchant_to_vendor = workspace_general_settings.map_merchant_to_vendor

    # TODO: remove this hack once workspace settings are saved
    if workspace_id == 98:
        category_sync_version = 'v1'
    else:
        category_sync_version = (
            workspace_general_settings.category_sync_version
            if workspace_general_settings
            else 'v2'
        )

    general_settings, _ = WorkspaceGeneralSettings.objects.update_or_create(
        workspace_id=workspace_id,
        category_sync_version=category_sync_version,
        defaults={
            'employee_field_mapping': general_settings_payload[
                'employee_field_mapping'
            ],
            'import_projects': general_settings_payload['import_projects'],
            'import_categories': general_settings_payload['import_categories'],
            'import_tax_codes': general_settings_payload['import_tax_codes'],
            'change_accounting_period': general_settings_payload[
                'change_accounting_period'
            ],
            'charts_of_accounts': general_settings_payload['charts_of_accounts'],
            'auto_map_employees': general_settings_payload['auto_map_employees'],
            'auto_create_destination_entity': general_settings_payload[
                'auto_create_destination_entity'
            ],
            'auto_create_merchants_as_vendors': general_settings_payload[
                'auto_create_merchants_as_vendors'
            ],
            'reimbursable_expenses_object': general_settings_payload[
                'reimbursable_expenses_object'
            ]
            if 'reimbursable_expenses_object' in general_settings_payload
            and general_settings_payload['reimbursable_expenses_object']
            else None,
            'corporate_credit_card_expenses_object': general_settings_payload[
                'corporate_credit_card_expenses_object'
            ]
            if 'corporate_credit_card_expenses_object' in general_settings_payload
            and general_settings_payload['corporate_credit_card_expenses_object']
            else None,
            'sync_fyle_to_qbo_payments': general_settings_payload[
                'sync_fyle_to_qbo_payments'
            ],
            'sync_qbo_to_fyle_payments': general_settings_payload[
                'sync_qbo_to_fyle_payments'
            ],
            'map_merchant_to_vendor': map_merchant_to_vendor,
            'je_single_credit_line': general_settings_payload['je_single_credit_line'],
            'map_fyle_cards_qbo_account': general_settings_payload[
                'map_fyle_cards_qbo_account'
            ],
            'import_vendors_as_merchants': general_settings_payload[
                'import_vendors_as_merchants'
            ],
        },
    )

    if (
        general_settings.map_merchant_to_vendor
        and general_settings.corporate_credit_card_expenses_object
        in ('CREDIT CARD PURCHASE', 'DEBIT CARD EXPENSE')
    ):
        expense_group_settings = ExpenseGroupSettings.objects.get(
            workspace_id=workspace_id
        )
        expense_group_settings.import_card_credits = (
            True
            if general_settings.corporate_credit_card_expenses_object
            == 'CREDIT CARD PURCHASE'
            else False
        )

        ccc_expense_group_fields = (
            expense_group_settings.corporate_credit_card_expense_group_fields
        )
        ccc_expense_group_fields.append('expense_id')
        expense_group_settings.corporate_credit_card_expense_group_fields = list(
            set(ccc_expense_group_fields)
        )
        expense_group_settings.ccc_export_date_type = 'spent_at'

        expense_group_settings.save()

    if (
        general_settings.corporate_credit_card_expenses_object == 'JOURNAL ENTRY'
        or general_settings.reimbursable_expenses_object in ('JOURNAL ENTRY', 'EXPENSE')
    ):
        expense_group_settings = ExpenseGroupSettings.objects.get(
            workspace_id=workspace_id
        )
        expense_group_settings.import_card_credits = True
        expense_group_settings.save()

    schedule_tax_groups_creation(
        import_tax_codes=general_settings.import_tax_codes, workspace_id=workspace_id
    )

    schedule_auto_map_employees(
        general_settings_payload['auto_map_employees'], workspace_id
    )

    schedule_auto_map_ccc_employees(workspace_id)

    schedule_bill_payment_creation(
        general_settings.sync_fyle_to_qbo_payments, workspace_id
    )

    schedule_qbo_objects_status_sync(
        sync_qbo_to_fyle_payments=general_settings.sync_qbo_to_fyle_payments,
        workspace_id=workspace_id,
    )

    schedule_reimbursements_sync(
        sync_qbo_to_fyle_payments=general_settings.sync_qbo_to_fyle_payments,
        workspace_id=workspace_id,
    )

    return general_settings


def delete_cards_mapping_settings(workspace_general_settings: WorkspaceGeneralSettings):
    if (
        not workspace_general_settings.map_fyle_cards_qbo_account
        or not workspace_general_settings.corporate_credit_card_expenses_object
    ):
        mapping_setting = MappingSetting.objects.filter(
            workspace_id=workspace_general_settings.workspace_id,
            source_field='CORPORATE_CARD',
            destination_field='CREDIT_CARD_ACCOUNT',
        ).first()
        if mapping_setting:
            mapping_setting.delete()
