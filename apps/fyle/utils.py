import json
from typing import List, Dict

from django.conf import settings

from fylesdk import FyleSDK, UnauthorizedClientError, NotFoundClientError, InternalServerError, WrongParamsError

from fyle_accounting_mappings.models import ExpenseAttribute

import requests

from apps.fyle.models import Reimbursement


# To do: Add this function to Fyle accounting mappings library
def bulk_create_or_update_expense_attributes(
        attributes: List[Dict], attribute_type: str, workspace_id: int, update: bool = False):
    """
    Create Expense Attributes in bulk
    :param update: Update Pre-existing records or not
    :param attribute_type: Attribute type
    :param attributes: attributes = [{
        'attribute_type': Type of attribute,
        'display_name': Display_name of attribute_field,
        'value': Value of attribute,
        'destination_id': Destination Id of the attribute,
        'detail': Extra Details of the attribute
    }]
    :param workspace_id: Workspace Id
    :return: created / updated attributes
    """
    attribute_value_list = [attribute['value'] for attribute in attributes]

    existing_attributes = ExpenseAttribute.objects.filter(
        value__in=attribute_value_list, attribute_type=attribute_type,
        workspace_id=workspace_id).all()

    existing_attribute_values = []

    primary_key_map = {}

    for existing_attribute in existing_attributes:
        existing_attribute_values.append(existing_attribute.value)
        primary_key_map[existing_attribute.value] = existing_attribute.id

    attributes_to_be_created = []
    attributes_to_be_updated = []

    values_appended = []
    for attribute in attributes:
        if attribute['value'] not in existing_attribute_values and attribute['value'] not in values_appended:
            values_appended.append(attribute['value'])
            attributes_to_be_created.append(
                ExpenseAttribute(
                    attribute_type=attribute_type,
                    display_name=attribute['display_name'],
                    value=attribute['value'],
                    source_id=attribute['source_id'],
                    detail=attribute['detail'] if 'detail' in attribute else None,
                    workspace_id=workspace_id
                )
            )
        else:
            if update:
                attributes_to_be_updated.append(
                    ExpenseAttribute(
                        id=primary_key_map[attribute['value']],
                        detail=attribute['detail'] if 'detail' in attribute else None,
                    )
                )
    if attributes_to_be_created:
        ExpenseAttribute.objects.bulk_create(attributes_to_be_created, batch_size=50)

    if attributes_to_be_updated:
        ExpenseAttribute.objects.bulk_update(attributes_to_be_updated, fields=['detail'], batch_size=50)


class FyleConnector:
    """
    Fyle utility functions
    """

    def __init__(self, refresh_token, workspace_id=None):
        client_id = settings.FYLE_CLIENT_ID
        client_secret = settings.FYLE_CLIENT_SECRET
        base_url = settings.FYLE_BASE_URL
        self.workspace_id = workspace_id

        self.connection = FyleSDK(
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token
        )

    def _post_request(self, url, body):
        """
        Create a HTTP post request.
        """

        access_token = self.connection.access_token
        api_headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer {0}'.format(access_token)
        }

        response = requests.post(
            url,
            headers=api_headers,
            data=body
        )

        if response.status_code == 200:
            return json.loads(response.text)

        elif response.status_code == 401:
            raise UnauthorizedClientError('Wrong client secret or/and refresh token', response.text)

        elif response.status_code == 404:
            raise NotFoundClientError('Client ID doesn\'t exist', response.text)

        elif response.status_code == 400:
            raise WrongParamsError('Some of the parameters were wrong', response.text)

        elif response.status_code == 500:
            raise InternalServerError('Internal server error', response.text)

    def _get_request(self, url, params):
        """
        Create a HTTP get request.
        """

        access_token = self.connection.access_token
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

        elif response.status_code == 401:
            raise UnauthorizedClientError('Wrong client secret or/and refresh token', response.text)

        elif response.status_code == 404:
            raise NotFoundClientError('Client ID doesn\'t exist', response.text)

        elif response.status_code == 400:
            raise WrongParamsError('Some of the parameters were wrong', response.text)

        elif response.status_code == 500:
            raise InternalServerError('Internal server error', response.text)

    def get_employee_profile(self):
        """
        Get expenses from fyle
        """
        employee_profile = self.connection.Employees.get_my_profile()

        return employee_profile['data']

    def get_cluster_domain(self):
        """
        Get cluster domain name from fyle
        """

        body = {}
        api_url = '{0}/oauth/cluster/'.format(settings.FYLE_BASE_URL)

        return self._post_request(api_url, body)

    def get_fyle_orgs(self, cluser_domain):
        """
        Get fyle orgs of a user
        """

        params = {}
        api_url = '{0}/api/orgs/'.format(cluser_domain)

        return self._get_request(api_url, params)

    def get_expenses(self, state, updated_at: List[str], fund_source: List[str]):
        """
        Get expenses from fyle
        """
        expenses = self.connection.Expenses.get_all(state=state, updated_at=updated_at, fund_source=fund_source)
        expenses = list(filter(lambda expense: expense['amount'] > 0, expenses))
        expenses = list(
            filter(lambda expense: not (not expense['reimbursable'] and expense['fund_source'] == 'PERSONAL'),
                   expenses))
        return expenses

    def sync_employees(self):
        """
        Get employees from fyle
        """
        employees = self.connection.Employees.get_all()

        employee_attributes = []

        for employee in employees:
            employee_attributes.append({
                'attribute_type': 'EMPLOYEE',
                'display_name': 'Employee',
                'value': employee['employee_email'],
                'source_id': employee['id'],
                'detail': {
                    'employee_code': employee['employee_code'],
                    'full_name': employee['full_name'],
                    'location': employee['location'],
                    'department': employee['department'],
                    'department_id': employee['department_id'],
                    'department_code': employee['department_code']
                }
            })

        bulk_create_or_update_expense_attributes(employee_attributes, 'EMPLOYEE', self.workspace_id, True)

        return []

    def sync_categories(self, active_only: bool):
        """
        Get categories from fyle
        """
        categories = self.connection.Categories.get(active_only=active_only)['data']

        category_attributes = []

        for category in categories:
            if category['name'] != category['sub_category']:
                category['name'] = '{0} / {1}'.format(category['name'], category['sub_category'])

            category_attributes.append({
                'attribute_type': 'CATEGORY',
                'display_name': 'Category',
                'value': category['name'],
                'source_id': category['id']
            })

        bulk_create_or_update_expense_attributes(category_attributes, 'CATEGORY', self.workspace_id)

        return []

    def sync_expense_custom_fields(self, active_only: bool):
        """
        Get Expense Custom Fields from Fyle (Type = Select)
        """
        expense_custom_fields = self.connection.ExpensesCustomFields.get(active=active_only)['data']

        expense_custom_fields = filter(lambda field: field['type'] == 'SELECT', expense_custom_fields)

        expense_custom_field_attributes = []

        for custom_field in expense_custom_fields:
            count = 1
            for option in custom_field['options']:
                expense_custom_field_attributes.append({
                    'attribute_type': custom_field['name'].upper().replace(' ', '_'),
                    'display_name': custom_field['name'],
                    'value': option,
                    'source_id': 'expense_custom_field.{}.{}'.format(custom_field['name'].lower(), count)
                })
                count = count + 1

        expense_custom_field_attributes = ExpenseAttribute.bulk_upsert_expense_attributes(
            expense_custom_field_attributes, self.workspace_id)

        return expense_custom_field_attributes

    def sync_cost_centers(self, active_only: bool):
        """
        Get cost centers from fyle
        """
        cost_centers = self.connection.CostCenters.get(active_only=active_only)['data']

        cost_center_attributes = []

        for cost_center in cost_centers:
            cost_center_attributes.append({
                'attribute_type': 'COST_CENTER',
                'display_name': 'Cost Center',
                'value': cost_center['name'],
                'source_id': cost_center['id']
            })

        bulk_create_or_update_expense_attributes(cost_center_attributes, 'COST_CENTER', self.workspace_id)

        return []

    def sync_projects(self):
        """
        Get projects from fyle
        """
        all_projects = []
        limit = 1000
        offset = 0

        while True:
            projects = self.connection.Projects.get(limit=str(limit), offset=str(offset))['data']

            if len(projects) == 0:
                break
            else:
                all_projects.extend(projects)
                offset = offset + limit

        project_attributes = []

        for project in all_projects:
            project_attributes.append({
                'attribute_type': 'PROJECT',
                'display_name': 'Project',
                'value': project['name'],
                'source_id': project['id']
            })

        bulk_create_or_update_expense_attributes(project_attributes, 'PROJECT', self.workspace_id)

        return []

    def get_attachments(self, expense_ids: List[str]):
        """
        Get attachments against expense_ids
        """
        attachments = []
        if expense_ids:
            for expense_id in expense_ids:
                attachment_file_names = []
                attachment = self.connection.Expenses.get_attachments(expense_id)
                if attachment['data']:
                    for attachment in attachment['data']:
                        attachment_format = attachment['filename'].split('.')
                        attachment_format = attachment_format[-1]
                        if attachment_format != 'html' and attachment['filename'] not in attachment_file_names:
                            attachment['expense_id'] = expense_id
                            attachments.append(attachment)
                            attachment_file_names.append(attachment['filename'])
                        
            return attachments

        return []

    def sync_reimbursements(self):
        """
        Get reimbursements from fyle
        """
        reimbursements = self.connection.Reimbursements.get_all()

        reimbursement_attributes = []

        for reimbursement in reimbursements:
            reimbursement_attributes.append({
                'reimbursement_id': reimbursement['id'],
                'settlement_id': reimbursement['settlement_id'],
                'state': reimbursement['state']
            })

        reimbursement_attributes = Reimbursement.create_reimbursement_objects(
            reimbursement_attributes, self.workspace_id
        )

        return reimbursement_attributes

    def post_reimbursement(self, reimbursement_ids: list):
        """
        Process Reimbursements in bulk.
        """
        return self.connection.Reimbursements.post(reimbursement_ids)


