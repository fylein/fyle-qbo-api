from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from fyle_rest_auth.models import AuthToken

from apps.fyle.utils import FyleConnector

from apps.workspaces.models import FyleCredential

class UserProfileView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Get User Details
        """
        fyle_credentials = AuthToken.objects.get(user__user_id=request.user)

        fyle_connector = FyleConnector(fyle_credentials.refresh_token)

        employee_profile = fyle_connector.get_employee_profile()

        return Response(
            data=employee_profile,
            status=status.HTTP_200_OK
        )

class CluserDomainView(generics.RetrieveAPIView):
    """
    CluserDomain view
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Get cluster domain from Fyle
        """
        try:
            fyle_credentials = AuthToken.objects.get(user__user_id=request.user)
            fyle_connector = FyleConnector(fyle_credentials.refresh_token)
            cluser_domain = fyle_connector.get_cluster_domain()['cluster_domain']

            return Response(
                data=cluser_domain,
                status=status.HTTP_200_OK
            )
        except FyleCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'Invalid / Expired Token'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

class FyleOrgsView(generics.ListCreateAPIView):
    """
    FyleOrgs view
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Get cluster domain from Fyle
        """
        try:
            fyle_credentials = AuthToken.objects.get(user__user_id=request.user)
            fyle_connector = FyleConnector(fyle_credentials.refresh_token)
            cluser_domain = fyle_connector.get_cluster_domain()['cluster_domain']
            fyle_orgs = fyle_connector.get_fyle_orgs(cluser_domain=cluser_domain)

            return Response(
                data=fyle_orgs,
                status=status.HTTP_200_OK
            )
        except FyleCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'Invalid / Expired Token'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
