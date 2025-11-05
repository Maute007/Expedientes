from django.contrib import admin
from .models import AssinaturaDocumento, AssinaturaUtilizador


@admin.register(AssinaturaUtilizador)
class AssinaturaUtilizadorAdmin(admin.ModelAdmin):
    list_display = ['utilizador', 'ativo', 'data_criacao', 'data_atualizacao']
    list_filter = ['ativo', 'data_criacao']
    search_fields = ['utilizador__first_name', 'utilizador__last_name', 'utilizador__email']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('utilizador', 'assinatura_imagem', 'ativo')
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AssinaturaDocumento)
class AssinaturaDocumentoAdmin(admin.ModelAdmin):
    list_display = ['utilizador', 'anexo', 'tipo_assinatura', 'data_assinatura', 'pagina', 'ativo']
    list_filter = ['tipo_assinatura', 'ativo', 'data_assinatura']
    search_fields = [
        'utilizador__first_name', 'utilizador__last_name', 'utilizador__email',
        'anexo__nome_original', 'anexo__expediente__numero_protocolo'
    ]
    readonly_fields = [
        'data_assinatura', 'ip_address', 'user_agent',
        'utilizador', 'anexo', 'tipo_assinatura', 'assinatura_imagem',
        'posicao_x', 'posicao_y', 'pagina', 'arquivo_original_backup'
    ]
    
    fieldsets = (
        ('Documento e Utilizador', {
            'fields': ('anexo', 'utilizador', 'tipo_assinatura')
        }),
        ('Assinatura', {
            'fields': ('assinatura_imagem', 'posicao_x', 'posicao_y', 'pagina')
        }),
        ('Auditoria', {
            'fields': ('data_assinatura', 'ip_address', 'user_agent', 'observacoes')
        }),
        ('Backup', {
            'fields': ('arquivo_original_backup',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('ativo',)
        }),
        ('Certificado Digital (Futuro)', {
            'fields': ('certificado_digital',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Não permitir adicionar assinaturas manualmente pelo admin
        return False
    
    def has_change_permission(self, request, obj=None):
        # Permitir apenas visualização
        return False
