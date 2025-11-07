import logging
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Notificacao, Sector, ConfiguracaoSistema

logger = logging.getLogger(__name__)
User = get_user_model()

# Constante para ícones de notificação
ICONES_NOTIFICACAO = {
    'documento_novo': 'bi-file-earmark-plus',
    'documento_encaminhado': 'bi-arrow-right-circle',
    'documento_recebido': 'bi-download',
    'documento_concluido': 'bi-check-circle',
    'documento_arquivado': 'bi-archive',
    'documento_devolvido': 'bi-arrow-left-circle',
    'documento_assinado': 'bi-pen-fill',
    'mensagem_nova': 'bi-chat-dots'
}


def enviar_notificacao(destinatario, titulo, mensagem, tipo, remetente=None, documento=None, prioridade='normal'):
    """
    Envia uma notificação para um utilizador específico.
    
    Args:
        destinatario: User - utilizador destinatário
        titulo: str - título da notificação
        mensagem: str - mensagem da notificação
        tipo: str - tipo da notificação (deve estar em TIPOS_NOTIFICACAO)
        remetente: User - utilizador remetente (opcional)
        documento: Model - documento relacionado (opcional)
        prioridade: str - prioridade ('normal' ou 'urgente')
    
    Returns:
        Notificacao: instância da notificação criada ou None se erro
    """
    try:
        # Validar se destinatario é instância de User
        if not isinstance(destinatario, User):
            logger.error(f"Destinatário deve ser instância de User, recebido: {type(destinatario)}")
            return None
        
        # Validar se tipo está em TIPOS_NOTIFICACAO válidos
        tipos_validos = [choice[0] for choice in Notificacao.TIPOS_NOTIFICACAO]
        if tipo not in tipos_validos:
            logger.error(f"Tipo de notificação inválido: {tipo}. Tipos válidos: {tipos_validos}")
            return None
        
        # Validar prioridade
        prioridades_validas = [choice[0] for choice in Notificacao.PRIORIDADES]
        if prioridade not in prioridades_validas:
            logger.warning(f"Prioridade inválida: {prioridade}. Usando 'normal'")
            prioridade = 'normal'
        
        # Preparar dados para criação
        notificacao_data = {
            'destinatario': destinatario,
            'titulo': titulo,
            'mensagem': mensagem,
            'tipo': tipo,
            'prioridade': prioridade
        }
        
        # Adicionar remetente se fornecido
        if remetente and isinstance(remetente, User):
            notificacao_data['remetente'] = remetente
        
        # Adicionar documento relacionado se fornecido
        if documento:
            try:
                content_type = ContentType.objects.get_for_model(documento)
                notificacao_data['content_type'] = content_type
                notificacao_data['object_id'] = documento.pk
            except Exception as e:
                logger.warning(f"Erro ao obter ContentType para documento: {e}")
        
        # Criar notificação
        notificacao = Notificacao.objects.create(**notificacao_data)
        
        # Enviar email se configurado
        enviar_notificacao_email(notificacao)
        
        # Log da criação da notificação
        logger.info(f"Notificação criada: {notificacao.titulo} para {destinatario.get_full_name()}")
        
        return notificacao
        
    except Exception as e:
        logger.error(f"Erro ao criar notificação: {e}")
        return None


def enviar_notificacoes_massa(destinatarios, titulo, mensagem, tipo, remetente=None, documento=None):
    """
    Envia notificações para múltiplos utilizadores.
    
    Args:
        destinatarios: list/QuerySet - lista de utilizadores destinatários
        titulo: str - título da notificação
        mensagem: str - mensagem da notificação
        tipo: str - tipo da notificação
        remetente: User - utilizador remetente (opcional)
        documento: Model - documento relacionado (opcional)
    
    Returns:
        list: lista de notificações criadas
    """
    notificacoes_criadas = []
    
    try:
        # Validar se destinatarios é lista/queryset de Users
        if not destinatarios:
            logger.warning("Lista de destinatários vazia")
            return notificacoes_criadas
        
        # Converter para lista se for QuerySet
        if hasattr(destinatarios, 'all'):
            destinatarios = list(destinatarios.all())
        
        # Loop para enviar notificação para cada destinatário
        for destinatario in destinatarios:
            if isinstance(destinatario, User):
                notificacao = enviar_notificacao(
                    destinatario=destinatario,
                    titulo=titulo,
                    mensagem=mensagem,
                    tipo=tipo,
                    remetente=remetente,
                    documento=documento
                )
                if notificacao:
                    notificacoes_criadas.append(notificacao)
            else:
                logger.warning(f"Destinatário inválido: {destinatario}")
        
        logger.info(f"Enviadas {len(notificacoes_criadas)} notificações em massa")
        
    except Exception as e:
        logger.error(f"Erro ao enviar notificações em massa: {e}")
    
    return notificacoes_criadas


def notificar_pca(titulo, mensagem, documento=None):
    """
    Envia notificação para o PCA.
    
    Args:
        titulo: str - título da notificação
        mensagem: str - mensagem da notificação
        documento: Model - documento relacionado (opcional)
    
    Returns:
        Notificacao: instância da notificação criada ou None se erro
    """
    try:
        # Buscar PCA
        pca = User.objects.filter(is_pca=True).first()
        
        if not pca:
            logger.error("PCA não encontrado no sistema")
            return None
        
        # Enviar notificação para PCA
        notificacao = enviar_notificacao(
            destinatario=pca,
            titulo=titulo,
            mensagem=mensagem,
            tipo='documento_novo',  # Tipo padrão para notificações do PCA
            documento=documento,
            prioridade='urgente'  # Notificações para PCA são urgentes por padrão
        )
        
        if notificacao:
            logger.info(f"Notificação enviada para PCA: {titulo}")
        
        return notificacao
        
    except Exception as e:
        logger.error(f"Erro ao notificar PCA: {e}")
        return None


def notificar_chefe_sector(sector, titulo, mensagem, documento=None):
    """
    Envia notificação para o chefe de um sector.
    
    Args:
        sector: Sector - sector cujo chefe deve ser notificado
        titulo: str - título da notificação
        mensagem: str - mensagem da notificação
        documento: Model - documento relacionado (opcional)
    
    Returns:
        Notificacao: instância da notificação criada ou None se erro
    """
    try:
        # Validar se sector é instância de Sector
        if not isinstance(sector, Sector):
            logger.error(f"Sector deve ser instância de Sector, recebido: {type(sector)}")
            return None
        
        # Obter chefe atual
        chefe_atual = sector.obter_chefe()
        
        if not chefe_atual:
            logger.error(f"Chefe não encontrado para sector: {sector.nome}")
            return None
        
        # Enviar notificação para chefe
        notificacao = enviar_notificacao(
            destinatario=chefe_atual,
            titulo=titulo,
            mensagem=mensagem,
            tipo='documento_encaminhado',  # Tipo padrão para notificações de chefes
            documento=documento,
            prioridade='normal'
        )
        
        if notificacao:
            logger.info(f"Notificação enviada para chefe {chefe_atual.get_full_name()} do sector {sector.nome}")
        
        return notificacao
        
    except Exception as e:
        logger.error(f"Erro ao notificar chefe do sector: {e}")
        return None


def notificar_colaboradores_sector(sector, titulo, mensagem, documento=None, excluir_chefe=True):
    """
    Envia notificação para todos os colaboradores de um sector.
    
    Args:
        sector: Sector - sector cujos colaboradores devem ser notificados
        titulo: str - título da notificação
        mensagem: str - mensagem da notificação
        documento: Model - documento relacionado (opcional)
        excluir_chefe: bool - se deve excluir o chefe da notificação
    
    Returns:
        list: lista de notificações criadas
    """
    try:
        # Validar se sector é instância de Sector
        if not isinstance(sector, Sector):
            logger.error(f"Sector deve ser instância de Sector, recebido: {type(sector)}")
            return []
        
        # Obter colaboradores do sector
        colaboradores = sector.obter_colaboradores()
        
        if excluir_chefe:
            chefe_atual = sector.obter_chefe()
            if chefe_atual:
                colaboradores = colaboradores.exclude(id=chefe_atual.id)
        
        # Enviar notificações em massa
        notificacoes = enviar_notificacoes_massa(
            destinatarios=colaboradores,
            titulo=titulo,
            mensagem=mensagem,
            tipo='mensagem_nova',
            documento=documento
        )
        
        logger.info(f"Notificações enviadas para {len(notificacoes)} colaboradores do sector {sector.nome}")
        
        return notificacoes
        
    except Exception as e:
        logger.error(f"Erro ao notificar colaboradores do sector: {e}")
        return []


def obter_icone_notificacao(tipo):
    """
    Obtém o ícone Bootstrap para um tipo de notificação.
    
    Args:
        tipo: str - tipo da notificação
    
    Returns:
        str: classe CSS do ícone Bootstrap
    """
    return ICONES_NOTIFICACAO.get(tipo, 'bi-bell')


def limpar_notificacoes_antigas(dias=30):
    """
    Remove notificações antigas para manter a base de dados limpa.
    
    Args:
        dias: int - número de dias para manter notificações
    
    Returns:
        int: número de notificações removidas
    """
    try:
        from datetime import timedelta
        
        data_limite = timezone.now() - timedelta(days=dias)
        
        # Remover notificações lidas antigas
        notificacoes_removidas = Notificacao.objects.filter(
            lida=True,
            data_criacao__lt=data_limite
        ).delete()[0]
        
        logger.info(f"Removidas {notificacoes_removidas} notificações antigas")
        
        return notificacoes_removidas
        
    except Exception as e:
        logger.error(f"Erro ao limpar notificações antigas: {e}")
        return 0


def enviar_notificacao_email(notificacao):
    """
    Envia notificação por email se configurado no sistema.
    
    Args:
        notificacao: Notificacao - instância da notificação
    """
    try:
        # Verificar se email está habilitado
        email_habilitado = ConfiguracaoSistema.obter_configuracao(
            'email_notificacoes', 
            valor_padrao=True
        )
        
        if not email_habilitado:
            return
        
        # Verificar se destinatário tem email
        if not notificacao.destinatario.email:
            logger.warning(f"Destinatário {notificacao.destinatario.get_full_name()} não tem email configurado")
            return
        
        # Obter nome do sistema
        nome_sistema = ConfiguracaoSistema.obter_configuracao(
            'nome_sistema', 
            valor_padrao='FTC Sistema de Processos'
        )
        
        # Preparar dados do email
        subject = f"[{nome_sistema}] {notificacao.titulo}"
        
        # Criar mensagem HTML
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #1F2937; border-bottom: 2px solid #E5E7EB; padding-bottom: 10px;">
                    {notificacao.titulo}
                </h2>
                
                <div style="background: #F9FAFB; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0; font-size: 16px;">{notificacao.mensagem}</p>
                </div>
                
                <div style="margin: 20px 0; padding: 15px; background: #EFF6FF; border-radius: 8px; border-left: 4px solid #3B82F6;">
                    <p style="margin: 0; font-size: 14px; color: #1E40AF;">
                        <strong>Tipo:</strong> {notificacao.get_tipo_display()}<br>
                        <strong>Prioridade:</strong> {notificacao.get_prioridade_display()}<br>
                        <strong>Data:</strong> {notificacao.data_criacao.strftime('%d/%m/%Y às %H:%M')}
                    </p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/notificacoes/" 
                       style="background: #1F2937; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                        Ver Notificação
                    </a>
                </div>
                
                <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 30px 0;">
                <p style="font-size: 12px; color: #6B7280; text-align: center;">
                    Esta é uma notificação automática do {nome_sistema}.<br>
                    Não responda a este email.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Enviar email
        send_mail(
            subject=subject,
            message=notificacao.mensagem,  # Versão texto simples
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notificacao.destinatario.email],
            html_message=html_message,
            fail_silently=False
        )
        
        # Marcar como enviado
        notificacao.email_enviado = True
        notificacao.save()
        
        logger.info(f"Email de notificação enviado para {notificacao.destinatario.email}")
        
    except Exception as e:
        logger.error(f"Erro ao enviar email de notificação: {e}")
