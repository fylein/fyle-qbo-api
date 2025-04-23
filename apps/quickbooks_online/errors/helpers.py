import re

from fyle_accounting_mappings.models import DestinationAttribute

field_map = {
    'Accounts': {'type': 'ACCOUNT', 'article_link': None},
    'Klasses': {'type': 'CLASS', 'article_link': None},
    'Names': {'type': ['VENDOR', 'EMPLOYEE', 'CUSTOMER'], 'article_link': None},
    'Depts': {'type': 'DEPARTMENT', 'article_link': None}
}


def error_matcher(error_msg):
    pattern = r'Invalid Reference Id : (\w+) element id (\d+) not found'

    match = re.search(pattern, error_msg)

    if match:
        # Extract the QBO element and its ID
        error_attribute, destination_id = match.groups()

        # Get the field info from the mapping
        field_info = field_map.get(error_attribute)

        if field_info:
            # Create a dictionary to store information about the error
            error_dict = {
                'attribute_type': field_info['type'],
                'destination_id': destination_id,
                'error_attribute': error_attribute,
                'article_link': field_info['article_link']
            }

            return error_dict

    # If no match is found, return None
    return None


def get_entity_values(error_dict, workspace_id):
    '''
    Get entity values from error dictionary
    :param error_dict: Error Dictionary containing information about the error
    :param workspace_id: ID of the workspace
    :return: Dictionary with 'destination_id' and 'value' if found, otherwise an empty dictionary
    '''
    # Convert attribute_type to list if it's not already
    attribute_types = error_dict['attribute_type'] if isinstance(error_dict['attribute_type'], list) else [error_dict['attribute_type']]

    # Fetch the destination attribute using attribute_type__in
    destination_attribute = DestinationAttribute.objects.filter(
        destination_id=error_dict['destination_id'],
        attribute_type__in=[attr_type.upper() for attr_type in attribute_types],
        workspace_id=workspace_id
    ).order_by('-updated_at').first()

    # If the destination attribute is found, return a dictionary with 'destination_id' and 'value'
    if destination_attribute:
        return {
            'destination_id': error_dict['destination_id'],
            'value': destination_attribute.value,
            'error_attribute': error_dict['error_attribute'],
            'attribute_type': error_dict['attribute_type']
        }

    # If no match is found or destination attribute is not active, return an empty dictionary
    return {}


def replace_destination_id_with_values(input_string, replacement):
    '''
    Replace destination ID with corresponding values in the input string
    :param input_string: Original string containing destination ID placeholders
    :param replacement: Dictionary with 'destination_id' and 'value' to replace in the string
    :return: String with destination ID replaced by formatted 'destination_id => value'
    '''

    # Extract destination ID and value from the replacement dictionary
    destination_id = replacement['destination_id']
    value = replacement['value']
    error_attribute = replacement['error_attribute']
    attribute_type = replacement['attribute_type']

    # Create a formatted string in the form of 'destination_id => value'
    arrowed_string_value = f'{destination_id} => {value}'
    arrowed_string_attribute = f'{error_attribute} => {attribute_type}'

    # Replace occurrences of destination ID in the input string with the formatted string
    input_string = input_string.replace(destination_id, arrowed_string_value)
    input_string = input_string.replace(error_attribute, arrowed_string_attribute)

    # Return the modified input string
    return input_string
