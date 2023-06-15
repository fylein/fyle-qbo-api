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
from .serializers import (ExpenseGroupSerializer, ExpenseSerializer, ExpenseFieldSerializer, 
    ExpenseGroupSettingsSerializer, ExpenseFilterSerializer)
from .actions import (get_expense_group_ids, get_expense_fields, sync_fyle_dimentions, refresh_fyle_dimension, 
                      get_custom_fields)

from apps.exceptions import handle_view_exceptions


logger = logging.getLogger(__name__)
logger.level = logging.INFO


class ExpenseGroupView(generics.ListCreateAPIView):
    """
    List Fyle Expenses
    """
    serializer_class = ExpenseGroupSerializer

    def get_queryset(self):
        state = self.request.query_params.get('state', 'ALL')
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        expense_group_ids = self.request.query_params.get('expense_group_ids', None)
        exported_at = self.request.query_params.get('exported_at', None)

        if expense_group_ids:
            return ExpenseGroup.objects.filter(
                workspace_id=self.kwargs['workspace_id'],
                id__in=expense_group_ids.split(',')
            )

        if state == 'ALL':
            return ExpenseGroup.objects.filter(workspace_id=self.kwargs['workspace_id']).order_by('-updated_at')

        if state == 'FAILED':
            return ExpenseGroup.objects.filter(tasklog__status='FAILED',
                                               workspace_id=self.kwargs['workspace_id']).order_by('-updated_at')

        elif state == 'COMPLETE':
            filters = {
                'workspace_id': self.kwargs['workspace_id'],
                'tasklog__status': 'COMPLETE'
            }

            if start_date and end_date:
                filters['exported_at__range'] = [start_date, end_date]

            if exported_at:
                filters['exported_at__gte'] = exported_at

            return ExpenseGroup.objects.filter(**filters).order_by('-exported_at')

        elif state == 'READY':
            return ExpenseGroup.objects.filter(
                workspace_id=self.kwargs['workspace_id'],
                bill__id__isnull=True,
                cheque__id__isnull=True,
                creditcardpurchase__id__isnull=True,
                journalentry__id__isnull=True,
                qboexpense__id__isnull=True
            ).order_by('-updated_at')

    def post(self, request, *args, **kwargs):
        """
        Create expense groups
        """
        task_log = TaskLog.objects.get(pk=request.data.get('task_log_id'))

        queryset = WorkspaceGeneralSettings.objects.all()
        general_settings = queryset.get(workspace_id=kwargs['workspace_id'])

        fund_source = []
        if general_settings.reimbursable_expenses_object:
            fund_source.append('PERSONAL')
        if general_settings.corporate_credit_card_expenses_object:
            fund_source.append('CCC')

        create_expense_groups(
            kwargs['workspace_id'],
            fund_source=fund_source,
            task_log=task_log,
        )
        return Response(
            status=status.HTTP_200_OK
        )


class ExportableExpenseGroupsView(generics.RetrieveAPIView):
    """
    List Exportable Expense Groups
    """
    def get(self, request, *args, **kwargs):
        expense_group_ids=get_expense_group_ids(workspace_id=self.kwargs['workspace_id'])

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

    serializer_class = ExpenseAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        return ExpenseAttribute.objects.filter(
            attribute_type='EMPLOYEE', active=True, workspace_id=self.kwargs['workspace_id']).order_by('value')


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
        sync_fyle_dimentions(workspace_id=kwargs['workspace_id'])

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

class ExpenseGetFilterView(generics.ListCreateAPIView):
    """
    Expense Filter view
    """
    queryset = ExpenseFilter.objects.all()
    serializer_class = ExpenseFilterSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('workspace_id',)


class ExpenseDeleteFilterView(generics.DestroyAPIView):
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
    filterset_fields = ('org_id', 'is_skipped', 'updated_at')


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

