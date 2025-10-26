"""
Signals para o app users.
Automatiza ações relacionadas com criação, atualização e remoção de utilizadores.
"""
from django.db.models.signals import post_save, pre_save, post_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
import logging

from .models import PerfilUtilizador, HierarquiaUtilizador

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def criar_perfil_utilizador(sender, instance, created, **kwargs):
    """
    Signal 1: Criar PerfilUtilizador automaticamente quando User é criado.
    """
    if created:
        # Criar perfil automaticamente
        perfil = PerfilUtilizador.objects.create(
            user=instance
        )
        
        logger.info(f"Perfil criado automaticamente para {instance.email}")
        
        # Enviar email de boas-vindas (apenas se não for superuser)
        if not instance.is_superuser and instance.email:
            try:
                assunto = 'Bem-vindo ao Sistema de Gestão de Expedientes - FTC'
                mensagem = f"""
Olá {instance.get_full_name()},

Bem-vindo ao Sistema de Gestão de Expedientes da Faculdade de Tecnologias de Cabo Delgado!

Suas credenciais de acesso:
- Email: {instance.email}
- Senha: [Definida pelo administrador]

Por favor, faça login e altere sua senha no primeiro acesso.

Acesse o sistema em: {settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost:8000'}

Atenciosamente,
Equipa FTC
                """
                
                send_mail(
                    assunto,
                    mensagem,
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.email],
                    fail_silently=True,
                )
                logger.info(f"Email de boas-vindas enviado para {instance.email}")
            except Exception as e:
                logger.error(f"Erro ao enviar email de boas-vindas para {instance.email}: {str(e)}")


@receiver(post_save, sender=PerfilUtilizador)
def atualizar_hierarquia_utilizador(sender, instance, created, **kwargs):
    """
    Signal 2: Atualizar/criar entrada em HierarquiaUtilizador quando perfil é salvo.
    """
    # Este signal está temporariamente desabilitado pois PerfilUtilizador não tem nivel_hierarquico
    # TODO: Implementar lógica de hierarquia baseada nos campos do PerfilUtilizador
    return
    
    user = instance.user
    
    # Verificar se o nível hierárquico mudou
    if not created and hasattr(instance, 'nivel_hierarquico') and instance.nivel_hierarquico:
        # Verificar se já existe uma hierarquia ativa
        hierarquia_ativa = HierarquiaUtilizador.objects.filter(
            subordinado=user,
            ativo=True
        ).first()
        
        # Se o nível mudou, finalizar a hierarquia antiga e criar nova
        if hierarquia_ativa and hierarquia_ativa.tipo_relacao != instance.nivel_hierarquico:
            hierarquia_ativa.ativo = False
            hierarquia_ativa.data_fim = timezone.now()
            hierarquia_ativa.save()
            logger.info(f"Hierarquia antiga finalizada para {user.email}")


@receiver(pre_save, sender=User)
def validar_e_log_alteracoes_user(sender, instance, **kwargs):
    """
    Signal 3: Validações e logs antes de salvar User.
    """
    if instance.pk:  # Apenas para updates, não para creates
        try:
            old_instance = User.objects.get(pk=instance.pk)
            
            # Log de alterações importantes
            alteracoes = []
            
            if old_instance.tipo_utilizador != instance.tipo_utilizador:
                alteracoes.append(f"Tipo: {old_instance.tipo_utilizador} → {instance.tipo_utilizador}")
            
            if old_instance.ativo != instance.ativo:
                status = "Ativado" if instance.ativo else "Desativado"
                alteracoes.append(f"Status: {status}")
            
            if old_instance.sector_atual != instance.sector_atual:
                old_sector = old_instance.sector_atual.nome if old_instance.sector_atual else "Nenhum"
                new_sector = instance.sector_atual.nome if instance.sector_atual else "Nenhum"
                alteracoes.append(f"Sector: {old_sector} → {new_sector}")
            
            if alteracoes:
                logger.info(f"Alterações no utilizador {instance.email}: {', '.join(alteracoes)}")
        
        except User.DoesNotExist:
            pass
    
    # Validar email único (caso não tenha sido validado no form)
    if instance.email:
        existing = User.objects.filter(email=instance.email).exclude(pk=instance.pk)
        if existing.exists():
            raise ValidationError(f"Email {instance.email} já está em uso por outro utilizador.")


@receiver(post_delete, sender=User)
def limpar_dados_relacionados_user(sender, instance, **kwargs):
    """
    Signal 4: Limpar dados relacionados quando User é removido.
    """
    logger.warning(f"Utilizador removido: {instance.email} ({instance.get_full_name()})")
    
    # Notificar administradores sobre remoção
    try:
        admins = User.objects.filter(tipo_utilizador='admin', ativo=True)
        admin_emails = [admin.email for admin in admins if admin.email]
        
        if admin_emails:
            assunto = f'ALERTA: Utilizador Removido - {instance.get_full_name()}'
            mensagem = f"""
ALERTA DE SEGURANÇA

Um utilizador foi removido do sistema:

- Nome: {instance.get_full_name()}
- Email: {instance.email}
- Tipo: {instance.get_tipo_utilizador_display()}
- Sector: {instance.sector_atual.nome if instance.sector_atual else 'N/A'}
- Data/Hora: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}

Esta ação foi registada nos logs do sistema para auditoria.

Atenciosamente,
Sistema FTC
            """
            
            send_mail(
                assunto,
                mensagem,
                settings.DEFAULT_FROM_EMAIL,
                admin_emails,
                fail_silently=True,
            )
            logger.info(f"Notificação de remoção enviada para administradores")
    except Exception as e:
        logger.error(f"Erro ao notificar administradores sobre remoção: {str(e)}")


@receiver(user_logged_in)
def atualizar_ultimo_acesso(sender, request, user, **kwargs):
    """
    Signal 5: Atualizar ultimo_acesso quando utilizador faz login.
    """
    user.ultimo_acesso = timezone.now()
    user.save(update_fields=['ultimo_acesso'])
    
    # Log de acesso para auditoria
    ip_address = request.META.get('REMOTE_ADDR', 'Desconhecido')
    user_agent = request.META.get('HTTP_USER_AGENT', 'Desconhecido')
    
    logger.info(
        f"Login: {user.email} | "
        f"IP: {ip_address} | "
        f"User-Agent: {user_agent[:100]}"
    )
    
    # Verificar se utilizador está ativo
    if not user.ativo:
        logger.warning(f"Utilizador inativo tentou fazer login: {user.email}")


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    """
    Signal 6: Log de logout para auditoria.
    """
    if user:
        ip_address = request.META.get('REMOTE_ADDR', 'Desconhecido')
        logger.info(f"Logout: {user.email} | IP: {ip_address}")

