import logging

from django.db.models import Q
from apps.workspaces.models import QBOCredential, Workspace
from django_filters.rest_framework import DjangoFilterBackend
from django_q.tasks import async_task
from fyle_accounting_mappings.models import DestinationAttribute
from fyle_accounting_mappings.serializers import DestinationAttributeSerializer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from apps.exceptions import handle_view_exceptions
from fyle_qbo_api.utils import LookupFieldMixin

from .serializers import QuickbooksFieldSerializer

logger = logging.getLogger(__name__)
logger.level = logging.INFO


class VendorView(LookupFieldMixin, generics.ListAPIView):
    """
    Vendor view
    """

    queryset = DestinationAttribute.objects.all()
    serializer_class = DestinationAttributeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = {'value': {'icontains'}, 'attribute_type': {'exact', 'in'}, 'active': {'exact'}}
    ordering_fields = ('value',)


class QBOFieldView(LookupFieldMixin, generics.ListAPIView):
    """
    QBOField view
    """
    queryset = DestinationAttribute.objects.filter(
        ~Q(attribute_type='EMPLOYEE') & ~Q(attribute_type='VENDOR') &
        ~Q(attribute_type='ACCOUNTS_PAYABLE') & ~Q(attribute_type='ACCOUNT') &
        ~Q(attribute_type='TAX_CODE') & ~Q(attribute_type='BANK_ACCOUNT') &
        ~Q(attribute_type='CREDIT_CARD_ACCOUNT')
    ).values('attribute_type', 'display_name').distinct()
    serializer_class = QuickbooksFieldSerializer
    filter_backends = (DjangoFilterBackend,)
    pagination_class = None


class EmployeeView(LookupFieldMixin, generics.ListAPIView):
    """
    Employee view
    """

    queryset = DestinationAttribute.objects.all()
    serializer_class = DestinationAttributeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = {'value': {'icontains'}, 'attribute_type': {'exact', 'in'}, 'active': {'exact'}}
    ordering_fields = ('value',)


class SyncQuickbooksDimensionView(generics.ListCreateAPIView):
    """
    Sync Quickbooks Dimension View
    """

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):

        # Check for a valid workspace and qbo creds and respond with 400 if not found
        Workspace.objects.get(id=kwargs['workspace_id'])
        QBOCredential.get_active_qbo_credentials(kwargs['workspace_id'])

        async_task('apps.quickbooks_online.actions.sync_quickbooks_dimensions', kwargs['workspace_id'])

        return Response(status=status.HTTP_200_OK)


class RefreshQuickbooksDimensionView(generics.ListCreateAPIView):
    """
    Refresh Quickbooks Dimensions view
    """

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        """
        Sync data from quickbooks
        """

        # Check for a valid workspace and qbo creds and respond with 400 if not found
        Workspace.objects.get(id=kwargs['workspace_id'])
        QBOCredential.get_active_qbo_credentials(kwargs['workspace_id'])

        async_task('apps.quickbooks_online.actions.refresh_quickbooks_dimensions', kwargs['workspace_id'])

        return Response(status=status.HTTP_200_OK)


class DestinationAttributesView(LookupFieldMixin, generics.ListAPIView):
    """
    Destination Attributes view
    """

    queryset = DestinationAttribute.objects.all()
    serializer_class = DestinationAttributeSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = {'attribute_type': {'exact', 'in'}, 'display_name': {'exact', 'in'}, 'active': {'exact'}}
    ordering_fields = ('value',)


class SearchedDestinationAttributesView(LookupFieldMixin, generics.ListAPIView):
    """
    Destination Attributes view
    """

    queryset = DestinationAttribute.objects.all()
    serializer_class = DestinationAttributeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = {'value': {'icontains'}, 'attribute_type': {'exact', 'in'}, 'display_name': {'exact', 'in'}, 'active': {'exact'}}
    ordering_fields = ('value',)


class QBOAttributesView(LookupFieldMixin, generics.ListAPIView):
    """
    GET Paginated QBO Attributes view
    """

    queryset = DestinationAttribute.objects.distinct('attribute_type')
    serializer_class = DestinationAttributeSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = {'attribute_type': {'exact', 'in'}}
