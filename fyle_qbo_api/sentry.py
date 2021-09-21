import sentry_sdk

from sentry_sdk.integrations.django import DjangoIntegration

from django.conf import settings
import os

class Sentry:

    @staticmethod
    def init():
        sentry_sdk.init(
            dsn=os.environ.get('SENTRY_DSN'),
            send_default_pii=True,
            integrations=[DjangoIntegration()],
            server_name='qucikbooks-api',
            environment='Quickbooks',
            traces_sampler=Sentry.traces_sampler,
            attach_stacktrace=True
        )

    @staticmethod
    def traces_sampler(sampling_context):
        # avoiding ready APIs in performance tracing
        if sampling_context.get('wsgi_environ') is not None:
            if sampling_context['wsgi_environ']['PATH_INFO'] in ['/ready']:
                return 0

        return 0.2