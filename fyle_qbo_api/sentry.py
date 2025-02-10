import os

import gevent
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.scrubber import EventScrubber


class Sentry:
    @staticmethod
    def init():
        sentry_sdk.init(
            dsn=os.environ.get('SENTRY_DSN'),
            send_default_pii=False,
            event_scrubber=EventScrubber(),
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

        return event
