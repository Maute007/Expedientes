from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count
from .models import (
    TipoRelatorio, ConfiguracaoRelatorio, ExecucaoRelatorio,
    Dashboard, WidgetDashboard
)


@admin.register(TipoRelatorio)
class TipoRelatorioAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'tipo_relatorio', 'formato_saida', 'ativo', 'ordem'
    ]
    list_filter = ['tipo_relatorio', 'formato_saida', 'ativo']
    search_fields = ['nome', 'descricao']
    ordering = ['ordem', 'nome']
    list_editable = ['ativo', 'ordem']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'tipo_relatorio', 'template')
        }),
        ('Configurações', {
            'fields': ('parametros_obrigatorios', 'parametros_opcionais', 'formato_saida')
        }),
        ('Controle', {
            'fields': ('ativo', 'ordem'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            relatorios_count=Count('configuracaorelatorio')
        )


@admin.register(ConfiguracaoRelatorio)
class ConfiguracaoRelatorioAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'tipo_relatorio', 'utilizador_criador', 'sector', 
        'publico', 'ativo', 'execucoes_count', 'data_ultima_execucao'
    ]
    list_filter = [
        'tipo_relatorio__tipo_relatorio', 'publico', 'ativo', 
        'sector', 'utilizador_criador'
    ]
    search_fields = ['nome', 'descricao', 'utilizador_criador__username']
    ordering = ['-data_criacao']
    list_editable = ['ativo', 'publico']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'tipo_relatorio')
        }),
        ('Configurações', {
            'fields': ('parametros', 'filtros', 'sector')
        }),
        ('Permissões', {
            'fields': ('utilizador_criador', 'publico', 'ativo')
        }),
        ('Estatísticas', {
            'fields': ('execucoes_count', 'data_ultima_execucao'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['execucoes_count', 'data_ultima_execucao']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'tipo_relatorio', 'utilizador_criador', 'sector'
        ).prefetch_related('execucoes')


@admin.register(ExecucaoRelatorio)
class ExecucaoRelatorioAdmin(admin.ModelAdmin):
    list_display = [
        'relatorio', 'utilizador', 'data_execucao', 'status_display',
        'tamanho_display', 'registros_processados', 'data_conclusao'
    ]
    list_filter = [
        'status', 'relatorio__tipo_relatorio', 'utilizador', 
        'data_execucao', 'data_conclusao'
    ]
    search_fields = [
        'relatorio__nome', 'utilizador__username', 'erro'
    ]
    ordering = ['-data_execucao']
    readonly_fields = [
        'data_execucao', 'data_conclusao', 'tamanho_ficheiro',
        'registros_processados', 'erro'
    ]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('relatorio', 'utilizador', 'status')
        }),
        ('Execução', {
            'fields': ('data_execucao', 'data_conclusao', 'parametros_utilizados', 'filtros_utilizados')
        }),
        ('Resultado', {
            'fields': ('ficheiro_gerado', 'tamanho_ficheiro', 'registros_processados')
        }),
        ('Erro', {
            'fields': ('erro',),
            'classes': ('collapse',)
        })
    )
    
    def status_display(self, obj):
        """Exibe o status com cor."""
        colors = {
            'pendente': 'orange',
            'processando': 'blue',
            'concluido': 'green',
            'erro': 'red',
            'cancelado': 'gray'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def tamanho_display(self, obj):
        """Exibe o tamanho formatado."""
        return obj.get_tamanho_display()
    tamanho_display.short_description = 'Tamanho'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'relatorio', 'utilizador'
        )


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'utilizador_criador', 'sector', 'widgets_count',
        'publico', 'ativo', 'data_criacao'
    ]
    list_filter = [
        'publico', 'ativo', 'sector', 'utilizador_criador', 'data_criacao'
    ]
    search_fields = ['nome', 'descricao', 'utilizador_criador__username']
    ordering = ['-data_criacao']
    list_editable = ['ativo', 'publico']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'sector')
        }),
        ('Configurações', {
            'fields': ('widgets', 'layout')
        }),
        ('Permissões', {
            'fields': ('utilizador_criador', 'publico', 'ativo')
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    def widgets_count(self, obj):
        """Exibe o número de widgets."""
        return obj.get_widgets_count()
    widgets_count.short_description = 'Widgets'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'utilizador_criador', 'sector'
        )


@admin.register(WidgetDashboard)
class WidgetDashboardAdmin(admin.ModelAdmin):
    list_display = [
        'dashboard', 'titulo', 'tipo_widget', 'ativo', 'ordem'
    ]
    list_filter = [
        'tipo_widget', 'ativo', 'dashboard', 'dashboard__utilizador_criador'
    ]
    search_fields = ['titulo', 'dashboard__nome']
    ordering = ['dashboard', 'ordem']
    list_editable = ['ativo', 'ordem']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('dashboard', 'titulo', 'tipo_widget')
        }),
        ('Configurações', {
            'fields': ('parametros', 'tamanho', 'posicao')
        }),
        ('Controle', {
            'fields': ('ativo', 'ordem')
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('dashboard')


# Personalização do admin site
admin.site.site_header = "FTC Expedientes - Administração"
admin.site.site_title = "FTC Expedientes Admin"
admin.site.index_title = "Painel de Administração"

# Adicionar ações personalizadas
@admin.action(description='Executar relatórios selecionados')
def executar_relatorios(modeladmin, request, queryset):
    """Ação para executar múltiplos relatórios."""
    count = 0
    for relatorio in queryset:
        if relatorio.ativo:
            execucao = relatorio.execute(request.user)
            count += 1
    
    modeladmin.message_user(
        request,
        f'{count} relatório(s) executado(s) com sucesso.'
    )

ConfiguracaoRelatorioAdmin.actions = [executar_relatorios]

@admin.action(description='Ativar relatórios selecionados')
def ativar_relatorios(modeladmin, request, queryset):
    """Ação para ativar múltiplos relatórios."""
    count = queryset.update(ativo=True)
    modeladmin.message_user(
        request,
        f'{count} relatório(s) ativado(s) com sucesso.'
    )

@admin.action(description='Desativar relatórios selecionados')
def desativar_relatorios(modeladmin, request, queryset):
    """Ação para desativar múltiplos relatórios."""
    count = queryset.update(ativo=False)
    modeladmin.message_user(
        request,
        f'{count} relatório(s) desativado(s) com sucesso.'
    )

ConfiguracaoRelatorioAdmin.actions.extend([ativar_relatorios, desativar_relatorios])

@admin.action(description='Limpar execuções antigas')
def limpar_execucoes_antigas(modeladmin, request, queryset):
    """Ação para limpar execuções antigas."""
    from django.utils import timezone
    from datetime import timedelta
    
    # Remover execuções com mais de 30 dias
    data_limite = timezone.now() - timedelta(days=30)
    count = queryset.filter(data_execucao__lt=data_limite).delete()[0]
    
    modeladmin.message_user(
        request,
        f'{count} execução(ões) antiga(s) removida(s) com sucesso.'
    )

ExecucaoRelatorioAdmin.actions = [limpar_execucoes_antigas]