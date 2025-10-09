from fyle_accounting_library.enums import CacheKeyEnum


class CacheKeyEnum(CacheKeyEnum):
    """
    Cache key enum
    """
    FEATURE_CONFIG = 'feature_config_{workspace_id}'
