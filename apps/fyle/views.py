import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from apps.exceptions import handle_view_exceptions
from fyle_accounting_mappings.models import ExpenseAttribute
from fyle_accounting_mappings.serializers import ExpenseAttributeSerializer
from fyle_qbo_api.utils import LookupFieldMixin

from .actions import (
    get_custom_fields,
    get_expense_fields,
    get_expense_group_ids,
    refresh_fyle_dimension,
    sync_fyle_dimensions,
)
from .models import Expense, ExpenseFilter, ExpenseGroup, ExpenseGroupSettings
from .serializers import (
    ExpenseFieldSerializer,
    ExpenseFilterSerializer,
    ExpenseGroupSerializer,
    ExpenseGroupSettingsSerializer,
    ExpenseSerializer,
)
from .tasks import async_create_expense_groups, get_task_log_and_fund_source

logger = logging.getLogger(__name__)
logger.level = logging.INFO


class ExpenseGroupView(LookupFieldMixin, generics.ListCreateAPIView):
    """
    List Fyle Expenses
    """

    queryset = ExpenseGroup.objects.all().order_by("-exported_at")
    serializer_class = ExpenseGroupSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = {"exported_at": {"gte", "lte"}, "tasklog__status": {"exact"}}


class ExportableExpenseGroupsView(generics.RetrieveAPIView):
    """
    List Exportable Expense Groups
    """

    def get(self, request, *args, **kwargs):
        expense_group_ids = get_expense_group_ids(
            workspace_id=self.kwargs['workspace_id']
        )

        return Response(
            data={'exportable_expense_group_ids': expense_group_ids},
            status=status.HTTP_200_OK,
        )


class ExpenseGroupSyncView(generics.CreateAPIView):
    """
    Create expense groups
    """

    def post(self, request, *args, **kwargs):
        """
        Post expense groups creation
        """

        task_log, fund_source = get_task_log_and_fund_source(kwargs['workspace_id'])

        async_create_expense_groups(kwargs['workspace_id'], fund_source, task_log)

        return Response(status=status.HTTP_200_OK)


class ExpenseGroupSettingsView(generics.ListCreateAPIView):
    """
    Expense Group Settings View
    """

    serializer_class = ExpenseGroupSettingsSerializer

    def get(self, request, *args, **kwargs):
        expense_group_settings = ExpenseGroupSettings.objects.get(
            workspace_id=self.kwargs['workspace_id']
        )
        return Response(
            data=self.serializer_class(expense_group_settings).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        expense_group_settings, _ = ExpenseGroupSettings.update_expense_group_settings(
            request.data, self.kwargs['workspace_id']
        )
        return Response(
            data=self.serializer_class(expense_group_settings).data,
            status=status.HTTP_200_OK,
        )


class ExpenseFieldsView(generics.ListAPIView):
    pagination_class = None
    serializer_class = ExpenseFieldSerializer

    def get(self, request, *args, **kwargs):
        expense_fields = get_expense_fields(workspace_id=self.kwargs['workspace_id'])

        return Response(expense_fields, status=status.HTTP_200_OK)


class SyncFyleDimensionView(generics.ListCreateAPIView):
    """
    Sync Fyle Dimensions View
    """

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        """
        Sync Data From Fyle
        """
        sync_fyle_dimensions(workspace_id=kwargs['workspace_id'])

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

        refresh_fyle_dimension(workspace_id=kwargs['workspace_id'])

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


class ExpenseView(generics.ListAPIView):
    """
    Expense view
    """

    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = {
        'org_id': {'exact'},
        'is_skipped': {'exact'},
        'updated_at': {'gte', 'lte'},
    }
    ordering_fields = ('-updated_at',)


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
