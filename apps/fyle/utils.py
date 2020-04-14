from typing import List

from django.conf import settings

from fylesdk import FyleSDK


class FyleConnector:
    """
    Fyle utility functions
    """
    def __init__(self, refresh_token):
        client_id = settings.FYLE_CLIENT_ID
        client_secret = settings.FYLE_CLIENT_SECRET
        base_url = settings.FYLE_BASE_URL

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

    def get_employees(self):
        """
        Get employees from fyle
        """
        return self.connection.Employees.get_all()

    def get_categories(self, active_only: bool):
        """
        Get categories from fyle
        """
        return self.connection.Categories.get(active_only=active_only)['data']

    def get_cost_centers(self, active_only: bool):
        """
        Get cost centers from fyle
        """
        return self.connection.CostCenters.get(active_only=active_only)['data']

    def get_projects(self, active_only: bool):
        """
        Get projects from fyle
        """
        return self.connection.Projects.get(active_only=active_only)['data']
