import unittest
from rest_framework import serializers
from apps.workspaces.apis.map_employees.serializers import MapEmployeesSerializer


def test_valid_data():
    valid_data = {'workspace_general_settings': {'employee_field_mapping': 'value'}}
    serializer = MapEmployeesSerializer(data=valid_data)
    assert serializer.is_valid() == True

if __name__ == '__main__':
    unittest.main()
