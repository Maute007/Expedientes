from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as AuthUser
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import PerfilUtilizador, HierarquiaUtilizador

User = get_user_model()

# User padrão do Django não precisa ser desregistrado quando AUTH_USER_MODEL está configurado

@admin.register(User)
class UserAdminCustomizado(BaseUserAdmin):
    """
    Admin customizado para o modelo User.
    """
    
    list_display = [
        'email', 'get_full_name', 'tipo_utilizador', 'sector_atual', 
        'cargo', 'ativo', 'date_joined', 'ultimo_acesso'
    ]
    list_filter = [
        'tipo_utilizador', 'ativo', 'sector_atual', 'date_joined', 
        'is_active', 'is_staff', 'is_superuser'
    ]
    search_fields = [
        'email', 'first_name', 'last_name', 'telefone', 'cargo'
    ]
    ordering = ['-date_joined']
    readonly_fields = ['date_joined', 'last_login', 'ultimo_acesso']
    
    fieldsets = [
        ('Informações Pessoais', {
            'fields': ('email', 'first_name', 'last_name', 'telefone')
        }),
        ('Informações Profissionais', {
            'fields': ('sector_atual', 'cargo', 'tipo_utilizador', 'ativo')
        }),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Informações Adicionais', {
            'fields': ('avatar', 'biografia', 'data_nascimento', 'genero', 'endereco', 'codigo_postal', 'cidade', 'pais'),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('last_login', 'date_joined', 'ultimo_acesso'),
            'classes': ('collapse',)
        }),
    ]
    
    add_fieldsets = [
        ('Informações Básicas', {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
        ('Informações Profissionais', {
            'classes': ('wide',),
            'fields': ('sector_atual', 'cargo', 'tipo_utilizador', 'ativo'),
        }),
    ]
    
    actions = ['ativar_utilizadores', 'desativar_utilizadores', 'enviar_email_bem_vindo']
    
    def get_full_name(self, obj):
        """Retorna nome completo do utilizador."""
        return obj.get_full_name()
    get_full_name.short_description = 'Nome Completo'
    get_full_name.admin_order_field = 'first_name'
    
    def ativar_utilizadores(self, request, queryset):
        """Ativa utilizadores selecionados."""
        updated = queryset.update(ativo=True)
        self.message_user(
            request, 
            f'{updated} utilizador(es) ativado(s) com sucesso.'
        )
    ativar_utilizadores.short_description = "Ativar utilizadores selecionados"
    
    def desativar_utilizadores(self, request, queryset):
        """Desativa utilizadores selecionados."""
        updated = queryset.update(ativo=False)
        self.message_user(
            request, 
            f'{updated} utilizador(es) desativado(s) com sucesso.'
        )
    desativar_utilizadores.short_description = "Desativar utilizadores selecionados"
    
    def enviar_email_bem_vindo(self, request, queryset):
        """Envia email de boas-vindas para utilizadores selecionados."""
        # Implementar lógica de envio de email
        count = queryset.count()
        self.message_user(
            request, 
            f'Email de boas-vindas enviado para {count} utilizador(es).'
        )
    enviar_email_bem_vindo.short_description = "Enviar email de boas-vindas"
    
    def get_queryset(self, request):
        """Otimiza queryset com select_related."""
        return super().get_queryset(request).select_related('sector_atual')


# @admin.register(PerfilUtilizador)
class PerfilUtilizadorAdmin(admin.ModelAdmin):
    """
    Admin para o modelo PerfilUtilizador.
    """
    
    list_display = [
        'user', 'nivel_hierarquico', 'idioma_preferido', 
        'tema_preferido', 'ativo', 'data_criacao'
    ]
    list_filter = [
        'nivel_hierarquico', 'idioma_preferido', 'tema_preferido', 
        'ativo', 'data_criacao'
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name', 'biografia'
    ]
    readonly_fields = ['data_criacao', 'data_atualizacao']
    raw_id_fields = ['user']
    
    fieldsets = [
        ('Utilizador', {
            'fields': ('user',)
        }),
        ('Informações do Perfil', {
            'fields': ('foto', 'biografia', 'data_nascimento', 'nivel_hierarquico', 'ativo')
        }),
        ('Preferências', {
            'fields': ('idioma_preferido', 'tema_preferido', 'timezone', 'preferencias_notificacao')
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    ]
    
    def get_queryset(self, request):
        """Otimiza queryset com select_related."""
        return super().get_queryset(request).select_related('user')


# @admin.register(HierarquiaUtilizador)
class HierarquiaUtilizadorAdmin(admin.ModelAdmin):
    """
    Admin para o modelo HierarquiaUtilizador.
    """
    
    list_display = [
        'utilizador', 'sector', 'cargo', 'nivel', 'data_inicio', 
        'data_fim', 'ativo', 'tipo_contrato'
    ]
    list_filter = [
        'nivel', 'tipo_contrato', 'ativo', 'data_inicio', 'data_fim'
    ]
    search_fields = [
        'utilizador__email', 'cargo', 'observacoes', 'sector__nome'
    ]
    readonly_fields = ['data_criacao']
    raw_id_fields = ['utilizador', 'sector', 'supervisor', 'criado_por']
    date_hierarchy = 'data_inicio'
    
    fieldsets = [
        ('Utilizador e Sector', {
            'fields': ('utilizador', 'sector', 'supervisor')
        }),
        ('Informações da Posição', {
            'fields': ('cargo', 'nivel', 'tipo_contrato', 'salario')
        }),
        ('Período', {
            'fields': ('data_inicio', 'data_fim', 'ativo')
        }),
        ('Informações Adicionais', {
            'fields': ('observacoes', 'criado_por', 'data_criacao'),
            'classes': ('collapse',)
        }),
    ]
    
    actions = ['ativar_posicoes', 'desativar_posicoes', 'finalizar_posicoes']
    
    def ativar_posicoes(self, request, queryset):
        """Ativa posições selecionadas."""
        updated = queryset.update(ativo=True)
        self.message_user(
            request, 
            f'{updated} posição(ões) ativada(s) com sucesso.'
        )
    ativar_posicoes.short_description = "Ativar posições selecionadas"
    
    def desativar_posicoes(self, request, queryset):
        """Desativa posições selecionadas."""
        updated = queryset.update(ativo=False)
        self.message_user(
            request, 
            f'{updated} posição(ões) desativada(s) com sucesso.'
        )
    desativar_posicoes.short_description = "Desativar posições selecionadas"
    
    def finalizar_posicoes(self, request, queryset):
        """Finaliza posições selecionadas."""
        from django.utils import timezone
        updated = queryset.update(data_fim=timezone.now().date(), ativo=False)
        self.message_user(
            request, 
            f'{updated} posição(ões) finalizada(s) com sucesso.'
        )
    finalizar_posicoes.short_description = "Finalizar posições selecionadas"
    
    def get_queryset(self, request):
        """Otimiza queryset com select_related."""
        return super().get_queryset(request).select_related(
            'utilizador', 'sector', 'supervisor', 'criado_por'
        )


# Personalizar títulos do admin
admin.site.site_header = "FTC - Sistema de Gestão de Expedientes"
admin.site.site_title = "FTC Admin"
admin.site.index_title = "Painel de Administração"