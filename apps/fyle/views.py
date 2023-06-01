import logging

from django.db.models import Q
from datetime import datetime, timezone

from rest_framework.views import status
from rest_framework import generics
from rest_framework.response import Response

from fyle_accounting_mappings.models import ExpenseAttribute
from fyle_accounting_mappings.serializers import ExpenseAttributeSerializer

from fyle_integrations_platform_connector import PlatformConnector

from apps.workspaces.models import FyleCredential, WorkspaceGeneralSettings, Workspace
from apps.tasks.models import TaskLog

from .tasks import create_expense_groups, get_task_log_and_fund_source, \
    async_create_expense_groups
from .models import Expense, ExpenseGroup, ExpenseGroupSettings, ExpenseFilter
from .serializers import ExpenseGroupSerializer, ExpenseSerializer, ExpenseFieldSerializer, \
    ExpenseGroupSettingsSerializer, ExpenseFilterSerializer, ExpenseGroupExpenseSerializer

from .constants import DEFAULT_FYLE_CONDITIONS

from fyle.platform import Platform
from fyle_qbo_api import settings

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
        configuration = WorkspaceGeneralSettings.objects.get(workspace_id=kwargs['workspace_id'])
        fund_source = []

        if configuration.reimbursable_expenses_object:
            fund_source.append('PERSONAL')
        if configuration.corporate_credit_card_expenses_object:
            fund_source.append('CCC')

        expense_group_ids = ExpenseGroup.objects.filter(
            workspace_id=self.kwargs['workspace_id'],
            exported_at__isnull=True,
            fund_source__in=fund_source
        ).values_list('id', flat=True)

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
        default_attributes = ['EMPLOYEE', 'CATEGORY', 'PROJECT', 'COST_CENTER', 'TAX_GROUP', 'CORPORATE_CARD', 'MERCHANT']

        attributes = ExpenseAttribute.objects.filter(
            ~Q(attribute_type__in=default_attributes),
            workspace_id=self.kwargs['workspace_id']
        ).values('attribute_type', 'display_name').distinct()

        expense_fields = [
            {'attribute_type': 'COST_CENTER', 'display_name': 'Cost Center'},
            {'attribute_type': 'PROJECT', 'display_name': 'Project'}
        ]

        for attribute in attributes:
            expense_fields.append(attribute)

        return Response(
            expense_fields,
            status=status.HTTP_200_OK
        )


class SyncFyleDimensionView(generics.ListCreateAPIView):
    """
    Sync Fyle Dimensions View
    """

    def post(self, request, *args, **kwargs):
        """
        Sync Data From Fyle
        """
        try:
            workspace = Workspace.objects.get(id=kwargs['workspace_id'])
            if workspace.source_synced_at:
                time_interval = datetime.now(timezone.utc) - workspace.source_synced_at

            if workspace.source_synced_at is None or time_interval.days > 0:
                fyle_credentials = FyleCredential.objects.get(workspace_id=kwargs['workspace_id'])
                platform = PlatformConnector(fyle_credentials)

                platform.import_fyle_dimensions(import_taxes=True)

                workspace.source_synced_at = datetime.now()
                workspace.save(update_fields=['source_synced_at'])

            return Response(
                status=status.HTTP_200_OK
            )

        except FyleCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'Fyle credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as exception:
            logger.exception(exception)
            return Response(
                data={
                    'message': 'Error in syncing Dimensions'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class RefreshFyleDimensionView(generics.ListCreateAPIView):
    """
    Refresh Fyle Dimensions view
    """

    def post(self, request, *args, **kwargs):
        """
        Sync data from Fyle
        """
        try:
            fyle_credentials = FyleCredential.objects.get(workspace_id=kwargs['workspace_id'])
            platform = PlatformConnector(fyle_credentials)

            platform.import_fyle_dimensions(import_taxes=True)

            workspace = Workspace.objects.get(id=kwargs['workspace_id'])
            workspace.source_synced_at = datetime.now()
            workspace.save(update_fields=['source_synced_at'])

            return Response(
                status=status.HTTP_200_OK
            )

        except FyleCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'Fyle credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as exception:
            logger.exception(exception)
            return Response(
                data={
                    'message': 'Error in refreshing Dimensions'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

class ExpenseFilterView(generics.ListCreateAPIView, generics.DestroyAPIView):
    """
    Expense Filter view
    """
    serializer_class = ExpenseFilterSerializer

    def get_queryset(self):
        queryset = ExpenseFilter.objects.filter(workspace_id=self.kwargs['workspace_id']).order_by('rank')
        return queryset

    def delete(self, request, *args, **kwargs):
        workspace_id = self.kwargs['workspace_id']
        rank = self.request.query_params.getlist('rank')
        ExpenseFilter.objects.filter(workspace_id=workspace_id, rank__in=rank).delete()

        return Response(data={
            'workspace_id': workspace_id,
            'rank' : rank,
            'message': 'Expense filter deleted'
        })


class ExpenseView(generics.ListAPIView):
    """
    Expense view
    """

    serializer_class = ExpenseSerializer

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        filters = {
            'org_id': Workspace.objects.get(id=self.kwargs['workspace_id']).fyle_org_id
        }
        is_skipped = self.request.query_params.get('is_skipped')
        if is_skipped == 'true':
            filters['is_skipped'] = True
        if start_date and end_date:
            filters['updated_at__range'] = [start_date, end_date]
        queryset = Expense.objects.filter(**filters).order_by('-updated_at')
        return queryset


class CustomFieldView(generics.RetrieveAPIView):
    """
    Custom Field view
    """
    def get(self, request, *args, **kwargs):
        """
        Get Custom Fields
        """
        workspace_id = self.kwargs['workspace_id']

        fyle_credentails = FyleCredential.objects.get(workspace_id=workspace_id)

        platform = PlatformConnector(fyle_credentails)

        custom_fields = platform.expense_custom_fields.list_all()

        response = []
        response.extend(DEFAULT_FYLE_CONDITIONS)
        for custom_field in custom_fields:
            if custom_field['type'] in ('SELECT', 'NUMBER', 'TEXT'):
                response.append({
                    'field_name': custom_field['field_name'],
                    'type': custom_field['type'],
                    'is_custom': custom_field['is_custom']
                })
            
        return Response(
            data=response,
            status=status.HTTP_200_OK
        )

