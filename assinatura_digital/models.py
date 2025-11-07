from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import os

User = get_user_model()


class AssinaturaUtilizador(models.Model):
    """
    Modelo para assinatura padrão de cada utilizador
    """
    utilizador = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='assinatura_padrao',
        verbose_name="Utilizador"
    )
    assinatura_imagem = models.ImageField(
        upload_to='assinaturas/usuarios/%Y/%m/',
        verbose_name="Imagem da Assinatura",
        help_text="Assinatura padrão do utilizador"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de Atualização"
    )
    
    class Meta:
        verbose_name = "Assinatura de Utilizador"
        verbose_name_plural = "Assinaturas de Utilizadores"
        ordering = ['-data_atualizacao']
    
    def __str__(self):
        return f"Assinatura de {self.utilizador.get_full_name()}"
    
    def get_signature_url(self):
        """Retorna URL da assinatura"""
        if self.assinatura_imagem:
            return self.assinatura_imagem.url
        return None


class AssinaturaDocumento(models.Model):
    """
    Modelo para registro de cada assinatura aplicada a um anexo
    """
    TIPOS_ASSINATURA = [
        ('canvas', 'Canvas (Mouse/Pad)'),
        ('upload', 'Upload de Imagem'),
        ('padrao', 'Assinatura Padrão'),
    ]
    
    # Relacionamento com anexo
    anexo = models.ForeignKey(
        'entrada.AnexoExpediente',
        on_delete=models.CASCADE,
        related_name='assinaturas',
        verbose_name="Anexo"
    )
    
    # Utilizador que assinou
    utilizador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='assinaturas_realizadas',
        verbose_name="Utilizador"
    )
    
    # Dados da assinatura
    tipo_assinatura = models.CharField(
        max_length=20,
        choices=TIPOS_ASSINATURA,
        default='canvas',
        verbose_name="Tipo de Assinatura"
    )
    
    assinatura_imagem = models.ImageField(
        upload_to='assinaturas/documentos/%Y/%m/',
        verbose_name="Imagem da Assinatura"
    )
    
    # Posicionamento no documento
    posicao_x = models.FloatField(
        verbose_name="Posição X",
        help_text="Posição X da assinatura no documento (em pontos ou pixels)"
    )
    posicao_y = models.FloatField(
        verbose_name="Posição Y",
        help_text="Posição Y da assinatura no documento (em pontos ou pixels)"
    )
    pagina = models.PositiveIntegerField(
        default=1,
        verbose_name="Página",
        help_text="Página do documento onde a assinatura foi aplicada"
    )
    
    # Dados de auditoria
    data_assinatura = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data da Assinatura"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Endereço IP"
    )
    user_agent = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="User Agent"
    )
    
    # Backup do arquivo original (caminho relativo)
    arquivo_original_backup = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="Caminho do Backup do Arquivo Original",
        help_text="Caminho do backup do arquivo antes de inserir a assinatura"
    )
    
    # Observações
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )
    
    # Status
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    # Preparação para certificado digital (futuro)
    certificado_digital = models.TextField(
        blank=True,
        null=True,
        verbose_name="Certificado Digital",
        help_text="Hash ou dados do certificado digital (para implementação futura)"
    )
    
    class Meta:
        verbose_name = "Assinatura de Documento"
        verbose_name_plural = "Assinaturas de Documentos"
        ordering = ['-data_assinatura']
        indexes = [
            models.Index(fields=['anexo', '-data_assinatura']),
            models.Index(fields=['utilizador', '-data_assinatura']),
        ]
    
    def __str__(self):
        return f"Assinatura de {self.utilizador.get_full_name()} em {self.anexo.nome_original}"
    
    def get_tipo_display(self):
        """Retorna o tipo de assinatura formatado"""
        return dict(self.TIPOS_ASSINATURA).get(self.tipo_assinatura, self.tipo_assinatura)
    
    def save_signature(self, signature_image, anexo_file, position_x, position_y, pagina=1):
        """
        Salva a assinatura e processa o documento
        """
        self.assinatura_imagem = signature_image
        self.posicao_x = position_x
        self.posicao_y = position_y
        self.pagina = pagina
        return self


class ParecerDocumento(models.Model):
    """
    Modelo para rastrear pareceres inseridos em anexos de expedientes.
    Sistema independente do módulo de assinaturas.
    """
    anexo = models.ForeignKey(
        'entrada.AnexoExpediente',
        on_delete=models.CASCADE,
        related_name='pareceres_inseridos',
        verbose_name="Anexo"
    )
    parecer = models.ForeignKey(
        'entrada.ParecerExpediente',
        on_delete=models.CASCADE,
        related_name='insercoes_documento',
        verbose_name="Parecer"
    )
    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem",
        help_text="Ordem do parecer na tabela (para ordenação)"
    )
    data_insercao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Inserção"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    arquivo_original_backup = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="Caminho do Backup do Arquivo Original",
        help_text="Caminho do backup do arquivo antes de inserir pareceres (apenas no primeiro registro)"
    )
    
    class Meta:
        verbose_name = "Parecer Inserido no Documento"
        verbose_name_plural = "Pareceres Inseridos em Documentos"
        ordering = ['ordem', 'data_insercao']
        unique_together = ['anexo', 'parecer']
    
    def __str__(self):
        return f"Parecer {self.parecer.titulo} em {self.anexo.nome_original}"
