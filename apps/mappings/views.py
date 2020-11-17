from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from fyle_qbo_api.utils import assert_valid

from .serializers import GeneralMappingSerializer, EmployeeMappingSerializer, \
    CategoryMappingSerializer, CostCenterMappingSerializer, ProjectMappingSerializer
from .models import GeneralMapping, EmployeeMapping, CategoryMapping, CostCenterMapping, ProjectMapping
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

        mapping_utils.upload_projects_to_fyle(destination_attribute_type='CUSTOMER')

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


class EmployeeMappingView(generics.ListCreateAPIView):
    """
    Employee mappings view
    """
    serializer_class = EmployeeMappingSerializer

    def get_queryset(self):
        return EmployeeMapping.objects.filter(workspace_id=self.kwargs['workspace_id']).order_by('-updated_at').all()

    def post(self, request, *args, **kwargs):
        """
        Post employee mapping view
        """
        employee_mapping_payload = request.data

        assert_valid(employee_mapping_payload is not None, 'Request body is empty')

        mapping_utils = MappingUtils(kwargs['workspace_id'])
        employee_mapping_object = mapping_utils.create_or_update_employee_mapping(employee_mapping_payload)

        return Response(
            data=self.serializer_class(employee_mapping_object).data,
            status=status.HTTP_200_OK
        )


class CategoryMappingView(generics.ListCreateAPIView):
    """
    Category mappings view
    """
    serializer_class = CategoryMappingSerializer

    def get_queryset(self):
        return CategoryMapping.objects.filter(workspace_id=self.kwargs['workspace_id']).order_by('-updated_at').all()

    def post(self, request, *args, **kwargs):
        """
        Post category mapping view
        """
        category_mapping_payload = request.data

        assert_valid(category_mapping_payload is not None, 'Request body is empty')

        mapping_utils = MappingUtils(kwargs['workspace_id'])
        category_mapping_object = mapping_utils.create_or_update_category_mapping(category_mapping_payload)

        return Response(
            data=self.serializer_class(category_mapping_object).data,
            status=status.HTTP_200_OK
        )


class CostCenterMappingView(generics.ListCreateAPIView):
    """
    Cost center mappings view
    """
    serializer_class = CostCenterMappingSerializer

    def get_queryset(self):
        return CostCenterMapping.objects.filter(workspace_id=self.kwargs['workspace_id']).order_by('-updated_at').all()

    def post(self, request, *args, **kwargs):
        """
        Post cost center mapping view
        """
        cost_center_mapping_payload = request.data

        assert_valid(cost_center_mapping_payload is not None, 'Request body is empty')

        mapping_utils = MappingUtils(kwargs['workspace_id'])
        cost_center_mapping_object = mapping_utils.create_or_update_cost_center_mapping(cost_center_mapping_payload)

        return Response(
            data=self.serializer_class(cost_center_mapping_object).data,
            status=status.HTTP_200_OK
        )


class ProjectMappingView(generics.ListCreateAPIView):
    """
    Project mappings view
    """
    serializer_class = ProjectMappingSerializer

    def get_queryset(self):
        return ProjectMapping.objects.filter(workspace_id=self.kwargs['workspace_id']).order_by('-updated_at').all()

    def post(self, request, *args, **kwargs):
        """
        Post project mapping view
        """
        project_mapping_payload = request.data

        assert_valid(project_mapping_payload is not None, 'Request body is empty')

        mapping_utils = MappingUtils(kwargs['workspace_id'])
        project_mapping_object = mapping_utils.create_or_update_project_mapping(project_mapping_payload)

        return Response(
            data=self.serializer_class(project_mapping_object).data,
            status=status.HTTP_200_OK
        )
