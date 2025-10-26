from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied


def is_pca(user):
    """
    Verifica se o utilizador é PCA.
    """
    return user.is_authenticated and user.is_pca


def is_chefe_sector(user):
    """
    Verifica se o utilizador é chefe de algum sector.
    """
    if not user.is_authenticated or not user.sector_atual:
        return False
    
    return user.sector_atual.eh_chefe(user)


def is_pca_or_chefe(user):
    """
    Verifica se o utilizador é PCA ou chefe de sector.
    """
    return is_pca(user) or is_chefe_sector(user)


def has_sector(user):
    """
    Verifica se o utilizador tem um sector atribuído.
    """
    return user.is_authenticated and user.sector_atual is not None


def can_access_sector(user, sector):
    """
    Verifica se o utilizador pode aceder a um sector específico.
    """
    if not user.is_authenticated:
        return False
    
    # PCA pode aceder a todos os sectores
    if is_pca(user):
        return True
    
    # Utilizador pode aceder ao seu próprio sector
    if user.sector_atual == sector:
        return True
    
    # Chefe pode aceder ao sector que chefia
    if is_chefe_sector(user) and user.sector_atual == sector:
        return True
    
    return False


def can_manage_sector(user, sector):
    """
    Verifica se o utilizador pode gerir um sector específico.
    """
    if not user.is_authenticated:
        return False
    
    # PCA pode gerir todos os sectores
    if is_pca(user):
        return True
    
    # Chefe pode gerir o sector que chefia
    if is_chefe_sector(user) and user.sector_atual == sector:
        return True
    
    return False


def can_view_document(user, documento):
    """
    Verifica se o utilizador pode visualizar um documento específico.
    """
    if not user.is_authenticated:
        return False
    
    # PCA pode visualizar todos os documentos
    if is_pca(user):
        return True
    
    # Verifica se o documento pertence ao sector do utilizador
    if hasattr(documento, 'sector_atual') and documento.sector_atual == user.sector_atual:
        return True
    
    # Verifica se o utilizador é o autor do documento
    if hasattr(documento, 'autor') and documento.autor == user:
        return True
    
    # Verifica se o utilizador é destinatário do documento
    if hasattr(documento, 'destinatario') and documento.destinatario == user:
        return True
    
    return False


def can_edit_document(user, documento):
    """
    Verifica se o utilizador pode editar um documento específico.
    """
    if not user.is_authenticated:
        return False
    
    # PCA pode editar todos os documentos
    if is_pca(user):
        return True
    
    # Chefe pode editar documentos do seu sector
    if is_chefe_sector(user) and hasattr(documento, 'sector_atual'):
        if documento.sector_atual == user.sector_atual:
            return True
    
    # Utilizador pode editar documentos que criou
    if hasattr(documento, 'autor') and documento.autor == user:
        return True
    
    return False


def can_delete_document(user, documento):
    """
    Verifica se o utilizador pode apagar um documento específico.
    """
    if not user.is_authenticated:
        return False
    
    # Apenas PCA pode apagar documentos
    return is_pca(user)


def can_create_despacho(user, tipo):
    """
    Verifica se o utilizador pode criar um despacho/parecer/comentário.
    """
    if not user.is_authenticated:
        return False
    
    # Todos podem criar comentários
    if tipo == 'comentario':
        return True
    
    # Apenas PCA e Chefes podem criar despachos e pareceres
    if tipo in ['despacho', 'parecer']:
        return is_pca_or_chefe(user)
    
    return False


def can_edit_despacho(user, despacho):
    """
    Verifica se o utilizador pode editar um despacho específico.
    """
    if not user.is_authenticated:
        return False
    
    # Apenas o autor pode editar
    if despacho.autor != user:
        return False
    
    # Verifica limite de tempo (24h)
    from django.utils import timezone
    from datetime import timedelta
    
    limite_tempo = timezone.now() - timedelta(days=1)
    return despacho.data_criacao >= limite_tempo


def can_view_despacho(user, despacho):
    """
    Verifica se o utilizador pode visualizar um despacho específico.
    """
    if not user.is_authenticated:
        return False
    
    # Verifica visibilidade
    if despacho.visivel_para == 'todos':
        return True
    
    if despacho.visivel_para == 'chefes':
        return is_pca_or_chefe(user)
    
    if despacho.visivel_para == 'pca':
        return is_pca(user)
    
    return False


def has_permission_for_document(user, documento, action='view'):
    """
    Função principal para verificar permissões de documentos.
    
    Args:
        user: Utilizador a verificar
        documento: Documento em questão
        action: Ação a verificar ('view', 'edit', 'delete')
    
    Returns:
        bool: True se tem permissão, False caso contrário
    """
    if not user.is_authenticated:
        return False
    
    if action == 'view':
        return can_view_document(user, documento)
    elif action == 'edit':
        return can_edit_document(user, documento)
    elif action == 'delete':
        return can_delete_document(user, documento)
    
    return False


def get_user_hierarchy_level(user):
    """
    Retorna o nível hierárquico do utilizador.
    
    Returns:
        int: 0 = PCA, 1 = Chefe, 2 = Colaborador
    """
    if not user.is_authenticated:
        return -1
    
    if is_pca(user):
        return 0
    elif is_chefe_sector(user):
        return 1
    else:
        return 2


def can_access_higher_level(user, target_level):
    """
    Verifica se o utilizador pode aceder a um nível hierárquico superior.
    """
    user_level = get_user_hierarchy_level(user)
    return user_level <= target_level
