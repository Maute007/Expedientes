from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def assinatura_permitida(view_func):
    """
    Decorador para verificar se o usuário tem permissão para assinar documentos.
    Apenas PCA, Secretaria e Chefes podem assinar.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        
        # Verificar se o usuário tem permissão de assinatura
        if user.tipo_utilizador not in ['pca', 'secretaria', 'chefe']:
            raise PermissionDenied(
                "Você não tem permissão para assinar documentos. "
                "Apenas PCA, Secretaria e Chefes podem assinar."
            )
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


class AssinaturaPermitidaMixin:
    """
    Mixin para views baseadas em classes que verifica permissão de assinatura
    """
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        
        if not user.is_authenticated:
            return redirect('users:login')
        
        # Verificar se o usuário tem permissão de assinatura
        if user.tipo_utilizador not in ['pca', 'secretaria', 'chefe']:
            raise PermissionDenied(
                "Você não tem permissão para assinar documentos. "
                "Apenas PCA, Secretaria e Chefes podem assinar."
            )
        
        return super().dispatch(request, *args, **kwargs)

