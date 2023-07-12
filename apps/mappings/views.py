
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from apps.exceptions import handle_view_exceptions

from ..workspaces.models import WorkspaceGeneralSettings
from .actions import trigger_auto_map_employees
from .models import GeneralMapping


class AutoMapEmployeeView(generics.CreateAPIView):
    """
    Auto Map Employees view
    """

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        """
        Trigger Auto Map employees
        """
        trigger_auto_map_employees(workspace_id=kwargs['workspace_id'])

        return Response(
            data={},
            status=status.HTTP_200_OK
        )
