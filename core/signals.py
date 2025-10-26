from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import logging

from .models import Notificacao, EstadoDocumento
from .utils import (
    enviar_notificacao, 
    notificar_pca, 
    notificar_chefe_sector,
    enviar_notificacoes_massa
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Notificacao)
def log_notificacao_criada(sender, instance, created, **kwargs):
    """
    Log quando uma notificação é criada.
    """
    if created:
        logger.info(f'Notificação criada: {instance.titulo} para {instance.destinatario.username}')


# Signals genéricos para documentos
# Estes signals serão conectados dinamicamente quando os modelos de documento forem criados

def notificar_mudanca_estado(sender, instance, **kwargs):
    """
    Signal para notificar mudança de estado de documento.
    """
    if not hasattr(instance, 'estado_atual') or not instance.estado_atual:
        return
    
    # Verificar se o estado mudou
    if hasattr(instance, '_state') and instance._state.adding:
        # Documento novo sendo criado
        return
    
    try:
        # Obter estado anterior (se existir)
        estado_anterior = getattr(instance, '_estado_anterior', None)
        estado_atual = instance.estado_atual
        
        if estado_anterior and estado_anterior != estado_atual:
            # Estado mudou, enviar notificação
            titulo = f"Estado alterado para {estado_atual.nome}"
            mensagem = f"O documento foi alterado de '{estado_anterior.nome}' para '{estado_atual.nome}'"
            
            # Notificar PCA
            notificar_pca(titulo, mensagem, instance)
            
            # Notificar chefe do sector se aplicável
            if hasattr(instance, 'sector_atual') and instance.sector_atual:
                notificar_chefe_sector(
                    instance.sector_atual, 
                    titulo, 
                    mensagem, 
                    instance
                )
            
            logger.info(f'Notificação de mudança de estado enviada para documento {instance.id}')
            
    except Exception as e:
        logger.error(f'Erro ao enviar notificação de mudança de estado: {e}')


def notificar_encaminhamento_documento(sender, instance, **kwargs):
    """
    Signal para notificar encaminhamento de documento.
    """
    if not hasattr(instance, 'destinatario') or not instance.destinatario:
        return
    
    try:
        titulo = "Documento encaminhado"
        mensagem = f"Um documento foi encaminhado para si"
        
        # Notificar destinatário
        enviar_notificacao(
            destinatario=instance.destinatario,
            titulo=titulo,
            mensagem=mensagem,
            tipo='documento_encaminhado',
            documento=instance,
            prioridade='normal'
        )
        
        logger.info(f'Notificação de encaminhamento enviada para {instance.destinatario.username}')
        
    except Exception as e:
        logger.error(f'Erro ao enviar notificação de encaminhamento: {e}')


def notificar_rececao_documento(sender, instance, **kwargs):
    """
    Signal para notificar receção de documento (quando é aberto pela primeira vez).
    """
    if not hasattr(instance, 'destinatario') or not instance.destinatario:
        return
    
    # Verificar se é a primeira vez que o documento é acedido
    if hasattr(instance, 'data_primeiro_acesso') and instance.data_primeiro_acesso:
        return  # Já foi acedido antes
    
    try:
        titulo = "Documento recebido"
        mensagem = f"Recebeu um novo documento para processar"
        
        # Notificar destinatário
        enviar_notificacao(
            destinatario=instance.destinatario,
            titulo=titulo,
            mensagem=mensagem,
            tipo='documento_recebido',
            documento=instance,
            prioridade='normal'
        )
        
        # Marcar como acedido pela primeira vez
        if hasattr(instance, 'data_primeiro_acesso'):
            instance.data_primeiro_acesso = timezone.now()
            instance.save(update_fields=['data_primeiro_acesso'])
        
        logger.info(f'Notificação de receção enviada para {instance.destinatario.username}')
        
    except Exception as e:
        logger.error(f'Erro ao enviar notificação de receção: {e}')


def notificar_conclusao_documento(sender, instance, **kwargs):
    """
    Signal para notificar conclusão de documento (notifica PCA).
    """
    if not hasattr(instance, 'estado_atual') or not instance.estado_atual:
        return
    
    # Verificar se o estado é "Concluído"
    if instance.estado_atual.nome != 'Concluído':
        return
    
    try:
        titulo = "Documento concluído"
        mensagem = f"Um documento foi concluído e está pronto para arquivamento"
        
        # Notificar PCA
        notificar_pca(titulo, mensagem, instance)
        
        # Notificar chefe do sector se aplicável
        if hasattr(instance, 'sector_atual') and instance.sector_atual:
            notificar_chefe_sector(
                instance.sector_atual, 
                titulo, 
                mensagem, 
                instance
            )
        
        logger.info(f'Notificação de conclusão enviada para documento {instance.id}')
        
    except Exception as e:
        logger.error(f'Erro ao enviar notificação de conclusão: {e}')


def notificar_arquivamento_documento(sender, instance, **kwargs):
    """
    Signal para notificar arquivamento de documento.
    """
    if not hasattr(instance, 'estado_atual') or not instance.estado_atual:
        return
    
    # Verificar se o estado é "Arquivado"
    if instance.estado_atual.nome != 'Arquivado':
        return
    
    try:
        titulo = "Documento arquivado"
        mensagem = f"Um documento foi arquivado definitivamente"
        
        # Notificar PCA
        notificar_pca(titulo, mensagem, instance)
        
        # Notificar todos os utilizadores que estiveram envolvidos no documento
        utilizadores_envolvidos = set()
        
        # Adicionar autor se existir
        if hasattr(instance, 'autor') and instance.autor:
            utilizadores_envolvidos.add(instance.autor)
        
        # Adicionar destinatário se existir
        if hasattr(instance, 'destinatario') and instance.destinatario:
            utilizadores_envolvidos.add(instance.destinatario)
        
        # Adicionar chefe do sector se aplicável
        if hasattr(instance, 'sector_atual') and instance.sector_atual:
            chefe = instance.sector_atual.obter_chefe()
            if chefe:
                utilizadores_envolvidos.add(chefe)
        
        # Enviar notificação para todos os utilizadores envolvidos
        if utilizadores_envolvidos:
            enviar_notificacoes_massa(
                destinatarios=list(utilizadores_envolvidos),
                titulo=titulo,
                mensagem=mensagem,
                tipo='documento_arquivado',
                documento=instance
            )
        
        logger.info(f'Notificação de arquivamento enviada para documento {instance.id}')
        
    except Exception as e:
        logger.error(f'Erro ao enviar notificação de arquivamento: {e}')


def notificar_devolucao_documento(sender, instance, **kwargs):
    """
    Signal para notificar devolução de documento.
    """
    if not hasattr(instance, 'estado_atual') or not instance.estado_atual:
        return
    
    # Verificar se o estado é "Devolvido"
    if instance.estado_atual.nome != 'Devolvido':
        return
    
    try:
        titulo = "Documento devolvido"
        mensagem = f"Um documento foi devolvido para reanálise"
        
        # Notificar PCA
        notificar_pca(titulo, mensagem, instance)
        
        # Notificar chefe do sector se aplicável
        if hasattr(instance, 'sector_atual') and instance.sector_atual:
            notificar_chefe_sector(
                instance.sector_atual, 
                titulo, 
                mensagem, 
                instance
            )
        
        logger.info(f'Notificação de devolução enviada para documento {instance.id}')
        
    except Exception as e:
        logger.error(f'Erro ao enviar notificação de devolução: {e}')


def notificar_despacho_criado(sender, instance, created, **kwargs):
    """
    Signal para notificar quando um despacho/parecer/comentário é criado.
    """
    if not created:
        return
    
    try:
        # Determinar o tipo de notificação baseado no tipo do despacho
        tipo_notificacao = 'mensagem_nova'  # Padrão
        
        if instance.tipo == 'despacho':
            tipo_notificacao = 'documento_encaminhado'
        elif instance.tipo == 'parecer':
            tipo_notificacao = 'documento_concluido'
        
        titulo = f"{instance.get_tipo_display()} adicionado"
        mensagem = f"{instance.autor.get_full_name()} adicionou um {instance.get_tipo_display().lower()}"
        
        # Determinar destinatários baseado na visibilidade
        destinatarios = []
        
        if instance.visivel_para == 'todos':
            # Notificar todos os utilizadores do sector do documento
            if hasattr(instance.documento, 'sector_atual') and instance.documento.sector_atual:
                destinatarios = list(instance.documento.sector_atual.obter_colaboradores())
        
        elif instance.visivel_para == 'chefes':
            # Notificar apenas chefes e PCA
            destinatarios = list(User.objects.filter(is_superuser=True))  # PCA
            if hasattr(instance.documento, 'sector_atual') and instance.documento.sector_atual:
                chefe = instance.documento.sector_atual.obter_chefe()
                if chefe:
                    destinatarios.append(chefe)
        
        elif instance.visivel_para == 'pca':
            # Notificar apenas PCA
            destinatarios = list(User.objects.filter(is_superuser=True))
        
        # Remover o autor da lista de destinatários
        destinatarios = [d for d in destinatarios if d != instance.autor]
        
        # Enviar notificações
        if destinatarios:
            enviar_notificacoes_massa(
                destinatarios=destinatarios,
                titulo=titulo,
                mensagem=mensagem,
                tipo=tipo_notificacao,
                remetente=instance.autor,
                documento=instance.documento
            )
        
        logger.info(f'Notificação de {instance.tipo} enviada para {len(destinatarios)} destinatários')
        
    except Exception as e:
        logger.error(f'Erro ao enviar notificação de despacho: {e}')


# Função para conectar signals dinamicamente
def conectar_signals_documento(model_class):
    """
    Conecta os signals de notificação a um modelo de documento específico.
    
    Args:
        model_class: Classe do modelo de documento
    """
    try:
        # Conectar signals
        post_save.connect(notificar_mudanca_estado, sender=model_class)
        post_save.connect(notificar_encaminhamento_documento, sender=model_class)
        post_save.connect(notificar_rececao_documento, sender=model_class)
        post_save.connect(notificar_conclusao_documento, sender=model_class)
        post_save.connect(notificar_arquivamento_documento, sender=model_class)
        post_save.connect(notificar_devolucao_documento, sender=model_class)
        
        logger.info(f'Signals conectados ao modelo {model_class.__name__}')
        
    except Exception as e:
        logger.error(f'Erro ao conectar signals ao modelo {model_class.__name__}: {e}')


# Conectar signals para DespachoDocumento
from .models import DespachoDocumento
post_save.connect(notificar_despacho_criado, sender=DespachoDocumento)
