import pytest
from fyle_accounting_mappings.models import (
    DestinationAttribute,
    EmployeeMapping,
    ExpenseAttribute,
)

from apps.fyle.models import Workspace


@pytest.fixture()
@pytest.mark.django_db(databases=["default"])
def add_mapping_expense_attributes():
    """
    Pytest fixture to add fyle credentials to a workspace
    """
    workspace_id = 3
    attribute = {
        "attribute_type": "CATEGORY",
        "value": "WET Paid",
        "source_id": 1212 + workspace_id,
        "display_name": "fyle12{}".format(workspace_id),
    }
    ExpenseAttribute.create_or_update_expense_attribute(attribute, workspace_id)

    workspace_id = 2
    attribute = {
        "attribute_type": "EMPLOYEE",
        "value": "ashwin.t+1@fyle.in",
        "source_id": 1212 + workspace_id,
        "display_name": "fyle12{}".format(workspace_id),
    }
    ExpenseAttribute.create_or_update_expense_attribute(attribute, workspace_id)

    attribute = {
        "attribute_type": "CATEGORY",
        "value": "ABCD",
        "destination_id": 1212 + workspace_id,
        "display_name": "fyle12{}".format(workspace_id),
    }
    DestinationAttribute.create_or_update_destination_attribute(attribute, workspace_id)


@pytest.fixture()
@pytest.mark.django_db(databases=["default"])
def create_employee_mapping():
    workspace_instance = Workspace.objects.get(id=2)
    EmployeeMapping.create_or_update_employee_mapping(7, workspace_instance)
    workspace_id = 2
    attribute = {
        "attribute_type": "EMPLOYEE",
        "value": "ashwin@fyle.in",
        "destination_id": 1212 + workspace_id,
        "display_name": "fyle12{}".format(workspace_id),
    }
    DestinationAttribute.create_or_update_destination_attribute(attribute, workspace_id)
