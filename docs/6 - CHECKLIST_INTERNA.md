# 📋 6. CHECKLIST - APP INTERNA

## 🎯 Objetivo
Gestão de comunicação entre sectores (Chefes ↔ Colaboradores, Chefes ↔ Chefes) com mensagens e documentos internos.

## 💬 Modelos de Comunicação

### 1. Mensagem Interna
- [ ] Criar modelo MensagemInterna em interna/models.py
  - [ ] Campo titulo: CharField(max_length=200) - título da mensagem
  - [ ] Campo conteudo: TextField() - conteúdo da mensagem
  - [ ] Campo tipo_mensagem: ForeignKey(TipoMensagem, on_delete=PROTECT, related_name='mensagens')
  - [ ] Campo prioridade: CharField(max_length=10, choices=PRIORIDADES, default='normal')
  - [ ] Campo remetente: ForeignKey('users.User', on_delete=CASCADE, related_name='mensagens_enviadas')
  - [ ] Campo destinatario: ForeignKey('users.User', on_delete=CASCADE, related_name='mensagens_recebidas', null=True, blank=True)
  - [ ] Campo sector_origem: ForeignKey('core.Sector', on_delete=PROTECT, related_name='mensagens_enviadas')
  - [ ] Campo sector_destino: ForeignKey('core.Sector', on_delete=PROTECT, related_name='mensagens_recebidas', null=True, blank=True)
  - [ ] Campo grupo_destino: ForeignKey('GrupoComunicacao', on_delete=CASCADE, related_name='mensagens', null=True, blank=True)
  - [ ] Campo data_envio: DateTimeField(auto_now_add=True) - quando foi enviada
  - [ ] Campo data_leitura: DateTimeField(null=True, blank=True) - quando foi lida
  - [ ] Campo lida: BooleanField(default=False) - se foi lida
  - [ ] Campo arquivada: BooleanField(default=False) - se foi arquivada
  - [ ] Campo ativo: BooleanField(default=True) - se está ativa
  - [ ] Campo urgente: BooleanField(default=False) - se é urgente
  - [ ] Campo confidencial: BooleanField(default=False) - se é confidencial
  - [ ] Campo requer_resposta: BooleanField(default=False) - se requer resposta
  - [ ] Campo data_limite_resposta: DateTimeField(null=True, blank=True) - prazo para resposta
  - [ ] Campo observacoes: TextField(blank=True, null=True) - observações adicionais
  - [ ] Campo data_atualizacao: DateTimeField(auto_now=True)
  - [ ] Constante PRIORIDADES = [
        ('baixa', 'Baixa'),
        ('normal', 'Normal'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente')
    ]
  - [ ] Constante TIPOS_COMUNICACAO = [
        ('individual', 'Individual'),
        ('sector', 'Sector'),
        ('grupo', 'Grupo'),
        ('geral', 'Geral')
    ]
  - [ ] Método __str__(): return f"{self.titulo} - {self.remetente.get_full_name()}"
  - [ ] Método obter_prioridade(): return self.get_prioridade_display()
  - [ ] Método marcar_como_lida(): self.lida = True, self.data_leitura = timezone.now(), self.save()
  - [ ] Método arquivar_mensagem(): self.arquivada = True, self.save()
  - [ ] Método pode_responder(): return self.requer_resposta and not self.arquivada
  - [ ] Método eh_urgente(): return self.urgente or self.prioridade == 'urgente'
  - [ ] Método obter_destinatarios(): retorna lista de destinatários (individual, sector, grupo)
  - [ ] Método obter_respostas(): return self.respostas.filter(ativo=True).order_by('data_resposta')
  - [ ] Método obter_anexos(): return self.anexos.filter(ativo=True)
  - [ ] Método pode_visualizar(utilizador): verifica permissões de visualização
  - [ ] Método pode_responder(utilizador): verifica se pode responder
  - [ ] Método obter_tempo_resposta(): calcula tempo médio de resposta
  - [ ] Meta: ordering = ['-data_envio']
  - [ ] Meta: verbose_name = "Mensagem Interna"
  - [ ] Meta: verbose_name_plural = "Mensagens Internas"

### 2. Tipos de Mensagem
- [ ] Criar modelo TipoMensagem em interna/models.py
  - [ ] Campo nome: CharField(max_length=50, unique=True) - nome do tipo
  - [ ] Campo descricao: CharField(max_length=200) - descrição do tipo
  - [ ] Campo cor: CharField(max_length=7, default='#007bff') - cor hexadecimal
  - [ ] Campo icone: CharField(max_length=50, default='fas fa-envelope') - classe do ícone
  - [ ] Campo ativo: BooleanField(default=True) - se está ativo
  - [ ] Campo prioridade_padrao: CharField(max_length=10, choices=PRIORIDADES, default='normal')
  - [ ] Campo requer_resposta_padrao: BooleanField(default=False) - se requer resposta por padrão
  - [ ] Campo confidencial_padrao: BooleanField(default=False) - se é confidencial por padrão
  - [ ] Campo template_conteudo: TextField(blank=True, null=True) - template de conteúdo
  - [ ] Campo data_criacao: DateTimeField(auto_now_add=True)
  - [ ] Campo criado_por: ForeignKey('users.User', on_delete=SET_NULL, null=True, related_name='tipos_mensagem_criados')
  - [ ] Constante PRIORIDADES = [
        ('baixa', 'Baixa'),
        ('normal', 'Normal'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente')
    ]
  - [ ] Constante CORES_PREDEFINIDAS = [
        ('#007bff', 'Azul'),
        ('#28a745', 'Verde'),
        ('#ffc107', 'Amarelo'),
        ('#dc3545', 'Vermelho'),
        ('#6f42c1', 'Roxo'),
        ('#17a2b8', 'Ciano'),
        ('#6c757d', 'Cinza')
    ]
  - [ ] Constante ICONES_PREDEFINIDOS = [
        ('fas fa-envelope', 'Envelope'),
        ('fas fa-exclamation-triangle', 'Aviso'),
        ('fas fa-calendar-alt', 'Reunião'),
        ('fas fa-tasks', 'Tarefa'),
        ('fas fa-info-circle', 'Informação'),
        ('fas fa-bullhorn', 'Anúncio'),
        ('fas fa-question-circle', 'Pergunta')
    ]
  - [ ] Método __str__(): return self.nome
  - [ ] Método obter_cor(): return self.cor
  - [ ] Método obter_icone(): return self.icone
  - [ ] Método obter_template(): return self.template_conteudo or ''
  - [ ] Método aplicar_template(contexto): aplica template com contexto
  - [ ] Meta: ordering = ['nome']
  - [ ] Meta: verbose_name = "Tipo de Mensagem"
  - [ ] Meta: verbose_name_plural = "Tipos de Mensagem"

### 3. Anexos de Mensagem
- [ ] Criar modelo AnexoMensagem em interna/models.py
  - [ ] Campo mensagem: ForeignKey(MensagemInterna, on_delete=CASCADE, related_name='anexos')
  - [ ] Campo ficheiro: FileField(upload_to='mensagens_internas/%Y/%m/') - ficheiro anexado
  - [ ] Campo nome_original: CharField(max_length=255) - nome original do ficheiro
  - [ ] Campo tamanho: PositiveIntegerField() - tamanho em bytes
  - [ ] Campo tipo_mime: CharField(max_length=100, blank=True) - tipo MIME do ficheiro
  - [ ] Campo extensao: CharField(max_length=10, blank=True) - extensão do ficheiro
  - [ ] Campo descricao: CharField(max_length=200, blank=True, null=True) - descrição do anexo
  - [ ] Campo data_upload: DateTimeField(auto_now_add=True) - quando foi carregado
  - [ ] Campo utilizador_upload: ForeignKey('users.User', on_delete=SET_NULL, null=True, related_name='anexos_mensagem_carregados')
  - [ ] Campo ativo: BooleanField(default=True) - se o anexo está ativo
  - [ ] Campo confidencial: BooleanField(default=False) - se é anexo confidencial
  - [ ] Campo hash_arquivo: CharField(max_length=64, blank=True) - hash SHA-256 para verificação
  - [ ] Campo virus_scan: CharField(max_length=20, choices=STATUS_VIRUS, default='pendente')
  - [ ] Campo data_scan: DateTimeField(null=True, blank=True) - quando foi feito o scan
  - [ ] Campo observacoes: TextField(blank=True, null=True) - observações sobre o anexo
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
  - [ ] Meta: verbose_name = "Anexo de Mensagem"
  - [ ] Meta: verbose_name_plural = "Anexos de Mensagens"

### 4. Respostas de Mensagem
- [ ] Criar modelo RespostaMensagem em interna/models.py
  - [ ] Campo mensagem_original: ForeignKey(MensagemInterna, on_delete=CASCADE, related_name='respostas')
  - [ ] Campo remetente: ForeignKey('users.User', on_delete=CASCADE, related_name='respostas_enviadas')
  - [ ] Campo conteudo: TextField() - conteúdo da resposta
  - [ ] Campo data_resposta: DateTimeField(auto_now_add=True) - quando foi respondida
  - [ ] Campo lida: BooleanField(default=False) - se foi lida pelo remetente original
  - [ ] Campo ativo: BooleanField(default=True) - se está ativa
  - [ ] Campo data_leitura: DateTimeField(null=True, blank=True) - quando foi lida
  - [ ] Campo confidencial: BooleanField(default=False) - se é resposta confidencial
  - [ ] Campo urgente: BooleanField(default=False) - se é resposta urgente
  - [ ] Campo observacoes: TextField(blank=True, null=True) - observações adicionais
  - [ ] Campo data_atualizacao: DateTimeField(auto_now=True)
  - [ ] Método __str__(): return f"Resposta de {self.remetente.get_full_name()} para {self.mensagem_original.titulo}"
  - [ ] Método marcar_como_lida(): self.lida = True, self.data_leitura = timezone.now(), self.save()
  - [ ] Método obter_tempo_resposta(): calcula tempo entre mensagem original e resposta
  - [ ] Método pode_visualizar(utilizador): verifica permissões de visualização
  - [ ] Método pode_responder(utilizador): verifica se pode responder à resposta
  - [ ] Método obter_anexos(): return self.anexos.filter(ativo=True)
  - [ ] Meta: ordering = ['data_resposta']
  - [ ] Meta: verbose_name = "Resposta de Mensagem"
  - [ ] Meta: verbose_name_plural = "Respostas de Mensagens"

### 5. Grupos de Comunicação
- [ ] Criar modelo GrupoComunicacao em interna/models.py
  - [ ] Campo nome: CharField(max_length=100, unique=True) - nome do grupo
  - [ ] Campo descricao: TextField(blank=True, null=True) - descrição do grupo
  - [ ] Campo sector: ForeignKey('core.Sector', on_delete=PROTECT, related_name='grupos_comunicacao', null=True, blank=True)
  - [ ] Campo membros: ManyToManyField('users.User', related_name='grupos_membro', blank=True)
  - [ ] Campo ativo: BooleanField(default=True) - se está ativo
  - [ ] Campo criado_por: ForeignKey('users.User', on_delete=CASCADE, related_name='grupos_criados')
  - [ ] Campo data_criacao: DateTimeField(auto_now_add=True)
  - [ ] Campo data_atualizacao: DateTimeField(auto_now=True)
  - [ ] Campo tipo_grupo: CharField(max_length=20, choices=TIPOS_GRUPO, default='geral')
  - [ ] Campo confidencial: BooleanField(default=False) - se é grupo confidencial
  - [ ] Campo max_membros: PositiveIntegerField(default=50) - máximo de membros
  - [ ] Campo observacoes: TextField(blank=True, null=True) - observações sobre o grupo
  - [ ] Constante TIPOS_GRUPO = [
        ('geral', 'Geral'),
        ('sector', 'Sector'),
        ('projeto', 'Projeto'),
        ('comissao', 'Comissão'),
        ('equipe', 'Equipe'),
        ('temporario', 'Temporário')
    ]
  - [ ] Método __str__(): return self.nome
  - [ ] Método obter_membros_count(): return self.membros.count()
  - [ ] Método add_membro(utilizador): adiciona utilizador ao grupo
  - [ ] Método remove_membro(utilizador): remove utilizador do grupo
  - [ ] Método eh_membro(utilizador): verifica se utilizador é membro
  - [ ] Método pode_adicionar_membro(utilizador): verifica se pode adicionar membros
  - [ ] Método obter_mensagens_recentes(): retorna últimas mensagens do grupo
  - [ ] Método obter_estatisticas(): retorna estatísticas do grupo
  - [ ] Meta: ordering = ['nome']
  - [ ] Meta: verbose_name = "Grupo de Comunicação"
  - [ ] Meta: verbose_name_plural = "Grupos de Comunicação"

## 🔄 Fluxo de Comunicação

### 1. Hierarquia de Comunicação
- [ ] Implementar regras de comunicação
  - [ ] Chefe → Colaboradores do mesmo sector
  - [ ] Chefe → Outros Chefes
  - [ ] Colaborador → Chefe do sector
  - [ ] PCA/CA → Todos os sectores

### 2. Estados da Mensagem
- [ ] Integrar com modelo EstadoDocumento do core
- [ ] Estados: Enviada, Entregue, Lida, Respondida, Arquivada
- [ ] Implementar notificações automáticas
- [ ] Implementar histórico de comunicação

## 📝 Forms

### 1. Forms de Mensagem
- [ ] Criar MensagemInternaForm em interna/forms.py
  - [ ] Meta: model = MensagemInterna
  - [ ] Meta: fields = ['titulo', 'tipo_mensagem', 'destinatario', 'sector_destino', 'grupo_destino', 'conteudo', 'prioridade', 'urgente', 'confidencial', 'requer_resposta', 'data_limite_resposta', 'observacoes']
  - [ ] Widget: TextInput para titulo com maxlength=200
  - [ ] Widget: SelectWidget para tipo_mensagem com choices dinâmicos
  - [ ] Widget: SelectWidget para destinatario com choices dinâmicos
  - [ ] Widget: SelectWidget para sector_destino com choices dinâmicos
  - [ ] Widget: SelectWidget para grupo_destino com choices dinâmicos
  - [ ] Widget: TextareaWidget para conteudo com rows=10
  - [ ] Widget: SelectWidget para prioridade com choices
  - [ ] Widget: DateTimeInput para data_limite_resposta
  - [ ] Método __init__(): filtrar choices por utilizador atual
  - [ ] Método clean_destinatario(): validar destinatário baseado em hierarquia
  - [ ] Método clean_conteudo(): validar conteúdo mínimo
  - [ ] Método clean(): validações cruzadas de destinatário

- [ ] Criar MensagemInternaUpdateForm em interna/forms.py
  - [ ] Meta: model = MensagemInterna
  - [ ] Meta: fields = ['titulo', 'conteudo', 'prioridade', 'urgente', 'confidencial', 'requer_resposta', 'data_limite_resposta', 'observacoes']
  - [ ] Método __init__(): verificar se pode editar
  - [ ] Método clean(): validar se mensagem não foi lida

- [ ] Criar AnexoMensagemForm em interna/forms.py
  - [ ] Meta: model = AnexoMensagem
  - [ ] Meta: fields = ['ficheiro', 'descricao', 'confidencial']
  - [ ] Widget: FileInput para ficheiro
  - [ ] Widget: TextareaWidget para descricao com rows=3
  - [ ] Método clean_ficheiro(): validar tipo e tamanho
  - [ ] Método clean(): validações de segurança

- [ ] Criar MultiAnexoMensagemForm em interna/forms.py
  - [ ] Campo ficheiros: MultipleFileField() - múltiplos ficheiros
  - [ ] Campo descricao_geral: CharField(max_length=200, required=False)
  - [ ] Método clean_ficheiros(): validar cada ficheiro
  - [ ] Método clean(): validar tamanho total

### 2. Forms de Resposta
- [ ] Criar RespostaMensagemForm em interna/forms.py
  - [ ] Meta: model = RespostaMensagem
  - [ ] Meta: fields = ['conteudo', 'confidencial', 'urgente', 'observacoes']
  - [ ] Widget: TextareaWidget para conteudo com rows=8
  - [ ] Widget: CheckboxInput para confidencial
  - [ ] Widget: CheckboxInput para urgente
  - [ ] Widget: TextareaWidget para observacoes com rows=3
  - [ ] Método clean_conteudo(): validar conteúdo mínimo
  - [ ] Método clean(): validações de resposta

- [ ] Criar RespostaRapidaForm em interna/forms.py
  - [ ] Campo conteudo: CharField(max_length=500) - resposta rápida
  - [ ] Campo urgente: BooleanField(required=False)
  - [ ] Widget: TextInput para conteudo com placeholder
  - [ ] Método clean_conteudo(): validar conteúdo mínimo

### 3. Forms de Grupo
- [ ] Criar GrupoComunicacaoForm em interna/forms.py
  - [ ] Meta: model = GrupoComunicacao
  - [ ] Meta: fields = ['nome', 'descricao', 'sector', 'tipo_grupo', 'confidencial', 'max_membros', 'observacoes']
  - [ ] Widget: TextInput para nome com maxlength=100
  - [ ] Widget: TextareaWidget para descricao com rows=3
  - [ ] Widget: SelectWidget para sector com choices dinâmicos
  - [ ] Widget: SelectWidget para tipo_grupo com choices
  - [ ] Widget: NumberInput para max_membros com min=1, max=100
  - [ ] Método clean_nome(): validar nome único
  - [ ] Método clean_max_membros(): validar limite máximo
  - [ ] Método clean(): validações cruzadas

- [ ] Criar GestaoMembrosForm em interna/forms.py
  - [ ] Campo membros: ModelMultipleChoiceField(queryset=User.objects.filter(ativo=True))
  - [ ] Widget: CheckboxSelectMultiple para membros
  - [ ] Método clean_membros(): validar número máximo de membros
  - [ ] Método clean(): validações de permissões

- [ ] Criar BuscaGrupoForm em interna/forms.py
  - [ ] Campo nome: CharField(max_length=100, required=False)
  - [ ] Campo tipo_grupo: CharField(max_length=20, required=False)
  - [ ] Campo sector: CharField(max_length=50, required=False)
  - [ ] Campo ativo: BooleanField(required=False, initial=True)
  - [ ] Widget: TextInput para nome com placeholder
  - [ ] Widget: SelectWidget para tipo_grupo com choices
  - [ ] Widget: SelectWidget para sector com choices

## 🎯 Views

### 1. Views de Mensagens
- [ ] Criar ListarMensagensInternasView em interna/views.py
  - [ ] Herdar de ListView
  - [ ] Model = MensagemInterna
  - [ ] Template = 'interna/mensagem_list.html'
  - [ ] Paginate_by = 20
  - [ ] Context_object_name = 'mensagens'
  - [ ] Decorator @login_required
  - [ ] Método get_queryset(): filtrar por utilizador atual (enviadas/recebidas)
  - [ ] Método get_context_data(): adicionar filtros, estatísticas, tipos_mensagem
  - [ ] Método post(): processar filtros AJAX
  - [ ] Context: 'filtros', 'estatisticas', 'tipos_mensagem', 'sectores'

- [ ] Criar DetalheMensagemInternaView em interna/views.py
  - [ ] Herdar de DetailView
  - [ ] Model = MensagemInterna
  - [ ] Template = 'interna/mensagem_detail.html'
  - [ ] Decorator @login_required
  - [ ] Método get_object(): verificar permissões de visualização
  - [ ] Método get_context_data(): adicionar respostas, anexos, histórico
  - [ ] Método post(): marcar como lida automaticamente
  - [ ] Context: 'respostas', 'anexos', 'historico', 'pode_responder', 'pode_arquivar'

- [ ] Criar CriarMensagemInternaView em interna/views.py
  - [ ] Herdar de CreateView
  - [ ] Model = MensagemInterna
  - [ ] Form_class = MensagemInternaForm
  - [ ] Template = 'interna/mensagem_form.html'
  - [ ] Decorator @login_required
  - [ ] Success_url = reverse_lazy('interna:lista_mensagens')
  - [ ] Método form_valid(): definir remetente e sector_origem
  - [ ] Método get_form_kwargs(): passar utilizador atual
  - [ ] Método get_context_data(): adicionar tipos_mensagem, destinatarios, grupos

- [ ] Criar EditarMensagemInternaView em interna/views.py
  - [ ] Herdar de UpdateView
  - [ ] Model = MensagemInterna
  - [ ] Form_class = MensagemInternaUpdateForm
  - [ ] Template = 'interna/mensagem_form.html'
  - [ ] Decorator @login_required
  - [ ] Success_url = reverse_lazy('interna:detalhe_mensagem')
  - [ ] Método get_object(): verificar permissões de edição
  - [ ] Método form_valid(): verificar se pode editar (não lida)

### 2. Views de Comunicação
- [ ] Criar CaixaEntradaView em interna/views.py
  - [ ] Herdar de ListView
  - [ ] Model = MensagemInterna
  - [ ] Template = 'interna/caixa_entrada.html'
  - [ ] Paginate_by = 15
  - [ ] Decorator @login_required
  - [ ] Método get_queryset(): filtrar mensagens recebidas pelo utilizador
  - [ ] Método get_context_data(): adicionar estatísticas de entrada
  - [ ] Context: 'mensagens_nao_lidas', 'mensagens_urgentes', 'estatisticas'

- [ ] Criar CaixaSaidaView em interna/views.py
  - [ ] Herdar de ListView
  - [ ] Model = MensagemInterna
  - [ ] Template = 'interna/caixa_saida.html'
  - [ ] Paginate_by = 15
  - [ ] Decorator @login_required
  - [ ] Método get_queryset(): filtrar mensagens enviadas pelo utilizador
  - [ ] Método get_context_data(): adicionar estatísticas de saída
  - [ ] Context: 'mensagens_enviadas', 'mensagens_respondidas', 'estatisticas'

- [ ] Criar MensagensNaoLidasView em interna/views.py
  - [ ] Herdar de ListView
  - [ ] Model = MensagemInterna
  - [ ] Template = 'interna/mensagens_nao_lidas.html'
  - [ ] Paginate_by = 10
  - [ ] Decorator @login_required
  - [ ] Método get_queryset(): filtrar mensagens não lidas
  - [ ] Método get_context_data(): adicionar contadores
  - [ ] Context: 'total_nao_lidas', 'urgentes_nao_lidas', 'requerem_resposta'

### 3. Views de Resposta
- [ ] Criar ResponderMensagemView em interna/views.py
  - [ ] Herdar de View
  - [ ] Template = 'interna/resposta_form.html'
  - [ ] Decorator @login_required
  - [ ] Método get(): mostrar formulário de resposta
  - [ ] Método post(): processar resposta
  - [ ] Método get_object(): verificar permissões de resposta
  - [ ] Método criar_resposta(): criar RespostaMensagem
  - [ ] Método notificar_resposta(): notificar remetente original

- [ ] Criar HistoricoComunicacaoView em interna/views.py
  - [ ] Herdar de DetailView
  - [ ] Model = MensagemInterna
  - [ ] Template = 'interna/historico_comunicacao.html'
  - [ ] Decorator @login_required
  - [ ] Método get_object(): verificar permissões de visualização
  - [ ] Método get_context_data(): adicionar histórico completo
  - [ ] Context: 'mensagem_original', 'respostas', 'anexos', 'timeline'

### 4. Views de Grupos
- [ ] Criar ListarGruposComunicacaoView em interna/views.py
  - [ ] Herdar de ListView
  - [ ] Model = GrupoComunicacao
  - [ ] Template = 'interna/grupo_list.html'
  - [ ] Paginate_by = 20
  - [ ] Decorator @login_required
  - [ ] Método get_queryset(): filtrar grupos do utilizador
  - [ ] Método get_context_data(): adicionar filtros por tipo
  - [ ] Context: 'grupos_membro', 'grupos_criados', 'tipos_grupo'

- [ ] Criar CriarGrupoComunicacaoView em interna/views.py
  - [ ] Herdar de CreateView
  - [ ] Model = GrupoComunicacao
  - [ ] Form_class = GrupoComunicacaoForm
  - [ ] Template = 'interna/grupo_form.html'
  - [ ] Decorator @login_required
  - [ ] Success_url = reverse_lazy('interna:lista_grupos')
  - [ ] Método form_valid(): definir criado_por e adicionar como membro
  - [ ] Método get_form_kwargs(): passar utilizador atual

- [ ] Criar EditarGrupoComunicacaoView em interna/views.py
  - [ ] Herdar de UpdateView
  - [ ] Model = GrupoComunicacao
  - [ ] Form_class = GrupoComunicacaoForm
  - [ ] Template = 'interna/grupo_form.html'
  - [ ] Decorator @login_required
  - [ ] Success_url = reverse_lazy('interna:lista_grupos')
  - [ ] Método get_object(): verificar permissões de edição

### 5. Views de Anexos
- [ ] Criar CarregarAnexoMensagemView em interna/views.py
  - [ ] Herdar de View
  - [ ] Template = 'interna/anexo_upload.html'
  - [ ] Decorator @login_required
  - [ ] Método get(): mostrar formulário de upload
  - [ ] Método post(): processar upload de anexo
  - [ ] Método validar_ficheiro(): validar tipo e tamanho
  - [ ] Método gerar_hash(): calcular hash do ficheiro
  - [ ] Método scan_virus(): executar scan de vírus

- [ ] Criar BaixarAnexoMensagemView em interna/views.py
  - [ ] Herdar de View
  - [ ] Decorator @login_required
  - [ ] Método get(): servir ficheiro para download
  - [ ] Método verificar_permissao(): verificar se pode baixar
  - [ ] Método registrar_download(): registrar download no log

- [ ] Criar VisualizarAnexoMensagemView em interna/views.py
  - [ ] Herdar de View
  - [ ] Template = 'interna/anexo_viewer.html'
  - [ ] Decorator @login_required
  - [ ] Método get(): mostrar visualizador de anexo
  - [ ] Método verificar_tipo(): verificar se pode visualizar inline
  - [ ] Método obter_url_visualizacao(): gerar URL para visualização

## 🎨 Templates

### 1. Templates de Mensagens
- [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para templates de mensagens
- [ ] Criar mensagem_list.html em templates/interna/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para mensagem_list.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Mensagens Internas"
  - [ ] Block content: container-fluid com row
  - [ ] Filtros: card com form para tipo, prioridade, data, sector
  - [ ] Estatísticas: cards com números de mensagens por estado
  - [ ] Tabela: mensagem_table.html com colunas (título, remetente, destinatário, tipo, prioridade, data, ações)
  - [ ] Paginação: pagination.html
  - [ ] JavaScript: filtros AJAX, atualização automática

- [ ] Criar mensagem_detail.html em templates/interna/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para mensagem_detail.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "{{ mensagem.titulo }}"
  - [ ] Block content: container com row
  - [ ] Header: card com informações principais (título, remetente, destinatário, tipo, prioridade)
  - [ ] Conteúdo: card com conteúdo da mensagem
  - [ ] Anexos: card com lista de anexos e botões de upload/download
  - [ ] Respostas: card com respostas e formulário de resposta
  - [ ] Ações: botões para responder, arquivar, marcar como lida (baseado em permissões)
  - [ ] JavaScript: preview de anexos, resposta rápida, confirmação de ações

- [ ] Criar mensagem_form.html em templates/interna/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para mensagem_form.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "{{ 'Criar' if not object else 'Editar' }} Mensagem Interna"
  - [ ] Block content: container com row
  - [ ] Form: card com form horizontal
  - [ ] Campos: titulo, tipo_mensagem, destinatario, sector_destino, grupo_destino
  - [ ] Campos: conteudo, prioridade, urgente, confidencial, requer_resposta
  - [ ] Campos opcionais: data_limite_resposta, observacoes
  - [ ] Botões: Enviar, Salvar Rascunho, Cancelar, Preview
  - [ ] JavaScript: validação em tempo real, preview de conteúdo, seleção dinâmica de destinatários

### 2. Templates de Comunicação
- [ ] Criar caixa_entrada.html em templates/interna/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para caixa_entrada.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Caixa de Entrada"
  - [ ] Block content: container com row
  - [ ] Estatísticas: cards com mensagens não lidas, urgentes, requerem resposta
  - [ ] Filtros: card com filtros por tipo, prioridade, data
  - [ ] Lista: cards com mensagens recebidas
  - [ ] Informações: título, remetente, tipo, prioridade, data_envio, lida
  - [ ] Ações: botões para ler, responder rapidamente, arquivar
  - [ ] Paginação: pagination.html

- [ ] Criar caixa_saida.html em templates/interna/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para caixa_saida.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Caixa de Saída"
  - [ ] Block content: container com row
  - [ ] Estatísticas: cards com mensagens enviadas, respondidas, pendentes
  - [ ] Filtros: card com filtros por destinatário, tipo, data
  - [ ] Lista: cards com mensagens enviadas
  - [ ] Informações: título, destinatário, tipo, prioridade, data_envio, status
  - [ ] Ações: botões para ver detalhes, reenviar, arquivar
  - [ ] Paginação: pagination.html

- [ ] Criar mensagens_nao_lidas.html em templates/interna/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para mensagens_nao_lidas.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Mensagens Não Lidas"
  - [ ] Block content: container com row
  - [ ] Contadores: badges com total de não lidas, urgentes, requerem resposta
  - [ ] Lista: cards com mensagens não lidas ordenadas por prioridade
  - [ ] Informações: título, remetente, tipo, prioridade, tempo desde envio
  - [ ] Ações: botões para marcar como lida, responder rapidamente
  - [ ] JavaScript: atualização automática de contadores

### 3. Templates de Resposta
- [ ] Criar resposta_form.html em templates/interna/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para resposta_form.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Responder Mensagem"
  - [ ] Block content: container com row
  - [ ] Mensagem original: card com resumo da mensagem original
  - [ ] Form: card com form de resposta
  - [ ] Campos: conteudo, confidencial, urgente, observacoes
  - [ ] Botões: Enviar Resposta, Cancelar
  - [ ] JavaScript: validação em tempo real, preview de resposta

- [ ] Criar historico_comunicacao.html em templates/interna/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para historico_comunicacao.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Histórico de Comunicação"
  - [ ] Block content: container com row
  - [ ] Timeline: componente com histórico cronológico
  - [ ] Entradas: mensagem original, respostas, anexos
  - [ ] Estados: badges coloridos para cada tipo de mensagem
  - [ ] Detalhes: expandir para ver conteúdo completo
  - [ ] JavaScript: navegação na timeline, expansão de detalhes

### 4. Templates de Grupos
- [ ] Criar grupo_list.html em templates/interna/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para grupo_list.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Grupos de Comunicação"
  - [ ] Block content: container com row
  - [ ] Filtros: card com busca por nome, tipo, sector
  - [ ] Tabela: grupo_table.html com colunas (nome, tipo, sector, membros, criado_por, ações)
  - [ ] Ações: editar, gerir membros, ver mensagens, apagar
  - [ ] Paginação: pagination.html

- [ ] Criar grupo_form.html em templates/interna/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para grupo_form.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "{{ 'Criar' if not object else 'Editar' }} Grupo"
  - [ ] Block content: container com row
  - [ ] Form: card com form em duas colunas
  - [ ] Coluna 1: nome, tipo_grupo, sector, max_membros
  - [ ] Coluna 2: descricao, confidencial, observacoes
  - [ ] Gestão de membros: card separado com seleção de membros
  - [ ] Botões: Salvar, Cancelar
  - [ ] JavaScript: validação de número máximo de membros

### 5. Templates de Anexos
- [ ] Criar anexo_upload.html em templates/interna/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para anexo_upload.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Carregar Anexo"
  - [ ] Block content: container com row
  - [ ] Upload: card com drag & drop area
  - [ ] Campos: ficheiro, descricao, confidencial
  - [ ] Preview: área para preview do ficheiro
  - [ ] Progress: barra de progresso para upload
  - [ ] Botões: Carregar, Cancelar
  - [ ] JavaScript: drag & drop, preview, validação

- [ ] Criar anexo_list.html em templates/interna/
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para anexo_list.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Anexos da Mensagem"
  - [ ] Block content: container com row
  - [ ] Lista: cards com anexos
  - [ ] Informações: nome, tamanho, tipo, data_upload, descricao
  - [ ] Ações: visualizar, baixar, apagar
  - [ ] Status: badges para virus_scan, confidencial

- [ ] Criar anexo_viewer.html em templates/interna/
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

### 1. URLs de Mensagens
- [ ] Configurar URLs em interna/urls.py
  - [ ] URL 'mensagens/' → ListarMensagensInternasView.as_view(), name='lista_mensagens'
  - [ ] URL 'mensagens/criar/' → CriarMensagemInternaView.as_view(), name='criar_mensagem'
  - [ ] URL 'mensagens/<int:pk>/' → DetalheMensagemInternaView.as_view(), name='detalhe_mensagem'
  - [ ] URL 'mensagens/<int:pk>/editar/' → EditarMensagemInternaView.as_view(), name='editar_mensagem'
  - [ ] URL 'mensagens/<int:pk>/apagar/' → ApagarMensagemInternaView.as_view(), name='apagar_mensagem'
  - [ ] URL 'mensagens/<int:pk>/arquivar/' → ArquivarMensagemInternaView.as_view(), name='arquivar_mensagem'

### 2. URLs de Comunicação
- [ ] Configurar URLs de caixa de entrada/saída
  - [ ] URL 'caixa-entrada/' → CaixaEntradaView.as_view(), name='caixa_entrada'
  - [ ] URL 'caixa-saida/' → CaixaSaidaView.as_view(), name='caixa_saida'
  - [ ] URL 'nao-lidas/' → MensagensNaoLidasView.as_view(), name='mensagens_nao_lidas'
  - [ ] URL 'marcar-lida/<int:pk>/' → MarcarMensagemLidaView.as_view(), name='marcar_lida'

### 3. URLs de Resposta
- [ ] Configurar URLs de resposta
  - [ ] URL 'responder/<int:pk>/' → ResponderMensagemView.as_view(), name='responder_mensagem'
  - [ ] URL 'historico/<int:pk>/' → HistoricoComunicacaoView.as_view(), name='historico_comunicacao'
  - [ ] URL 'resposta-rapida/<int:pk>/' → RespostaRapidaView.as_view(), name='resposta_rapida'

### 4. URLs de Grupos
- [ ] Configurar URLs de gestão de grupos
  - [ ] URL 'grupos/' → ListarGruposComunicacaoView.as_view(), name='lista_grupos'
  - [ ] URL 'grupos/criar/' → CriarGrupoComunicacaoView.as_view(), name='criar_grupo'
  - [ ] URL 'grupos/<int:pk>/' → DetalheGrupoComunicacaoView.as_view(), name='detalhe_grupo'
  - [ ] URL 'grupos/<int:pk>/editar/' → EditarGrupoComunicacaoView.as_view(), name='editar_grupo'
  - [ ] URL 'grupos/<int:pk>/membros/' → GestaoMembrosGrupoView.as_view(), name='gestao_membros'

### 5. URLs de Anexos
- [ ] Configurar URLs de upload/download
  - [ ] URL 'anexos/carregar/<int:mensagem_id>/' → CarregarAnexoMensagemView.as_view(), name='carregar_anexo'
  - [ ] URL 'anexos/<int:pk>/baixar/' → BaixarAnexoMensagemView.as_view(), name='baixar_anexo'
  - [ ] URL 'anexos/<int:pk>/visualizar/' → VisualizarAnexoMensagemView.as_view(), name='visualizar_anexo'
  - [ ] URL 'anexos/<int:pk>/apagar/' → ApagarAnexoMensagemView.as_view(), name='apagar_anexo'

## 🛠️ Admin

### 1. Admin Customizado
- [ ] Configurar MensagemInternaAdmin em interna/admin.py
  - [ ] List_display: ['titulo', 'remetente', 'destinatario', 'tipo_mensagem', 'prioridade', 'data_envio', 'lida']
  - [ ] List_filter: ['tipo_mensagem', 'prioridade', 'urgente', 'confidencial', 'lida', 'arquivada', 'data_envio']
  - [ ] Search_fields: ['titulo', 'conteudo', 'remetente__first_name', 'destinatario__first_name']
  - [ ] Readonly_fields: ['data_envio', 'data_leitura', 'data_atualizacao']
  - [ ] Fieldsets: (('Informações Básicas', {'fields': ('titulo', 'tipo_mensagem', 'remetente', 'destinatario')}), ('Conteúdo', {'fields': ('conteudo', 'observacoes')}), ('Configurações', {'fields': ('prioridade', 'urgente', 'confidencial', 'requer_resposta')}), ('Status', {'fields': ('lida', 'arquivada', 'ativo')}), ('Metadados', {'fields': ('data_envio', 'data_leitura', 'data_atualizacao')}))
  - [ ] Actions: ['marcar_como_lidas', 'arquivar_mensagens', 'ativar_mensagens']

- [ ] Configurar TipoMensagemAdmin em interna/admin.py
  - [ ] List_display: ['nome', 'descricao', 'cor', 'icone', 'prioridade_padrao', 'ativo']
  - [ ] List_filter: ['ativo', 'prioridade_padrao', 'requer_resposta_padrao', 'confidencial_padrao']
  - [ ] Search_fields: ['nome', 'descricao']
  - [ ] Fieldsets: (('Informações', {'fields': ('nome', 'descricao', 'cor', 'icone')}), ('Configurações Padrão', {'fields': ('prioridade_padrao', 'requer_resposta_padrao', 'confidencial_padrao')}), ('Template', {'fields': ('template_conteudo',)}), ('Status', {'fields': ('ativo',)}))

- [ ] Configurar RespostaMensagemAdmin em interna/admin.py
  - [ ] List_display: ['mensagem_original', 'remetente', 'data_resposta', 'lida', 'urgente']
  - [ ] List_filter: ['lida', 'urgente', 'confidencial', 'data_resposta']
  - [ ] Search_fields: ['conteudo', 'mensagem_original__titulo', 'remetente__first_name']
  - [ ] Readonly_fields: ['data_resposta', 'data_leitura', 'data_atualizacao']

- [ ] Configurar GrupoComunicacaoAdmin em interna/admin.py
  - [ ] List_display: ['nome', 'tipo_grupo', 'sector', 'obter_membros_count', 'criado_por', 'ativo']
  - [ ] List_filter: ['tipo_grupo', 'sector', 'confidencial', 'ativo', 'data_criacao']
  - [ ] Search_fields: ['nome', 'descricao', 'criado_por__first_name']
  - [ ] Filter_horizontal: ['membros']
  - [ ] Actions: ['ativar_grupos', 'desativar_grupos']

- [ ] Configurar AnexoMensagemAdmin em interna/admin.py
  - [ ] List_display: ['nome_original', 'mensagem', 'tamanho', 'tipo_mime', 'virus_scan', 'data_upload']
  - [ ] List_filter: ['virus_scan', 'confidencial', 'data_upload']
  - [ ] Search_fields: ['nome_original', 'descricao', 'mensagem__titulo']
  - [ ] Readonly_fields: ['hash_arquivo', 'data_upload', 'data_scan']
  - [ ] Actions: ['scan_virus_anexos', 'verificar_integridade_anexos']

## 🔄 Signals

### 1. Signals de Mensagem
- [ ] Criar signals em interna/signals.py
  - [ ] Signal post_save para MensagemInterna: notificar destinatário
  - [ ] Signal post_save para RespostaMensagem: notificar remetente original
  - [ ] Signal pre_save para MensagemInterna: definir sector_origem automaticamente
  - [ ] Signal post_delete para MensagemInterna: limpar anexos relacionados
  - [ ] Signal post_save para AnexoMensagem: gerar hash e scan de vírus
  - [ ] Método notificar_nova_mensagem(): enviar notificação para destinatário
  - [ ] Método notificar_nova_resposta(): enviar notificação para remetente original
  - [ ] Método definir_sector_origem(): definir sector baseado no remetente
  - [ ] Método processar_anexo_novo(): hash e scan de vírus

### 2. Signals de Notificação
- [ ] Criar signals de notificação
  - [ ] Signal para notificar mensagem urgente
  - [ ] Signal para notificar mensagem requer resposta
  - [ ] Signal para notificar mensagem confidencial
  - [ ] Signal para notificar grupo de comunicação
  - [ ] Método notificar_mensagem_urgente(): notificar imediatamente
  - [ ] Método notificar_requer_resposta(): notificar com prazo
  - [ ] Método notificar_grupo(): notificar todos os membros

## 📦 Fixtures

### 1. Dados Iniciais
- [ ] Criar fixtures/interna/tipos_mensagem.json
  - [ ] Informativa: cor='#007bff', icone='fas fa-info-circle', prioridade_padrao='normal'
  - [ ] Urgente: cor='#dc3545', icone='fas fa-exclamation-triangle', prioridade_padrao='urgente'
  - [ ] Reunião: cor='#28a745', icone='fas fa-calendar-alt', prioridade_padrao='alta'
  - [ ] Tarefa: cor='#ffc107', icone='fas fa-tasks', prioridade_padrao='normal', requer_resposta_padrao=True
  - [ ] Aviso: cor='#6f42c1', icone='fas fa-bullhorn', prioridade_padrao='alta'
  - [ ] Pergunta: cor='#17a2b8', icone='fas fa-question-circle', prioridade_padrao='normal', requer_resposta_padrao=True

- [ ] Criar fixtures/interna/grupos_iniciais.json
  - [ ] Grupo Geral: tipo_grupo='geral', max_membros=100
  - [ ] Comissão Diretiva: tipo_grupo='comissao', max_membros=10
  - [ ] Equipe de Projeto: tipo_grupo='projeto', max_membros=20

### 2. Management Commands
- [ ] Criar management/commands/criar_tipos_mensagem.py
  - [ ] Comando para criar/atualizar tipos de mensagem
  - [ ] Validação de dados existentes
  - [ ] Criação de novos tipos se necessário

- [ ] Criar management/commands/criar_grupos_iniciais.py
  - [ ] Comando para criar grupos iniciais
  - [ ] Adicionar membros automaticamente
  - [ ] Configurar permissões

## 🧪 Testes

### 1. Testes de Modelos
- [ ] Criar testes em interna/tests.py
  - [ ] TestCase MensagemInternaModelTest
    - [ ] Teste criar_mensagem(): criar mensagem válida
    - [ ] Teste marcar_como_lida(): verificar marcação de lida
    - [ ] Teste arquivar_mensagem(): verificar arquivamento
    - [ ] Teste pode_responder(): verificar permissões de resposta
    - [ ] Teste eh_urgente(): verificar urgência
    - [ ] Teste obter_destinatarios(): verificar destinatários
    - [ ] Teste obter_respostas(): verificar respostas
    - [ ] Teste obter_anexos(): verificar anexos

  - [ ] TestCase TipoMensagemModelTest
    - [ ] Teste criar_tipo(): criar tipo válido
    - [ ] Teste obter_cor(): verificar cor
    - [ ] Teste obter_icone(): verificar ícone
    - [ ] Teste aplicar_template(): verificar aplicação de template

  - [ ] TestCase RespostaMensagemModelTest
    - [ ] Teste criar_resposta(): criar resposta válida
    - [ ] Teste marcar_como_lida(): verificar marcação de lida
    - [ ] Teste obter_tempo_resposta(): verificar cálculo de tempo
    - [ ] Teste pode_visualizar(): verificar permissões

  - [ ] TestCase GrupoComunicacaoModelTest
    - [ ] Teste criar_grupo(): criar grupo válido
    - [ ] Teste add_membro(): adicionar membro
    - [ ] Teste remove_membro(): remover membro
    - [ ] Teste eh_membro(): verificar membro
    - [ ] Teste obter_membros_count(): verificar contagem
    - [ ] Teste obter_estatisticas(): verificar estatísticas

  - [ ] TestCase AnexoMensagemModelTest
    - [ ] Teste criar_anexo(): criar anexo válido
    - [ ] Teste obter_tamanho_formatado(): verificar formatação
    - [ ] Teste eh_imagem(): verificar tipo de ficheiro
    - [ ] Teste eh_pdf(): verificar tipo de ficheiro
    - [ ] Teste gerar_hash(): verificar hash SHA-256
    - [ ] Teste verificar_integridade(): verificar integridade

### 2. Testes de Views
- [ ] TestCase MensagemInternaViewTest
  - [ ] Teste listar_mensagens(): verificar listagem
  - [ ] Teste criar_mensagem(): verificar criação
  - [ ] Teste editar_mensagem(): verificar edição
  - [ ] Teste detalhe_mensagem(): verificar detalhes
  - [ ] Teste permissoes_visualizacao(): verificar permissões
  - [ ] Teste filtros_mensagens(): verificar filtros

- [ ] TestCase ComunicacaoViewTest
  - [ ] Teste caixa_entrada(): verificar caixa de entrada
  - [ ] Teste caixa_saida(): verificar caixa de saída
  - [ ] Teste mensagens_nao_lidas(): verificar não lidas
  - [ ] Teste marcar_lida(): verificar marcação de lida

- [ ] TestCase RespostaViewTest
  - [ ] Teste responder_mensagem(): verificar resposta
  - [ ] Teste resposta_rapida(): verificar resposta rápida
  - [ ] Teste historico_comunicacao(): verificar histórico
  - [ ] Teste permissoes_resposta(): verificar permissões

- [ ] TestCase GrupoViewTest
  - [ ] Teste listar_grupos(): verificar listagem
  - [ ] Teste criar_grupo(): verificar criação
  - [ ] Teste editar_grupo(): verificar edição
  - [ ] Teste gestao_membros(): verificar gestão de membros

- [ ] TestCase AnexoMensagemViewTest
  - [ ] Teste carregar_anexo(): verificar upload
  - [ ] Teste baixar_anexo(): verificar download
  - [ ] Teste visualizar_anexo(): verificar visualização
  - [ ] Teste apagar_anexo(): verificar apagar
  - [ ] Teste permissoes_anexo(): verificar permissões

### 3. Testes de Forms
- [ ] TestCase MensagemInternaFormTest
  - [ ] Teste form_valido(): verificar validação
  - [ ] Teste clean_destinatario(): verificar validação de destinatário
  - [ ] Teste clean_conteudo(): verificar validação de conteúdo
  - [ ] Teste campos_obrigatorios(): verificar campos obrigatórios

- [ ] TestCase RespostaMensagemFormTest
  - [ ] Teste form_valido(): verificar validação
  - [ ] Teste clean_conteudo(): verificar validação de conteúdo
  - [ ] Teste campos_obrigatorios(): verificar campos obrigatórios

- [ ] TestCase GrupoComunicacaoFormTest
  - [ ] Teste form_valido(): verificar validação
  - [ ] Teste clean_nome(): verificar nome único
  - [ ] Teste clean_max_membros(): verificar limite máximo
  - [ ] Teste campos_obrigatorios(): verificar campos obrigatórios

### 4. Testes de Signals
- [ ] TestCase MensagemInternaSignalsTest
  - [ ] Teste signal_criacao(): verificar notificação de criação
  - [ ] Teste signal_resposta(): verificar notificação de resposta
  - [ ] Teste signal_sector_origem(): verificar definição de sector
  - [ ] Teste signal_anexo_novo(): verificar processamento de anexo

### 5. Testes de Integração
- [ ] TestCase FluxoComunicacaoTest
  - [ ] Teste fluxo_completo(): enviar → receber → responder → arquivar
  - [ ] Teste fluxo_grupo(): criar grupo → enviar mensagem → responder
  - [ ] Teste fluxo_anexos(): enviar mensagem → anexar ficheiro → baixar
  - [ ] Teste notificacoes_fluxo(): verificar notificações em cada etapa

## 📋 Validação Final
- [ ] Mensagens enviadas corretamente
- [ ] Fluxo de comunicação funcionando
- [ ] Estados atualizados corretamente
- [ ] Anexos uploadados e acessíveis
- [ ] Grupos geridos corretamente
- [ ] Notificações enviadas
- [ ] Relatórios gerados
- [ ] Testes passando
- [ ] Templates renderizando corretamente
- [ ] URLs funcionando
- [ ] Admin configurado
- [ ] Signals funcionando
- [ ] Fixtures carregadas
- [ ] Hierarquia de comunicação respeitada
- [ ] Respostas funcionando
- [ ] Grupos de comunicação funcionando

---

**Nota:** Esta app gere toda a comunicação interna entre sectores e utilizadores.
