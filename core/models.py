from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import json
import os
from .managers import (
    EstadoDocumentoManager, 
    NotificacaoManager, 
    SectorManager, 
    DespachoDocumentoManager
)


class EstadoDocumento(models.Model):
    """
    Modelo para definir os estados possíveis de um documento no workflow.
    """
    nome = models.CharField(max_length=50, unique=True, verbose_name="Nome")
    descricao = models.TextField(verbose_name="Descrição")
    cor = models.CharField(max_length=7, verbose_name="Cor (código hex)")
    ordem = models.PositiveIntegerField(verbose_name="Ordem")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    requer_acao = models.BooleanField(default=False, verbose_name="Requer Ação")
    
    objects = EstadoDocumentoManager()
    
    class Meta:
        ordering = ['ordem']
        verbose_name = "Estado de Documento"
        verbose_name_plural = "Estados de Documentos"
    
    def __str__(self):
        return self.nome
    
    def obter_proximos_estados(self):
        """
        Retorna QuerySet dos próximos estados possíveis baseado na ordem.
        """
        return EstadoDocumento.objects.filter(
            ordem__gt=self.ordem,
            ativo=True
        ).order_by('ordem')
    
    def obter_estados_anteriores(self):
        """
        Retorna QuerySet dos estados anteriores baseado na ordem.
        """
        return EstadoDocumento.objects.filter(
            ordem__lt=self.ordem,
            ativo=True
        ).order_by('-ordem')
    
    def pode_transicionar_para(self, estado):
        """
        Valida se a transição para o estado especificado é permitida.
        """
        if not isinstance(estado, EstadoDocumento):
            return False
        
        if not estado.ativo:
            return False
        
        # Regras de transição específicas
        if self.nome == "Recebido":
            return estado.nome in ["Encaminhado", "Arquivado"]
        elif self.nome == "Encaminhado":
            return estado.nome in ["Em Tratamento", "Arquivado"]
        elif self.nome == "Em Tratamento":
            return estado.nome in ["Concluído", "Devolvido", "Arquivado"]
        elif self.nome == "Concluído":
            return estado.nome in ["Arquivado"]
        elif self.nome == "Devolvido":
            return estado.nome in ["Encaminhado", "Em Tratamento", "Arquivado"]
        elif self.nome == "Arquivado":
            return False  # Estado final
        
        return False
    
    def clean(self):
        """
        Validação personalizada do modelo.
        """
        super().clean()
        
        # Validar formato da cor
        if self.cor and not self.cor.startswith('#'):
            raise ValidationError({'cor': 'A cor deve começar com # (ex: #007bff)'})
        
        # Validar cores obrigatórias
        cores_obrigatorias = {
            "Recebido": "#007bff",
            "Encaminhado": "#fd7e14", 
            "Em Tratamento": "#ffc107",
            "Concluído": "#198754",
            "Arquivado": "#6c757d",
            "Devolvido": "#dc3545"
        }
        
        if self.nome in cores_obrigatorias and self.cor != cores_obrigatorias[self.nome]:
            raise ValidationError({
                'cor': f'A cor para "{self.nome}" deve ser {cores_obrigatorias[self.nome]}'
            })


class Notificacao(models.Model):
    """
    Modelo para notificações internas do sistema.
    """
    TIPOS_NOTIFICACAO = [
        ('documento_novo', 'Novo Documento'),
        ('documento_encaminhado', 'Documento Encaminhado'),
        ('documento_recebido', 'Documento Recebido'),
        ('documento_concluido', 'Documento Concluído'),
        ('documento_arquivado', 'Documento Arquivado'),
        ('documento_devolvido', 'Documento Devolvido'),
        ('mensagem_nova', 'Nova Mensagem')
    ]
    
    PRIORIDADES = [
        ('normal', 'Normal'),
        ('urgente', 'Urgente')
    ]
    
    destinatario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notificacoes_recebidas',
        verbose_name="Destinatário"
    )
    remetente = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notificacoes_enviadas', 
        null=True, 
        blank=True,
        verbose_name="Remetente"
    )
    titulo = models.CharField(max_length=200, verbose_name="Título")
    mensagem = models.TextField(verbose_name="Mensagem")
    tipo = models.CharField(
        max_length=50, 
        choices=TIPOS_NOTIFICACAO,
        verbose_name="Tipo"
    )
    lida = models.BooleanField(default=False, verbose_name="Lida")
    email_enviado = models.BooleanField(default=False, verbose_name="Email Enviado")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_lida = models.DateTimeField(null=True, blank=True, verbose_name="Data de Leitura")
    
    # Generic Foreign Key para documento relacionado
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    documento_relacionado = GenericForeignKey('content_type', 'object_id')
    
    prioridade = models.CharField(
        max_length=10, 
        choices=PRIORIDADES, 
        default='normal',
        verbose_name="Prioridade"
    )
    
    objects = NotificacaoManager()
    
    class Meta:
        ordering = ['-data_criacao']
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
    
    def __str__(self):
        return f"{self.titulo} - {self.destinatario.get_full_name()}"
    
    def marcar_como_lida(self):
        """
        Marca a notificação como lida e define a data de leitura.
        """
        self.lida = True
        self.data_lida = timezone.now()
        self.save()
    
    @classmethod
    def obter_nao_lidas_usuario(cls, user):
        """
        Retorna todas as notificações não lidas de um utilizador.
        """
        return cls.objects.filter(destinatario=user, lida=False)
    
    @classmethod
    def marcar_todas_lidas(cls, user):
        """
        Marca todas as notificações de um utilizador como lidas.
        """
        count = cls.objects.filter(destinatario=user, lida=False).count()
        cls.objects.filter(destinatario=user, lida=False).update(
            lida=True, 
            data_lida=timezone.now()
        )
        return count
    
    def obter_icone(self):
        """
        Retorna o ícone Bootstrap baseado no tipo de notificação.
        """
        icones = {
            'documento_novo': 'bi-file-earmark-plus',
            'documento_encaminhado': 'bi-arrow-right-circle',
            'documento_recebido': 'bi-download',
            'documento_concluido': 'bi-check-circle',
            'documento_arquivado': 'bi-archive',
            'documento_devolvido': 'bi-arrow-left-circle',
            'mensagem_nova': 'bi-chat-dots'
        }
        return icones.get(self.tipo, 'bi-bell')
    
    def obter_url(self):
        """
        Retorna a URL do documento relacionado ou página de notificações.
        """
        if self.documento_relacionado:
            # Mapear tipos de documento para suas URLs específicas
            model_name = self.content_type.model.lower()
            
            if model_name == 'expediente':
                return f"/entrada/detalhar/{self.object_id}/"
            elif model_name == 'documentosaida':
                return f"/saida/detalhar/{self.object_id}/"
            elif model_name == 'documentointerna':
                return f"/interna/detalhar/{self.object_id}/"
            elif model_name == 'documentoexterna':
                return f"/externa/detalhar/{self.object_id}/"
            else:
                # URL genérica para outros tipos de documento
                return f"/documentos/{model_name}/{self.object_id}/"
        
        return "/notificacoes/"
    
    def eh_urgente(self):
        """
        Verifica se a notificação é urgente.
        """
        return self.prioridade == 'urgente'


class Sector(models.Model):
    """
    Modelo para sectores/departamentos da organização.
    """
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    chefe = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='sectores_chefiados',
        verbose_name="Chefe"
    )
    chefe_substituto = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='sectores_substituicao',
        verbose_name="Chefe Substituto"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    
    objects = SectorManager()
    
    class Meta:
        ordering = ['nome']
        verbose_name = "Sector"
        verbose_name_plural = "Sectores"
    
    def __str__(self):
        return self.nome
    
    def obter_chefe(self):
        """
        Retorna o chefe atual (substituto se chefe estiver inativo).
        """
        if self.chefe_substituto and not self.chefe.is_active:
            return self.chefe_substituto
        return self.chefe
    
    def obter_colaboradores(self):
        """
        Retorna todos os colaboradores ativos do sector.
        """
        return User.objects.filter(sector_atual=self, is_active=True)
    
    def obter_subordinados(self):
        """
        Retorna colaboradores + chefes de sectores subordinados.
        """
        colaboradores = self.obter_colaboradores()
        chefes_subordinados = User.objects.filter(sectores_chefiados=self, is_active=True)
        return colaboradores.union(chefes_subordinados)
    
    def eh_chefe(self, user):
        """
        Verifica se o utilizador é chefe deste sector.
        """
        return self.chefe == user or self.chefe_substituto == user


class ConfiguracaoSistema(models.Model):
    """
    Modelo para configurações globais do sistema.
    """
    TIPOS_VALOR = [
        ('string', 'Texto'),
        ('int', 'Número Inteiro'),
        ('bool', 'Booleano'),
        ('json', 'JSON')
    ]
    
    chave = models.CharField(max_length=100, unique=True, verbose_name="Chave")
    valor = models.TextField(verbose_name="Valor")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    tipo = models.CharField(
        max_length=10, 
        choices=TIPOS_VALOR, 
        default='string',
        verbose_name="Tipo"
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        ordering = ['chave']
        verbose_name = "Configuração do Sistema"
        verbose_name_plural = "Configurações do Sistema"
    
    def __str__(self):
        return f"{self.chave}: {self.valor}"
    
    def obter_valor(self):
        """
        Retorna o valor convertido para o tipo correto.
        """
        try:
            if self.tipo == 'int':
                return int(self.valor)
            elif self.tipo == 'bool':
                return self.valor.lower() in ('true', '1', 'yes', 'sim')
            elif self.tipo == 'json':
                return json.loads(self.valor)
            else:  # string
                return self.valor
        except (ValueError, json.JSONDecodeError):
            return self.valor
    
    def definir_valor(self, valor):
        """
        Define o valor convertendo para string para armazenamento.
        """
        if self.tipo == 'json':
            self.valor = json.dumps(valor, ensure_ascii=False)
        else:
            self.valor = str(valor)
        self.save()
    
    @classmethod
    def obter_configuracao(cls, chave, valor_padrao=None):
        """
        Obtém uma configuração específica ou retorna valor padrão.
        """
        try:
            config = cls.objects.get(chave=chave)
            return config.obter_valor()
        except cls.DoesNotExist:
            return valor_padrao
    
    @classmethod
    def definir_configuracao(cls, chave, valor, descricao='', tipo='string'):
        """
        Define ou atualiza uma configuração.
        """
        config, created = cls.objects.get_or_create(
            chave=chave,
            defaults={'descricao': descricao, 'tipo': tipo}
        )
        config.definir_valor(valor)
        return config


class DespachoDocumento(models.Model):
    """
    Modelo para despachos, pareceres e comentários em documentos.
    """
    TIPOS_DESPACHO = [
        ('despacho', 'Despacho'),      # PCA e Chefes
        ('parecer', 'Parecer'),         # PCA e Chefes
        ('comentario', 'Comentário')    # Todos
    ]
    
    VISIBILIDADE = [
        ('todos', 'Todos'),
        ('chefes', 'Apenas Chefes e PCA'),
        ('pca', 'Apenas PCA')
    ]
    
    # Generic Foreign Key para documento relacionado
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    documento = GenericForeignKey('content_type', 'object_id')
    
    tipo = models.CharField(
        max_length=20, 
        choices=TIPOS_DESPACHO,
        verbose_name="Tipo"
    )
    conteudo = models.TextField(verbose_name="Conteúdo")
    autor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='despachos_criados',
        verbose_name="Autor"
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    visivel_para = models.CharField(
        max_length=20, 
        choices=VISIBILIDADE, 
        default='todos',
        verbose_name="Visível Para"
    )
    editado = models.BooleanField(default=False, verbose_name="Editado")
    
    objects = DespachoDocumentoManager()
    
    class Meta:
        ordering = ['data_criacao']
        verbose_name = "Despacho/Parecer/Comentário"
        verbose_name_plural = "Despachos/Pareceres/Comentários"
    
    def __str__(self):
        return f"{self.get_tipo_display()} de {self.autor.get_full_name()}"
    
    def pode_criar(user, tipo):
        """
        Valida se o utilizador pode criar este tipo de despacho.
        """
        if tipo == 'comentario':
            return True  # Todos podem criar comentários
        
        if tipo in ['despacho', 'parecer']:
            # Apenas PCA e Chefes podem criar despachos e pareceres
            return user.is_pca or user.sector_atual.eh_chefe(user) if user.sector_atual else False
        
        return False
    
    def pode_editar(self, user):
        """
        Verifica se o utilizador pode editar este despacho.
        """
        if self.autor != user:
            return False
        
        # Pode editar até 24h após criação
        from django.utils import timezone
        tempo_decorrido = timezone.now() - self.data_criacao
        return tempo_decorrido.days < 1
    
    def pode_visualizar(self, user, documento):
        """
        Verifica se o utilizador pode visualizar este despacho.
        """
        if self.visivel_para == 'todos':
            return True
        
        if self.visivel_para == 'chefes':
            return user.is_pca or (user.sector_atual and user.sector_atual.eh_chefe(user))
        
        if self.visivel_para == 'pca':
            return user.is_pca
        
        return False
    
    def marcar_como_editado(self):
        """
        Marca o despacho como editado.
        """
        self.editado = True
        self.save()


class AnexoDespacho(models.Model):
    """
    Modelo para anexos de despachos/pareceres/comentários.
    """
    despacho = models.ForeignKey(
        DespachoDocumento, 
        on_delete=models.CASCADE, 
        related_name='anexos',
        verbose_name="Despacho"
    )
    ficheiro = models.FileField(
        upload_to='despachos/%Y/%m/',
        verbose_name="Ficheiro"
    )
    nome_original = models.CharField(max_length=255, verbose_name="Nome Original")
    tamanho = models.PositiveIntegerField(verbose_name="Tamanho (bytes)")
    tipo_mime = models.CharField(max_length=100, blank=True, verbose_name="Tipo MIME")
    data_upload = models.DateTimeField(auto_now_add=True, verbose_name="Data de Upload")
    
    class Meta:
        verbose_name = "Anexo de Despacho"
        verbose_name_plural = "Anexos de Despachos"
    
    def __str__(self):
        return self.nome_original
    
    def obter_tamanho_formatado(self):
        """
        Retorna o tamanho formatado do ficheiro (ex: "1.5 MB", "500 KB").
        """
        tamanho = self.tamanho
        
        if tamanho < 1024:
            return f"{tamanho} B"
        elif tamanho < 1024 * 1024:
            return f"{tamanho / 1024:.1f} KB"
        elif tamanho < 1024 * 1024 * 1024:
            return f"{tamanho / (1024 * 1024):.1f} MB"
        else:
            return f"{tamanho / (1024 * 1024 * 1024):.1f} GB"
    
    def obter_extensao(self):
        """
        Retorna a extensão do ficheiro.
        """
        return os.path.splitext(self.nome_original)[1]
