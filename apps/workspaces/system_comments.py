from enum import Enum
from typing import Union

from fyle_accounting_library.system_comments.models import SystemComment


def add_system_comment(
    system_comments: list | None,
    source: Union[Enum, str],
    intent: Union[Enum, str],
    entity_type: Union[Enum, str],
    workspace_id: int,
    entity_id: int = None,
    export_type: Union[Enum, str] = None,
    is_user_visible: bool = False,
    reason: Union[Enum, str] = None,
    info: dict = None,
    persist_without_export: bool = True
) -> None:
    """
    Add a system comment to the list

    :param system_comments: list of system comments
    :param source: source of the system comment
    :param intent: intent of the system comment
    :param entity_type: entity type of the system comment
    :param workspace_id: workspace id
    :param entity_id: entity id
    :param export_type: export type of the system comment
    :param is_user_visible: whether the system comment is user visible
    :param reason: reason of the system comment
    :param info: info of the system comment
    :param persist_without_export: whether to persist this comment even if export fails (default True)
    :return: None
    """
    if system_comments is None:
        return

    system_comments.append({
        'workspace_id': workspace_id,
        'source': source.value if isinstance(source, Enum) else source,
        'intent': intent.value if isinstance(intent, Enum) else intent,
        'entity_type': entity_type.value if isinstance(entity_type, Enum) else entity_type,
        'entity_id': entity_id,
        'export_type': export_type.value if isinstance(export_type, Enum) else export_type,
        'is_user_visible': is_user_visible,
        'persist_without_export': persist_without_export,
        'detail': {
            'reason': reason.value if isinstance(reason, Enum) else reason,
            'info': info or {}
        }
    })


def create_filtered_system_comments(
    system_comments: list | None,
    workspace_id: int,
    export_type: Union[Enum, str],
    persist_without_export: bool = True
) -> None:
    """
    Filter and create system comments based on persist_without_export flag

    :param system_comments: list of system comments to create
    :param workspace_id: workspace id
    :param export_type: export type enum or string
    :param persist_without_export: default persist_without_export value if not set in comment (default True)
    :return: None
    """
    if not system_comments:
        return

    comments_to_flush = []
    export_type_value = export_type.value if isinstance(export_type, Enum) else export_type

    for comment in system_comments:
        comment['workspace_id'] = workspace_id
        comment['export_type'] = export_type_value
        if comment.get('persist_without_export', persist_without_export):
            comments_to_flush.append(comment)

    if comments_to_flush:
        SystemComment.bulk_create_comments(comments_to_flush)
