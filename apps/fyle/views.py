import logging

from apps.fyle.helpers import ExpenseGroupSearchFilter, ExpenseSearchFilter

from apps.workspaces.models import FyleCredential, Workspace
from django_filters.rest_framework import DjangoFilterBackend
from django_q.tasks import async_task
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status
from fyle_accounting_library.fyle_platform.enums import ExpenseImportSourceEnum

from apps.exceptions import handle_view_exceptions
from apps.fyle.actions import (
    get_custom_fields,
    get_expense_fields,
    get_expense_group_ids,
)
from apps.fyle.models import Expense, ExpenseFilter, ExpenseGroup, ExpenseGroupSettings
from apps.fyle.queue import async_import_and_export_expenses
from apps.fyle.serializers import (
    ExpenseFieldSerializer,
    ExpenseFilterSerializer,
    ExpenseGroupSerializer,
    ExpenseGroupSettingsSerializer,
    ExpenseSerializer,
)
from apps.fyle.tasks import create_expense_groups, get_task_log_and_fund_source
from fyle_qbo_api.utils import LookupFieldMixin

logger = logging.getLogger(__name__)
logger.level = logging.INFO


class ExpenseGroupView(LookupFieldMixin, generics.ListCreateAPIView):
    """
    List Fyle Expenses
    """

    queryset = ExpenseGroup.objects.all().order_by("-exported_at").distinct()
    serializer_class = ExpenseGroupSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ExpenseGroupSearchFilter


class ExportableExpenseGroupsView(generics.RetrieveAPIView):
    """
    List Exportable Expense Groups
    """

    def get(self, request, *args, **kwargs):
        expense_group_ids = get_expense_group_ids(workspace_id=self.kwargs['workspace_id'])

        return Response(data={'exportable_expense_group_ids': expense_group_ids}, status=status.HTTP_200_OK)


class ExpenseGroupSyncView(generics.CreateAPIView):
    """
    Create expense groups
    """

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        """
        Post expense groups creation
        """

        task_log, fund_source = get_task_log_and_fund_source(kwargs['workspace_id'])

        create_expense_groups(workspace_id=kwargs['workspace_id'], fund_source=fund_source, task_log=task_log, imported_from=ExpenseImportSourceEnum.DASHBOARD_SYNC)

        return Response(status=status.HTTP_200_OK)


class ExpenseGroupSettingsView(generics.ListCreateAPIView):
    """
    Expense Group Settings View
    """

    serializer_class = ExpenseGroupSettingsSerializer

    def get(self, request, *args, **kwargs):
        expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=self.kwargs['workspace_id'])
        return Response(data=self.serializer_class(expense_group_settings).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        expense_group_settings, _ = ExpenseGroupSettings.update_expense_group_settings(request.data, self.kwargs['workspace_id'], request.user)
        return Response(data=self.serializer_class(expense_group_settings).data, status=status.HTTP_200_OK)


class ExpenseFieldsView(generics.ListAPIView):
    pagination_class = None
    serializer_class = ExpenseFieldSerializer

    def get(self, request, *args, **kwargs):
        expense_fields = get_expense_fields(workspace_id=self.kwargs['workspace_id'])

        return Response(expense_fields, status=status.HTTP_200_OK)


class ExportView(generics.CreateAPIView):
    """
    Export View
    """
    authentication_classes = []
    permission_classes = []

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        async_import_and_export_expenses(request.data, int(kwargs['workspace_id']))

        return Response(data={}, status=status.HTTP_200_OK)


class SyncFyleDimensionView(generics.ListCreateAPIView):
    """
    Sync Fyle Dimensions View
    """

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        """
        Sync Data From Fyle
        """

        # Check for a valid workspace and fyle creds and respond with 400 if not found
        Workspace.objects.get(id=kwargs['workspace_id'])
        FyleCredential.objects.get(workspace_id=kwargs['workspace_id'])

        async_task('apps.fyle.actions.sync_fyle_dimensions', kwargs['workspace_id'])

        return Response(status=status.HTTP_200_OK)


class RefreshFyleDimensionView(generics.ListCreateAPIView):
    """
    Refresh Fyle Dimensions view
    """

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        """
        Sync data from Fyle
        """

        # Check for a valid workspace and fyle creds and respond with 400 if not found
        Workspace.objects.get(id=kwargs['workspace_id'])
        FyleCredential.objects.get(workspace_id=kwargs['workspace_id'])

        async_task('apps.fyle.actions.refresh_fyle_dimension', kwargs['workspace_id'])

        return Response(status=status.HTTP_200_OK)


class ExpenseFilterView(LookupFieldMixin, generics.ListCreateAPIView):
    """
    Expense Filter view
    """

    queryset = ExpenseFilter.objects.all()
    serializer_class = ExpenseFilterSerializer


class ExpenseFilterDeleteView(generics.DestroyAPIView):
    """
    Expense Filter view
    """

    queryset = ExpenseFilter.objects.all()
    serializer_class = ExpenseFilterSerializer


class ExpenseView(LookupFieldMixin, generics.ListAPIView):
    """
    Expense view
    """

    queryset = Expense.objects.all().order_by("-updated_at").distinct()
    serializer_class = ExpenseSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ExpenseSearchFilter


class CustomFieldView(generics.RetrieveAPIView):
    """
    Custom Field view
    """

    def get(self, request, *args, **kwargs):
        """
        Get Custom Fields
        """
        response = get_custom_fields(workspace_id=self.kwargs['workspace_id'])
        return Response(data=response, status=status.HTTP_200_OK)
