from django.contrib import admin
from .models import AssinaturaDocumento, AssinaturaUtilizador, ParecerDocumento


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


@admin.register(ParecerDocumento)
class ParecerDocumentoAdmin(admin.ModelAdmin):
    list_display = ['parecer', 'anexo', 'ordem', 'data_insercao', 'ativo']
    list_filter = ['ativo', 'data_insercao']
    search_fields = [
        'parecer__titulo', 'parecer__parecerista__first_name', 'parecer__parecerista__last_name',
        'anexo__nome_original', 'anexo__expediente__numero_protocolo'
    ]
    readonly_fields = ['data_insercao']
    
    fieldsets = (
        ('Documento e Parecer', {
            'fields': ('anexo', 'parecer', 'ordem')
        }),
        ('Auditoria', {
            'fields': ('data_insercao',)
        }),
        ('Status', {
            'fields': ('ativo',)
        }),
    )
    
    def has_add_permission(self, request):
        # Não permitir adicionar manualmente pelo admin (inserção é automática)
        return False
    
    def has_change_permission(self, request, obj=None):
        # Permitir apenas visualização
        return False
