from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from apps.exceptions import handle_view_exceptions
from workers.helpers import RoutingKeyEnum, WorkerActionEnum, publish_to_rabbitmq


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
        payload = {
            'workspace_id': workspace_id,
            'action': WorkerActionEnum.TRIGGER_AUTO_MAP_EMPLOYEES.value,
            'data': {
                'workspace_id': workspace_id,

            }
        }
        publish_to_rabbitmq(payload=payload, routing_key=RoutingKeyEnum.IMPORT.value)

        return Response(data={}, status=status.HTTP_200_OK)
