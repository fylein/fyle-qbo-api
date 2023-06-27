import pytest
from pytest import fail
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from apps.workspaces.apis.map_employees.serializers import MapEmployeesSerializer


def test_employee_field_mapping_required():
    invalid_data = {'workspace_general_settings': {}}
    serializer = MapEmployeesSerializer(data=invalid_data)
    with pytest.raises(ValidationError):
        serializer.is_valid(raise_exception=True)


def test_auto_map_employees_value():
    invalid_data = {'workspace_general_settings': {'auto_map_employees': 'INVALID_VALUE'}}
    serializer = MapEmployeesSerializer(data=invalid_data)
    with pytest.raises(ValidationError):
        serializer.is_valid(raise_exception=True)


def test_valid_data():
    valid_data = {'workspace_general_settings': {'employee_field_mapping': 'value'}}
    serializer = MapEmployeesSerializer(data=valid_data)
    assert serializer.is_valid() is True
