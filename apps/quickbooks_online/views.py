import logging
from django.db.models import Q
from datetime import datetime, timezone
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework import generics

from qbosdk.exceptions import WrongParamsError, InvalidTokenError

from django_q.tasks import Chain

from fyle_accounting_mappings.models import DestinationAttribute, MappingSetting
from fyle_accounting_mappings.serializers import DestinationAttributeSerializer

from fyle_qbo_api.utils import assert_valid

from apps.fyle.models import ExpenseGroup, ExpenseGroupSettings
from apps.tasks.models import TaskLog
from apps.workspaces.models import QBOCredential, WorkspaceGeneralSettings, Workspace
from apps.workspaces.serializers import QBOCredentialSerializer
from apps.fyle.serializers import ExpenseGroupSettingsSerializer

from .utils import QBOConnector
from .tasks import create_bill, schedule_bills_creation, create_cheque, schedule_cheques_creation, \
    create_credit_card_purchase, schedule_credit_card_purchase_creation, create_journal_entry, \
    schedule_journal_entry_creation, create_bill_payment, process_reimbursements, check_qbo_object_status,\
    schedule_qbo_expense_creation
from .models import Bill, Cheque, CreditCardPurchase, JournalEntry
from .serializers import BillSerializer, ChequeSerializer, CreditCardPurchaseSerializer, JournalEntrySerializer, \
    QuickbooksFieldSerializer

logger = logging.getLogger(__name__)
logger.level = logging.INFO

class VendorView(generics.ListCreateAPIView):
    """
    Vendor view
    """
    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        search_term = self.request.query_params.get('search_term')
        if search_term:
            return DestinationAttribute.objects.filter(
                attribute_type='VENDOR', active=True, workspace_id=self.kwargs['workspace_id'],value__icontains=search_term).order_by('value')[:10]
        return DestinationAttribute.objects.filter(
            attribute_type='VENDOR', active=True, workspace_id=self.kwargs['workspace_id']).order_by('value')[:10]

    def post(self, request, *args, **kwargs):
        """
        Get vendors from QBO
        """
        try:
            qbo_credentials = QBOCredential.get_active_qbo_credentials(kwargs['workspace_id'])

            qbo_connector = QBOConnector(qbo_credentials, workspace_id=kwargs['workspace_id'])

            vendors = qbo_connector.sync_vendors()

            return Response(
                data=self.serializer_class(vendors, many=True).data,
                status=status.HTTP_200_OK
            )
        except QBOCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'QBO credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class EmployeeView(generics.ListCreateAPIView):
    """
    Employee view
    """
    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        search_term = self.request.query_params.get('search_term')
        if search_term:
            return DestinationAttribute.objects.filter(
                attribute_type='EMPLOYEE', active=True, workspace_id=self.kwargs['workspace_id'],value__icontains=search_term).order_by('value')[:10]
        return DestinationAttribute.objects.filter(
            attribute_type='EMPLOYEE', active=True, workspace_id=self.kwargs['workspace_id']).order_by('value')[:10]

    def post(self, request, *args, **kwargs):
        """
        Get employees from QBO
        """
        try:
            qbo_credentials = QBOCredential.get_active_qbo_credentials(kwargs['workspace_id'])

            qbo_connector = QBOConnector(qbo_credentials, workspace_id=kwargs['workspace_id'])

            employees = qbo_connector.sync_employees()

            return Response(
                data=self.serializer_class(employees, many=True).data,
                status=status.HTTP_200_OK
            )
        except QBOCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'QBO credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class PreferencesView(generics.RetrieveAPIView):
    """
    Preferences View
    """
    def post(self, request, **kwargs):
        try:
            qbo_credentials = QBOCredential.get_active_qbo_credentials(kwargs['workspace_id'])
            qbo_connector = QBOConnector(qbo_credentials, workspace_id=kwargs['workspace_id'])

            company_info = qbo_connector.get_company_info()
            qbo_credentials.country = company_info['Country']
            qbo_credentials.company_name = company_info['CompanyName']
            qbo_credentials.is_expired = False
            qbo_credentials.save()

            return Response(
                data=QBOCredentialSerializer(qbo_credentials).data,
                status=status.HTTP_200_OK
            )

        except (WrongParamsError, InvalidTokenError) as exception:
            logger.info('QBO token expired workspace_id - %s %s', kwargs['workspace_id'], {'error': exception.response})
            return Response(
                data={
                    'message': 'QBO token expired workspace_id'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    def get(self, request, *args, **kwargs):
        try:
            qbo_credentials = QBOCredential.get_active_qbo_credentials(kwargs['workspace_id'])

            qbo_connector = QBOConnector(qbo_credentials, workspace_id=kwargs['workspace_id'])

            preferences = qbo_connector.get_company_preference()

            return Response(
                data=preferences,
                status=status.HTTP_200_OK
            )
        except QBOCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'QBO credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except WrongParamsError:
            if qbo_credentials:
                qbo_credentials.refresh_token = None
                qbo_credentials.is_expired = True
                qbo_credentials.save()
            return Response(
                data={
                    'message': 'Quickbooks Online connection expired'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except InvalidTokenError:
            if qbo_credentials:
                qbo_credentials.refresh_token = None
                qbo_credentials.is_expired = True
                qbo_credentials.save()
            return Response(
                data={
                    'message': 'Invalid token, try to refresh it'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class BillPaymentView(generics.CreateAPIView):
    """
    Create Bill Payment View
    """
    def post(self, request, *args, **kwargs):
        """
        Create bill payment
        """
        create_bill_payment(workspace_id=self.kwargs['workspace_id'])

        return Response(
            data={},
            status=status.HTTP_200_OK
        )


class SyncQuickbooksDimensionView(generics.ListCreateAPIView):
    """
    Sync Quickbooks Dimension View
    """

    def post(self, request, *args, **kwargs):

        try:
            workspace = Workspace.objects.get(id=kwargs['workspace_id'])
            if workspace.destination_synced_at:
                time_interval = datetime.now(timezone.utc) - workspace.destination_synced_at

            if workspace.destination_synced_at is None or time_interval.days > 0:
                quickbooks_credentials = QBOCredential.get_active_qbo_credentials(kwargs['workspace_id'])
                quickbooks_connector = QBOConnector(quickbooks_credentials, workspace_id=kwargs['workspace_id'])
                quickbooks_connector.sync_dimensions()

                workspace.destination_synced_at = datetime.now()
                workspace.save(update_fields=['destination_synced_at'])

            return Response(
                status=status.HTTP_200_OK
            )

        except (QBOCredential.DoesNotExist, InvalidTokenError):
            return Response(
                data={
                    'message': 'Quickbooks Credentials not found / expired in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except WrongParamsError as exception:
            logger.info('QBO token expired workspace_id - %s %s', workspace.id, {'error': exception.response})
            return Response(
                data={
                    'message': 'Error in syncing Dimensions'
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


class RefreshQuickbooksDimensionView(generics.ListCreateAPIView):
    """
    Refresh Quickbooks Dimensions view
    """

    def post(self, request, *args, **kwargs):
        """
        Sync data from quickbooks
        """
        try:
            quickbooks_credentials = QBOCredential.get_active_qbo_credentials(kwargs['workspace_id'])
            quickbooks_connector = QBOConnector(quickbooks_credentials, workspace_id=kwargs['workspace_id'])

            mapping_settings = MappingSetting.objects.filter(workspace_id=kwargs['workspace_id'], import_to_fyle=True)
            chain = Chain()

            for mapping_setting in mapping_settings:
                if mapping_setting.source_field == 'PROJECT':
                    chain.append('apps.mappings.tasks.auto_import_and_map_fyle_fields', int(kwargs['workspace_id']))
                elif mapping_setting.source_field == 'COST_CENTER':
                    chain.append('apps.mappings.tasks.auto_create_cost_center_mappings', int(kwargs['workspace_id']))
                elif mapping_setting.is_custom:
                    chain.append('apps.mappings.tasks.async_auto_create_custom_field_mappings',
                                int(kwargs['workspace_id']))

            if chain.length() > 0:
                chain.run()

            quickbooks_connector.sync_dimensions()

            workspace = Workspace.objects.get(id=kwargs['workspace_id'])
            workspace.destination_synced_at = datetime.now()
            workspace.save(update_fields=['destination_synced_at'])

            return Response(
                status=status.HTTP_200_OK
            )

        except (QBOCredential.DoesNotExist, InvalidTokenError):
            return Response(
                data={
                    'message': 'Quickbooks Credentials not found / expired in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except WrongParamsError as exception:
            logger.info('QBO token expired workspace_id - %s %s', workspace.id, {'error': exception.response})
            return Response(
                data={
                    'message': 'Error in refreshing Dimensions'
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


class DestinationAttributesView(generics.ListAPIView):
    """
    Destination Attributes view
    """
    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        attribute_types = self.request.query_params.get('attribute_types').split(',')
        display_name = self.request.query_params.get('display_name')

        filters = {
            'attribute_type__in' : attribute_types,
            'workspace_id': self.kwargs['workspace_id'],
            'active': True
        }

        if display_name:
            display_name = display_name.split(',')
            filters['display_name__in'] = display_name

        return DestinationAttribute.objects.filter(**filters).order_by('value')

class SearchedDestinationAttributesView(generics.ListAPIView):
    """
    Destination Attributes view
    """
    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        attribute_type = self.request.query_params.get('attribute_type').split(',')
        active = self.request.query_params.get('active')
        search_term = self.request.query_params.get('search_term')
        display_name = self.request.query_params.get('display_name')

        filters = {
            'attribute_type__in' : attribute_type,
            'workspace_id': self.kwargs['workspace_id'],
            'active': True
        }

        if display_name:
            display_name = display_name.split(',')
            filters['display_name__in'] = display_name

        if search_term:
            filters['value__icontains'] = search_term

        if active and active.lower() == 'true':
            filters['active'] = True

        return DestinationAttribute.objects.filter(**filters).order_by('value')[:30]



class QBOAttributesView(generics.ListCreateAPIView):
    """
    GET Paginated QBO Attributes view
    """
    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        attribute_types = self.request.query_params.get('attribute_types').split(',')

        return DestinationAttribute.objects.filter(
            attribute_type__in=attribute_types, workspace_id=self.kwargs['workspace_id']).distinct('attribute_type')
