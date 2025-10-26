from django.contrib import admin
from .models import TipoDocumento, Expediente, AnexoExpediente, HistoricoExpediente


@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    """
    Admin para TipoDocumento
    """
    list_display = ['nome', 'categoria', 'prazo_resposta', 'prioridade_padrao', 'requer_anexos', 'ativo', 'data_criacao']
    list_filter = ['categoria', 'prioridade_padrao', 'requer_anexos', 'ativo', 'data_criacao']
    search_fields = ['nome', 'descricao']
    list_editable = ['ativo']
    readonly_fields = ['data_criacao', 'criado_por']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'categoria', 'descricao')
        }),
        ('Configurações', {
            'fields': ('prazo_resposta', 'prioridade_padrao', 'requer_anexos', 'campos_obrigatorios')
        }),
        ('Template de Resposta', {
            'fields': ('template_resposta',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('ativo',)
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'criado_por'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se está criando
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(Expediente)
class ExpedienteAdmin(admin.ModelAdmin):
    """
    Admin para Expediente
    """
    list_display = ['numero_protocolo', 'tipo', 'assunto', 'status', 'criado_por', 'data_criacao']
    list_filter = ['tipo', 'status', 'origem', 'ativo', 'data_criacao']
    search_fields = ['numero_protocolo', 'assunto', 'descricao']
    readonly_fields = ['numero_protocolo', 'data_criacao', 'data_atualizacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('numero_protocolo', 'tipo', 'origem', 'remetente')
        }),
        ('Detalhes', {
            'fields': ('assunto', 'descricao', 'telefone')
        }),
        ('Status e Controle', {
            'fields': ('status', 'estado_atual', 'rascunho', 'ativo')
        }),
        ('Responsabilidades', {
            'fields': ('criado_por', 'sector_responsavel')
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao', 'data_submissao', 'data_aprovacao')
        })
    )
    
    filter_horizontal = ['sectores_envolvidos', 'membros_envolvidos']


@admin.register(AnexoExpediente)
class AnexoExpedienteAdmin(admin.ModelAdmin):
    """
    Admin para AnexoExpediente
    """
    list_display = ['expediente', 'nome_original', 'tamanho_humanizado', 'tipo_mime', 'upload_por', 'data_upload']
    list_filter = ['tipo_mime', 'data_upload', 'upload_por']
    search_fields = ['expediente__numero_protocolo', 'nome_original', 'descricao']
    readonly_fields = ['nome_original', 'tamanho', 'tipo_mime', 'data_upload']
    
    fieldsets = (
        ('Arquivo', {
            'fields': ('expediente', 'arquivo', 'descricao')
        }),
        ('Metadados', {
            'fields': ('nome_original', 'tamanho', 'tipo_mime', 'upload_por', 'data_upload'),
            'classes': ('collapse',)
        })
    )


@admin.register(HistoricoExpediente)
class HistoricoExpedienteAdmin(admin.ModelAdmin):
    """
    Admin para HistoricoExpediente
    """
    list_display = ['expediente', 'acao', 'usuario', 'data_acao']
    list_filter = ['acao', 'data_acao', 'usuario']
    search_fields = ['expediente__numero_protocolo', 'acao', 'descricao']
    readonly_fields = ['data_acao']
    
    fieldsets = (
        ('Ação', {
            'fields': ('expediente', 'acao', 'descricao', 'usuario', 'data_acao')
        }),
        ('Mudanças de Estado', {
            'fields': ('estado_anterior', 'estado_novo'),
            'classes': ('collapse',)
        })
    )