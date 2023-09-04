import json
from typing import List, Union

import requests
from django.conf import settings
from django.db.models import Q

from apps.fyle.models import ExpenseFilter, Expense
from apps.workspaces.models import Workspace


def post_request(url, body, refresh_token=None):
    """
    Create a HTTP post request.
    """
    access_token = None
    api_headers = {}
    if refresh_token:
        access_token = get_access_token(refresh_token)

        api_headers['content-type'] = 'application/json'
        api_headers['Authorization'] = 'Bearer {0}'.format(access_token)

    response = requests.post(url, headers=api_headers, data=body)

    if response.status_code in [200, 201]:
        return json.loads(response.text)
    else:
        raise Exception(response.text)


def get_request(url, params, refresh_token):
    """
    Create a HTTP get request.
    """
    access_token = get_access_token(refresh_token)
    api_headers = {'content-type': 'application/json', 'Authorization': 'Bearer {0}'.format(access_token)}
    api_params = {}

    for k in params:
        # ignore all unused params
        if not params[k] is None:
            p = params[k]

            # convert boolean to lowercase string
            if isinstance(p, bool):
                p = str(p).lower()

            api_params[k] = p

    response = requests.get(url, headers=api_headers, params=api_params)

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception(response.text)


def get_access_token(refresh_token: str) -> str:
    """
    Get access token from fyle
    """
    api_data = {'grant_type': 'refresh_token', 'refresh_token': refresh_token, 'client_id': settings.FYLE_CLIENT_ID, 'client_secret': settings.FYLE_CLIENT_SECRET}
    return post_request(settings.FYLE_TOKEN_URI, body=api_data)['access_token']


def get_fyle_orgs(refresh_token: str, cluster_domain: str):
    """
    Get fyle orgs of a user
    """
    api_url = '{0}/api/orgs/'.format(cluster_domain)

    return get_request(api_url, {}, refresh_token)


def get_cluster_domain(refresh_token: str) -> str:
    """
    Get cluster domain name from fyle
    :param refresh_token: (str)
    :return: cluster_domain (str)
    """
    cluster_api_url = '{0}/oauth/cluster/'.format(settings.FYLE_BASE_URL)

    return post_request(cluster_api_url, {}, refresh_token)['cluster_domain']


def construct_expense_filter_query(expense_filters: List[ExpenseFilter]):
    final_filter = None
    join_by = None
    for expense_filter in expense_filters:
        constructed_expense_filter = construct_expense_filter(expense_filter)

        # If this is the first filter, set it as the final filter
        if expense_filter.rank == 1:
            final_filter = constructed_expense_filter

        # If join by is AND, OR
        elif expense_filter.rank != 1:
            if join_by == 'AND':
                final_filter = final_filter & (constructed_expense_filter)
            else:
                final_filter = final_filter | (constructed_expense_filter)

        # Set the join type for the additonal filter
        join_by = expense_filter.join_by

    return final_filter


def construct_expense_filter(expense_filter):
    constructed_expense_filter = {}

    # If the expense filter is a custom field and the operator is not isnull
    if expense_filter.is_custom and expense_filter.operator != 'isnull':
        # If the custom field is of type SELECT and the operator is not_in
        if expense_filter.custom_field_type == 'SELECT' and expense_filter.operator == 'not_in':
            # Construct the filter for the custom property
            filter1 = {f'custom_properties__{expense_filter.condition}__in': expense_filter.values}
            # Invert the filter using the ~Q operator and assign it to the constructed expense filter
            constructed_expense_filter = ~Q(**filter1)
        else:
            # If the custom field is of type NUMBER, convert the values to integers
            if expense_filter.custom_field_type == 'NUMBER':
                expense_filter.values = [int(value) for value in expense_filter.values]
            # Construct the filter for the custom property
            filter1 = {f'custom_properties__{expense_filter.condition}__{expense_filter.operator}': expense_filter.values[0] if len(expense_filter.values) == 1 and expense_filter.operator != 'in' else expense_filter.values}
            # Assign the constructed filter to the constructed expense filter
            constructed_expense_filter = Q(**filter1)

    # If the expense filter is a custom field and the operator is isnull
    elif expense_filter.is_custom and expense_filter.operator == 'isnull':
        # Determine the value for the isnull filter based on the first value in the values list
        expense_filter_value: bool = True if expense_filter.values[0].lower() == 'true' else False
        # Construct the isnull filter for the custom property
        filter1 = {f'custom_properties__{expense_filter.condition}__isnull': expense_filter_value}
        # Construct the exact filter for the custom property
        filter2 = {f'custom_properties__{expense_filter.condition}__exact': None}
        if expense_filter_value:
            # If the isnull filter value is True, combine the two filters using the | operator and assign it to the constructed expense filter
            constructed_expense_filter = Q(**filter1) | Q(**filter2)
        else:
            # If the isnull filter value is False, invert the exact filter using the ~Q operator and assign it to the constructed expense filter
            constructed_expense_filter = ~Q(**filter2)

    # For all non-custom fields
    else:
        # Construct the filter for the non-custom field
        filter1 = {f'{expense_filter.condition}__{expense_filter.operator}': expense_filter.values[0] if len(expense_filter.values) == 1 and expense_filter.operator != 'in' else expense_filter.values}
        # Assign the constructed filter to the constructed expense filter
        constructed_expense_filter = Q(**filter1)

    # Return the constructed expense filter
    return constructed_expense_filter


def mark_accounting_export_summary_as_synced(expenses: List[Expense]) -> None:
    """
    Mark accounting export summary as synced in bulk
    :param expenses: List of expenses
    :return: None
    """
    # Mark all expenses as synced
    expense_to_be_updated = []
    for expense in expenses:
        expense.accounting_export_summary['synced'] = True
        updated_accounting_export_summary = expense.accounting_export_summary
        expense_to_be_updated.append(
            Expense(
                id=expense.id,
                accounting_export_summary=updated_accounting_export_summary
            )
        )

    Expense.objects.bulk_update(expense_to_be_updated, ['accounting_export_summary'], batch_size=50)


def get_updated_accounting_export_summary(
        expense_id: str, state: str, error_type: Union[str, None], url: Union[str, None], is_synced: bool) -> dict:
    """
    Get updated accounting export summary
    :param expense_id: expense id
    :param state: state
    :param error_type: error type
    :param url: url
    :param is_synced: is synced
    :return: updated accounting export summary
    """
    return {
        'id': expense_id,
        'state': state,
        'error_type': error_type,
        'url': url,
        'synced': is_synced
    }


def __bulk_update_expenses(expense_to_be_updated: List[Expense]) -> None:
    """
    Bulk update expenses
    :param expense_to_be_updated: expenses to be updated
    :return: None
    """
    if expense_to_be_updated:
        Expense.objects.bulk_update(expense_to_be_updated, ['is_skipped', 'accounting_export_summary'], batch_size=50)


def mark_expenses_as_skipped(final_query: Q, expenses_object_ids: List, workspace: Workspace) -> None:
    """
    Mark expenses as skipped in bulk
    :param final_query: final query
    :param expenses_object_ids: expenses object ids
    :param workspace: workspace object
    :return: None
    """
    # We'll iterate through the list of expenses to be skipped, construct accounting export summary and update expenses
    expense_to_be_updated = []
    expenses_to_be_skipped = Expense.objects.filter(
        final_query,
        id__in=expenses_object_ids,
        expensegroup__isnull=True,
        org_id=workspace.fyle_org_id
    )

    for expense in expenses_to_be_skipped:
        expense_to_be_updated.append(
            Expense(
                id=expense.id,
                is_skipped=True,
                accounting_export_summary=get_updated_accounting_export_summary(
                    expense.expense_id,
                    'SKIPPED',
                    None,
                    '{}/workspaces/main/export_log'.format(settings.QBO_INTEGRATION_APP_URL),
                    False
                )
            )
        )

    __bulk_update_expenses(expense_to_be_updated)


def update_expenses_in_progress(in_progress_expenses: List[Expense]) -> None:
    """
    Update expenses in progress in bulk
    :param in_progress_expenses: in progress expenses
    :return: None
    """
    expense_to_be_updated = []
    for expense in in_progress_expenses:
        expense_to_be_updated.append(
            Expense(
                id=expense.id,
                accounting_export_summary=get_updated_accounting_export_summary(
                    expense.expense_id,
                    'IN_PROGRESS',
                    None,
                    '{}/workspaces/main/dashboard'.format(settings.QBO_INTEGRATION_APP_URL),
                    False
                )
            )
        )

    __bulk_update_expenses(expense_to_be_updated)


def update_failed_expenses(in_progress_expenses: List[Expense], is_mapping_error: bool) -> None:
    """
    Update failed expenses
    :param in_progress_expenses: In progress expenses
    """
    expense_to_be_updated = []
    for expense in in_progress_expenses:
        expense_to_be_updated.append(
            Expense(
                id=expense.id,
                accounting_export_summary=get_updated_accounting_export_summary(
                    expense.expense_id,
                    'ERROR',
                    'MAPPING' if is_mapping_error else 'ACCOUNTING_INTEGRATION_ERROR',
                    '{}/workspaces/main/dashboard'.format(settings.QBO_INTEGRATION_APP_URL),
                    False
                )
            )
        )

    __bulk_update_expenses(expense_to_be_updated)
