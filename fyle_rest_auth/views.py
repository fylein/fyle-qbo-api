"""
Fyle Authentication views
"""
from rest_framework.views import APIView, status
from rest_framework.response import Response

from .helpers import (
    validate_code_and_login,
    validate_and_refresh_token,
    validate_refresh_token_and_login,
    get_cluster_domain_by_code
)


class LoginView(APIView):
    """
    Login Using Fyle Account
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """
        Login using authorization code
        """
        tokens = validate_code_and_login(request)

        return Response(
            data=tokens,
            status=status.HTTP_200_OK,
        )


class LoginWithRefreshTokenView(APIView):
    """
    Login Using Fyle Account
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """
        Login using refresh token
        """
        tokens = validate_refresh_token_and_login(request)

        return Response(
            data=tokens,
            status=status.HTTP_200_OK,
        )


class RefreshView(APIView):
    """
    Refresh Access Token
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        tokens = validate_and_refresh_token(request)

        return Response(
            data=tokens,
            status=status.HTTP_200_OK
        )


class ClusterDomainView(APIView):
    """
    Get Cluster Domain
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        response = get_cluster_domain_by_code(request)

        return Response(
            data=response,
            status=status.HTTP_200_OK
        )
