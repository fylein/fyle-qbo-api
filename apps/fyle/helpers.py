import json
import requests

from django.conf import settings
from django.db.models import Q
from apps.fyle.models import ExpenseFilter
from typing import List

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

    response = requests.post(
        url,
        headers=api_headers,
        data=body
    )

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception(response.text)


def get_request(url, params, refresh_token):
    """
    Create a HTTP get request.
    """
    access_token = get_access_token(refresh_token)
    api_headers = {
        'content-type': 'application/json',
        'Authorization': 'Bearer {0}'.format(access_token)
    }
    api_params = {}

    for k in params:
        # ignore all unused params
        if not params[k] is None:
            p = params[k]

            # convert boolean to lowercase string
            if isinstance(p, bool):
                p = str(p).lower()

            api_params[k] = p

    response = requests.get(
        url,
        headers=api_headers,
        params=api_params
    )

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception(response.text)


def get_access_token(refresh_token: str) -> str:
    """
    Get access token from fyle
    """
    api_data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': settings.FYLE_CLIENT_ID,
        'client_secret': settings.FYLE_CLIENT_SECRET
    }
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
    for expense_filter in expense_filters:
        constructed_expense_filter = construct_expense_filter(expense_filter)
        
        # If this is the first filter, set it as the final filter
        if expense_filter.rank == 1:
            final_filter = (constructed_expense_filter)
        
        # If not first filter and join type is "AND", add to filter1 using "and" operator
        elif expense_filter.rank != 1 and join_by == 'AND':
            final_filter = final_filter & (constructed_expense_filter)
        
        # If not first filter and join type is "OR", add to filter1 using "or" operator
        elif expense_filter.rank != 1 and join_by == 'OR':
            final_filter = final_filter | (constructed_expense_filter)

        # Set the join type for the additonal filter
        join_by = expense_filter.join_by

    return final_filter


def construct_expense_filter(expense_filter: ExpenseFilter):
    constructed_expense_filter = {}
    if expense_filter.is_custom and expense_filter.operator != 'isnull':
        #custom-field for equals to, dynamic value
        if expense_filter.custom_field_type == 'SELECT' and expense_filter.operator == 'not_in':
            filter1 = {
                'custom_properties__{0}__{1}'.format(
                    expense_filter.condition,
                    'in'
                ): expense_filter.values
            }
            constructed_expense_filter = ~Q(**filter1)
        else:
            if expense_filter.custom_field_type == 'NUMBER':
                expense_filter.values = [int(expense_filter_value) for expense_filter_value in expense_filter.values]

            filter1 = {
                'custom_properties__{0}__{1}'.format(
                    expense_filter.condition,
                    expense_filter.operator
                ): expense_filter.values if len(expense_filter.values) > 1 or expense_filter.operator == 'in' else expense_filter.values[0]
            }
            constructed_expense_filter = Q(**filter1)

    elif expense_filter.is_custom and expense_filter.operator == 'isnull':
        #custom_field is_null
        expense_filter_value: bool = True if expense_filter.values[0].lower() == 'true' else False
        filter1 = {
            'custom_properties__{0}__{1}'.format(
                expense_filter.condition,
                expense_filter.operator
            ): expense_filter_value
        }
        filter2 = {
            'custom_properties__{0}__exact'.format(expense_filter.condition): None
        }
        if expense_filter_value == True:
            #if isnull=True
            constructed_expense_filter = Q(**filter1) | Q(**filter2)
        else:
            #if isnull=False
            constructed_expense_filter = ~Q(**filter2)

    else:
        #Default_fields
        filter1 = {
            '{0}__{1}'.format(
                expense_filter.condition,
                expense_filter.operator
            ):expense_filter.values if len(expense_filter.values) > 1 or expense_filter.operator == 'in' else expense_filter.values[0]
        }
        constructed_expense_filter = Q(**filter1)

    return constructed_expense_filter