from typing import List

from django.conf import settings

from fylesdk import FyleSDK

from apps.workspaces.models import FyleCredential
from apps.fyle.models import Reimbursement, ExpenseGroupSettings


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

    def post_reimbursement(self, reimbursement_ids: list):
        """
        Process Reimbursements in bulk.
        """
        return self.connection.Reimbursements.post(reimbursement_ids)

