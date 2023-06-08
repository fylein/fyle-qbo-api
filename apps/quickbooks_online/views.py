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

from apps.workspaces.models import QBOCredential, Workspace
from apps.workspaces.serializers import QBOCredentialSerializer

from .utils import QBOConnector
from .tasks import create_bill_payment
from apps.exceptions import handle_view_exceptions


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

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        """
        Get employees from QBO
        """
        qbo_credentials = QBOCredential.get_active_qbo_credentials(kwargs['workspace_id'])

        qbo_connector = QBOConnector(qbo_credentials, workspace_id=kwargs['workspace_id'])

        employees = qbo_connector.sync_employees()

        return Response(
            data=self.serializer_class(employees, many=True).data,
            status=status.HTTP_200_OK
        )


class PreferencesView(generics.RetrieveAPIView):
    """
    Preferences View
    """

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

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
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


class RefreshQuickbooksDimensionView(generics.ListCreateAPIView):
    """
    Refresh Quickbooks Dimensions view
    """

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        """
        Sync data from quickbooks
        """
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
