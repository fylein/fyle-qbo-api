from apps.quickbooks_online.errors.helpers import error_matcher, get_entity_values, replace_destination_id_with_values
from tests.test_quickbooks_online.errors.fixtures import (
    entity_result_dict_list,
    error_dict,
    error_msgs,
    input_strings,
    output_strings,
    replacements,
    result_dict_list,
)


def test_error_matcher():
    for index in range(len(error_msgs)):
        assert error_matcher(error_msgs[index]) == result_dict_list[index]


def test_get_entity_values(db):
    for index in range(len(error_dict)):
        assert get_entity_values(error_dict[index], 4) == entity_result_dict_list[index]


def test_replace_destination_id_with_values():
    for index in range(len(input_strings)):
        assert replace_destination_id_with_values(input_strings[index], replacements[index]) == output_strings[index]
