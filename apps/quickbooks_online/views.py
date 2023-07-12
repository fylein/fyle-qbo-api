import logging

from django_filters.rest_framework import DjangoFilterBackend
from fyle_accounting_mappings.models import DestinationAttribute
from fyle_accounting_mappings.serializers import DestinationAttributeSerializer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from apps.exceptions import handle_view_exceptions
from fyle_qbo_api.utils import LookupFieldMixin

from .actions import get_preferences, refresh_quickbooks_dimensions, sync_quickbooks_dimensions
from .tasks import create_bill_payment

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

class EmployeeView(LookupFieldMixin, generics.ListAPIView):
    """
    Employee view
    """
    queryset = DestinationAttribute.objects.all()
    serializer_class = DestinationAttributeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = {'value': {'icontains'}, 'attribute_type': {'exact', 'in'}, 'active': {'exact'}}
    ordering_fields = ('value',)


class PreferencesView(generics.RetrieveAPIView):
    """
    Preferences View
    """

    def get(self, request, *args, **kwargs):
        return get_preferences(kwargs['workspace_id'])


class SyncQuickbooksDimensionView(generics.ListCreateAPIView):
    """
    Sync Quickbooks Dimension View
    """

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        sync_quickbooks_dimensions(kwargs['workspace_id'])

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
        refresh_quickbooks_dimensions(kwargs['workspace_id'])

        return Response(
            status=status.HTTP_200_OK
        )


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
