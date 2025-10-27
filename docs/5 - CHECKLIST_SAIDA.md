# 📋 5. CHECKLIST - APP SAIDA

## 🎯 Objetivo
Gestão de documentos emitidos para fora da instituição com controle de aprovação e envio.

## 📤 Modelos de Documentos

### 1. Documento de Saída
- [ ] Criar modelo DocumentoSaida em saida/models.py
  - [ ] Campo numero_documento: CharField(max_length=50, unique=True) - número único gerado automaticamente
  - [ ] Campo data_criacao: DateTimeField(auto_now_add=True) - quando foi criado
  - [ ] Campo tipo_documento: ForeignKey(TipoDocumentoSaida, on_delete=PROTECT, related_name='documentos')
  - [ ] Campo destinatario: ForeignKey(Destinatario, on_delete=PROTECT, related_name='documentos_recebidos')
  - [ ] Campo assunto: CharField(max_length=500) - assunto do documento
  - [ ] Campo conteudo: TextField() - conteúdo detalhado
  - [ ] Campo prioridade: CharField(max_length=10, choices=PRIORIDADES, default='normal')
  - [ ] Campo estado_atual: ForeignKey('core.EstadoDocumento', on_delete=PROTECT, related_name='documentos_saida')
  - [ ] Campo sector_origem: ForeignKey('core.Sector', on_delete=PROTECT, related_name='documentos_emitidos')
  - [ ] Campo utilizador_criador: ForeignKey('users.User', on_delete=PROTECT, related_name='documentos_saida_criados')
  - [ ] Campo aprovado_por: ForeignKey('users.User', on_delete=SET_NULL, null=True, blank=True, related_name='documentos_saida_aprovados')
  - [ ] Campo data_aprovacao: DateTimeField(null=True, blank=True) - quando foi aprovado
  - [ ] Campo data_envio: DateTimeField(null=True, blank=True) - quando foi enviado
  - [ ] Campo metodo_envio: CharField(max_length=20, choices=METODOS_ENVIO, blank=True, null=True)
  - [ ] Campo ativo: BooleanField(default=True)
  - [ ] Campo documento_referencia: CharField(max_length=100, blank=True, null=True) - ref. documento de entrada
  - [ ] Campo confidencial: BooleanField(default=False)
  - [ ] Campo requer_comprovativo: BooleanField(default=False) - se requer comprovativo de entrega
  - [ ] Campo observacoes: TextField(blank=True, null=True)
  - [ ] Campo data_atualizacao: DateTimeField(auto_now=True)
  - [ ] Constante PRIORIDADES = [
        ('baixa', 'Baixa'),
        ('normal', 'Normal'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente')
    ]
  - [ ] Constante METODOS_ENVIO = [
        ('email', 'Email'),
        ('correio', 'Correio'),
        ('pessoal', 'Entrega Pessoal'),
        ('courier', 'Courier'),
        ('fax', 'Fax'),
        ('digital', 'Plataforma Digital')
    ]
  - [ ] Método __str__(): return f"{self.numero_documento} - {self.assunto}"
  - [ ] Método obter_estado(): return self.estado_atual.nome
  - [ ] Método obter_prioridade(): return self.get_prioridade_display()
  - [ ] Método obter_metodo_envio(): return self.get_metodo_envio_display() if self.metodo_envio else 'Não enviado'
  - [ ] Método pode_aprovar(utilizador): verifica se utilizador pode aprovar (PCA ou Chefe do sector)
  - [ ] Método pode_editar(utilizador): verifica se pode editar (criador, antes de aprovação)
  - [ ] Método eh_aprovado(): return self.aprovado_por is not None
  - [ ] Método eh_enviado(): return self.data_envio is not None
  - [ ] Método obter_anexos(): return self.anexos.filter(ativo=True)
  - [ ] Método obter_aprovacoes(): return self.aprovacoes.all().order_by('-data_aprovacao')
  - [ ] Método gerar_numero_documento(): gera número sequencial baseado em ano/sector
  - [ ] Meta: ordering = ['-data_criacao']
  - [ ] Meta: verbose_name = "Documento de Saída"
  - [ ] Meta: verbose_name_plural = "Documentos de Saída"

### 2. Tipos de Documento de Saída
- [ ] Criar modelo TipoDocumentoSaida em saida/models.py
  - [ ] Campo nome: CharField(max_length=100, unique=True) - nome do tipo
  - [ ] Campo categoria: CharField(max_length=20, choices=CATEGORIAS) - categoria do documento
  - [ ] Campo descricao: TextField() - descrição detalhada
  - [ ] Campo requer_aprovacao: CharField(max_length=20, choices=NIVEIS_APROVACAO) - quem deve aprovar
  - [ ] Campo template_padrao: TextField(blank=True, null=True) - template do documento
  - [ ] Campo prazo_aprovacao: PositiveIntegerField(help_text="Prazo em dias úteis", default=5)
  - [ ] Campo numeracao_automatica: BooleanField(default=True) - se usa numeração automática
  - [ ] Campo prefixo_numero: CharField(max_length=10, blank=True) - prefixo do número (ex: "OFF")
  - [ ] Campo ativo: BooleanField(default=True)
  - [ ] Campo data_criacao: DateTimeField(auto_now_add=True)
  - [ ] Campo criado_por: ForeignKey('users.User', on_delete=SET_NULL, null=True, related_name='tipos_saida_criados')
  - [ ] Constante CATEGORIAS = [
        ('despacho', 'Despacho'),
        ('notificacao', 'Notificação'),
        ('certidao', 'Certidão'),
        ('atestado', 'Atestado'),
        ('declaracao', 'Declaração'),
        ('oficio', 'Ofício'),
        ('carta', 'Carta'),
        ('resposta', 'Resposta'),
        ('convocatoria', 'Convocatória'),
        ('comunicado', 'Comunicado'),
        ('relatorio', 'Relatório'),
        ('outro', 'Outro')
    ]
  - [ ] Constante NIVEIS_APROVACAO = [
        ('nenhum', 'Não Requer Aprovação'),
        ('chefe', 'Chefe de Sector'),
        ('pca', 'PCA'),
        ('ambos', 'Chefe + PCA')
    ]
  - [ ] Método __str__(): return f"{self.nome} ({self.get_categoria_display()})"
  - [ ] Método obter_template_content(): return self.template_padrao or f"[Template para {self.nome}]"
  - [ ] Método requer_aprovacao_pca(): return self.requer_aprovacao in ['pca', 'ambos']
  - [ ] Método requer_aprovacao_chefe(): return self.requer_aprovacao in ['chefe', 'ambos']
  - [ ] Método gerar_numero_documento(sector, ano): gera número baseado em prefixo + ano + sequencial
  - [ ] Meta: ordering = ['categoria', 'nome']
  - [ ] Meta: verbose_name = "Tipo de Documento de Saída"
  - [ ] Meta: verbose_name_plural = "Tipos de Documentos de Saída"

### 3. Destinatários
- [ ] Criar modelo Destinatario em saida/models.py
  - [ ] Campo nome: CharField(max_length=200) - nome completo ou razão social
  - [ ] Campo email: EmailField(max_length=254, blank=True, null=True) - email principal
  - [ ] Campo telefone: CharField(max_length=20, blank=True, null=True) - telefone principal
  - [ ] Campo telefone_alternativo: CharField(max_length=20, blank=True, null=True) - telefone alternativo
  - [ ] Campo endereco: TextField() - endereço completo
  - [ ] Campo cidade: CharField(max_length=100, blank=True, null=True)
  - [ ] Campo provincia: CharField(max_length=100, blank=True, null=True)
  - [ ] Campo pais: CharField(max_length=100, default='Moçambique')
  - [ ] Campo codigo_postal: CharField(max_length=10, blank=True, null=True)
  - [ ] Campo tipo: CharField(max_length=20, choices=TIPOS_DESTINATARIO) - tipo de destinatário
  - [ ] Campo contacto_principal: CharField(max_length=200, blank=True, null=True) - pessoa de contacto
  - [ ] Campo cargo_contacto: CharField(max_length=100, blank=True, null=True) - cargo da pessoa de contacto
  - [ ] Campo observacoes: TextField(blank=True, null=True) - observações sobre o destinatário
  - [ ] Campo ativo: BooleanField(default=True)
  - [ ] Campo data_criacao: DateTimeField(auto_now_add=True)
  - [ ] Campo data_atualizacao: DateTimeField(auto_now=True)
  - [ ] Campo criado_por: ForeignKey('users.User', on_delete=SET_NULL, null=True, related_name='destinatarios_criados')
  - [ ] Campo preferencia_envio: CharField(max_length=20, choices=PREFERENCIAS_ENVIO, default='email')
  - [ ] Campo confidencial: BooleanField(default=False) - se é destinatário confidencial
  - [ ] Campo bloqueado: BooleanField(default=False) - se está bloqueado para envios
  - [ ] Campo motivo_bloqueio: TextField(blank=True, null=True) - motivo do bloqueio
  - [ ] Constante TIPOS_DESTINATARIO = [
        ('pessoa', 'Pessoa Física'),
        ('instituicao', 'Instituição'),
        ('empresa', 'Empresa'),
        ('ong', 'ONG'),
        ('governo', 'Entidade Governamental'),
        ('internacional', 'Entidade Internacional')
    ]
  - [ ] Constante PREFERENCIAS_ENVIO = [
        ('email', 'Email'),
        ('correio', 'Correio'),
        ('pessoal', 'Entrega Pessoal'),
        ('fax', 'Fax'),
        ('digital', 'Plataforma Digital')
    ]
  - [ ] Método __str__(): return f"{self.nome} ({self.get_tipo_display()})"
  - [ ] Método obter_tipo_display(): return dict(self.TIPOS_DESTINATARIO).get(self.tipo, 'Desconhecido')
  - [ ] Método obter_endereco_completo(): return f"{self.endereco}, {self.cidade}, {self.provincia}, {self.pais}"
  - [ ] Método pode_receber_documentos(): return self.ativo and not self.bloqueado
  - [ ] Método obter_contacto_principal(): return self.contacto_principal or self.nome
  - [ ] Método obter_preferencia_envio(): return self.get_preferencia_envio_display()
  - [ ] Método bloquear_destinatario(motivo): self.bloqueado = True, self.motivo_bloqueio = motivo, self.save()
  - [ ] Método desbloquear_destinatario(): self.bloqueado = False, self.motivo_bloqueio = None, self.save()
  - [ ] Meta: ordering = ['nome']
  - [ ] Meta: verbose_name = "Destinatário"
  - [ ] Meta: verbose_name_plural = "Destinatários"

### 4. Anexos de Saída
- [ ] Criar modelo AnexoDocumentoSaida em saida/models.py
  - [ ] Campo documento: ForeignKey(DocumentoSaida, on_delete=CASCADE, related_name='anexos')
  - [ ] Campo ficheiro: FileField(upload_to='documentos_saida/%Y/%m/') - ficheiro anexado
  - [ ] Campo nome_original: CharField(max_length=255) - nome original do ficheiro
  - [ ] Campo tamanho: PositiveIntegerField() - tamanho em bytes
  - [ ] Campo tipo_mime: CharField(max_length=100, blank=True) - tipo MIME do ficheiro
  - [ ] Campo extensao: CharField(max_length=10, blank=True) - extensão do ficheiro
  - [ ] Campo descricao: CharField(max_length=200, blank=True, null=True) - descrição do anexo
  - [ ] Campo data_upload: DateTimeField(auto_now_add=True) - quando foi carregado
  - [ ] Campo utilizador_upload: ForeignKey('users.User', on_delete=SET_NULL, null=True, related_name='anexos_saida_carregados')
  - [ ] Campo ativo: BooleanField(default=True) - se o anexo está ativo
  - [ ] Campo anexo_obrigatorio: BooleanField(default=False) - se é anexo obrigatório
  - [ ] Campo eh_assinado: BooleanField(default=False) - se contém assinatura digital
  - [ ] Campo hash_arquivo: CharField(max_length=64, blank=True) - hash SHA-256 para verificação
  - [ ] Campo virus_scan: CharField(max_length=20, choices=STATUS_VIRUS, default='pendente')
  - [ ] Campo data_scan: DateTimeField(null=True, blank=True) - quando foi feito o scan
  - [ ] Campo observacoes: TextField(blank=True, null=True) - observações sobre o anexo
  - [ ] Campo confidencial: BooleanField(default=False) - se é anexo confidencial
  - [ ] Constante STATUS_VIRUS = [
        ('pendente', 'Pendente'),
        ('limpo', 'Limpo'),
        ('infectado', 'Infectado'),
        ('erro', 'Erro no Scan')
    ]
  - [ ] Constante TIPOS_PERMITIDOS = [
        'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'image/jpeg', 'image/png', 'image/gif', 'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/plain', 'application/zip'
    ]
  - [ ] Constante TAMANHO_MAXIMO = 10 * 1024 * 1024  # 10MB
  - [ ] Método __str__(): return f"{self.nome_original} ({self.obter_tamanho_formatado()})"
  - [ ] Método obter_tamanho_formatado(): retorna tamanho em KB/MB/GB
  - [ ] Método obter_extensao(): return os.path.splitext(self.nome_original)[1].lower()
  - [ ] Método eh_imagem(): return self.tipo_mime.startswith('image/')
  - [ ] Método eh_pdf(): return self.tipo_mime == 'application/pdf'
  - [ ] Método eh_documento(): return self.tipo_mime in ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
  - [ ] Método pode_visualizar(utilizador): verifica se utilizador pode ver este anexo
  - [ ] Método pode_baixar(utilizador): verifica se utilizador pode baixar este anexo
  - [ ] Método pode_apagar(utilizador): verifica se utilizador pode apagar este anexo
  - [ ] Método gerar_hash(): calcula e define hash SHA-256 do ficheiro
  - [ ] Método verificar_integridade(): verifica se hash atual corresponde ao ficheiro
  - [ ] Método scan_virus(): executa scan de vírus (integração futura)
  - [ ] Método obter_url_visualizacao(): retorna URL para visualização inline
  - [ ] Método obter_url_download(): retorna URL para download
  - [ ] Meta: ordering = ['data_upload']
  - [ ] Meta: verbose_name = "Anexo de Documento de Saída"
  - [ ] Meta: verbose_name_plural = "Anexos de Documentos de Saída"

### 5. Aprovações
- [ ] Criar modelo AprovacaoDocumento em saida/models.py
  - [ ] Campo documento: ForeignKey(DocumentoSaida, on_delete=CASCADE, related_name='aprovacoes')
  - [ ] Campo aprovador: ForeignKey('users.User', on_delete=CASCADE, related_name='aprovacoes_realizadas')
  - [ ] Campo data_aprovacao: DateTimeField(auto_now_add=True) - quando foi aprovado/rejeitado
  - [ ] Campo aprovado: BooleanField() - True=aprovado, False=rejeitado
  - [ ] Campo observacoes: TextField(blank=True, null=True) - observações do aprovador
  - [ ] Campo nivel_aprovacao: CharField(max_length=20, choices=NIVEIS_APROVACAO) - nível da aprovação
  - [ ] Campo ativo: BooleanField(default=True) - se a aprovação está ativa
  - [ ] Campo data_limite: DateTimeField(null=True, blank=True) - prazo para aprovação
  - [ ] Campo automatica: BooleanField(default=False) - se foi aprovação automática
  - [ ] Campo documento_anterior: ForeignKey('self', on_delete=SET_NULL, null=True, blank=True, related_name='aprovacoes_subsequentes')
  - [ ] Campo alteracoes_solicitadas: TextField(blank=True, null=True) - alterações solicitadas
  - [ ] Campo data_alteracoes: DateTimeField(null=True, blank=True) - quando alterações foram feitas
  - [ ] Campo reenviado_para: ForeignKey('users.User', on_delete=SET_NULL, null=True, blank=True, related_name='documentos_reenviados')
  - [ ] Campo data_reenvio: DateTimeField(null=True, blank=True) - quando foi reenviado
  - [ ] Constante NIVEIS_APROVACAO = [
        ('chefe', 'Chefe de Sector'),
        ('pca', 'PCA'),
        ('ambos', 'Chefe + PCA'),
        ('automatica', 'Aprovação Automática')
    ]
  - [ ] Constante STATUS_APROVACAO = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
        ('alteracoes', 'Alterações Solicitadas'),
        ('expirado', 'Expirado')
    ]
  - [ ] Método __str__(): return f"{self.documento.numero_documento} - {self.get_nivel_aprovacao_display()}"
  - [ ] Método obter_status(): retorna status baseado em aprovado e data_limite
  - [ ] Método eh_aprovado(): return self.aprovado is True
  - [ ] Método eh_rejeitado(): return self.aprovado is False
  - [ ] Método eh_pendente(): return self.aprovado is None and (self.data_limite is None or self.data_limite > timezone.now())
  - [ ] Método eh_expirado(): return self.data_limite and self.data_limite < timezone.now() and self.aprovado is None
  - [ ] Método pode_aprovar(utilizador): verifica se utilizador pode aprovar neste nível
  - [ ] Método solicitar_alteracoes(observacoes): marca como rejeitado e solicita alterações
  - [ ] Método aprovar_documento(observacoes): marca como aprovado
  - [ ] Método rejeitar_documento(observacoes): marca como rejeitado
  - [ ] Método reenviar_para_correcao(utilizador): marca para reenvio
  - [ ] Meta: ordering = ['-data_aprovacao']
  - [ ] Meta: verbose_name = "Aprovação de Documento"
  - [ ] Meta: verbose_name_plural = "Aprovações de Documentos"

## 🔄 Fluxo de Aprovação

### 1. Estados do Documento
- [ ] Integrar com modelo EstadoDocumento do core
- [ ] Estados: Rascunho, Em Aprovação, Aprovado, Enviado, Arquivado
- [ ] Implementar transições de estado
- [ ] Implementar validações de aprovação

### 2. Workflow de Aprovação
- [ ] Implementar aprovação por níveis
- [ ] Implementar aprovação por sector
- [ ] Implementar notificações de aprovação
- [ ] Implementar histórico de aprovações

## 📝 Forms

### 1. Forms de Documento
- [ ] Criar DocumentoSaidaForm em saida/forms.py
  - [ ] Meta: model = DocumentoSaida
  - [ ] Meta: fields = ['tipo_documento', 'destinatario', 'assunto', 'conteudo', 'prioridade', 'confidencial', 'requer_comprovativo', 'observacoes']
  - [ ] Widget: SelectWidget para tipo_documento com choices dinâmicos
  - [ ] Widget: SelectWidget para destinatario com choices dinâmicos
  - [ ] Widget: TextareaWidget para conteudo com rows=10
  - [ ] Widget: SelectWidget para prioridade com choices
  - [ ] Método __init__(): filtrar choices por utilizador atual
  - [ ] Método clean_destinatario(): validar se destinatário pode receber documentos
  - [ ] Método clean_conteudo(): validar conteúdo mínimo
  - [ ] Método clean(): validações cruzadas

- [ ] Criar DocumentoSaidaUpdateForm em saida/forms.py
  - [ ] Meta: model = DocumentoSaida
  - [ ] Meta: fields = ['assunto', 'conteudo', 'prioridade', 'confidencial', 'requer_comprovativo', 'observacoes']
  - [ ] Método __init__(): verificar se pode editar
  - [ ] Método clean(): validar se documento não foi aprovado

- [ ] Criar AnexoSaidaForm em saida/forms.py
  - [ ] Meta: model = AnexoDocumentoSaida
  - [ ] Meta: fields = ['ficheiro', 'descricao', 'anexo_obrigatorio', 'confidencial']
  - [ ] Widget: FileInput para ficheiro
  - [ ] Widget: TextareaWidget para descricao com rows=3
  - [ ] Método clean_ficheiro(): validar tipo e tamanho
  - [ ] Método clean(): validações de segurança

- [ ] Criar MultiAnexoSaidaForm em saida/forms.py
  - [ ] Campo ficheiros: MultipleFileField() - múltiplos ficheiros
  - [ ] Campo descricao_geral: CharField(max_length=200, required=False)
  - [ ] Método clean_ficheiros(): validar cada ficheiro
  - [ ] Método clean(): validar tamanho total

### 2. Forms de Aprovação
- [ ] Criar AprovacaoForm em saida/forms.py
  - [ ] Meta: model = AprovacaoDocumento
  - [ ] Meta: fields = ['aprovado', 'observacoes', 'alteracoes_solicitadas']
  - [ ] Widget: RadioSelect para aprovado com choices
  - [ ] Widget: TextareaWidget para observacoes com rows=5
  - [ ] Widget: TextareaWidget para alteracoes_solicitadas com rows=3
  - [ ] Método clean(): validar se observações são obrigatórias para rejeição
  - [ ] Método clean_alteracoes_solicitadas(): validar se alterações são necessárias

- [ ] Criar RejeicaoForm em saida/forms.py
  - [ ] Campo motivo: CharField(max_length=200) - motivo da rejeição
  - [ ] Campo observacoes: TextField() - observações detalhadas
  - [ ] Campo alteracoes_solicitadas: TextField() - alterações necessárias
  - [ ] Método clean(): validar se motivo é obrigatório

### 3. Forms de Destinatário
- [ ] Criar DestinatarioForm em saida/forms.py
  - [ ] Meta: model = Destinatario
  - [ ] Meta: fields = ['nome', 'email', 'telefone', 'telefone_alternativo', 'endereco', 'cidade', 'provincia', 'pais', 'codigo_postal', 'tipo', 'contacto_principal', 'cargo_contacto', 'preferencia_envio', 'confidencial', 'observacoes']
  - [ ] Widget: TextInput para nome com maxlength=200
  - [ ] Widget: EmailInput para email
  - [ ] Widget: TextInput para telefones com pattern
  - [ ] Widget: TextareaWidget para endereco com rows=3
  - [ ] Widget: SelectWidget para tipo com choices
  - [ ] Widget: SelectWidget para preferencia_envio com choices
  - [ ] Método clean_email(): validar formato de email
  - [ ] Método clean_telefone(): validar formato de telefone
  - [ ] Método clean(): validações cruzadas

- [ ] Criar DestinatarioBuscaForm em saida/forms.py
  - [ ] Campo nome: CharField(max_length=200, required=False)
  - [ ] Campo tipo: CharField(max_length=20, required=False)
  - [ ] Campo cidade: CharField(max_length=100, required=False)
  - [ ] Campo ativo: BooleanField(required=False, initial=True)
  - [ ] Widget: TextInput para nome com placeholder
  - [ ] Widget: SelectWidget para tipo com choices
  - [ ] Widget: TextInput para cidade com placeholder

## 🎯 Views

### 1. Views de Documentos
- [ ] Criar ListarDocumentosSaidaView em saida/views.py
  - [ ] Herdar de ListView
  - [ ] Model = DocumentoSaida
  - [ ] Template = 'saida/documento_saida_list.html'
  - [ ] Paginate_by = 20
  - [ ] Context_object_name = 'documentos'
  - [ ] Decorator @login_required
  - [ ] Método get_queryset(): filtrar por sector do utilizador e permissões
  - [ ] Método get_context_data(): adicionar filtros, estatísticas, sectores
  - [ ] Método post(): processar filtros AJAX
  - [ ] Context: 'filtros', 'estatisticas', 'sectores', 'tipos_documento'

- [ ] Criar DetalheDocumentoSaidaView em saida/views.py
  - [ ] Herdar de DetailView
  - [ ] Model = DocumentoSaida
  - [ ] Template = 'saida/documento_saida_detail.html'
  - [ ] Decorator @login_required
  - [ ] Método get_object(): verificar permissões de visualização
  - [ ] Método get_context_data(): adicionar anexos, aprovações, histórico
  - [ ] Context: 'anexos', 'aprovacoes', 'historico', 'pode_aprovar', 'pode_editar'

- [ ] Criar CriarDocumentoSaidaView em saida/views.py
  - [ ] Herdar de CreateView
  - [ ] Model = DocumentoSaida
  - [ ] Form_class = DocumentoSaidaForm
  - [ ] Template = 'saida/documento_saida_form.html'
  - [ ] Decorator @login_required
  - [ ] Success_url = reverse_lazy('saida:lista_documentos')
  - [ ] Método form_valid(): definir utilizador_criador e sector_origem
  - [ ] Método get_form_kwargs(): passar utilizador atual
  - [ ] Método get_context_data(): adicionar tipos_documento, destinatarios

- [ ] Criar EditarDocumentoSaidaView em saida/views.py
  - [ ] Herdar de UpdateView
  - [ ] Model = DocumentoSaida
  - [ ] Form_class = DocumentoSaidaUpdateForm
  - [ ] Template = 'saida/documento_saida_form.html'
  - [ ] Decorator @login_required
  - [ ] Success_url = reverse_lazy('saida:detalhe_documento')
  - [ ] Método get_object(): verificar permissões de edição
  - [ ] Método form_valid(): verificar se pode editar (não aprovado)

### 2. Views de Aprovação
- [ ] Criar AprovarDocumentoView em saida/views.py
  - [ ] Herdar de View
  - [ ] Template = 'saida/aprovacao_form.html'
  - [ ] Decorator @login_required
  - [ ] Método get(): mostrar formulário de aprovação
  - [ ] Método post(): processar aprovação/rejeição
  - [ ] Método get_object(): verificar permissões de aprovação
  - [ ] Método aprovar_documento(): criar AprovacaoDocumento
  - [ ] Método rejeitar_documento(): criar AprovacaoDocumento com rejeição
  - [ ] Método solicitar_alteracoes(): criar AprovacaoDocumento com alterações

- [ ] Criar ListarAprovacoesView em saida/views.py
  - [ ] Herdar de ListView
  - [ ] Model = AprovacaoDocumento
  - [ ] Template = 'saida/aprovacao_list.html'
  - [ ] Paginate_by = 15
  - [ ] Decorator @login_required
  - [ ] Método get_queryset(): filtrar por aprovador atual
  - [ ] Método get_context_data(): adicionar estatísticas de aprovação

- [ ] Criar HistoricoAprovacaoView em saida/views.py
  - [ ] Herdar de DetailView
  - [ ] Model = DocumentoSaida
  - [ ] Template = 'saida/historico_aprovacao.html'
  - [ ] Decorator @login_required
  - [ ] Método get_object(): verificar permissões de visualização
  - [ ] Método get_context_data(): adicionar histórico completo de aprovações

### 3. Views de Destinatários
- [ ] Criar ListarDestinatariosView em saida/views.py
  - [ ] Herdar de ListView
  - [ ] Model = Destinatario
  - [ ] Template = 'saida/destinatario_list.html'
  - [ ] Paginate_by = 25
  - [ ] Decorator @login_required
  - [ ] Método get_queryset(): filtrar destinatários ativos
  - [ ] Método get_context_data(): adicionar filtros por tipo

- [ ] Criar CriarDestinatarioView em saida/views.py
  - [ ] Herdar de CreateView
  - [ ] Model = Destinatario
  - [ ] Form_class = DestinatarioForm
  - [ ] Template = 'saida/destinatario_form.html'
  - [ ] Decorator @login_required
  - [ ] Success_url = reverse_lazy('saida:lista_destinatarios')
  - [ ] Método form_valid(): definir criado_por

- [ ] Criar EditarDestinatarioView em saida/views.py
  - [ ] Herdar de UpdateView
  - [ ] Model = Destinatario
  - [ ] Form_class = DestinatarioForm
  - [ ] Template = 'saida/destinatario_form.html'
  - [ ] Decorator @login_required
  - [ ] Success_url = reverse_lazy('saida:lista_destinatarios')

### 4. Views de Anexos
- [ ] Criar CarregarAnexoSaidaView em saida/views.py
  - [ ] Herdar de View
  - [ ] Template = 'saida/anexo_upload.html'
  - [ ] Decorator @login_required
  - [ ] Método get(): mostrar formulário de upload
  - [ ] Método post(): processar upload de anexo
  - [ ] Método validar_ficheiro(): validar tipo e tamanho
  - [ ] Método gerar_hash(): calcular hash do ficheiro
  - [ ] Método scan_virus(): executar scan de vírus

- [ ] Criar BaixarAnexoSaidaView em saida/views.py
  - [ ] Herdar de View
  - [ ] Decorator @login_required
  - [ ] Método get(): servir ficheiro para download
  - [ ] Método verificar_permissao(): verificar se pode baixar
  - [ ] Método registrar_download(): registrar download no log

- [ ] Criar VisualizarAnexoSaidaView em saida/views.py
  - [ ] Herdar de View
  - [ ] Template = 'saida/anexo_viewer.html'
  - [ ] Decorator @login_required
  - [ ] Método get(): mostrar visualizador de anexo
  - [ ] Método verificar_tipo(): verificar se pode visualizar inline
  - [ ] Método obter_url_visualizacao(): gerar URL para visualização

- [ ] Criar ApagarAnexoSaidaView em saida/views.py
  - [ ] Herdar de DeleteView
  - [ ] Model = AnexoDocumentoSaida
  - [ ] Template = 'saida/anexo_confirmar_apagar.html'
  - [ ] Decorator @login_required
  - [ ] Success_url = reverse_lazy('saida:detalhe_documento')
  - [ ] Método get_object(): verificar permissões de apagar

## 🎨 Templates

### 1. Templates de Documentos
- [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para templates de documentos de saída
- [ ] Criar documento_saida_list.html em templates/saida/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para documento_saida_list.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Documentos de Saída"
  - [ ] Block content: container-fluid com row
  - [ ] Filtros: card com form para estado, sector, tipo, data
  - [ ] Estatísticas: cards com números de documentos por estado
  - [ ] Tabela: documento_saida_table.html com colunas (número, assunto, destinatário, estado, data, ações)
  - [ ] Paginação: pagination.html
  - [ ] JavaScript: filtros AJAX, atualização automática

- [ ] Criar documento_saida_detail.html em templates/saida/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para documento_saida_detail.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "{{ documento.numero_documento }}"
  - [ ] Block content: container com row
  - [ ] Header: card com informações principais (número, assunto, destinatário, estado)
  - [ ] Conteúdo: card com conteúdo do documento
  - [ ] Anexos: card com lista de anexos e botões de upload/download
  - [ ] Aprovações: card com histórico de aprovações
  - [ ] Ações: botões para aprovar, editar, enviar (baseado em permissões)
  - [ ] JavaScript: preview de anexos, confirmação de ações

- [ ] Criar documento_saida_form.html em templates/saida/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para documento_saida_form.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "{{ 'Criar' if not object else 'Editar' }} Documento de Saída"
  - [ ] Block content: container com row
  - [ ] Form: card com form horizontal
  - [ ] Campos: tipo_documento, destinatario, assunto, conteudo, prioridade
  - [ ] Campos opcionais: confidencial, requer_comprovativo, observacoes
  - [ ] Botões: Salvar, Cancelar, Preview
  - [ ] JavaScript: validação em tempo real, preview de conteúdo

### 2. Templates de Aprovação
- [ ] Criar aprovacao_form.html em templates/saida/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para aprovacao_form.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Aprovar Documento"
  - [ ] Block content: container com row
  - [ ] Documento: card com resumo do documento
  - [ ] Form: card com radio buttons (Aprovar/Rejeitar/Solicitar Alterações)
  - [ ] Campos: observacoes, alteracoes_solicitadas
  - [ ] Botões: Confirmar, Cancelar
  - [ ] JavaScript: mostrar/ocultar campos baseado na escolha

- [ ] Criar aprovacao_list.html em templates/saida/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para aprovacao_list.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Aprovações Pendentes"
  - [ ] Block content: container com row
  - [ ] Filtros: card com filtros por estado, data, sector
  - [ ] Lista: cards com documentos pendentes de aprovação
  - [ ] Informações: número, assunto, criador, data_limite, prioridade
  - [ ] Ações: botões para aprovar/rejeitar rapidamente
  - [ ] Paginação: pagination.html

- [ ] Criar historico_aprovacao.html em templates/saida/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para historico_aprovacao.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Histórico de Aprovações"
  - [ ] Block content: container com row
  - [ ] Timeline: componente com histórico cronológico
  - [ ] Entradas: data, aprovador, ação, observações
  - [ ] Estados: badges coloridos para cada estado
  - [ ] Detalhes: expandir para ver observações completas

### 3. Templates de Destinatários
- [ ] Criar destinatario_list.html em templates/saida/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para destinatario_list.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Destinatários"
  - [ ] Block content: container com row
  - [ ] Filtros: card com busca por nome, tipo, cidade
  - [ ] Tabela: destinatario_table.html com colunas (nome, tipo, contacto, cidade, ações)
  - [ ] Ações: editar, bloquear/desbloquear, ver histórico
  - [ ] Paginação: pagination.html

- [ ] Criar destinatario_form.html em templates/saida/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para destinatario_form.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "{{ 'Criar' if not object else 'Editar' }} Destinatário"
  - [ ] Block content: container com row
  - [ ] Form: card com form em duas colunas
  - [ ] Coluna 1: nome, tipo, contacto_principal, cargo_contacto
  - [ ] Coluna 2: email, telefone, telefone_alternativo, preferencia_envio
  - [ ] Endereço: card separado com endereco, cidade, provincia, pais, codigo_postal
  - [ ] Opções: confidencial, observacoes
  - [ ] Botões: Salvar, Cancelar

### 4. Templates de Anexos
- [ ] Criar anexo_saida_upload.html em templates/saida/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para anexo_saida_upload.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Carregar Anexo"
  - [ ] Block content: container com row
  - [ ] Upload: card com drag & drop area
  - [ ] Campos: ficheiro, descricao, anexo_obrigatorio, confidencial
  - [ ] Preview: área para preview do ficheiro
  - [ ] Progress: barra de progresso para upload
  - [ ] Botões: Carregar, Cancelar
  - [ ] JavaScript: drag & drop, preview, validação

- [ ] Criar anexo_saida_list.html em templates/saida/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para anexo_saida_list.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Anexos do Documento"
  - [ ] Block content: container com row
  - [ ] Lista: cards com anexos
  - [ ] Informações: nome, tamanho, tipo, data_upload, descricao
  - [ ] Ações: visualizar, baixar, apagar
  - [ ] Status: badges para virus_scan, confidencial, obrigatorio

- [ ] Criar anexo_viewer.html em templates/saida/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para anexo_viewer.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "{{ anexo.nome_original }}"
  - [ ] Block content: container-fluid
  - [ ] Viewer: área principal para visualização
  - [ ] PDF: embed para PDFs
  - [ ] Imagem: img tag para imagens
  - [ ] Outros: link para download
  - [ ] Controles: zoom, fullscreen, download
  - [ ] JavaScript: controles de visualização

## 🔗 URLs

### 1. URLs de Documentos
- [ ] Configurar URLs em saida/urls.py
  - [ ] URL 'documentos/' → ListarDocumentosSaidaView.as_view(), name='lista_documentos'
  - [ ] URL 'documentos/criar/' → CriarDocumentoSaidaView.as_view(), name='criar_documento'
  - [ ] URL 'documentos/<int:pk>/' → DetalheDocumentoSaidaView.as_view(), name='detalhe_documento'
  - [ ] URL 'documentos/<int:pk>/editar/' → EditarDocumentoSaidaView.as_view(), name='editar_documento'
  - [ ] URL 'documentos/<int:pk>/apagar/' → ApagarDocumentoSaidaView.as_view(), name='apagar_documento'
  - [ ] URL 'documentos/<int:pk>/enviar/' → EnviarDocumentoSaidaView.as_view(), name='enviar_documento'

### 2. URLs de Aprovação
- [ ] Configurar URLs de aprovação
  - [ ] URL 'aprovacoes/' → ListarAprovacoesView.as_view(), name='lista_aprovacoes'
  - [ ] URL 'aprovacoes/<int:pk>/' → AprovarDocumentoView.as_view(), name='aprovar_documento'
  - [ ] URL 'aprovacoes/<int:pk>/historico/' → HistoricoAprovacaoView.as_view(), name='historico_aprovacao'
  - [ ] URL 'aprovacoes/<int:pk>/aprovar/' → AprovarDocumentoView.as_view(), name='aprovar_rapido'
  - [ ] URL 'aprovacoes/<int:pk>/rejeitar/' → RejeitarDocumentoView.as_view(), name='rejeitar_rapido'

### 3. URLs de Destinatários
- [ ] Configurar URLs de gestão de contactos
  - [ ] URL 'destinatarios/' → ListarDestinatariosView.as_view(), name='lista_destinatarios'
  - [ ] URL 'destinatarios/criar/' → CriarDestinatarioView.as_view(), name='criar_destinatario'
  - [ ] URL 'destinatarios/<int:pk>/' → DetalheDestinatarioView.as_view(), name='detalhe_destinatario'
  - [ ] URL 'destinatarios/<int:pk>/editar/' → EditarDestinatarioView.as_view(), name='editar_destinatario'
  - [ ] URL 'destinatarios/<int:pk>/apagar/' → ApagarDestinatarioView.as_view(), name='apagar_destinatario'
  - [ ] URL 'destinatarios/<int:pk>/bloquear/' → BloquearDestinatarioView.as_view(), name='bloquear_destinatario'

### 4. URLs de Anexos
- [ ] Configurar URLs de upload/download
  - [ ] URL 'anexos/carregar/<int:documento_id>/' → CarregarAnexoSaidaView.as_view(), name='carregar_anexo'
  - [ ] URL 'anexos/<int:pk>/baixar/' → BaixarAnexoSaidaView.as_view(), name='baixar_anexo'
  - [ ] URL 'anexos/<int:pk>/visualizar/' → VisualizarAnexoSaidaView.as_view(), name='visualizar_anexo'
  - [ ] URL 'anexos/<int:pk>/apagar/' → ApagarAnexoSaidaView.as_view(), name='apagar_anexo'
  - [ ] URL 'anexos/<int:documento_id>/lista/' → ListarAnexosSaidaView.as_view(), name='lista_anexos'
  - [ ] URL 'anexos/upload-multiplo/<int:documento_id>/' → UploadMultiploAnexosSaidaView.as_view(), name='upload_multiplo_anexos'

## 🛠️ Admin

### 1. Admin Customizado
- [ ] Configurar DocumentoSaidaAdmin em saida/admin.py
  - [ ] List_display: ['numero_documento', 'assunto', 'destinatario', 'tipo_documento', 'estado_atual', 'data_criacao', 'aprovado_por']
  - [ ] List_filter: ['estado_atual', 'tipo_documento', 'prioridade', 'sector_origem', 'confidencial', 'data_criacao']
  - [ ] Search_fields: ['numero_documento', 'assunto', 'destinatario__nome', 'conteudo']
  - [ ] Readonly_fields: ['numero_documento', 'data_criacao', 'data_atualizacao']
  - [ ] Fieldsets: (('Informações Básicas', {'fields': ('numero_documento', 'tipo_documento', 'destinatario', 'assunto')}), ('Conteúdo', {'fields': ('conteudo', 'observacoes')}), ('Configurações', {'fields': ('prioridade', 'confidencial', 'requer_comprovativo')}), ('Aprovação', {'fields': ('aprovado_por', 'data_aprovacao', 'data_envio')}), ('Metadados', {'fields': ('data_criacao', 'data_atualizacao')}))
  - [ ] Actions: ['aprovar_documentos', 'rejeitar_documentos', 'enviar_documentos']
  - [ ] Método aprovar_documentos(): aprovar documentos selecionados
  - [ ] Método rejeitar_documentos(): rejeitar documentos selecionados
  - [ ] Método enviar_documentos(): enviar documentos aprovados

- [ ] Configurar TipoDocumentoSaidaAdmin em saida/admin.py
  - [ ] List_display: ['nome', 'categoria', 'requer_aprovacao', 'numeracao_automatica', 'ativo']
  - [ ] List_filter: ['categoria', 'requer_aprovacao', 'numeracao_automatica', 'ativo']
  - [ ] Search_fields: ['nome', 'descricao']
  - [ ] Fieldsets: (('Informações', {'fields': ('nome', 'categoria', 'descricao')}), ('Configurações', {'fields': ('requer_aprovacao', 'template_padrao', 'prazo_aprovacao')}), ('Numeração', {'fields': ('numeracao_automatica', 'prefixo_numero')}), ('Status', {'fields': ('ativo',)}))
  - [ ] Actions: ['ativar_tipos', 'desativar_tipos']

- [ ] Configurar DestinatarioAdmin em saida/admin.py
  - [ ] List_display: ['nome', 'tipo', 'email', 'telefone', 'cidade', 'ativo', 'bloqueado']
  - [ ] List_filter: ['tipo', 'ativo', 'bloqueado', 'confidencial', 'cidade', 'provincia']
  - [ ] Search_fields: ['nome', 'email', 'telefone', 'contacto_principal']
  - [ ] Fieldsets: (('Informações Básicas', {'fields': ('nome', 'tipo', 'contacto_principal', 'cargo_contacto')}), ('Contacto', {'fields': ('email', 'telefone', 'telefone_alternativo', 'preferencia_envio')}), ('Endereço', {'fields': ('endereco', 'cidade', 'provincia', 'pais', 'codigo_postal')}), ('Configurações', {'fields': ('confidencial', 'ativo', 'bloqueado', 'motivo_bloqueio')}), ('Observações', {'fields': ('observacoes',)}))
  - [ ] Actions: ['bloquear_destinatarios', 'desbloquear_destinatarios']

- [ ] Configurar AnexoDocumentoSaidaAdmin em saida/admin.py
  - [ ] List_display: ['nome_original', 'documento', 'tamanho', 'tipo_mime', 'virus_scan', 'data_upload']
  - [ ] List_filter: ['virus_scan', 'anexo_obrigatorio', 'confidencial', 'eh_assinado', 'data_upload']
  - [ ] Search_fields: ['nome_original', 'descricao', 'documento__numero_documento']
  - [ ] Readonly_fields: ['hash_arquivo', 'data_upload', 'data_scan']
  - [ ] Actions: ['scan_virus_anexos', 'verificar_integridade_anexos']

- [ ] Configurar AprovacaoDocumentoAdmin em saida/admin.py
  - [ ] List_display: ['documento', 'aprovador', 'nivel_aprovacao', 'aprovado', 'data_aprovacao']
  - [ ] List_filter: ['nivel_aprovacao', 'aprovado', 'automatica', 'data_aprovacao']
  - [ ] Search_fields: ['documento__numero_documento', 'aprovador__first_name', 'aprovador__last_name']
  - [ ] Readonly_fields: ['data_aprovacao', 'data_limite']

## 🔄 Signals

### 1. Signals de Documento
- [ ] Criar signals em saida/signals.py
  - [ ] Signal post_save para DocumentoSaida: notificar criação para aprovadores
  - [ ] Signal post_save para AprovacaoDocumento: atualizar estado do documento
  - [ ] Signal pre_save para DocumentoSaida: gerar número automático se necessário
  - [ ] Signal post_delete para DocumentoSaida: limpar anexos relacionados
  - [ ] Signal post_save para AnexoDocumentoSaida: gerar hash e scan de vírus
  - [ ] Método notificar_criacao_documento(): enviar notificação para aprovadores
  - [ ] Método atualizar_estado_apos_aprovacao(): mudar estado baseado na aprovação
  - [ ] Método gerar_numero_documento(): gerar número sequencial
  - [ ] Método processar_anexo_novo(): hash e scan de vírus

### 2. Signals de Notificação
- [ ] Criar signals de notificação
  - [ ] Signal para notificar aprovação pendente
  - [ ] Signal para notificar documento aprovado
  - [ ] Signal para notificar documento rejeitado
  - [ ] Signal para notificar documento enviado
  - [ ] Método notificar_aprovacao_pendente(): notificar aprovadores
  - [ ] Método notificar_documento_aprovado(): notificar criador
  - [ ] Método notificar_documento_rejeitado(): notificar criador com motivo

## 📦 Fixtures

### 1. Dados Iniciais
- [ ] Criar fixtures/saida/tipos_documento_saida.json
  - [ ] Despacho: categoria='despacho', requer_aprovacao='pca', numeracao_automatica=True
  - [ ] Notificação: categoria='notificacao', requer_aprovacao='chefe', numeracao_automatica=True
  - [ ] Certidão: categoria='certidao', requer_aprovacao='ambos', numeracao_automatica=True
  - [ ] Ofício: categoria='oficio', requer_aprovacao='chefe', numeracao_automatica=True
  - [ ] Circular: categoria='circular', requer_aprovacao='pca', numeracao_automatica=True
  - [ ] Memorando: categoria='memorando', requer_aprovacao='chefe', numeracao_automatica=False
  - [ ] Aviso: categoria='aviso', requer_aprovacao='chefe', numeracao_automatica=True
  - [ ] Portaria: categoria='portaria', requer_aprovacao='pca', numeracao_automatica=True

- [ ] Criar fixtures/saida/destinatarios_iniciais.json
  - [ ] Ministérios governamentais
  - [ ] Instituições públicas
  - [ ] Empresas parceiras
  - [ ] ONGs conhecidas
  - [ ] Entidades internacionais

### 2. Management Commands
- [ ] Criar management/commands/criar_tipos_documento_saida.py
  - [ ] Comando para criar/atualizar tipos de documento
  - [ ] Validação de dados existentes
  - [ ] Criação de novos tipos se necessário
  - [ ] Atualização de tipos existentes

- [ ] Criar management/commands/criar_destinatarios_iniciais.py
  - [ ] Comando para criar destinatários iniciais
  - [ ] Importação de dados de CSV/JSON
  - [ ] Validação de dados de contacto
  - [ ] Criação em lote

## 🧪 Testes

### 1. Testes de Modelos
- [ ] Criar testes em saida/tests.py
  - [ ] TestCase DocumentoSaidaModelTest
    - [ ] Teste criar_documento(): criar documento válido
    - [ ] Teste gerar_numero_documento(): verificar numeração automática
    - [ ] Teste pode_aprovar(): verificar permissões de aprovação
    - [ ] Teste eh_aprovado(): verificar status de aprovação
    - [ ] Teste obter_anexos(): verificar anexos ativos
    - [ ] Teste obter_aprovacoes(): verificar histórico de aprovações

  - [ ] TestCase TipoDocumentoSaidaModelTest
    - [ ] Teste criar_tipo(): criar tipo válido
    - [ ] Teste obter_template_content(): verificar template
    - [ ] Teste requer_aprovacao_pca(): verificar níveis de aprovação
    - [ ] Teste gerar_numero_documento(): verificar numeração

  - [ ] TestCase DestinatarioModelTest
    - [ ] Teste criar_destinatario(): criar destinatário válido
    - [ ] Teste obter_endereco_completo(): verificar endereço completo
    - [ ] Teste pode_receber_documentos(): verificar status
    - [ ] Teste bloquear_destinatario(): verificar bloqueio
    - [ ] Teste desbloquear_destinatario(): verificar desbloqueio

  - [ ] TestCase AnexoDocumentoSaidaModelTest
    - [ ] Teste criar_anexo(): criar anexo válido
    - [ ] Teste obter_tamanho_formatado(): verificar formatação
    - [ ] Teste eh_imagem(): verificar tipo de ficheiro
    - [ ] Teste eh_pdf(): verificar tipo de ficheiro
    - [ ] Teste gerar_hash(): verificar hash SHA-256
    - [ ] Teste verificar_integridade(): verificar integridade

  - [ ] TestCase AprovacaoDocumentoModelTest
    - [ ] Teste criar_aprovacao(): criar aprovação válida
    - [ ] Teste eh_aprovado(): verificar status
    - [ ] Teste eh_rejeitado(): verificar status
    - [ ] Teste eh_pendente(): verificar status
    - [ ] Teste eh_expirado(): verificar expiração
    - [ ] Teste aprovar_documento(): aprovar documento
    - [ ] Teste rejeitar_documento(): rejeitar documento

### 2. Testes de Views
- [ ] TestCase DocumentoSaidaViewTest
  - [ ] Teste listar_documentos(): verificar listagem
  - [ ] Teste criar_documento(): verificar criação
  - [ ] Teste editar_documento(): verificar edição
  - [ ] Teste detalhe_documento(): verificar detalhes
  - [ ] Teste permissoes_visualizacao(): verificar permissões
  - [ ] Teste filtros_documentos(): verificar filtros

- [ ] TestCase AprovacaoViewTest
  - [ ] Teste aprovar_documento(): verificar aprovação
  - [ ] Teste rejeitar_documento(): verificar rejeição
  - [ ] Teste solicitar_alteracoes(): verificar alterações
  - [ ] Teste permissoes_aprovacao(): verificar permissões
  - [ ] Teste historico_aprovacao(): verificar histórico

- [ ] TestCase DestinatarioViewTest
  - [ ] Teste listar_destinatarios(): verificar listagem
  - [ ] Teste criar_destinatario(): verificar criação
  - [ ] Teste editar_destinatario(): verificar edição
  - [ ] Teste bloquear_destinatario(): verificar bloqueio
  - [ ] Teste filtros_destinatarios(): verificar filtros

- [ ] TestCase AnexoSaidaViewTest
  - [ ] Teste carregar_anexo(): verificar upload
  - [ ] Teste baixar_anexo(): verificar download
  - [ ] Teste visualizar_anexo(): verificar visualização
  - [ ] Teste apagar_anexo(): verificar apagar
  - [ ] Teste permissoes_anexo(): verificar permissões

### 3. Testes de Forms
- [ ] TestCase DocumentoSaidaFormTest
  - [ ] Teste form_valido(): verificar validação
  - [ ] Teste clean_destinatario(): verificar validação de destinatário
  - [ ] Teste clean_conteudo(): verificar validação de conteúdo
  - [ ] Teste campos_obrigatorios(): verificar campos obrigatórios

- [ ] TestCase AprovacaoFormTest
  - [ ] Teste form_valido(): verificar validação
  - [ ] Teste clean(): verificar validações cruzadas
  - [ ] Teste observacoes_obrigatorias(): verificar observações

- [ ] TestCase DestinatarioFormTest
  - [ ] Teste form_valido(): verificar validação
  - [ ] Teste clean_email(): verificar formato de email
  - [ ] Teste clean_telefone(): verificar formato de telefone
  - [ ] Teste campos_obrigatorios(): verificar campos obrigatórios

### 4. Testes de Signals
- [ ] TestCase DocumentoSaidaSignalsTest
  - [ ] Teste signal_criacao(): verificar notificação de criação
  - [ ] Teste signal_aprovacao(): verificar atualização de estado
  - [ ] Teste signal_numero_automatico(): verificar numeração
  - [ ] Teste signal_anexo_novo(): verificar processamento de anexo

### 5. Testes de Integração
- [ ] TestCase FluxoAprovacaoTest
  - [ ] Teste fluxo_completo(): criar → aprovar → enviar
  - [ ] Teste fluxo_rejeicao(): criar → rejeitar → corrigir → aprovar
  - [ ] Teste fluxo_alteracoes(): criar → solicitar alterações → corrigir → aprovar
  - [ ] Teste notificacoes_fluxo(): verificar notificações em cada etapa

## 📋 Validação Final
- [ ] Documentos de saída criados corretamente
- [ ] Fluxo de aprovação funcionando
- [ ] Estados atualizados corretamente
- [ ] Anexos uploadados e acessíveis
- [ ] Destinatários geridos corretamente
- [ ] Notificações enviadas
- [ ] Relatórios gerados
- [ ] Testes passando
- [ ] Numeração automática funcionando
- [ ] Templates renderizando corretamente
- [ ] URLs funcionando
- [ ] Admin configurado
- [ ] Signals funcionando
- [ ] Fixtures carregadas

---

**Nota:** Esta app gere o fluxo de saída de documentos com controle de aprovação.
