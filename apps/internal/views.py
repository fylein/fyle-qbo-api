import logging
import traceback

from rest_framework import generics, status
from rest_framework.response import Response

from apps.internal.actions import get_accounting_fields, get_exported_entry
from apps.workspaces.permissions import IsAuthenticatedForInternalAPI
from fyle_qbo_api.utils import assert_valid

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AccountingFieldsView(generics.GenericAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticatedForInternalAPI]

    def get(self, request, *args, **kwargs):
        try:
            params = request.query_params

            assert_valid(params.get('org_id') is not None, 'Org ID is required')
            assert_valid(params.get('resource_type') is not None, 'Resource Type is required')

            response = get_accounting_fields(request.query_params)
            return Response(
                data={'data': response},
                status=status.HTTP_200_OK
            )

        except Exception:
            logger.info(f"Error in AccountingFieldsView: {traceback.format_exc()}")
            return Response(
                data={'error': traceback.format_exc()},
                status=status.HTTP_400_BAD_REQUEST
            )


class ExportedEntryView(generics.GenericAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticatedForInternalAPI]

    def get(self, request, *args, **kwargs):
        try:
            params = request.query_params
            assert_valid(params.get('org_id') is not None, 'Org ID is required')
            assert_valid(params.get('resource_type') is not None, 'Resource Type is required')
            assert_valid(params.get('internal_id') is not None, 'Internal ID is required')

            response = get_exported_entry(request.query_params)

            return Response(
                data={'data': response},
                status=status.HTTP_200_OK
            )

        except Exception:
            logger.info(f"Error in AccountingFieldsView: {traceback.format_exc()}")
            return Response(
                data={'error': traceback.format_exc()},
                status=status.HTTP_400_BAD_REQUEST
            )
