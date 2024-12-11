from apps.quickbooks_online.errors.helpers import error_matcher, get_entity_values, replace_destination_id_with_values
from apps.tasks.models import Error

errors_count = Error.objects.filter(type='QBO_ERROR', is_resolved=False).count()
print(errors_count)
page_size = 200
count = 0
for offset in range(0, errors_count, page_size):
    limit = offset + page_size
    paginated_errors = Error.objects.filter(type='QBO_ERROR', is_resolved=False).order_by('id')[offset:limit]
    for error in paginated_errors:
        error_dict = error_matcher(error.error_detail)
        if error_dict:
            error_entity_values = get_entity_values(error_dict, error.workspace_id)
            if error_entity_values:
                error_msg = replace_destination_id_with_values(error.error_detail, error_entity_values)
                error.is_parsed = True
                error.article_link = error_dict['article_link']
                error.attribute_type = error_dict['attribute_type']
                error.error_detail = error_msg
                error.save()
                count += 1

print(count)
