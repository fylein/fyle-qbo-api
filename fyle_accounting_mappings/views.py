import logging
from typing import Dict, List

from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import status

from .exceptions import BulkError
from .utils import assert_valid
from .models import MappingSetting, Mapping
from .serializers import MappingSettingSerializer, MappingSerializer

logger = logging.getLogger(__name__)


class MappingSettingsView(ListCreateAPIView):
	"""
	Mapping Settings VIew
	"""
	serializer_class = MappingSettingSerializer

	def get_queryset(self):
		return MappingSetting.objects.filter(workspace_id=self.kwargs['workspace_id'])

	def post(self, request, *args, **kwargs):
		"""
		Post mapping settings
		"""
		try:
			mapping_settings: List[Dict] = request.data.get('mapping_settings', [])

			assert_valid(mapping_settings != [], 'Mapping settings not found')

			mapping_settings = MappingSetting.bulk_upsert_mapping_setting(mapping_settings, self.kwargs['workspace_id'])

			return Response(data=self.serializer_class(mapping_settings, many=True), status=status.HTTP_200_OK)
		except BulkError as exception:
			logger.error(exception.response)
			return Response(
				data=exception.response,
				status=status.HTTP_400_BAD_REQUEST
			)


class MappingsView(ListCreateAPIView):
	"""
	Mapping Settings VIew
	"""
	serializer_class = MappingSerializer

	def get_queryset(self):
		source_type = self.request.query_params.get('source_type')

		assert_valid(source_type is not None, 'query param source type not found')

		return Mapping.objects.filter(source_type=source_type, workspace_id=self.kwargs['workspace_id'])

	def post(self, request, *args, **kwargs):
		"""
		Post mapping settings
		"""
		try:
			mappings: List[Dict] = request.data.get('mapping_settings', [])

			assert_valid(mappings != [], 'Mappings not found')

			mappings = Mapping.bulk_upsert_mappings(mappings, self.kwargs['workspace_id'])

			return Response(data=self.serializer_class(mappings, many=True), status=status.HTTP_200_OK)
		except BulkError as exception:
			logger.error(exception.response)
			return Response(
				data=exception.response,
				status=status.HTTP_400_BAD_REQUEST
			)
