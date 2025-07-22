from apps.internal.actions import get_accounting_fields, get_exported_entry
from tests.test_quickbooks_online.fixtures import data


def test_get_accounting_fields(db, mocker):
    query_params = {
        'org_id': 'or79Cob97KSh',
        'resource_type': 'employees',
    }
    mocker.patch(
        'qbosdk.apis.Employees.get_all_generator',
        return_value=[data['employee_response']]
    )

    fields = get_accounting_fields(query_params)
    assert fields is not None


def test_get_exported_entry(db, mocker):
    query_params = {
        'org_id': 'or79Cob97KSh',
        'resource_type': 'bills',
        'internal_id': '1'
    }
    mocker.patch(
        'qbosdk.apis.Bills.get_by_id',
        return_value={'summa': 'hehe'}
    )

    entry = get_exported_entry(query_params)
    assert entry is not None
