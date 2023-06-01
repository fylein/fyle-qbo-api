from django_q.tasks import Chain
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from fyle_qbo_api.utils import assert_valid

from .serializers import GeneralMappingSerializer
from .models import GeneralMapping
from .utils import MappingUtils
from ..workspaces.models import WorkspaceGeneralSettings



class AutoMapEmployeeView(generics.CreateAPIView):
    """
    Auto Map Employees view
    """

    def post(self, request, *args, **kwargs):
        """
        Trigger Auto Map employees
        """
        try:
            workspace_id = kwargs['workspace_id']
            general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

            chain = Chain()

            if not general_settings.auto_map_employees:
                return Response(
                    data={
                        'message': 'Employee mapping preference not found for this workspace'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            chain.append(
                'apps.mappings.tasks.async_auto_map_employees', workspace_id)

            general_mappings = GeneralMapping.objects.get(workspace_id=workspace_id)

            if general_mappings.default_ccc_account_name:
                chain.append(
                    'apps.mappings.tasks.async_auto_map_ccc_account', workspace_id)

            if chain.length():
                chain.run()

            return Response(
                data={},
                status=status.HTTP_200_OK
            )

        except GeneralMapping.DoesNotExist:
            return Response(
                {
                    'message': 'General mappings do not exist for this workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
