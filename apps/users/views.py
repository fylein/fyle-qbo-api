from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.actions import get_fyle_orgs_view

class FyleOrgsView(generics.ListCreateAPIView):
    """
    FyleOrgs view
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Get cluster domain from Fyle
        """
        fyle_orgs = get_fyle_orgs_view(request.user)

        return Response(
            data=len(fyle_orgs),
            status=status.HTTP_200_OK
        )
