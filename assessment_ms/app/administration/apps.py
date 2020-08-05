from django.apps import AppConfig


class AdministrationConfig(AppConfig):
    name = 'administration'

    def ready(self):
        import administration.signals