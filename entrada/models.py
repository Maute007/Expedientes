from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from core.models import Sector, EstadoDocumento

User = get_user_model()


class TipoDocumento(models.Model):
    """
    Modelo para tipos de documentos conforme checklist
    """
    CATEGORIAS = [
        ('carta', 'Carta'),
        ('requerimento', 'Requerimento'),
        ('informacao', 'Informação'),
        ('reclamacao', 'Reclamação'),
        ('denuncia', 'Denúncia'),
        ('oficio', 'Ofício'),
        ('convite', 'Convite'),
        ('circular', 'Circular'),
        ('memorando', 'Memorando'),
        ('relatorio', 'Relatório'),
        ('contrato', 'Contrato'),
        ('proposta', 'Proposta'),
        ('licitacao', 'Licitação'),
        ('certificacao', 'Certificação'),
        ('outro', 'Outro')
    ]
    
    PRIORIDADES = [
        ('baixa', 'Baixa'),
        ('normal', 'Normal'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente')
    ]

    # ße e confindencial÷

    
    nome = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome do Tipo"
    )
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIAS,
        verbose_name="Categoria"
    )
    descricao = models.TextField(
        verbose_name="Descrição"
    )
    prazo_resposta = models.PositiveIntegerField(
        help_text="Prazo em dias úteis",
        verbose_name="Prazo de Resposta"
    )
    prioridade_padrao = models.CharField(
        max_length=10,
        choices=PRIORIDADES,
        default='normal',
        verbose_name="Prioridade Padrão"
    )
    requer_anexos = models.BooleanField(
        default=False,
        verbose_name="Requer Anexos"
    )
    template_resposta = models.TextField(
        blank=True,
        null=True,
        verbose_name="Template de Resposta"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    criado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='tipos_criados',
        verbose_name="Criado por"
    )
    
    class Meta:
        ordering = ['nome']
        verbose_name = "Tipo de Documento"
        verbose_name_plural = "Tipos de Documento"
    
    def __str__(self):
        return self.nome


class Expediente(models.Model):
    """
    Modelo principal para expedientes de entrada
    """
    
    # Constantes para status
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('submetido', 'Submetido'),
        ('em_analise', 'Em Análise'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
        ('arquivado', 'Arquivado'),
    ]
    
    # Constantes da checklist
    ORIGENS = [
        ('secretaria', 'Secretaria'),
        ('portal', 'Portal Online'),
        ('quiosque', 'Quiosque'),
        ('email', 'Email'),
        ('fax', 'Fax'),
        ('correio', 'Correio'),
        ('pessoal', 'Entrega Pessoal')
    ]
    
    PRIORIDADES = [
        ('baixa', 'Baixa'),
        ('normal', 'Normal'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente')
    ]
    
    # Etapa 1: Informações Básicas
    referencia = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Referência do Documento",
        help_text="Referência do documento recebido (ex: Ofício nº 123/2025)"
    )
    numero_protocolo = models.CharField(
        max_length=15,
        unique=True,
        verbose_name="Número de Protocolo",
        help_text="Formato: AAAAMMXXXXX (gerado automaticamente)"
    )
    tipo = models.ForeignKey(
        TipoDocumento,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Documento"
    )
    origem = models.CharField(
        max_length=20,
        choices=ORIGENS,
        default='secretaria',
        verbose_name="Origem",
        help_text="Como o documento entrou no sistema"
    )
    remetente = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Remetente",
        help_text="Nome do remetente"
    )
    
    # Etapa 2: Detalhes
    assunto = models.CharField(
        max_length=300,
        verbose_name="Assunto",
        help_text="Resumo do assunto do processo"
    )
    descricao = models.TextField(
        blank=True,
        verbose_name="Descrição",
        help_text="Descrição detalhada do processo (opcional)"
    )
    telefone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Telefone",
        help_text="Ex: +258 82 123 4567"
    )
    
    # Campos da checklist DocumentoEntrada
    prioridade = models.CharField(
        max_length=10,
        choices=PRIORIDADES,
        default='normal',
        verbose_name="Prioridade"
    )
    conteudo = models.TextField(
        blank=True,
        verbose_name="Conteúdo",
        help_text="Conteúdo detalhado do documento"
    )
    data_limite = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data Limite",
        help_text="Prazo para resposta"
    )
    requer_resposta = models.BooleanField(
        default=True,
        verbose_name="Requer Resposta"
    )
    confidencial = models.BooleanField(
        default=False,
        verbose_name="Confidencial"
    )
    numero_paginas = models.PositiveIntegerField(
        default=1,
        verbose_name="Número de Páginas"
    )
    valor_monetario = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor Monetário"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações Internas"
    )
    data_recebido = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data Recebido"
    )
    recebido_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_recebidos',
        verbose_name="Recebido por"
    )
    utilizador_atual = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_posse',
        verbose_name="Utilizador Atual",
        help_text="Utilizador que está atualmente com o documento"
    )
    
    # Etapa 3: Membros (relacionamentos)
    sectores_envolvidos = models.ManyToManyField(
        Sector,
        blank=True,
        related_name='expedientes_entrada',
        verbose_name="Sectores Envolvidos"
    )
    membros_envolvidos = models.ManyToManyField(
        User,
        blank=True,
        related_name='expedientes_entrada',
        verbose_name="Membros Envolvidos"
    )
    
    # Metadados do sistema
    criado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='expedientes_criados',
        verbose_name="Criado por"
    )
    sector_responsavel = models.ForeignKey(
        Sector,
        on_delete=models.PROTECT,
        related_name='expedientes_responsavel',
        verbose_name="Sector Responsável"
    )
    estado_atual = models.ForeignKey(
        EstadoDocumento,
        on_delete=models.PROTECT,
        verbose_name="Estado Atual"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='rascunho',
        verbose_name="Status"
    )
    
    # Datas
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de Atualização"
    )
    data_submissao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Submissão"
    )
    data_aprovacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Aprovação"
    )
    
    # Campos de controle
    rascunho = models.BooleanField(
        default=True,
        verbose_name="É Rascunho"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    class Meta:
        ordering = ['-data_criacao']
        verbose_name = "Expediente"
        verbose_name_plural = "Expedientes"
    
    def __str__(self):
        return f"{self.numero_protocolo} - {self.assunto}"
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o save para gerar número de protocolo automaticamente
        """
        if not self.numero_protocolo:
            self.numero_protocolo = self.gerar_numero_protocolo()
        super().save(*args, **kwargs)
    
    def gerar_numero_protocolo(self):
        """
        Gera número de protocolo no formato: AAAAMMXXXXX
        AAAA = ano, MM = mês, XXXXX = número sequencial mensal
        """
        from datetime import datetime
        hoje = datetime.now()
        prefixo = hoje.strftime("%Y%m")  # Apenas ano e mês
        
        # Contar expedientes do mês
        ultimo_expediente = Expediente.objects.filter(
            numero_protocolo__startswith=prefixo
        ).order_by('-numero_protocolo').first()
        
        if ultimo_expediente:
            ultimo_numero = int(ultimo_expediente.numero_protocolo[-5:])
            novo_numero = ultimo_numero + 1
        else:
            novo_numero = 1
        
        # Garantir que o número não existe (proteção contra concorrência)
        numero_protocolo = f"{prefixo}{novo_numero:05d}"
        while Expediente.objects.filter(numero_protocolo=numero_protocolo).exists():
            novo_numero += 1
            numero_protocolo = f"{prefixo}{novo_numero:05d}"
        
        return numero_protocolo
    
    def marcar_como_submetido(self):
        """
        Marca o expediente como submetido
        """
        self.status = 'submetido'
        self.rascunho = False
        self.data_submissao = timezone.now()
        self.save()
    
    def aprovar(self, aprovado_por):
        """
        Aprova o expediente
        """
        self.status = 'aprovado'
        self.data_aprovacao = timezone.now()
        self.save()
    
    # Métodos da checklist DocumentoEntrada
    def obter_estado(self):
        """Retorna o estado atual do documento"""
        return self.estado_atual.nome if self.estado_atual else 'Desconhecido'
    
    def obter_prioridade(self):
        """Retorna a prioridade formatada"""
        return self.get_prioridade_display()
    
    def marcar_como_recebido(self, utilizador):
        """Marca o documento como recebido"""
        self.data_recebido = timezone.now()
        self.recebido_por = utilizador
        self.utilizador_atual = utilizador
        self.save()
    
    def pode_marcar_recebido(self, utilizador):
        """Verifica se utilizador pode marcar como recebido"""
        # Se já foi recebido por este utilizador, não pode marcar novamente
        if self.recebido_por == utilizador:
            return False
        
        # Se está atribuído ao utilizador ou ao sector dele
        if self.utilizador_atual == utilizador:
            return True
        
        # Se está no sector do utilizador
        if hasattr(utilizador, 'sector_atual') and utilizador.sector_atual:
            return self.sector_responsavel == utilizador.sector_atual
        
        return False
    
    def pode_encaminhar(self, utilizador):
        """Verifica se utilizador pode encaminhar este documento"""
        # PCA e Secretaria podem encaminhar para qualquer sector
        if utilizador.tipo_utilizador in ['pca', 'secretaria']:
            return True
        
        # Chefe pode encaminhar para colaboradores do seu sector
        if utilizador.tipo_utilizador == 'chefe':
            return self.sector_responsavel == utilizador.sector_atual
        
        # Colaborador pode encaminhar para seu chefe
        if utilizador.tipo_utilizador == 'colaborador':
            return self.sector_responsavel == utilizador.sector_atual
        
        return False
    
    def obter_dias_para_limite(self):
        """Calcula dias restantes para data_limite"""
        if not self.data_limite:
            return None
        from datetime import date
        hoje = date.today()
        dias_restantes = (self.data_limite - hoje).days
        return dias_restantes
    
    def eh_atrasado(self):
        """Verifica se documento está em atraso"""
        if not self.data_limite:
            return False
        from datetime import date
        hoje = date.today()
        return (self.data_limite < hoje and 
                self.estado_atual and 
                self.estado_atual.nome != 'Concluído')
    
    def obter_anexos(self):
        """Retorna anexos ativos"""
        return self.anexos.filter(ativo=True)
    
    def obter_movimentacoes(self):
        """Retorna movimentações ordenadas por data"""
        return self.historico.all().order_by('-data_acao')
    
    def pode_visualizar(self, utilizador):
        """Verifica permissões de visualização"""
        # Secretaria vê todos
        if utilizador.tipo_utilizador == 'secretaria':
            return True
        
        # Utilizador atual
        if self.utilizador_atual == utilizador:
            return True
        
        # Membros envolvidos (histórico de quem já trabalhou no documento)
        if utilizador in self.membros_envolvidos.all():
            return True
        
        # Se utilizador_atual é None, verificar relações alternativas
        if not self.utilizador_atual:
            if self.criado_por == utilizador:
                return True
            if (utilizador.tipo_utilizador == 'chefe' and 
                self.sector_responsavel == utilizador.sector_atual):
                return True
            if (utilizador.tipo_utilizador == 'pca' and 
                self.sector_responsavel == utilizador.sector_atual):
                return True
        
        return False
    
    def pode_editar(self, utilizador):
        """Verifica permissões de edição"""
        # Apenas criador pode editar
        return self.criado_por == utilizador
    
    def obter_proximo_numero(self):
        """Gera próximo número de expediente"""
        return self.gerar_numero_protocolo()
    
    def obter_acoes_disponiveis(self, utilizador):
        """
        Retorna lista de ações disponíveis baseado no estado atual e tipo de utilizador.
        Cada ação é um dict com: nome, url_name, classe_css, icone, label
        """
        acoes = []
        estado = self.estado_atual.nome if self.estado_atual else None
        tipo_user = utilizador.tipo_utilizador
        
        # PCA e Secretaria têm mais permissões
        eh_admin = tipo_user in ['pca', 'secretaria']
        
        # Verificar se é responsável atual
        eh_responsavel = self.utilizador_atual == utilizador
        
        # Verificar se é do mesmo sector
        eh_do_sector = self.sector_responsavel == utilizador.sector_atual if self.sector_responsavel else False
        
        # Estado: Recebido/Pendente
        if estado in ['Recebido', 'Pendente']:
            if eh_admin or eh_responsavel:
                # Encaminhar baseado no tipo de usuário
                if eh_admin:
                    acoes.append({
                        'nome': 'encaminhar',
                        'url_name': 'entrada:encaminhar_pca_sector',
                        'classe_css': 'btn-primary',
                        'icone': 'bi-send',
                        'label': 'Encaminhar'
                    })
                elif tipo_user == 'chefe':
                    acoes.append({
                        'nome': 'encaminhar',
                        'url_name': 'entrada:encaminhar_chefe_colaborador',
                        'classe_css': 'btn-primary',
                        'icone': 'bi-send',
                        'label': 'Encaminhar para Colaborador'
                    })
                elif tipo_user == 'colaborador':
                    acoes.append({
                        'nome': 'encaminhar',
                        'url_name': 'entrada:encaminhar_chefe_colaborador',
                        'classe_css': 'btn-primary',
                        'icone': 'bi-send',
                        'label': 'Encaminhar para Chefe'
                    })
                    
                acoes.append({
                    'nome': 'tratar',
                    'url_name': 'entrada:iniciar_tratamento',
                    'classe_css': 'btn-warning',
                    'icone': 'bi-gear',
                    'label': 'Iniciar Tratamento'
                })
            if eh_admin:
                acoes.append({
                    'nome': 'arquivar',
                    'url_name': 'entrada:arquivar_documento',
                    'classe_css': 'btn-secondary',
                    'icone': 'bi-archive',
                    'label': 'Arquivar'
                })
        
        # Estado: Encaminhado
        elif estado == 'Encaminhado':
            if eh_responsavel or eh_do_sector:
                acoes.append({
                    'nome': 'marcar_recebido',
                    'url_name': 'entrada:marcar_recebido',
                    'classe_css': 'btn-success',
                    'icone': 'bi-check-circle',
                    'label': 'Marcar como Recebido'
                })
            if eh_admin:
                acoes.append({
                    'nome': 'reencaminhar',
                    'url_name': 'entrada:encaminhar_pca_sector',
                    'classe_css': 'btn-primary',
                    'icone': 'bi-arrow-repeat',
                    'label': 'Reencaminhar'
                })
                acoes.append({
                    'nome': 'devolver',
                    'url_name': 'entrada:devolver_documento',
                    'classe_css': 'btn-warning',
                    'icone': 'bi-arrow-left',
                    'label': 'Devolver'
                })
        
        # Estado: Em Tratamento
        elif estado == 'Em Tratamento':
            if eh_responsavel or eh_do_sector:
                acoes.append({
                    'nome': 'concluir',
                    'url_name': 'entrada:concluir_documento',
                    'classe_css': 'btn-success',
                    'icone': 'bi-check-lg',
                    'label': 'Concluir'
                })
                
                # Encaminhar baseado no tipo de usuário
                if tipo_user == 'chefe':
                    acoes.append({
                        'nome': 'encaminhar',
                        'url_name': 'entrada:encaminhar_chefe_colaborador',
                        'classe_css': 'btn-primary',
                        'icone': 'bi-send',
                        'label': 'Encaminhar para Colaborador'
                    })
                elif tipo_user == 'colaborador':
                    acoes.append({
                        'nome': 'encaminhar',
                        'url_name': 'entrada:encaminhar_chefe_colaborador',
                        'classe_css': 'btn-primary',
                        'icone': 'bi-send',
                        'label': 'Encaminhar para Chefe'
                    })
                elif eh_admin:
                    acoes.append({
                        'nome': 'encaminhar',
                        'url_name': 'entrada:encaminhar_pca_sector',
                        'classe_css': 'btn-primary',
                        'icone': 'bi-send',
                        'label': 'Encaminhar'
                    })
                    
            # Apenas chefe e secretaria podem devolver
            if tipo_user in ['chefe', 'secretaria']:
                acoes.append({
                    'nome': 'devolver',
                    'url_name': 'entrada:devolver_documento',
                    'classe_css': 'btn-warning',
                    'icone': 'bi-arrow-left',
                    'label': 'Devolver ao PCA'
                })
        
        # Estado: Concluído
        elif estado == 'Concluído':
            if eh_admin:
                acoes.append({
                    'nome': 'arquivar',
                    'url_name': 'entrada:arquivar_documento',
                    'classe_css': 'btn-secondary',
                    'icone': 'bi-archive',
                    'label': 'Arquivar'
                })
                acoes.append({
                    'nome': 'reabrir',
                    'url_name': 'entrada:reabrir_documento',
                    'classe_css': 'btn-info',
                    'icone': 'bi-arrow-clockwise',
                    'label': 'Reabrir'
                })
        
        # Estado: Arquivado
        elif estado == 'Arquivado':
            if eh_admin:
                acoes.append({
                    'nome': 'reabrir',
                    'url_name': 'entrada:reabrir_documento',
                    'classe_css': 'btn-info',
                    'icone': 'bi-arrow-clockwise',
                    'label': 'Reabrir'
                })
        
        # Ação sempre disponível: Ver Histórico
        acoes.append({
            'nome': 'historico',
            'url_name': 'entrada:historico_movimentacao',
            'classe_css': 'btn-outline-secondary',
            'icone': 'bi-clock-history',
            'label': 'Ver Histórico'
        })
        
        return acoes


class AnexoExpediente(models.Model):
    """
    Modelo para anexos de expedientes
    """
    expediente = models.ForeignKey(
        Expediente,
        on_delete=models.CASCADE,
        related_name='anexos',
        verbose_name="Expediente"
    )
    arquivo = models.FileField(
        upload_to='expedientes/anexos/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']
            )
        ],
        verbose_name="Arquivo"
    )
    nome_original = models.CharField(
        max_length=255,
        verbose_name="Nome Original"
    )
    tamanho = models.PositiveIntegerField(
        verbose_name="Tamanho (bytes)"
    )
    tipo_mime = models.CharField(
        max_length=100,
        verbose_name="Tipo MIME"
    )
    descricao = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Descrição"
    )
    data_upload = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Upload"
    )
    upload_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Upload por"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    class Meta:
        ordering = ['-data_upload']
        verbose_name = "Anexo de Expediente"
        verbose_name_plural = "Anexos de Expediente"
    
    def __str__(self):
        return f"{self.expediente.numero_protocolo} - {self.nome_original}"
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o save para extrair metadados do arquivo
        """
        if self.arquivo:
            self.nome_original = self.arquivo.name
            self.tamanho = self.arquivo.size
            # Detectar tipo MIME baseado na extensão
            import mimetypes
            self.tipo_mime, _ = mimetypes.guess_type(self.arquivo.name)
            if not self.tipo_mime:
                self.tipo_mime = 'application/octet-stream'
        super().save(*args, **kwargs)
    
    @property
    def tamanho_humanizado(self):
        """
        Retorna o tamanho do arquivo em formato humanizado
        """
        tamanho = self.tamanho
        for unidade in ['B', 'KB', 'MB', 'GB']:
            if tamanho < 1024.0:
                return f"{tamanho:.1f} {unidade}"
            tamanho /= 1024.0
        return f"{tamanho:.1f} TB"

    def pode_ser_assinado(self):
        """
        Verifica se o anexo pode ser assinado
        Retorna True se o formato é suportado (PDF, DOC, DOCX, JPG, PNG)
        """
        formatos_suportados = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'image/jpeg',
            'image/jpg',
            'image/png'
        ]
        
        # Verificar por tipo MIME
        if self.tipo_mime in formatos_suportados:
            return True
        
        # Verificar por extensão como fallback
        nome_lower = self.nome_original.lower()
        extensoes_suportadas = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
        return any(nome_lower.endswith(ext) for ext in extensoes_suportadas)
    
    def obter_assinaturas(self):
        """
        Retorna todas as assinaturas ativas do anexo
        """
        try:
            from assinatura_digital.models import AssinaturaDocumento
            return AssinaturaDocumento.objects.filter(anexo=self, ativo=True).order_by('-data_assinatura')
        except ImportError:
            return []
    
    def tem_assinatura(self):
        """
        Verifica se o anexo já tem pelo menos uma assinatura ativa
        """
        return self.obter_assinaturas().exists()
    
    def pode_assinador_acessar(self, usuario):
        """
        Verifica se o usuário tem acesso ao anexo para poder assinar
        Verifica tanto permissão de visualização quanto permissão de assinatura
        """
        # Verificar acesso ao expediente
        if not self.expediente.pode_visualizar(usuario):
            return False
        
        # Verificar se usuário tem permissão de assinatura (PCA, Secretaria ou Chefe)
        if usuario.tipo_utilizador not in ['pca', 'secretaria', 'chefe']:
            return False
        
        return True


class ParecerExpediente(models.Model):
    """
    Modelo para pareceres sobre expedientes
    """
    TIPOS_PARECER = [
        ('favoravel', 'Favorável'),
        ('desfavoravel', 'Desfavorável'),
        ('com_reservas', 'Com Reservas'),
        ('informativo', 'Informativo'),
        ('recomendacao', 'Recomendação'),
        ('observacao', 'Observação')
    ]
    
    PRIORIDADES_PARECER = [
        ('baixa', 'Baixa'),
        ('normal', 'Normal'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente')
    ]
    
    expediente = models.ForeignKey(
        Expediente,
        on_delete=models.CASCADE,
        related_name='pareceres',
        verbose_name="Expediente"
    )
    parecerista = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pareceres_emitidos',
        verbose_name="Parecerista"
    )
    tipo_parecer = models.CharField(
        max_length=20,
        choices=TIPOS_PARECER,
        verbose_name="Tipo de Parecer"
    )
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título do Parecer"
    )
    conteudo = models.TextField(
        verbose_name="Conteúdo do Parecer"
    )
    recomendacoes = models.TextField(
        blank=True,
        verbose_name="Recomendações"
    )
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações Adicionais"
    )
    prioridade = models.CharField(
        max_length=10,
        choices=PRIORIDADES_PARECER,
        default='normal',
        verbose_name="Prioridade"
    )
    data_parecer = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data do Parecer"
    )
    data_limite = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data Limite para Implementação"
    )
    implementado = models.BooleanField(
        default=False,
        verbose_name="Implementado"
    )
    data_implementacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Implementação"
    )
    implementado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pareceres_implementados',
        verbose_name="Implementado por"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    class Meta:
        verbose_name = "Parecer de Expediente"
        verbose_name_plural = "Pareceres de Expedientes"
        ordering = ['-data_parecer']
    
    def __str__(self):
        return f"Parecer {self.get_tipo_parecer_display()} - {self.expediente.numero_protocolo}"
    
    def pode_editar(self, utilizador):
        """Verifica se utilizador pode editar este parecer"""
        # Só o parecerista pode editar (se ainda não implementado)
        if self.implementado:
            return False
        return self.parecerista == utilizador
    
    def pode_implementar(self, utilizador):
        """Verifica se utilizador pode implementar este parecer"""
        # PCA, Secretaria e Chefes podem implementar
        return utilizador.tipo_utilizador in ['pca', 'secretaria', 'chefe']
    
    def pode_visualizar(self, utilizador):
        """Verifica se utilizador pode visualizar este parecer"""
        # Todos os intervenientes podem visualizar
        if utilizador.tipo_utilizador in ['pca', 'secretaria']:
            return True
        
        # Chefe pode ver pareceres do seu sector
        if utilizador.tipo_utilizador == 'chefe':
            return self.expediente.sector_responsavel == utilizador.sector_atual
        
        # Colaborador pode ver pareceres de documentos atribuídos a ele
        if utilizador.tipo_utilizador == 'colaborador':
            return self.expediente.utilizador_atual == utilizador
        
        return False


class MovimentacaoDocumento(models.Model):
    """
    Modelo para histórico de movimentação de documentos conforme checklist
    """
    TIPOS_MOVIMENTACAO = [
        ('encaminhamento', 'Encaminhamento'),
        ('devolucao', 'Devolução'),
        ('recebimento', 'Recebimento'),
        ('conclusao', 'Conclusão'),
        ('arquivamento', 'Arquivamento'),
        ('reativacao', 'Reativação'),
        ('parecer', 'Parecer')
    ]
    
    documento = models.ForeignKey(
        Expediente,
        on_delete=models.CASCADE,
        related_name='movimentacoes',
        verbose_name="Documento"
    )
    de_utilizador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_enviadas',
        verbose_name="De Utilizador"
    )
    para_utilizador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_recebidas',
        verbose_name="Para Utilizador"
    )
    de_sector = models.ForeignKey(
        Sector,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_enviadas',
        verbose_name="De Sector"
    )
    para_sector = models.ForeignKey(
        Sector,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_recebidas',
        verbose_name="Para Sector"
    )
    estado_anterior = models.ForeignKey(
        EstadoDocumento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_anterior',
        verbose_name="Estado Anterior"
    )
    estado_novo = models.ForeignKey(
        EstadoDocumento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_novo',
        verbose_name="Estado Novo"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )
    data_movimentacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data da Movimentação"
    )
    tipo_movimentacao = models.CharField(
        max_length=20,
        choices=TIPOS_MOVIMENTACAO,
        verbose_name="Tipo de Movimentação"
    )
    automatica = models.BooleanField(
        default=False,
        verbose_name="Automática"
    )
    notificacao_enviada = models.BooleanField(
        default=False,
        verbose_name="Notificação Enviada"
    )
    data_notificacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data da Notificação"
    )
    
    class Meta:
        ordering = ['-data_movimentacao']
        verbose_name = "Movimentação de Documento"
        verbose_name_plural = "Movimentações de Documentos"
    
    def __str__(self):
        return f"{self.documento.numero_protocolo} - {self.get_tipo_movimentacao_display()}"
    
    def obter_tempo_resposta(self):
        """Calcula tempo entre movimentações"""
        # Implementar lógica de cálculo de tempo
        return None
    
    def obter_origem(self):
        """Retorna origem da movimentação"""
        if self.de_utilizador:
            return f"{self.de_utilizador.get_full_name()} ({self.de_sector.nome if self.de_sector else 'N/A'})"
        return "Sistema"
    
    def obter_destino(self):
        """Retorna destino da movimentação"""
        if self.para_utilizador:
            return f"{self.para_utilizador.get_full_name()} ({self.para_sector.nome if self.para_sector else 'N/A'})"
        return "Sistema"
    
    def eh_encaminhamento(self):
        """Verifica se é encaminhamento"""
        return self.tipo_movimentacao == 'encaminhamento'
    
    def eh_devolucao(self):
        """Verifica se é devolução"""
        return self.tipo_movimentacao == 'devolucao'
    
    def eh_recebimento(self):
        """Verifica se é recebimento"""
        return self.tipo_movimentacao == 'recebimento'
    
    def obter_descricao(self):
        """Retorna descrição legível da movimentação"""
        origem = self.obter_origem()
        destino = self.obter_destino()
        return f"{self.get_tipo_movimentacao_display()} de {origem} para {destino}"
    
    def pode_visualizar(self, utilizador):
        """Verifica se utilizador pode ver esta movimentação"""
        # Implementar lógica de permissões
        return True


class HistoricoExpediente(models.Model):
    """
    Modelo para histórico de mudanças do expediente
    """
    expediente = models.ForeignKey(
        Expediente,
        on_delete=models.CASCADE,
        related_name='historico',
        verbose_name="Expediente"
    )
    acao = models.CharField(
        max_length=100,
        verbose_name="Ação"
    )
    descricao = models.TextField(
        verbose_name="Descrição"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Usuário"
    )
    data_acao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data da Ação"
    )
    estado_anterior = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Estado Anterior"
    )
    estado_novo = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Estado Novo"
    )
    
    class Meta:
        ordering = ['-data_acao']
        verbose_name = "Histórico de Expediente"
        verbose_name_plural = "Histórico de Expedientes"
    
    def __str__(self):
        return f"{self.expediente.numero_protocolo} - {self.acao}"