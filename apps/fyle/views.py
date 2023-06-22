import logging

from rest_framework.views import status
from rest_framework import generics
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from fyle_accounting_mappings.models import ExpenseAttribute
from fyle_accounting_mappings.serializers import ExpenseAttributeSerializer

from apps.workspaces.models import WorkspaceGeneralSettings
from apps.tasks.models import TaskLog

from .tasks import create_expense_groups, get_task_log_and_fund_source, async_create_expense_groups
from .models import Expense, ExpenseGroup, ExpenseGroupSettings, ExpenseFilter
from .serializers import (
                ExpenseGroupSerializer, ExpenseSerializer, ExpenseFieldSerializer, 
                ExpenseGroupSettingsSerializer, ExpenseFilterSerializer
                )
from .actions import (
                get_expense_group_ids, get_expense_fields, sync_fyle_dimensions, 
                refresh_fyle_dimension, get_custom_fields, get_fyle_expenses_list,
                create_expense_groups_view
                )

from apps.exceptions import handle_view_exceptions


logger = logging.getLogger(__name__)
logger.level = logging.INFO


class ExpenseGroupView(generics.ListCreateAPIView):
    """
    List Fyle Expenses
    """
    serializer_class = ExpenseGroupSerializer

    def get_queryset(self):
        return get_fyle_expenses_list(state = self.request.query_params.get('state', 'ALL'),
                                      start_date = self.request.query_params.get('start_date', None),
                                      end_date = self.request.query_params.get('end_date', None),
                                      expense_group_ids = self.request.query_params.get('expense_group_ids', None),
                                      exported_at = self.request.query_params.get('exported_at', None),
                                      workspace_id = self.kwargs['workspace_id'])
        

    def post(self, request, *args, **kwargs):
        """
        Create expense groups
        """
        create_expense_groups_view(
            task_log_id = request.data.get('task_log_id'),
            workspace_id = kwargs['workspace_id']
        )
        return Response(
            status=status.HTTP_200_OK
        )


class ExportableExpenseGroupsView(generics.RetrieveAPIView):
    """
    List Exportable Expense Groups
    """
    def get(self, request, *args, **kwargs):
        expense_group_ids = get_expense_group_ids(workspace_id=self.kwargs['workspace_id'])

        return Response(
            data={'exportable_expense_group_ids': expense_group_ids},
            status=status.HTTP_200_OK
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

        return Response(
            status=status.HTTP_200_OK
        )


class ExpenseGroupSettingsView(generics.ListCreateAPIView):
    """
    Expense Group Settings View
    """
    serializer_class = ExpenseGroupSettingsSerializer

    def get(self, request, *args, **kwargs):
        expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=self.kwargs['workspace_id'])
        return Response(
            data=self.serializer_class(expense_group_settings).data,
            status=status.HTTP_200_OK
        )

    def post(self, request, *args, **kwargs):
        expense_group_settings, _ = ExpenseGroupSettings.update_expense_group_settings(
            request.data, self.kwargs['workspace_id'])
        return Response(
            data=self.serializer_class(expense_group_settings).data,
            status=status.HTTP_200_OK
        )


class EmployeeView(generics.ListCreateAPIView):
    """
    Employee view
    """
    queryset = ExpenseAttribute.objects.all()
    serializer_class = ExpenseAttributeSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = {'attribute_type': {'exact', 'in'}, 'workspace_id': {'exact'}, 'active': {'exact'}}
    ordering_fields = ('value',)


class ExpenseFieldsView(generics.ListAPIView):
    pagination_class = None
    serializer_class = ExpenseFieldSerializer

    def get(self, request, *args, **kwargs):
        expense_fields=get_expense_fields(workspace_id=self.kwargs['workspace_id'])

        return Response(
            expense_fields,
            status=status.HTTP_200_OK
        )


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

        return Response(
            status=status.HTTP_200_OK
        )


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

        return Response(
            status=status.HTTP_200_OK
        )

class ExpenseFilterView(generics.ListCreateAPIView, generics.DestroyAPIView):
    """
    Expense Filter view
    """
    lookup_field = 'workspace_id'
    queryset = ExpenseFilter.objects.all()
    serializer_class = ExpenseFilterSerializer



class ExpenseView(generics.ListAPIView):
    """
    Expense view
    """
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = {'org_id':{'exact'}, 'is_skipped':{'exact'}, 'updated_at':{'gte', 'lte'}}


class CustomFieldView(generics.RetrieveAPIView):
    """
    Custom Field view
    """
    def get(self, request, *args, **kwargs):
        """
        Get Custom Fields
        """
        response=get_custom_fields(workspace_id=self.kwargs['workspace_id'])
            
        return Response(
            data=response,
            status=status.HTTP_200_OK
        )

