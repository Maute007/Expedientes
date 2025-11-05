from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django.contrib.admin import SimpleListFilter

from .models import (
    EstadoDocumento, 
    Notificacao, 
    Sector, 
    ConfiguracaoSistema, 
    DespachoDocumento, 
    AnexoDespacho
)


class EstadoDocumentoAdmin(admin.ModelAdmin):
    """
    Admin para Estados de Documento.
    """
    list_display = ['nome', 'descricao', 'cor_display', 'ordem', 'ativo', 'requer_acao']
    list_filter = ['ativo', 'requer_acao']
    search_fields = ['nome', 'descricao']
    ordering = ['ordem']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'cor')
        }),
        ('Configurações', {
            'fields': ('ordem', 'ativo', 'requer_acao')
        }),
    )
    
    def cor_display(self, obj):
        """
        Mostra a cor como um quadrado colorido.
        """
        if obj.cor:
            return format_html(
                '<span style="display: inline-block; width: 20px; height: 20px; '
                'background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></span> {}',
                obj.cor, obj.cor
            )
        return '-'
    cor_display.short_description = 'Cor'
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('ordem')


class NotificacaoLidaFilter(SimpleListFilter):
    """
    Filtro personalizado para notificações lidas/não lidas.
    """
    title = 'Status de Leitura'
    parameter_name = 'lida'
    
    def lookups(self, request, model_admin):
        return (
            ('true', 'Lidas'),
            ('false', 'Não Lidas'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(lida=True)
        elif self.value() == 'false':
            return queryset.filter(lida=False)
        return queryset


class NotificacaoPrioridadeFilter(SimpleListFilter):
    """
    Filtro personalizado para prioridade de notificações.
    """
    title = 'Prioridade'
    parameter_name = 'prioridade'
    
    def lookups(self, request, model_admin):
        return Notificacao.PRIORIDADES
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(prioridade=self.value())
        return queryset


class NotificacaoAdmin(admin.ModelAdmin):
    """
    Admin para Notificações.
    """
    list_display = [
        'titulo', 'destinatario', 'tipo', 'prioridade_display', 
        'lida_display', 'data_criacao', 'remetente'
    ]
    list_filter = [
        NotificacaoLidaFilter, 
        NotificacaoPrioridadeFilter, 
        'tipo', 
        'data_criacao'
    ]
    search_fields = ['titulo', 'mensagem', 'destinatario__email', 'destinatario__first_name', 'destinatario__last_name']
    readonly_fields = ['data_criacao', 'data_lida']
    ordering = ['-data_criacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('destinatario', 'remetente', 'titulo', 'mensagem')
        }),
        ('Configurações', {
            'fields': ('tipo', 'prioridade', 'lida')
        }),
        ('Documento Relacionado', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_lida'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['marcar_como_lidas', 'marcar_como_nao_lidas', 'marcar_como_urgentes']
    
    def prioridade_display(self, obj):
        """
        Mostra prioridade com cor.
        """
        if obj.prioridade == 'urgente':
            return format_html(
                '<span style="color: red; font-weight: bold;">{}</span>',
                obj.get_prioridade_display()
            )
        return obj.get_prioridade_display()
    prioridade_display.short_description = 'Prioridade'
    
    def lida_display(self, obj):
        """
        Mostra status de leitura com ícone.
        """
        if obj.lida:
            return format_html(
                '<span style="color: green;">✓ Lida</span>'
            )
        return format_html(
            '<span style="color: red;">✗ Não Lida</span>'
        )
    lida_display.short_description = 'Status'
    
    def marcar_como_lidas(self, request, queryset):
        """
        Ação para marcar notificações como lidas.
        """
        count = queryset.update(lida=True)
        self.message_user(request, f'{count} notificações marcadas como lidas.')
    marcar_como_lidas.short_description = 'Marcar como lidas'
    
    def marcar_como_nao_lidas(self, request, queryset):
        """
        Ação para marcar notificações como não lidas.
        """
        count = queryset.update(lida=False)
        self.message_user(request, f'{count} notificações marcadas como não lidas.')
    marcar_como_nao_lidas.short_description = 'Marcar como não lidas'
    
    def marcar_como_urgentes(self, request, queryset):
        """
        Ação para marcar notificações como urgentes.
        """
        count = queryset.update(prioridade='urgente')
        self.message_user(request, f'{count} notificações marcadas como urgentes.')
    marcar_como_urgentes.short_description = 'Marcar como urgentes'


class SectorAdmin(admin.ModelAdmin):
    """
    Admin para Sectores.
    """
    list_display = ['nome', 'chefe', 'chefe_substituto', 'ativo', 'data_criacao', 'colaboradores_count']
    list_filter = ['ativo', 'data_criacao']
    search_fields = ['nome', 'descricao', 'chefe__email', 'chefe__first_name', 'chefe__last_name']
    ordering = ['nome']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao')
        }),
        ('Liderança', {
            'fields': ('chefe', 'chefe_substituto')
        }),
        ('Configurações', {
            'fields': ('ativo', 'observacoes')
        }),
    )
    
    def colaboradores_count(self, obj):
        """
        Mostra número de colaboradores do sector.
        """
        count = obj.obter_colaboradores().count()
        return count
    colaboradores_count.short_description = 'Colaboradores'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('chefe', 'chefe_substituto')


class ConfiguracaoSistemaAdmin(admin.ModelAdmin):
    """
    Admin para Configurações do Sistema.
    """
    list_display = ['chave', 'valor_preview', 'tipo', 'data_criacao', 'data_atualizacao']
    list_filter = ['tipo', 'data_criacao']
    search_fields = ['chave', 'descricao', 'valor']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    ordering = ['chave']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('chave', 'descricao')
        }),
        ('Valor', {
            'fields': ('valor', 'tipo')
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def valor_preview(self, obj):
        """
        Mostra preview do valor (truncado).
        """
        if len(obj.valor) > 50:
            return obj.valor[:50] + '...'
        return obj.valor
    valor_preview.short_description = 'Valor'


class DespachoDocumentoAdmin(admin.ModelAdmin):
    """
    Admin para Despachos/Pareceres/Comentários.
    """
    list_display = [
        'tipo', 'autor', 'documento_info', 'visivel_para', 
        'editado', 'data_criacao', 'data_atualizacao'
    ]
    list_filter = ['tipo', 'visivel_para', 'editado', 'data_criacao']
    search_fields = ['conteudo', 'autor__email', 'autor__first_name', 'autor__last_name']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    ordering = ['-data_criacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('tipo', 'conteudo', 'autor')
        }),
        ('Documento Relacionado', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Configurações', {
            'fields': ('visivel_para', 'editado')
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def documento_info(self, obj):
        """
        Mostra informação do documento relacionado.
        """
        if obj.documento:
            return f"{obj.content_type.model} #{obj.object_id}"
        return '-'
    documento_info.short_description = 'Documento'


class AnexoDespachoAdmin(admin.ModelAdmin):
    """
    Admin para Anexos de Despachos.
    """
    list_display = [
        'nome_original', 'despacho', 'tamanho_display', 
        'data_upload', 'tipo_mime'
    ]
    list_filter = ['data_upload', 'tipo_mime']
    search_fields = ['nome_original', 'despacho__conteudo']
    readonly_fields = ['data_upload', 'tamanho']
    ordering = ['-data_upload']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('despacho', 'ficheiro', 'nome_original')
        }),
        ('Detalhes Técnicos', {
            'fields': ('tamanho', 'tipo_mime', 'data_upload'),
            'classes': ('collapse',)
        }),
    )
    
    def tamanho_display(self, obj):
        """
        Mostra tamanho formatado.
        """
        return obj.obter_tamanho_formatado()
    tamanho_display.short_description = 'Tamanho'


# Registrar modelos no admin
admin.site.register(EstadoDocumento, EstadoDocumentoAdmin)
admin.site.register(Notificacao, NotificacaoAdmin)
admin.site.register(Sector, SectorAdmin)
admin.site.register(ConfiguracaoSistema, ConfiguracaoSistemaAdmin)
admin.site.register(DespachoDocumento, DespachoDocumentoAdmin)
admin.site.register(AnexoDespacho, AnexoDespachoAdmin)

# Configurações do admin
admin.site.site_header = "FTC Sistema de Processos - Administração"
admin.site.site_title = "FTC Admin"
admin.site.index_title = "Painel de Administração"