from django.apps import AppConfig


class RelatoriosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'relatorios'
    verbose_name = 'Relatórios e Dashboards'
    
    def ready(self):
        import relatorios.signals
