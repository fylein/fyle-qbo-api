from typing import List

from django.conf import settings

from fylesdk import FyleSDK

from fyle_accounting_mappings.models import ExpenseAttribute


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

    def get_employee_profile(self):
        """
        Get expenses from fyle
        """
        employee_profile = self.connection.Employees.get_my_profile()

        return employee_profile['data']

    def get_expenses(self, state: List[str], updated_at: List[str], fund_source: List[str]):
        """
        Get expenses from fyle
        """
        expenses = self.connection.Expenses.get_all(state=state, updated_at=updated_at, fund_source=fund_source)
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
                'source_id': employee['id']
            })

        employee_attributes = ExpenseAttribute.bulk_upsert_expense_attributes(employee_attributes, self.workspace_id)

        return employee_attributes

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

        category_attributes = ExpenseAttribute.bulk_upsert_expense_attributes(category_attributes, self.workspace_id)

        return category_attributes

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

        cost_center_attributes = ExpenseAttribute.bulk_upsert_expense_attributes(
            cost_center_attributes, self.workspace_id)

        return cost_center_attributes

    def sync_projects(self, active_only: bool):
        """
        Get projects from fyle
        """
        projects = self.connection.Projects.get(active_only=active_only)['data']

        project_attributes = []

        for project in projects:
            project_attributes.append({
                'attribute_type': 'PROJECT',
                'display_name': 'Project',
                'value': project['name'],
                'source_id': project['id']
            })

        project_attributes = ExpenseAttribute.bulk_upsert_expense_attributes(project_attributes, self.workspace_id)

        return project_attributes
