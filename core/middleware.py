from django.contrib.sessions.models import Session
from django.utils import timezone
from django.conf import settings
from .models import ConfiguracaoSistema


class DynamicSessionTimeoutMiddleware:
    """
    Middleware para aplicar timeout de sessão dinâmico baseado nas configurações do sistema.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Aplicar timeout de sessão dinâmico
        self.set_dynamic_session_timeout(request)
        
        response = self.get_response(request)
        return response
    
    def set_dynamic_session_timeout(self, request):
        """
        Define o timeout de sessão baseado nas configurações do sistema.
        """
        try:
            # Obter timeout configurado (em minutos)
            timeout_minutos = ConfiguracaoSistema.obter_configuracao(
                'timeout_sessao', 
                valor_padrao=30
            )
            
            # Converter para segundos
            timeout_segundos = timeout_minutos * 60
            
            # Definir timeout da sessão
            if hasattr(request, 'session'):
                request.session.set_expiry(timeout_segundos)
                
        except Exception:
            # Em caso de erro, usar timeout padrão do Django
            pass
