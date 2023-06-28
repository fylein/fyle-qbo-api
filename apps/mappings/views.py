from django_q.tasks import Chain
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from .models import GeneralMapping
from ..workspaces.models import WorkspaceGeneralSettings
from apps.exceptions import handle_view_exceptions



class AutoMapEmployeeView(generics.CreateAPIView):
    """
    Auto Map Employees view
    """

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        """
        Trigger Auto Map employees
        """
        workspace_id = kwargs['workspace_id']
        general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id, auto_map_employees__isnull=False)

        chain = Chain()

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
