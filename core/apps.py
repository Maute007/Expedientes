from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        """
        Método chamado quando a app está pronta.
        Importa os signals para garantir que sejam registrados.
        """
        import core.signals