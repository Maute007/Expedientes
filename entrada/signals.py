from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
import logging

from .models import Expediente, MovimentacaoDocumento
from core.utils import enviar_notificacao

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=Expediente)
def notificar_novo_expediente(sender, instance, created, **kwargs):
    """
    Signal para notificar quando um novo expediente é criado.
    Notifica o PCA (diretor) e a secretaria.
    """
    if not created:
        return
    
    try:
        # Buscar usuários PCA (diretor) e secretaria
        usuarios_pca = User.objects.filter(tipo_utilizador='pca', ativo=True)
        usuarios_secretaria = User.objects.filter(tipo_utilizador='secretaria', ativo=True)
        
        # Preparar dados da notificação
        titulo = "Novo Expediente Registado"
        mensagem = f"Foi registado um novo expediente: {instance.numero_protocolo}"
        
        if instance.assunto:
            mensagem += f" - {instance.assunto}"
        
        # Notificar PCA (diretor)
        for pca in usuarios_pca:
            enviar_notificacao(
                destinatario=pca,
                titulo=titulo,
                mensagem=mensagem,
                tipo='documento_novo',
                documento=instance,
                prioridade='urgente'
            )
            logger.info(f'Notificação de novo expediente enviada para PCA: {pca.email}')
        
        # Notificar Secretaria
        for secretaria in usuarios_secretaria:
            enviar_notificacao(
                destinatario=secretaria,
                titulo=titulo,
                mensagem=mensagem,
                tipo='documento_novo',
                documento=instance,
                prioridade='normal'
            )
            logger.info(f'Notificação de novo expediente enviada para Secretaria: {secretaria.email}')
        
        # Log geral
        logger.info(f'Notificações de novo expediente {instance.numero_protocolo} enviadas para {usuarios_pca.count()} PCA(s) e {usuarios_secretaria.count()} Secretaria(s)')
        
    except Exception as e:
        logger.error(f'Erro ao enviar notificações de novo expediente: {e}')


@receiver(post_save, sender=Expediente)
def encaminhar_para_pca(sender, instance, created, **kwargs):
    """
    Signal para encaminhar automaticamente novos expedientes para o PCA.
    """
    if not created:
        return
    
    try:
        # Buscar PCA (diretor) para encaminhar
        usuarios_pca = User.objects.filter(tipo_utilizador='pca', ativo=True).first()
        
        if usuarios_pca:
            # Atualizar o expediente para ser encaminhado para o PCA
            instance.sector_responsavel = usuarios_pca.sector_atual if usuarios_pca.sector_atual else None
            instance.utilizador_atual = usuarios_pca  # ADICIONAR ESTA LINHA
            instance.save(update_fields=['sector_responsavel', 'utilizador_atual'])  # ATUALIZAR LISTA
            
            # Adicionar PCA aos membros envolvidos
            instance.membros_envolvidos.add(usuarios_pca)
            
            logger.info(f'Expediente {instance.numero_protocolo} encaminhado automaticamente para PCA: {usuarios_pca.email}')
        
    except Exception as e:
        logger.error(f'Erro ao encaminhar expediente para PCA: {e}')


@receiver(post_save, sender=Expediente)
def notificar_mudanca_estado_expediente(sender, instance, **kwargs):
    """
    Signal para notificar mudanças de estado do expediente.
    """
    if not hasattr(instance, '_state') or instance._state.adding:
        return  # Documento novo sendo criado
    
    try:
        # Verificar se o estado mudou
        estado_anterior = getattr(instance, '_estado_anterior', None)
        estado_atual = instance.estado_atual
        
        if estado_anterior and estado_anterior != estado_atual:
            # Estado mudou, enviar notificações
            titulo = f"Estado do Expediente Alterado"
            mensagem = f"O expediente {instance.numero_protocolo} foi alterado de '{estado_anterior.nome}' para '{estado_atual.nome}'"
            
            # Notificar PCA
            usuarios_pca = User.objects.filter(tipo_utilizador='pca', ativo=True)
            for pca in usuarios_pca:
                enviar_notificacao(
                    destinatario=pca,
                    titulo=titulo,
                    mensagem=mensagem,
                    tipo='mudanca_estado',
                    documento=instance,
                    prioridade='normal'
                )
            
            # Notificar Secretaria
            usuarios_secretaria = User.objects.filter(tipo_utilizador='secretaria', ativo=True)
            for secretaria in usuarios_secretaria:
                enviar_notificacao(
                    destinatario=secretaria,
                    titulo=titulo,
                    mensagem=mensagem,
                    tipo='mudanca_estado',
                    documento=instance,
                    prioridade='normal'
                )
            
            logger.info(f'Notificações de mudança de estado enviadas para expediente {instance.numero_protocolo}')
            
    except Exception as e:
        logger.error(f'Erro ao enviar notificações de mudança de estado: {e}')


@receiver(post_save, sender=Expediente)
def salvar_estado_anterior(sender, instance, **kwargs):
    """
    Signal para salvar o estado anterior antes de uma mudança.
    """
    if not hasattr(instance, '_state') or instance._state.adding:
        return  # Documento novo sendo criado
    
    try:
        # Salvar estado atual como anterior para próxima comparação
        if instance.estado_atual:
            instance._estado_anterior = instance.estado_atual
            
    except Exception as e:
        logger.error(f'Erro ao salvar estado anterior: {e}')


@receiver(post_save, sender=Expediente)
def marcar_como_recebido_automatico(sender, instance, created, **kwargs):
    """
    Signal para marcar automaticamente como "Recebido" quando documento é visualizado pela primeira vez.
    Este signal será disparado quando o utilizador_atual for definido.
    """
    if created:
        return  # Não processar documentos novos
    
    try:
        # Verificar se utilizador_atual foi definido e não havia antes
        if instance.utilizador_atual and not instance.data_recebido:
            # Marcar como recebido automaticamente
            instance.data_recebido = timezone.now()
            instance.recebido_por = instance.utilizador_atual
            instance.save(update_fields=['data_recebido', 'recebido_por'])
            
            # Criar movimentação de recebimento
            MovimentacaoDocumento.objects.create(
                documento=instance,
                para_utilizador=instance.utilizador_atual,
                para_sector=instance.utilizador_atual.sector_atual if hasattr(instance.utilizador_atual, 'sector_atual') else None,
                tipo_movimentacao='recebimento',
                observacoes='Documento marcado como recebido automaticamente',
                automatica=True
            )
            
            logger.info(f'Expediente {instance.numero_protocolo} marcado como recebido automaticamente por {instance.utilizador_atual.email}')
            
    except Exception as e:
        logger.error(f'Erro ao marcar expediente como recebido automaticamente: {e}')


@receiver(post_save, sender=Expediente)
def criar_historico_movimentacao(sender, instance, created, **kwargs):
    """
    Signal para criar histórico automático de movimentações.
    
    OBS: Signal DESABILITADO para evitar duplicação de movimentações e notificações.
    As movimentações devem ser criadas manualmente nas views com as notificações correspondentes.
    """
    # Desabilitar este signal para evitar duplicação
    return
    
    if created:
        return  # Não processar documentos novos
    
    try:
        # Verificar se houve mudança de utilizador_atual
        if hasattr(instance, '_utilizador_atual_anterior'):
            utilizador_anterior = instance._utilizador_atual_anterior
            utilizador_atual = instance.utilizador_atual
            
            if utilizador_anterior != utilizador_atual:
                # Criar movimentação
                MovimentacaoDocumento.objects.create(
                    documento=instance,
                    de_utilizador=utilizador_anterior,
                    para_utilizador=utilizador_atual,
                    de_sector=utilizador_anterior.sector_atual if utilizador_anterior and hasattr(utilizador_anterior, 'sector_atual') else None,
                    para_sector=utilizador_atual.sector_atual if utilizador_atual and hasattr(utilizador_atual, 'sector_atual') else None,
                    tipo_movimentacao='encaminhamento',
                    observacoes='Movimentação automática de documento',
                    automatica=True
                )
                
                logger.info(f'Movimentação automática criada para expediente {instance.numero_protocolo}')
                
    except Exception as e:
        logger.error(f'Erro ao criar histórico de movimentação: {e}')


@receiver(pre_save, sender=Expediente)
def salvar_utilizador_atual_anterior(sender, instance, **kwargs):
    """
    Signal para salvar o utilizador_atual anterior antes de uma mudança.
    """
    if not hasattr(instance, '_state') or instance._state.adding:
        return  # Documento novo sendo criado
    
    try:
        # Salvar utilizador_atual atual como anterior para próxima comparação
        if instance.pk:
            try:
                instance_anterior = Expediente.objects.get(pk=instance.pk)
                instance._utilizador_atual_anterior = instance_anterior.utilizador_atual
            except Expediente.DoesNotExist:
                instance._utilizador_atual_anterior = None
                
    except Exception as e:
        logger.error(f'Erro ao salvar utilizador_atual anterior: {e}')
