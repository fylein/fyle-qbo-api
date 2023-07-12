from django.apps import AppConfig


class WorkspaceConfig(AppConfig):
    name = 'apps.workspaces'

    def ready(self):
        super(WorkspaceConfig, self).ready()
        import apps.workspaces.signals
