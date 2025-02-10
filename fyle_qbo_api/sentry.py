import os

import gevent
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


class Sentry:
    @staticmethod
    def init():
        sentry_sdk.init(
            dsn=os.environ.get('SENTRY_DSN'),
            send_default_pii=True,
            integrations=[DjangoIntegration()],
            environment=os.environ.get('SENTRY_ENV'),
            attach_stacktrace=True,
            before_send=Sentry.before_send,
            max_request_body_size='small',
            in_app_include=['apps.users', 'apps.workspaces', 'apps.mappings', 'apps.fyle', 'apps.quickbooks_online', 'apps.tasks', 'fyle_rest_auth', 'fyle_accounting_mappings'],
        )

    @staticmethod
    def before_send(event, hint):
        if 'exc_info' in hint:
            exc_info = hint['exc_info']
            exc_type, exc_value, tb = exc_info
            if isinstance(exc_value, gevent.GreenletExit):
                return None
            if exc_value.args and exc_value.args[0] in ['Error: 502']:
                return None

        # 1. Scrub user data (if any)
        user = event.get("user", {})
        if user:
            if "email" in user:
                user["email"] = "[Filtered]"
            if "username" in user:
                user["username"] = "[Filtered]"
            if "workspace" in user:
                user["workspace"] = "[Filtered]"
            if "workspace_name" in user:
                user["workspace_name"] = "[Filtered]"
            if "org" in user:
                user["org"] = "[Filtered]"
            event["user"] = user

        # 2. Scrub data in the "extra" section (if any)
        extra = event.get("extra", {})
        sensitive_extra_keys = {"email", "workspace", "org", "name", "workspace_name"}
        for key in list(extra.keys()):
            if key.lower() in sensitive_extra_keys:
                extra[key] = "[Filtered]"
        event["extra"] = extra

        # 3. Scrub data in the "request" section (if any)
        request = event.get("request", {})
        headers = request.get("headers", {})
        for header in list(headers.keys()):
            if header.lower() in ("authorization", "cookie"):
                headers[header] = "[Filtered]"
        request["headers"] = headers
        event["request"] = request

        return event
