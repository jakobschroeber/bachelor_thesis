from django.apps import AppConfig


class AdministrationConfig(AppConfig):
    name = 'data_sink'

    def ready(self):
        import data_sink.signals