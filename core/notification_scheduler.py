from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Notificacao, ConfiguracaoSistema
import logging

logger = logging.getLogger(__name__)


def process_pending_notifications():
    """
    Processa notificações pendentes baseado na frequência configurada.
    """
    try:
        # Obter frequência configurada
        frequencia = ConfiguracaoSistema.obter_configuracao(
            'frequencia_notificacoes', 
            valor_padrao='imediata'
        )
        
        if frequencia == 'imediata':
            # Notificações imediatas já são processadas na criação
            return
        
        # Obter notificações pendentes de envio por email
        notificacoes_pendentes = Notificacao.objects.filter(
            email_enviado=False,
            data_criacao__gte=timezone.now() - timezone.timedelta(days=1)  # Últimas 24h
        )
        
        if frequencia == 'diaria':
            # Enviar notificações diárias (apenas uma vez por dia)
            enviar_notificacoes_diarias(notificacoes_pendentes)
        elif frequencia == 'semanal':
            # Enviar notificações semanais (apenas uma vez por semana)
            enviar_notificacoes_semanais(notificacoes_pendentes)
            
    except Exception as e:
        logger.error(f"Erro ao processar notificações pendentes: {e}")


def enviar_notificacoes_diarias(notificacoes):
    """
    Envia resumo diário de notificações.
    """
    try:
        # Agrupar por destinatário
        destinatarios = {}
        for notificacao in notificacoes:
            if notificacao.destinatario.email:
                if notificacao.destinatario not in destinatarios:
                    destinatarios[notificacao.destinatario] = []
                destinatarios[notificacao.destinatario].append(notificacao)
        
        # Enviar resumo para cada destinatário
        for destinatario, notificacoes_user in destinatarios.items():
            enviar_resumo_diario(destinatario, notificacoes_user)
            
            # Marcar como enviadas
            for notificacao in notificacoes_user:
                notificacao.email_enviado = True
                notificacao.save()
                
    except Exception as e:
        logger.error(f"Erro ao enviar notificações diárias: {e}")


def enviar_notificacoes_semanais(notificacoes):
    """
    Envia resumo semanal de notificações.
    """
    try:
        # Agrupar por destinatário
        destinatarios = {}
        for notificacao in notificacoes:
            if notificacao.destinatario.email:
                if notificacao.destinatario not in destinatarios:
                    destinatarios[notificacao.destinatario] = []
                destinatarios[notificacao.destinatario].append(notificacao)
        
        # Enviar resumo para cada destinatário
        for destinatario, notificacoes_user in destinatarios.items():
            enviar_resumo_semanal(destinatario, notificacoes_user)
            
            # Marcar como enviadas
            for notificacao in notificacoes_user:
                notificacao.email_enviado = True
                notificacao.save()
                
    except Exception as e:
        logger.error(f"Erro ao enviar notificações semanais: {e}")


def enviar_resumo_diario(destinatario, notificacoes):
    """
    Envia resumo diário de notificações para um destinatário.
    """
    try:
        nome_sistema = ConfiguracaoSistema.obter_configuracao(
            'nome_sistema', 
            valor_padrao='FTC Sistema de Correspondência'
        )
        
        subject = f"[{nome_sistema}] Resumo Diário - {len(notificacoes)} notificações"
        
        # Criar HTML do resumo
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #1F2937; border-bottom: 2px solid #E5E7EB; padding-bottom: 10px;">
                    Resumo Diário - {len(notificacoes)} notificações
                </h2>
                
                <div style="background: #F9FAFB; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0; font-size: 16px;">
                        Olá {destinatario.get_full_name()},<br><br>
                        Você tem {len(notificacoes)} notificações pendentes no sistema.
                    </p>
                </div>
        """
        
        # Adicionar lista de notificações
        for notificacao in notificacoes[:10]:  # Limitar a 10 notificações
            html_message += f"""
                <div style="border: 1px solid #E5E7EB; border-radius: 8px; padding: 15px; margin: 10px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #1F2937;">{notificacao.titulo}</h4>
                    <p style="margin: 0 0 10px 0; color: #6B7280;">{notificacao.mensagem}</p>
                    <small style="color: #9CA3AF;">
                        {notificacao.get_tipo_display()} • {notificacao.data_criacao.strftime('%d/%m/%Y às %H:%M')}
                    </small>
                </div>
            """
        
        if len(notificacoes) > 10:
            html_message += f"""
                <div style="text-align: center; margin: 20px 0; padding: 15px; background: #EFF6FF; border-radius: 8px;">
                    <p style="margin: 0; color: #1E40AF;">
                        E mais {len(notificacoes) - 10} notificações...
                    </p>
                </div>
            """
        
        html_message += """
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{}/notificacoes/" 
                       style="background: #1F2937; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                        Ver Todas as Notificações
                    </a>
                </div>
                
                <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 30px 0;">
                <p style="font-size: 12px; color: #6B7280; text-align: center;">
                    Este é um resumo automático do {}.<br>
                    Não responda a este email.
                </p>
            </div>
        </body>
        </html>
        """.format(getattr(settings, 'SITE_URL', 'http://localhost:8000'), nome_sistema)
        
        # Enviar email
        send_mail(
            subject=subject,
            message=f"Você tem {len(notificacoes)} notificações pendentes no {nome_sistema}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinatario.email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Resumo diário enviado para {destinatario.email}")
        
    except Exception as e:
        logger.error(f"Erro ao enviar resumo diário: {e}")


def enviar_resumo_semanal(destinatario, notificacoes):
    """
    Envia resumo semanal de notificações para um destinatário.
    """
    try:
        nome_sistema = ConfiguracaoSistema.obter_configuracao(
            'nome_sistema', 
            valor_padrao='FTC Sistema de Correspondência'
        )
        
        subject = f"[{nome_sistema}] Resumo Semanal - {len(notificacoes)} notificações"
        
        # Criar HTML do resumo
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #1F2937; border-bottom: 2px solid #E5E7EB; padding-bottom: 10px;">
                    Resumo Semanal - {len(notificacoes)} notificações
                </h2>
                
                <div style="background: #F9FAFB; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0; font-size: 16px;">
                        Olá {destinatario.get_full_name()},<br><br>
                        Esta semana você recebeu {len(notificacoes)} notificações no sistema.
                    </p>
                </div>
        """
        
        # Adicionar lista de notificações
        for notificacao in notificacoes[:15]:  # Limitar a 15 notificações
            html_message += f"""
                <div style="border: 1px solid #E5E7EB; border-radius: 8px; padding: 15px; margin: 10px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #1F2937;">{notificacao.titulo}</h4>
                    <p style="margin: 0 0 10px 0; color: #6B7280;">{notificacao.mensagem}</p>
                    <small style="color: #9CA3AF;">
                        {notificacao.get_tipo_display()} • {notificacao.data_criacao.strftime('%d/%m/%Y às %H:%M')}
                    </small>
                </div>
            """
        
        if len(notificacoes) > 15:
            html_message += f"""
                <div style="text-align: center; margin: 20px 0; padding: 15px; background: #EFF6FF; border-radius: 8px;">
                    <p style="margin: 0; color: #1E40AF;">
                        E mais {len(notificacoes) - 15} notificações...
                    </p>
                </div>
            """
        
        html_message += """
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{}/notificacoes/" 
                       style="background: #1F2937; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                        Ver Todas as Notificações
                    </a>
                </div>
                
                <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 30px 0;">
                <p style="font-size: 12px; color: #6B7280; text-align: center;">
                    Este é um resumo automático do {}.<br>
                    Não responda a este email.
                </p>
            </div>
        </body>
        </html>
        """.format(getattr(settings, 'SITE_URL', 'http://localhost:8000'), nome_sistema)
        
        # Enviar email
        send_mail(
            subject=subject,
            message=f"Esta semana você recebeu {len(notificacoes)} notificações no {nome_sistema}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinatario.email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Resumo semanal enviado para {destinatario.email}")
        
    except Exception as e:
        logger.error(f"Erro ao enviar resumo semanal: {e}")
