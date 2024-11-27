error_msgs = [
    "Invalid Reference Id : Accounts element id 7 not found",
    "Invalid Reference Id : Klasses element id 5000000000000142240 not found",
    "Invalid Reference Id : Depts element id 2 not found",
    "Invalid Reference Id : Names element id 75 not found"
]

result_dict_list = [
    {'attribute_type': 'ACCOUNT', 'destination_id': '7', 'error_attribute': 'Accounts', 'article_link': None},
    {'attribute_type': 'CLASS', 'destination_id': '5000000000000142240', 'error_attribute': 'Klasses', 'article_link': None},
    {'attribute_type': 'DEPARTMENT', 'destination_id': '2', 'error_attribute': 'Depts', 'article_link': None},
    {'attribute_type': 'VENDOR', 'destination_id': '75', 'error_attribute': 'Names', 'article_link': None},
]

error_dict = [
    {'attribute_type': 'ACCOUNT', 'destination_id': '7', 'error_attribute': 'Accounts', 'article_link': None},
    {'attribute_type': 'CLASS', 'destination_id': '5000000000000142240', 'error_attribute': 'Klasses', 'article_link': None},
    {'attribute_type': 'DEPARTMENT', 'destination_id': '2', 'error_attribute': 'Depts', 'article_link': None},
    {'attribute_type': 'VENDOR', 'destination_id': '75', 'error_attribute': 'Names', 'article_link': None},
]

entity_result_dict_list = [
    {'destination_id': '7', 'value': 'Advertising', 'error_attribute': 'Accounts', 'attribute_type': 'ACCOUNT'},
    {'destination_id': '5000000000000142240', 'value': 'cc2', 'error_attribute': 'Klasses', 'attribute_type': 'CLASS'},
    {'destination_id': '2', 'value': 'Bangalore', 'error_attribute': 'Depts', 'attribute_type': 'DEPARTMENT'},
    {'destination_id': '75', 'value': 'SPEEDWAY', 'error_attribute': 'Names', 'attribute_type': 'VENDOR'},
]

input_strings = [
    "Invalid Reference Id : Accounts element id 7 not found",
    "Invalid Reference Id : Klasses element id 5000000000000142240 not found",
    "Invalid Reference Id : Depts element id 2 not found",
    "Invalid Reference Id : Names element id 75 not found"
]

replacements = [
    {'destination_id': '7', 'value': 'Advertising', 'error_attribute': 'Accounts', 'attribute_type': 'ACCOUNT'},
    {'destination_id': '5000000000000142240', 'value': 'cc2', 'error_attribute': 'Klasses', 'attribute_type': 'CLASS'},
    {'destination_id': '2', 'value': 'Bangalore', 'error_attribute': 'Depts', 'attribute_type': 'DEPARTMENT'},
    {'destination_id': '75', 'value': 'SPEEDWAY', 'error_attribute': 'Names', 'attribute_type': 'VENDOR'}
]

output_strings = [
    "Invalid Reference Id : Accounts => ACCOUNT element id 7 => Advertising not found",
    "Invalid Reference Id : Klasses => CLASS element id 5000000000000142240 => cc2 not found",
    "Invalid Reference Id : Depts => DEPARTMENT element id 2 => Bangalore not found",
    "Invalid Reference Id : Names => VENDOR element id 75 => SPEEDWAY not found"
]
