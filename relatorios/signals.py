from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import os
import logging

from .models import ConfiguracaoRelatorio, ExecucaoRelatorio, Dashboard, WidgetDashboard
from core.models import Notificacao

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=ExecucaoRelatorio)
def notificar_execucao_relatorio(sender, instance, created, **kwargs):
    """
    Notifica quando uma execução de relatório é criada ou atualizada.
    """
    if created:
        # Notificação de criação
        notificacao = Notificacao.objects.create(
            destinatario=instance.utilizador,
            titulo=f'Relatório "{instance.relatorio.nome}" em execução',
            mensagem=f'O relatório "{instance.relatorio.nome}" foi iniciado e está sendo processado.',
            tipo='documento_novo',
            lida=False
        )
        logger.info(f'Notificação criada para execução de relatório: {instance.pk}')
    
    elif instance.status == 'concluido':
        # Notificação de conclusão
        notificacao = Notificacao.objects.create(
            destinatario=instance.utilizador,
            titulo=f'Relatório "{instance.relatorio.nome}" concluído',
            mensagem=f'O relatório "{instance.relatorio.nome}" foi concluído com sucesso e está disponível para download.',
            tipo='documento_concluido',
            lida=False
        )
        logger.info(f'Notificação de conclusão criada para execução: {instance.pk}')
        
        # Enviar email se configurado
        if hasattr(settings, 'EMAIL_BACKEND') and settings.EMAIL_BACKEND:
            try:
                send_mail(
                    subject=f'Relatório "{instance.relatorio.nome}" concluído',
                    message=f'O relatório "{instance.relatorio.nome}" foi concluído com sucesso.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.utilizador.email],
                    fail_silently=True
                )
                logger.info(f'Email enviado para {instance.utilizador.email}')
            except Exception as e:
                logger.error(f'Erro ao enviar email: {e}')
    
    elif instance.status == 'erro':
        # Notificação de erro
        notificacao = Notificacao.objects.create(
            destinatario=instance.utilizador,
            titulo=f'Erro na execução do relatório "{instance.relatorio.nome}"',
            mensagem=f'Ocorreu um erro ao executar o relatório "{instance.relatorio.nome}". Detalhes: {instance.erro}',
            tipo='documento_devolvido',
            lida=False
        )
        logger.error(f'Notificação de erro criada para execução: {instance.pk}')


@receiver(post_save, sender=ConfiguracaoRelatorio)
def notificar_criacao_relatorio(sender, instance, created, **kwargs):
    """
    Notifica quando um novo relatório é criado.
    """
    if created:
        # Notificar administradores
        administradores = User.objects.filter(is_staff=True, is_active=True)
        
        for admin in administradores:
            if admin != instance.utilizador_criador:
                notificacao = Notificacao.objects.create(
                    destinatario=admin,
                    titulo=f'Novo relatório criado: "{instance.nome}"',
                    mensagem=f'O utilizador {instance.utilizador_criador.get_full_name()} criou um novo relatório: "{instance.nome}".',
                    tipo='documento_novo',
                    lida=False
                )
                logger.info(f'Notificação de novo relatório enviada para admin: {admin.username}')


@receiver(post_save, sender=Dashboard)
def notificar_criacao_dashboard(sender, instance, created, **kwargs):
    """
    Notifica quando um novo dashboard é criado.
    """
    if created:
        # Notificar administradores
        administradores = User.objects.filter(is_staff=True, is_active=True)
        
        for admin in administradores:
            if admin != instance.utilizador_criador:
                notificacao = Notificacao.objects.create(
                    destinatario=admin,
                    titulo=f'Novo dashboard criado: "{instance.nome}"',
                    mensagem=f'O utilizador {instance.utilizador_criador.get_full_name()} criou um novo dashboard: "{instance.nome}".',
                    tipo='documento_novo',
                    lida=False
                )
                logger.info(f'Notificação de novo dashboard enviada para admin: {admin.username}')


@receiver(post_delete, sender=ExecucaoRelatorio)
def limpar_ficheiro_execucao(sender, instance, **kwargs):
    """
    Remove o ficheiro gerado quando uma execução é apagada.
    """
    if instance.ficheiro_gerado:
        try:
            if os.path.exists(instance.ficheiro_gerado.path):
                os.remove(instance.ficheiro_gerado.path)
                logger.info(f'Ficheiro removido: {instance.ficheiro_gerado.path}')
        except Exception as e:
            logger.error(f'Erro ao remover ficheiro: {e}')


@receiver(post_delete, sender=ConfiguracaoRelatorio)
def limpar_execucoes_relatorio(sender, instance, **kwargs):
    """
    Remove todas as execuções quando um relatório é apagado.
    """
    execucoes = ExecucaoRelatorio.objects.filter(relatorio=instance)
    for execucao in execucoes:
        if execucao.ficheiro_gerado:
            try:
                if os.path.exists(execucao.ficheiro_gerado.path):
                    os.remove(execucao.ficheiro_gerado.path)
                    logger.info(f'Ficheiro removido: {execucao.ficheiro_gerado.path}')
            except Exception as e:
                logger.error(f'Erro ao remover ficheiro: {e}')
    
    logger.info(f'Execuções removidas para relatório: {instance.nome}')


@receiver(post_delete, sender=Dashboard)
def limpar_widgets_dashboard(sender, instance, **kwargs):
    """
    Remove todos os widgets quando um dashboard é apagado.
    """
    widgets = WidgetDashboard.objects.filter(dashboard=instance)
    for widget in widgets:
        widget.delete()
    
    logger.info(f'Widgets removidos para dashboard: {instance.nome}')


# Signal para limpeza automática de ficheiros antigos
def limpar_ficheiros_antigos():
    """
    Remove ficheiros de execuções antigas (mais de 30 dias).
    """
    from datetime import timedelta
    
    data_limite = timezone.now() - timedelta(days=30)
    execucoes_antigas = ExecucaoRelatorio.objects.filter(
        data_execucao__lt=data_limite,
        ficheiro_gerado__isnull=False
    )
    
    for execucao in execucoes_antigas:
        if execucao.ficheiro_gerado:
            try:
                if os.path.exists(execucao.ficheiro_gerado.path):
                    os.remove(execucao.ficheiro_gerado.path)
                    logger.info(f'Ficheiro antigo removido: {execucao.ficheiro_gerado.path}')
            except Exception as e:
                logger.error(f'Erro ao remover ficheiro antigo: {e}')
    
    logger.info(f'Limpeza de ficheiros antigos concluída')


# Signal para notificação de relatórios em atraso
def notificar_relatorios_atraso():
    """
    Notifica sobre relatórios que estão em execução há mais de 1 hora.
    """
    from datetime import timedelta
    
    data_limite = timezone.now() - timedelta(hours=1)
    execucoes_atrasadas = ExecucaoRelatorio.objects.filter(
        status='executando',
        data_execucao__lt=data_limite
    )
    
    for execucao in execucoes_atrasadas:
        notificacao = Notificacao.objects.create(
            utilizador=execucao.utilizador,
            titulo=f'Relatório "{execucao.relatorio.nome}" em atraso',
            mensagem=f'O relatório "{execucao.relatorio.nome}" está em execução há mais de 1 hora. Verifique se há algum problema.',
            tipo='warning',
            url=f'/relatorios/relatorios/{execucao.relatorio.pk}/',
            lida=False
        )
        logger.warning(f'Notificação de atraso criada para execução: {execucao.pk}')


# Signal para notificação de dashboards não utilizados
def notificar_dashboards_nao_utilizados():
    """
    Notifica sobre dashboards que não foram visualizados há mais de 30 dias.
    """
    from datetime import timedelta
    
    data_limite = timezone.now() - timedelta(days=30)
    dashboards_nao_utilizados = Dashboard.objects.filter(
        ativo=True,
        data_ultima_atualizacao__lt=data_limite
    )
    
    for dashboard in dashboards_nao_utilizados:
        notificacao = Notificacao.objects.create(
            utilizador=dashboard.utilizador_criador,
            titulo=f'Dashboard "{dashboard.nome}" não utilizado',
            mensagem=f'O dashboard "{dashboard.nome}" não foi visualizado há mais de 30 dias. Considere removê-lo ou atualizá-lo.',
            tipo='info',
            url=f'/relatorios/dashboards/{dashboard.pk}/',
            lida=False
        )
        logger.info(f'Notificação de dashboard não utilizado criada: {dashboard.pk}')
