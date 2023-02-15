import pytest
from asyncio.log import logger
from unittest import mock
from rest_framework.response import Response
from rest_framework.views import status
from apps.fyle.helpers import *


def test_post_request(mocker):
    mocker.patch(
        'apps.fyle.helpers.requests.post',
        return_value=Response(
            {
                'message': 'Post request'
            },
            status=status.HTTP_200_OK
        )
    )
    try:
        post_request(url='sdfghjk', body={}, refresh_token='srtyu')
    except:
        logger.info('Error in post request')
    
    mocker.patch(
        'apps.fyle.helpers.requests.post',
        return_value=Response(
            {
                'message': 'Post request'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    )
    try:
        post_request(url='sdfghjk', body={}, refresh_token='srtyu')
    except:
        logger.info('Error in post request')


def test_get_request(mocker):
    mocker.patch(
        'apps.fyle.helpers.requests.get',
        return_value=Response(
            {
                'message': 'Get request'
            },
            status=status.HTTP_200_OK
        )
    )
    try:
        get_request(url='sdfghjk', params={'sample': True}, refresh_token='srtyu')
    except:
        logger.info('Error in post request')

    mocker.patch(
        'apps.fyle.helpers.requests.get',
        return_value=Response(
            {
                'message': 'Get request'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    )
    try:
        get_request(url='sdfghjk', params={'sample': True}, refresh_token='srtyu')
    except:
        logger.info('Error in post request')


def test_get_cluster_domain(mocker):
    mocker.patch(
        'apps.fyle.helpers.requests.post',
        return_value=Response(
            {
                'message': 'Post request'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    )
    try:
        get_cluster_domain(refresh_token='srtyu')
    except:
        logger.info('Error in post request')

@pytest.mark.django_db()
def test_construct_expense_filter(mocker, add_fyle_credentials):
    #employee-email-is-equal
    expense_filter = ExpenseFilter(
        condition = 'employee_email',
        operator = 'in',
        values = ['killua.z@fyle.in', 'naruto.u@fyle.in'],
        rank = 1
    )
    constructed_expense_filter = construct_expense_filter(expense_filter)

    filter_1 = {'employee_email__in':['killua.z@fyle.in', 'naruto.u@fyle.in']}
    response = Q(**filter_1)

    assert constructed_expense_filter == response

    #employee-email-is-equal-one-email-only
    expense_filter = ExpenseFilter(
        condition = 'employee_email',
        operator = 'in',
        values = ['killua.z@fyle.in'],
        rank = 1
    )
    constructed_expense_filter = construct_expense_filter(expense_filter)

    filter_1 = {'employee_email__in':['killua.z@fyle.in']}
    response = Q(**filter_1)

    assert constructed_expense_filter == response

    #claim-number-is-equal
    expense_filter = ExpenseFilter(
        condition = 'claim_number',
        operator = 'in',
        values = ['ajdnwjnadw', 'ajdnwjnlol'],
        rank = 1
    )
    constructed_expense_filter = construct_expense_filter(expense_filter)

    filter_1 = {'claim_number__in':['ajdnwjnadw', 'ajdnwjnlol']}
    response = Q(**filter_1)

    assert constructed_expense_filter == response

    #claim-number-is-equal-one-claim_number-only
    expense_filter = ExpenseFilter(
        condition = 'claim_number',
        operator = 'in',
        values = ['ajdnwjnadw'],
        rank = 1
    )
    constructed_expense_filter = construct_expense_filter(expense_filter)

    filter_1 = {'claim_number__in':['ajdnwjnadw']}
    response = Q(**filter_1)

    assert constructed_expense_filter == response

    #report-name-is-equal
    expense_filter = ExpenseFilter(
        condition = 'report_title',
        operator = 'iexact',
        values = ['#17:  Dec 2022'],
        rank = 1
    )
    constructed_expense_filter = construct_expense_filter(expense_filter)

    filter_1 = {'report_title__iexact':'#17:  Dec 2022'}
    response = Q(**filter_1)

    assert constructed_expense_filter == response

    #report-name-contains
    expense_filter = ExpenseFilter(
        condition = 'report_title',
        operator = 'icontains',
        values = ['Dec 2022'],
        rank = 1
    )
    constructed_expense_filter = construct_expense_filter(expense_filter)

    filter_1 = {'report_title__icontains':'Dec 2022'}
    response = Q(**filter_1)

    assert constructed_expense_filter == response

    #spent-at-is-before
    expense_filter = ExpenseFilter(
        condition = 'spent_at',
        operator = 'lt',
        values = ['2020-04-20 23:59:59+00'],
        rank = 1
    )
    constructed_expense_filter = construct_expense_filter(expense_filter)

    filter_1 = {'spent_at__lt':'2020-04-20 23:59:59+00'}
    response = Q(**filter_1)

    assert constructed_expense_filter == response

    #spent-at-is-on-or-before
    expense_filter = ExpenseFilter(
        condition = 'spent_at',
        operator = 'lte',
        values = ['2020-04-20 23:59:59+00'],
        rank = 1
    )
    constructed_expense_filter = construct_expense_filter(expense_filter)

    filter_1 = {'spent_at__lte':'2020-04-20 23:59:59+00'}
    response = Q(**filter_1)

    assert constructed_expense_filter == response

    #custom-properties-number-is-equal
    expense_filter = ExpenseFilter(
        condition = 'Gon Number',
        operator = 'in',
        values = [102,108],
        rank = 1,
        is_custom = True
    )
    constructed_expense_filter = construct_expense_filter(expense_filter)

    filter_1 = {'custom_properties__Gon Number__in':[102, 108]}
    response = Q(**filter_1)

    assert constructed_expense_filter == response

    #custom-properties-number-is-not-empty
    expense_filter = ExpenseFilter(
        condition = 'Gon Number',
        operator = 'isnull',
        values = ['False'],
        rank = 1,
        is_custom = True
    )
    constructed_expense_filter = construct_expense_filter(expense_filter)

    filter_1 = {'custom_properties__Gon Number__exact': None}
    response = ~Q(**filter_1)

    assert constructed_expense_filter == response

    #custom-properties-number-is--empty
    expense_filter = ExpenseFilter(
        condition = 'Gon Number',
        operator = 'isnull',
        values = ['True'],
        rank = 1,
        is_custom = True
    )
    constructed_expense_filter = construct_expense_filter(expense_filter)

    filter_1 = {'custom_properties__Gon Number__isnull': True}
    filter_2 = {'custom_properties__Gon Number__exact': None}
    response = Q(**filter_1) | Q(**filter_2)

    assert constructed_expense_filter == response

    #custom-properties-text-is-equal
    expense_filter = ExpenseFilter(
        condition = 'Killua Text',
        operator = 'in',
        values = ['hunter', 'naruto', 'sasuske'],
        rank = 1,
        is_custom = True
    )
    constructed_expense_filter = construct_expense_filter(expense_filter)

    filter_1 = {'custom_properties__Killua Text__in':['hunter', 'naruto', 'sasuske']}
    response = Q(**filter_1)

    assert constructed_expense_filter == response

    #custom-properties-text-is-not-empty
    expense_filter = ExpenseFilter(
        condition = 'Killua Text',
        operator = 'isnull',
        values = ['False'],
        rank = 1,
        is_custom = True
    )
    constructed_expense_filter = construct_expense_filter(expense_filter)

    filter_1 = {'custom_properties__Killua Text__exact': None}
    response = ~Q(**filter_1)

    assert constructed_expense_filter == response

    #custom-properties-text-is--empty
    expense_filter = ExpenseFilter(
        condition = 'Killua Text',
        operator = 'isnull',
        values = ['True'],
        rank = 1,
        is_custom = True
    )
    constructed_expense_filter = construct_expense_filter(expense_filter)

    filter_1 = {'custom_properties__Killua Text__isnull': True}
    filter_2 = {'custom_properties__Killua Text__exact': None}
    response = Q(**filter_1) | Q(**filter_2)

    assert constructed_expense_filter == response

    #custom-properties-select-is-equal
    expense_filter = ExpenseFilter(
        condition = 'Kratos',
        operator = 'in',
        values = ['BOOK', 'Dev-D'],
        rank = 1,
        is_custom = True
    )
    constructed_expense_filter = construct_expense_filter(expense_filter)

    filter_1 = {'custom_properties__Kratos__in':['BOOK', 'Dev-D']}
    response = Q(**filter_1)

    assert constructed_expense_filter == response

    #custom-properties-select-is-equal-one-value
    expense_filter = ExpenseFilter(
        condition = 'Kratos',
        operator = 'in',
        values = ['BOOK'],
        rank = 1,
        is_custom = True
    )
    constructed_expense_filter = construct_expense_filter(expense_filter)

    filter_1 = {'custom_properties__Kratos__in':['BOOK']}
    response = Q(**filter_1)

    assert constructed_expense_filter == response

    #custom-properties-select-is-not-empty
    expense_filter = ExpenseFilter(
        condition = 'Kratos',
        operator = 'isnull',
        values = ['False'],
        rank = 1,
        is_custom = True
    )
    constructed_expense_filter = construct_expense_filter(expense_filter)

    filter_1 = {'custom_properties__Kratos__exact': None}
    response = ~Q(**filter_1)

    assert constructed_expense_filter == response

    #custom-properties-select-is--empty
    expense_filter = ExpenseFilter(
        condition = 'Kratos',
        operator = 'isnull',
        values = ['True'],
        rank = 1,
        is_custom = True
    )
    constructed_expense_filter = construct_expense_filter(expense_filter)

    filter_1 = {'custom_properties__Kratos__isnull': True}
    filter_2 = {'custom_properties__Kratos__exact': None}
    response = Q(**filter_1) | Q(**filter_2)

    assert constructed_expense_filter == response


@pytest.mark.django_db()
def test_multiple_construct_expense_filter(mocker, add_fyle_credentials):
    #employee-email-is-equal and claim-number-is-equal
    expense_filters = [
        ExpenseFilter(
            condition = 'employee_email',
            operator = 'in',
            values = ['killua.z@fyle.in', 'naruto.u@fyle.in'],
            rank = 1,
            join_by = 'AND'
        ), 
        ExpenseFilter(
        condition = 'claim_number',
        operator = 'in',
        values = ['ajdnwjnadw', 'ajdnwjnlol'],
        rank = 2,
        )
    ]

    final_filter = construct_expense_filter_query(expense_filters)

    filter_1 = {'employee_email__in':['killua.z@fyle.in', 'naruto.u@fyle.in']}
    filter_2 = {'claim_number__in':['ajdnwjnadw', 'ajdnwjnlol']}
    response = Q(**filter_1) & Q(**filter_2)

    assert final_filter == response

    #employee-email-is-equal or claim-number-is-equal
    expense_filters = [
        ExpenseFilter(
            condition = 'employee_email',
            operator = 'in',
            values = ['killua.z@fyle.in', 'naruto.u@fyle.in'],
            rank = 1,
            join_by = 'OR'
        ), 
        ExpenseFilter(
        condition = 'claim_number',
        operator = 'in',
        values = ['ajdnwjnadw', 'ajdnwjnlol'],
        rank = 2,
        )
    ]

    final_filter = construct_expense_filter_query(expense_filters)
    
    filter_1 = {'employee_email__in':['killua.z@fyle.in', 'naruto.u@fyle.in']}
    filter_2 = {'claim_number__in':['ajdnwjnadw', 'ajdnwjnlol']}
    response = Q(**filter_1) | Q(**filter_2)

    assert final_filter == response

    #employee-email-is-equal or report-title-contains
    expense_filters = [
        ExpenseFilter(
            condition = 'employee_email',
            operator = 'in',
            values = ['killua.z@fyle.in', 'naruto.u@fyle.in'],
            rank = 1,
            join_by = 'OR'
        ), 
        ExpenseFilter(
            condition = 'report_title',
            operator = 'icontains',
            values = ['Dec 2022'],
            rank = 2
        )
    ]

    final_filter = construct_expense_filter_query(expense_filters)
    
    filter_1 = {'employee_email__in':['killua.z@fyle.in', 'naruto.u@fyle.in']}
    filter_2 = {'report_title__icontains':'Dec 2022'}
    response = Q(**filter_1) | Q(**filter_2)

    assert final_filter == response

    #custom-properties-number-is-empty and spent-at-less-than
    expense_filters = [
        ExpenseFilter(
            condition = 'Gon Number',
            operator = 'isnull',
            values = ['True'],
            rank = 1,
            is_custom = True,
            join_by = 'AND'
        ),
        ExpenseFilter(
            condition = 'spent_at',
            operator = 'lt',
            values = ['2020-04-20 23:59:59+00'],
            rank = 2
        )
    ]

    final_filter = construct_expense_filter_query(expense_filters)

    filter_1 = {'custom_properties__Gon Number__isnull': True}
    filter_2 = {'custom_properties__Gon Number__exact': None}
    filter_3 = {'spent_at__lt':'2020-04-20 23:59:59+00'}
    response = (Q(**filter_1) | Q(**filter_2)) & (Q(**filter_3))

    assert final_filter == response

    #custom-properties-number-is-empty and custom-properties-select-is-not-empty
    expense_filters = [
        ExpenseFilter(
            condition = 'Gon Number',
            operator = 'isnull',
            values = ['True'],
            rank = 1,
            is_custom = True,
            join_by = 'AND'
        ),
        ExpenseFilter(
            condition = 'Kratos',
            operator = 'isnull',
            values = ['False'],
            rank = 2,
            is_custom = True
        )
    ]

    final_filter = construct_expense_filter_query(expense_filters)

    filter_1 = {'custom_properties__Gon Number__isnull': True}
    filter_2 = {'custom_properties__Gon Number__exact': None}
    filter_3 = {'custom_properties__Kratos__exact': None}
    response = (Q(**filter_1) | Q(**filter_2)) & (~Q(**filter_3))

    assert final_filter == response

    #report-name-is-equal or custom-properties-number-is-equal  
    expense_filters = [
        ExpenseFilter(
            condition = 'report_title',
            operator = 'iexact',
            values = ['#17:  Dec 2022'],
            rank = 1,
            join_by = 'OR'
        ),
        ExpenseFilter(
            condition = 'Gon Number',
            operator = 'in',
            values = [102,108],
            rank = 2,
            is_custom = True
        )
    ]

    final_filter = construct_expense_filter_query(expense_filters)
    
    filter_1 = {'report_title__iexact':'#17:  Dec 2022'}
    filter_2 = {'custom_properties__Gon Number__in':[102, 108]}
    response = (Q(**filter_1)) | (Q(**filter_2))

    assert final_filter == response

    #custom-properties-number-is-equal and custom-properties-text-is-equal
    expense_filters = [
        ExpenseFilter(
            condition = 'Gon Number',
            operator = 'in',
            values = [102,108],
            rank = 1,
            is_custom = True,
            join_by='AND'
        ),
        ExpenseFilter(
            condition = 'Killua Text',
            operator = 'in',
            values = ['hunter', 'naruto', 'sasuske'],
            rank = 2,
            is_custom = True
        )
    ]

    final_filter = construct_expense_filter_query(expense_filters)

    filter_1 = {'custom_properties__Gon Number__in':[102, 108]}
    filter_2 = {'custom_properties__Killua Text__in':['hunter', 'naruto', 'sasuske']}
    response = (Q(**filter_1)) & (Q(**filter_2))

    assert final_filter == response

    #custom-properties-select-is-equal and custom-properties-text-is--empty
    expense_filters = [
        ExpenseFilter(
            condition = 'Kratos',
            operator = 'in',
            values = ['BOOK', 'Dev-D'],
            rank = 1,
            is_custom = True,
            join_by = 'AND'
        ),
        ExpenseFilter(
            condition = 'Killua Text',
            operator = 'isnull',
            values = ['True'],
            rank = 2,
            is_custom = True
        )
    ]

    final_filter = construct_expense_filter_query(expense_filters)

    filter_1 = {'custom_properties__Kratos__in':['BOOK', 'Dev-D']}
    filter_2 = {'custom_properties__Killua Text__isnull': True}
    filter_3 = {'custom_properties__Killua Text__exact': None}
    response = (Q(**filter_1)) & (Q(**filter_2) | Q(**filter_3))

    assert final_filter == response

    #custom-properties-select-is-equal
    expense_filters = [
        ExpenseFilter(
            condition = 'Kratos',
            operator = 'in',
            values = ['BOOK', 'Dev-D'],
            rank = 1,
            is_custom = True,
            join_by = 'AND'
        )
    ]

    final_filter = construct_expense_filter_query(expense_filters)

    filter_1 = {'custom_properties__Kratos__in':['BOOK', 'Dev-D']}
    response = (Q(**filter_1))

    assert final_filter == response
    #custom-properties-text-is-null
    expense_filters = [
        ExpenseFilter(
            condition = 'Killua Text',
            operator = 'isnull',
            values = ['True'],
            rank = 1,
            is_custom = True
        )
    ]

    final_filter = construct_expense_filter_query(expense_filters)

    filter_2 = {'custom_properties__Killua Text__isnull': True}
    filter_3 = {'custom_properties__Killua Text__exact': None}
    response = (Q(**filter_2) | Q(**filter_3))

    assert final_filter == response

    #employee-email-is-equal
    expense_filters = [
        ExpenseFilter(
            condition = 'employee_email',
            operator = 'in',
            values = ['killua.z@fyle.in'],
            rank = 1
        ),
        ExpenseFilter(
            condition = 'Killua Text',
            operator = 'isnull',
            values = ['True'],
            rank = 2,
            is_custom = True
        )
    ]

    final_filter = construct_expense_filter_query(expense_filters)

    filter_1 = {'employee_email__in':['killua.z@fyle.in']}
    response = Q(**filter_1)

    assert final_filter == response
