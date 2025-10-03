import logging
import os
from typing import Dict

import django
from django.utils.module_loading import import_string
from fyle_accounting_library.common_resources.helpers import mask_sensitive_data

from workers.helpers import ACTION_METHOD_MAP

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fyle_qbo_api.settings")
django.setup()

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def handle_tasks(payload: Dict) -> None:
    """
    Handle tasks
    :param data: Dict
    :return: None
    """
    action = payload.get('action')
    data = payload.get('data')

    if action is None:
        masked_data = mask_sensitive_data(data) if data else data
        logger.error('Action is None for payload - %s', masked_data)
        return

    method = ACTION_METHOD_MAP.get(action)

    if method is None:
        masked_data = mask_sensitive_data(data) if data else data
        logger.error('Method is None for action - %s and payload - %s', action, masked_data)
        return

    import_string(method)(**data)
