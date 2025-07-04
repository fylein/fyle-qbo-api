import logging
from rest_framework.throttling import SimpleRateThrottle

logger = logging.getLogger(__name__)


class PerUserPathThrottle(SimpleRateThrottle):
    scope = 'per_user_path'

    def allow_request(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return True

        result = super().allow_request(request, view)
        logger.info(f"PerUserPathThrottle.allow_request result: {result}")

        if not result:
            logger.warning(f"🚫 REQUEST THROTTLED - User {request.user.pk} on path {request.path}")

        return result

    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return None

        ident = request.user.pk
        normalized_path = request.path.replace('/', '_').strip('_')
        cache_key = f"throttle_{self.scope}_{normalized_path}_{ident}"

        return cache_key
