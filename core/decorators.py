from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse


def login_required_custom(view_func):
    """
    Decorator customizado para requerer login.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Deve fazer login para aceder a esta página.')
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({'error': 'Login necessário'}, status=401)
            return redirect('users:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def pca_required(view_func):
    """
    Decorator para requerer que o utilizador seja PCA.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Deve fazer login para aceder a esta página.')
            return redirect('users:login')
        
        if not request.user.is_pca:
            messages.error(request, 'Apenas o PCA pode aceder a esta página.')
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({'error': 'Permissão negada'}, status=403)
            raise PermissionDenied('Apenas o PCA pode aceder a esta página.')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def chefe_required(view_func):
    """
    Decorator para requerer que o utilizador seja chefe de sector.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Deve fazer login para aceder a esta página.')
            return redirect('users:login')
        
        if not (request.user.sector_atual and 
                request.user.sector_atual.eh_chefe(request.user)):
            messages.error(request, 'Apenas Chefes de Sector podem aceder a esta página.')
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({'error': 'Permissão negada'}, status=403)
            raise PermissionDenied('Apenas Chefes de Sector podem aceder a esta página.')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def pca_or_chefe_required(view_func):
    """
    Decorator para requerer que o utilizador seja PCA ou chefe de sector.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Deve fazer login para aceder a esta página.')
            return redirect('users:login')
        
        is_pca = request.user.is_pca
        is_chefe = (request.user.sector_atual and 
                   request.user.sector_atual.eh_chefe(request.user))
        
        if not (is_pca or is_chefe):
            messages.error(request, 'Apenas PCA ou Chefes de Sector podem aceder a esta página.')
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({'error': 'Permissão negada'}, status=403)
            raise PermissionDenied('Apenas PCA ou Chefes de Sector podem aceder a esta página.')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def sector_required(view_func):
    """
    Decorator para garantir que o utilizador tem um sector atribuído.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Deve fazer login para aceder a esta página.')
            return redirect('users:login')
        
        if not request.user.sector_atual:
            messages.error(request, 'Deve ter um sector atribuído para aceder a esta página.')
            return redirect('users:perfil')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def permission_required(permission):
    """
    Decorator genérico para verificar permissões específicas.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Deve fazer login para aceder a esta página.')
                return redirect('users:login')
            
            if not request.user.has_perm(permission):
                messages.error(request, 'Não tem permissão para aceder a esta página.')
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse({'error': 'Permissão negada'}, status=403)
                raise PermissionDenied('Não tem permissão para aceder a esta página.')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def ajax_required(view_func):
    """
    Decorator para garantir que a requisição é AJAX.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Requisição AJAX necessária'}, status=400)
        return view_func(request, *args, **kwargs)
    return wrapper
