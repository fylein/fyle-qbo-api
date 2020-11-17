from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from fyle_qbo_api.utils import assert_valid

from .serializers import GeneralMappingSerializer
from .models import GeneralMapping
from .utils import MappingUtils


class GeneralMappingView(generics.ListCreateAPIView):
    """
    General mappings
    """
    serializer_class = GeneralMappingSerializer
    queryset = GeneralMapping.objects.all()

    def post(self, request, *args, **kwargs):
        """
        Create general mappings
        """
        general_mapping_payload = request.data

        assert_valid(general_mapping_payload is not None, 'Request body is empty')

        mapping_utils = MappingUtils(kwargs['workspace_id'])

        general_mapping = mapping_utils.create_or_update_general_mapping(general_mapping_payload)

        return Response(
            data=self.serializer_class(general_mapping).data,
            status=status.HTTP_200_OK
        )

    def get(self, request, *args, **kwargs):
        """
        Get general mappings
        """
        try:
            general_mapping = self.queryset.get(workspace_id=kwargs['workspace_id'])
            return Response(
                data=self.serializer_class(general_mapping).data,
                status=status.HTTP_200_OK
            )
        except GeneralMapping.DoesNotExist:
            return Response(
                {
                    'message': 'General mappings do not exist for the workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
