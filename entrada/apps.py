from django.apps import AppConfig


class EntradaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'entrada'
    
    def ready(self):
        """
        Importa os signals quando a app está pronta.
        """
        import entrada.signals