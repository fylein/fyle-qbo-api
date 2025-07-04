from rest_framework.throttling import SimpleRateThrottle

class PerUserPathThrottle(SimpleRateThrottle):
    scope = 'per_user_path'

    def allow_request(self, request, view):
        # Only throttle authenticated users
        if not request.user or not request.user.is_authenticated:
            return True  # skip for anonymous (e.g., webhooks)

        return super().allow_request(request, view)

    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return None  # no cache key for anon

        ident = request.user.pk
        normalized_path = request.path.replace('/', '_').strip('_')

        return f"throttle_{self.scope}_{normalized_path}_{ident}"
