from fyle_accounting_mappings.models import (
    DestinationAttribute, 
    ExpenseAttribute,
    Mapping,
)
from apps.quickbooks_online.utils import QBOConnector
from apps.workspaces.models import QBOCredential
from fyle_integrations_imports.modules import Project
from tests.test_fyle_integrations_imports.test_modules.fixtures import projects_data

def test_sync_destination_attributes(mocker, db):
    workspace_id = 3

    mocker.patch('qbosdk.apis.Customers.count', return_value=5)
    mocker.patch('qbosdk.apis.Customers.get', return_value=projects_data['get_projects_destination_attributes_customers'])

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)
    
    destination_attributes_count = DestinationAttribute.objects.filter(workspace_id=3, attribute_type='CUSTOMER').count()
    assert destination_attributes_count == 29

    project = Project(3, 'CUSTOMER', None,  qbo_connection, 'customers', True)
    project.sync_destination_attributes()

    destination_attributes_count = DestinationAttribute.objects.filter(workspace_id=3, attribute_type='CUSTOMER').count()
    assert destination_attributes_count == 30
