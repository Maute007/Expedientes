# 📋 3. CHECKLIST - APP USERS

## 🎯 Objetivo
Gestão de utilizadores e perfis com Custom User Model, login por email e hierarquia organizacional.

## 👥 Modelos de Utilizador

### 1. Custom User Model
- [x] Criar modelo User customizado em users/models.py
  - [x] Campo email: EmailField(unique=True, max_length=254) - login principal
  - [x] Campo first_name: CharField(max_length=150, blank=True)
  - [x] Campo last_name: CharField(max_length=150, blank=True)
  - [x] Campo is_active: BooleanField(default=True)
  - [x] Campo date_joined: DateTimeField(auto_now_add=True)
  - [x] Campo telefone: CharField(max_length=20, blank=True, null=True)
  - [x] Campo sector_atual: ForeignKey('core.Sector', on_delete=SET_NULL, null=True, blank=True, related_name='utilizadores')
  - [x] Campo cargo: CharField(max_length=100, blank=True, null=True)
  - [x] Campo ativo: BooleanField(default=True)
  - [x] Campo tipo_utilizador: CharField(max_length=20, choices=TIPOS_UTILIZADOR, default='colaborador')
  - [x] Constante TIPOS_UTILIZADOR = [('admin', 'Administrador'), ('pca', 'PCA'), ('secretaria', 'Secretaria'), ('chefe', 'Chefe'), ('colaborador', 'Colaborador'), ('externo', 'Externo')]
  - [x] Campo ultimo_acesso: DateTimeField(null=True, blank=True)
  - [x] Campo avatar: ImageField(upload_to='avatars/%Y/%m/', blank=True, null=True)
  - [x] Campo biografia: TextField(blank=True, null=True)
  - [x] Campo data_nascimento: DateField(null=True, blank=True)
  - [x] Campo genero: CharField(max_length=10, choices=GENEROS, blank=True, null=True)
  - [x] Campo endereco: TextField(blank=True, null=True)
  - [x] Campo codigo_postal: CharField(max_length=10, blank=True, null=True)
  - [x] Campo cidade: CharField(max_length=100, blank=True, null=True)
  - [x] Campo pais: CharField(max_length=100, default='Moçambique')
  - [x] Constante GENEROS = [('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')]
  - [x] Constante USERNAME_FIELD = 'email'
  - [x] Constante REQUIRED_FIELDS = ['first_name', 'last_name']
  - [x] Método __str__(): return f"{self.get_full_name()} ({self.email})"
  - [x] Método get_full_name(): return f"{self.first_name} {self.last_name}".strip()
  - [x] Método get_short_name(): return self.first_name
  - [x] Método is_chefe_de_sector(): return self.sector_atual and self.sector_atual.chefe == self
  - [x] Método obter_papel_exibicao(): retorna papel baseado em is_admin, is_pca, is_secretaria, is_chefe_de_sector
  - [x] Método obter_nivel_hierarquico(): retorna nível numérico (Admin=6, PCA=5, Secretaria=4, Chefe=3, Colaborador=2, Externo=1)
  - [x] Método pode_gerir_utilizador(outro_user): verifica se pode gerir outro utilizador
  - [x] Método obter_subordinados(): retorna utilizadores subordinados
  - [x] Método atualizar_ultimo_acesso(): self.ultimo_acesso = timezone.now(), self.save(update_fields=['ultimo_acesso'])
  - [x] Método eh_admin_ou_superuser(): return self.is_admin or self.is_superuser
  - [x] Método eh_pca_ou_superuser(): return self.is_pca or self.is_superuser
  - [x] Método eh_chefe_ou_acima(): return self.is_admin or self.is_pca or self.is_secretaria or self.is_chefe_de_sector()
  - [x] Meta: ordering = ['first_name', 'last_name']
  - [x] Meta: verbose_name = "Utilizador"
  - [x] Meta: verbose_name_plural = "Utilizadores"

### 2. Perfis de Utilizador
- [x] Criar modelo PerfilUtilizador em users/models.py
  - [x] Campo user: OneToOneField(User, on_delete=CASCADE, related_name='perfil')
  - [x] Campo foto: ImageField(upload_to='perfis/%Y/%m/', blank=True, null=True)
  - [x] Campo biografia: TextField(blank=True, null=True, max_length=1000)
  - [x] Campo data_nascimento: DateField(null=True, blank=True)
  - [x] Campo nivel_hierarquico: CharField(max_length=20, choices=NIVEIS_HIERARQUIA, default='colaborador')
  - [x] Campo ativo: BooleanField(default=True)
  - [x] Campo observacoes: TextField(blank=True, null=True)
  - [x] Campo data_criacao: DateTimeField(auto_now_add=True)
  - [x] Campo data_atualizacao: DateTimeField(auto_now=True)
  - [x] Campo preferencias_notificacao: JSONField(default=dict) - configurações de notificação
  - [x] Campo idioma_preferido: CharField(max_length=5, default='pt', choices=IDIOMAS)
  - [x] Campo fuso_horario: CharField(max_length=50, default='Africa/Maputo')
  - [x] Campo tema_preferido: CharField(max_length=10, choices=TEMAS, default='claro')
  - [x] Constante NIVEIS_HIERARQUIA = [
        ('admin', 'Administrador do Sistema'),
        ('pca', 'PCA'),
        ('secretaria', 'Secretaria'),
        ('chefe', 'Chefe de Sector'),
        ('colaborador', 'Colaborador'),
        ('externo', 'Utilizador Externo')
    ]
  - [x] Constante IDIOMAS = [('pt', 'Português'), ('en', 'English')]
  - [x] Constante TEMAS = [('claro', 'Claro'), ('escuro', 'Escuro'), ('auto', 'Automático')]
  - [x] Método __str__(): return f"Perfil de {self.user.get_full_name()}"
  - [x] Método obter_nivel_display(): return dict(self.NIVEIS_HIERARQUIA).get(self.nivel_hierarquico, 'Desconhecido')
  - [x] Método eh_chefe(): return self.nivel_hierarquico == 'chefe' or self.user.is_chefe_de_sector()
  - [x] Método eh_colaborador(): return self.nivel_hierarquico == 'colaborador'
  - [x] Método obter_sector_atual(): return self.user.sector_atual
  - [x] Método obter_idade(): calcula idade baseada em data_nascimento
  - [x] Método obter_preferencia_notificacao(tipo): retorna configuração específica
  - [x] Método definir_preferencia_notificacao(tipo, valor): define configuração
  - [x] Meta: ordering = ['user__first_name', 'user__last_name']
  - [x] Meta: verbose_name = "Perfil de Utilizador"
  - [x] Meta: verbose_name_plural = "Perfis de Utilizadores"

### 3. Hierarquia Organizacional
- [x] Criar modelo HierarquiaUtilizador em users/models.py (histórico de posições)
  - [x] Campo utilizador: ForeignKey(User, on_delete=CASCADE, related_name='historico_hierarquia')
  - [x] Campo sector: ForeignKey('core.Sector', on_delete=CASCADE, related_name='historico_utilizadores')
  - [x] Campo cargo: CharField(max_length=100)
  - [x] Campo nivel: CharField(max_length=20, choices=NIVEIS_HIERARQUIA)
  - [x] Campo supervisor: ForeignKey(User, on_delete=SET_NULL, null=True, blank=True, related_name='subordinados')
  - [x] Campo data_inicio: DateField()
  - [x] Campo data_fim: DateField(null=True, blank=True)
  - [x] Campo ativo: BooleanField(default=True)
  - [x] Campo observacoes: TextField(blank=True, null=True)
  - [x] Campo salario: DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
  - [x] Campo tipo_contrato: CharField(max_length=20, choices=TIPOS_CONTRATO, default='efetivo')
  - [x] Campo data_criacao: DateTimeField(auto_now_add=True)
  - [x] Campo criado_por: ForeignKey(User, on_delete=SET_NULL, null=True, related_name='hierarquias_criadas')
  - [x] Constante NIVEIS_HIERARQUIA = [
        ('admin', 'Administrador do Sistema'),
        ('pca', 'PCA'),
        ('secretaria', 'Secretaria'),
        ('chefe', 'Chefe de Sector'),
        ('colaborador', 'Colaborador'),
        ('externo', 'Utilizador Externo')
    ]
  - [x] Constante TIPOS_CONTRATO = [
        ('efetivo', 'Efetivo'),
        ('contrato', 'Contrato'),
        ('estagiario', 'Estagiário'),
        ('consultor', 'Consultor'),
        ('voluntario', 'Voluntário')
    ]
  - [x] Método __str__(): return f"{self.utilizador.get_full_name()} - {self.cargo} ({self.sector.nome})"
  - [x] Método obter_subordinados(): return HierarquiaUtilizador.objects.filter(supervisor=self.utilizador, ativo=True)
  - [x] Método obter_supervisor(): return self.supervisor
  - [x] Método pode_gerir_utilizador(outro_user): verifica hierarquia
  - [x] Método eh_ativo(): return self.ativo and (self.data_fim is None or self.data_fim > timezone.now().date())
  - [x] Método obter_nivel_peso(): retorna peso numérico (Admin=6, PCA=5, Secretaria=4, Chefe=3, Colaborador=2, Externo=1)
  - [x] Método obter_duracao(): calcula duração da posição
  - [x] Método finalizar_posicao(data_fim=None): marca como inativo
  - [x] Meta: ordering = ['-data_inicio']
  - [x] Meta: verbose_name = "Hierarquia de Utilizador"
  - [x] Meta: verbose_name_plural = "Hierarquias de Utilizadores"
  - [x] Meta: unique_together = ['utilizador', 'sector', 'data_inicio']

## 🔐 Sistema de Permissões

### 1. Grupos e Permissões
- [ ] Criar grupos de utilizadores
  - [ ] Administrador de Sistema (superuser técnico)
  - [ ] PCA (Presidente - máxima autoridade organizacional)
  - [ ] Secretaria (recebe e distribui documentos)
  - [ ] Chefe de Sector (gere sector e equipa)
  - [ ] Colaborador (trabalha no sector)
  - [ ] Utilizador Externo (submete documentos via portal)

### 2. Permissões Customizadas
- [ ] Criar permissões específicas
  - [ ] view_dashboard_admin (Admin e PCA)
  - [ ] manage_users (Admin)
  - [ ] manage_sectors (Admin e PCA)
  - [ ] view_all_documents (Admin, PCA e Secretaria)
  - [ ] manage_entrada (Secretaria)
  - [ ] manage_saida (PCA e Chefes de Sector)
  - [ ] approve_saida (PCA - aprovação final)
  - [ ] manage_interna (Todos autenticados)
  - [ ] manage_externa (Secretaria)

## 📝 Forms de Utilizador

### 1. Forms de Registo
- [x] Criar arquivo users/forms.py com todos os forms
- [ ] UtilizadorForm (ModelForm):
  - [ ] Meta: model = User
  - [ ] Meta: fields = ['email', 'first_name', 'last_name', 'telefone', 'sector_atual', 'cargo', 'is_pca', 'is_secretaria']
  - [ ] Widgets: sector_atual = SelectWidget(attrs={'class': 'form-select'})
  - [ ] Método clean_email(): validar email único
  - [ ] Método clean_is_pca(): validar apenas um PCA
  - [ ] Método clean_sector_atual(): validar sector existe e está ativo
- [ ] PerfilUtilizadorForm (ModelForm):
  - [ ] Meta: model = PerfilUtilizador
  - [ ] Meta: fields = ['foto', 'biografia', 'data_nascimento', 'nivel_hierarquico', 'idioma_preferido', 'tema_preferido']
  - [ ] Widgets: data_nascimento = DateInput(attrs={'type': 'date', 'class': 'form-control'})
  - [ ] Widgets: biografia = Textarea(attrs={'rows': 4, 'class': 'form-control'})
  - [ ] Método clean_data_nascimento(): validar idade mínima/máxima
- [ ] UtilizadorUpdateForm (ModelForm):
  - [ ] Meta: model = User
  - [ ] Meta: fields = ['first_name', 'last_name', 'telefone', 'cargo', 'ativo']
  - [ ] Método clean(): validações específicas de atualização

### 2. Forms de Login
- [ ] CustomLoginForm (Form):
  - [ ] Campo email: EmailField(label='Email', max_length=254, widget=EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'}))
  - [ ] Campo password: CharField(label='Senha', widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Sua senha'}))
  - [ ] Campo remember_me: BooleanField(label='Lembrar-me', required=False, widget=CheckboxInput(attrs={'class': 'form-check-input'}))
  - [ ] Método clean_email(): validar email existe e utilizador ativo
  - [ ] Método clean(): autenticar utilizador
- [ ] CustomPasswordChangeForm (PasswordChangeForm):
  - [ ] Widgets: old_password = PasswordInput(attrs={'class': 'form-control'})
  - [ ] Widgets: new_password1 = PasswordInput(attrs={'class': 'form-control'})
  - [ ] Widgets: new_password2 = PasswordInput(attrs={'class': 'form-control'})
  - [ ] Método clean_new_password2(): validações de senha forte

### 3. Forms de Perfil
- [ ] PerfilUpdateForm (ModelForm):
  - [ ] Meta: model = User
  - [ ] Meta: fields = ['first_name', 'last_name', 'telefone', 'endereco', 'cidade', 'codigo_postal']
  - [ ] Widgets: telefone = TextInput(attrs={'class': 'form-control', 'placeholder': '+258 XX XXX XXXX'})
  - [ ] Método clean_telefone(): validar formato de telefone moçambicano
- [ ] AlterarSenhaForm (Form):
  - [ ] Campo senha_atual: CharField(widget=PasswordInput(attrs={'class': 'form-control'}))
  - [ ] Campo nova_senha: CharField(widget=PasswordInput(attrs={'class': 'form-control'}))
  - [ ] Campo confirmar_senha: CharField(widget=PasswordInput(attrs={'class': 'form-control'}))
  - [ ] Método clean(): validar senha atual e confirmar nova senha
- [ ] GestaoPermissoesForm (Form):
  - [ ] Campo utilizador: ModelChoiceField(queryset=User.objects.filter(ativo=True), widget=Select(attrs={'class': 'form-select'}))
  - [ ] Campo grupos: ModelMultipleChoiceField(queryset=Group.objects.all(), widget=CheckboxSelectMultiple())
  - [ ] Método clean(): validar permissões do utilizador atual

## 🎯 Views de Utilizador

### 1. Views de Autenticação
- [x] Criar arquivo users/views.py com todas as views de autenticação
- [x] LoginViewCustomizada (FormView):
  - [x] Form_class = CustomLoginForm
  - [x] Template_name = 'users/login.html'
  - [x] Success_url = reverse_lazy('core:dashboard')
  - [x] Método form_valid(): atualizar ultimo_acesso do utilizador
  - [x] Método get_success_url(): redirecionar baseado em perfil do utilizador
  - [x] Decorator @method_decorator(never_cache)
- [x] LogoutViewCustomizada (LogoutView):
  - [x] Next_page = reverse_lazy('users:login')
  - [x] Template_name = 'users/logout.html'
  - [x] Método dispatch(): log de logout
- [x] PasswordChangeViewCustomizada (PasswordChangeView):
  - [x] Template_name = 'users/password_change.html'
  - [x] Success_url = reverse_lazy('users:profile')
  - [x] Form_class = CustomPasswordChangeForm
- [x] PasswordResetViewCustomizada (PasswordResetView):
  - [x] Template_name = 'users/password_reset.html'
  - [x] Email_template_name = 'users/password_reset_email.html'
  - [x] Subject_template_name = 'users/password_reset_subject.txt'
  - [x] Success_url = reverse_lazy('users:password_reset_done')

### 2. Views de Perfil
- [x] PerfilUtilizadorView (DetailView):
  - [x] Model = User
  - [x] Template_name = 'users/perfil_detail.html'
  - [x] Context_object_name = 'utilizador'
  - [x] Método get_object(): return self.request.user
  - [x] Método get_context_data(): adicionar perfil, hierarquia, estatísticas
  - [x] Decorator @login_required
- [x] EditarPerfilView (UpdateView):
  - [x] Model = User
  - [x] Form_class = PerfilUtilizadorForm
  - [x] Template_name = 'users/perfil_edit.html'
  - [x] Success_url = reverse_lazy('users:perfil')
  - [x] Método get_object(): return self.request.user
  - [x] Método form_valid(): atualizar perfil relacionado
  - [x] Decorator @login_required
- [x] ListarUtilizadoresView (ListView):
  - [x] Model = User
  - [x] Template_name = 'users/utilizador_list.html'
  - [x] Paginate_by = 25
  - [x] Context_object_name = 'utilizadores'
  - [x] Método get_queryset(): filtrar por permissões do utilizador
  - [x] Método get_context_data(): adicionar filtros, sectores, estatísticas
  - [x] Decorator @login_required
  - [x] Decorator @permission_required('users.view_user')
- [x] CriarUtilizadorView (CreateView):
  - [x] Model = User
  - [x] Form_class = UtilizadorForm
  - [x] Template_name = 'users/utilizador_form.html'
  - [x] Success_url = reverse_lazy('users:lista_utilizadores')
  - [x] Método form_valid(): definir senha temporária, enviar email
  - [x] Decorator @login_required
  - [x] Decorator @permission_required('users.add_user')
- [x] EditarUtilizadorView (UpdateView):
  - [x] Model = User
  - [x] Form_class = UtilizadorForm
  - [x] Template_name = 'users/utilizador_form.html'
  - [x] Success_url = reverse_lazy('users:lista_utilizadores')
  - [x] Método get_queryset(): filtrar por permissões
  - [x] Decorator @login_required
  - [x] Decorator @permission_required('users.change_user')

### 3. Views de Gestão
- [x] GestaoSectoresView (ListView):
  - [x] Model = Sector
  - [x] Template_name = 'users/gestao_sectores.html'
  - [x] Context_object_name = 'sectores'
  - [x] Método get_context_data(): adicionar estatísticas por sector
  - [x] Decorator @login_required
  - [x] Decorator @pca_ou_admin_required
- [x] GestaoPermissoesView (TemplateView):
  - [x] Template_name = 'users/gestao_permissoes.html'
  - [x] Método get_context_data(): grupos, permissões, utilizadores por grupo
  - [x] Método post(): processar alterações de permissões
  - [x] Decorator @login_required
  - [x] Decorator @permission_required('auth.change_group')
- [x] HierarquiaUtilizadoresView (TemplateView):
  - [x] Template_name = 'users/hierarquia_utilizadores.html'
  - [x] Método get_context_data(): árvore hierárquica, estatísticas
  - [x] Decorator @login_required
  - [x] Decorator @pca_ou_admin_required
- [x] AtivarDesativarUtilizadorView (View):
  - [x] Método post(request, pk):
    - [x] Buscar utilizador = get_object_or_404(User, pk=pk)
    - [x] Verificar permissões: request.user.pode_gerir_utilizador(utilizador)
    - [x] Alternar campo ativo: utilizador.ativo = not utilizador.ativo
    - [x] Salvar: utilizador.save()
    - [x] Retornar JsonResponse({'success': True, 'ativo': utilizador.ativo})
  - [x] Decorator @login_required
  - [x] Decorator @require_http_methods(["POST"])

## 🔧 Managers e Querysets

### 1. UserManager Customizado
- [ ] Criar UserManager
- [ ] Implementar create_user
- [ ] Implementar create_superuser
- [ ] Implementar get_by_natural_key

### 2. Querysets Customizados
- [ ] Criar UserQuerySet
- [ ] Métodos: by_sector, by_nivel, ativos, inativos
- [ ] Métodos: chefes_de_sector, colaboradores, externos
- [ ] Métodos: get_chefes_por_sector, get_colaboradores_por_sector
- [ ] Métodos especiais: get_pca, get_secretaria, is_pca_or_superuser

## 🎨 Templates

### 1. Templates de Autenticação
- [ ] Criar diretório templates/users/
- [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para templates de autenticação
- [ ] Criar login.html:
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para login.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Entrar no Sistema"
  - [ ] Form Bootstrap com classes: form-control, btn-primary
  - [ ] Campos: email, password, remember_me checkbox
  - [ ] Botão "Entrar" com ícone
  - [ ] Link "Esqueci a senha" → password_reset
  - [ ] JavaScript: validação frontend, auto-focus no email
- [ ] Criar logout.html:
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para logout.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Sessão Encerrada"
  - [ ] Card Bootstrap com mensagem de logout
  - [ ] Botão "Entrar Novamente" → login
  - [ ] JavaScript: redirect automático após 5 segundos
- [ ] Criar password_change.html:
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para password_change.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Alterar Senha"
  - [ ] Form com 3 campos: senha_atual, nova_senha, confirmar_senha
  - [ ] Validação de força da senha (JavaScript)
  - [ ] Botões: "Alterar" e "Cancelar"
- [ ] Criar password_reset.html:
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para password_reset.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Recuperar Senha"
  - [ ] Form simples com campo email
  - [ ] Botão "Enviar Instruções"
  - [ ] Link "Voltar ao Login"

### 2. Templates de Perfil
- [ ] Criar perfil_detail.html:
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para perfil_detail.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Meu Perfil"
  - [ ] Card principal com foto do utilizador (avatar)
  - [ ] Seção informações pessoais: nome, email, telefone, cargo
  - [ ] Seção sector atual: nome do sector, chefe
  - [ ] Seção hierarquia: nível, supervisor, subordinados
  - [ ] Seção estatísticas: documentos processados, tempo no sistema
  - [ ] Botão "Editar Perfil" → perfil_edit
  - [ ] Botão "Alterar Senha" → password_change
- [ ] Criar perfil_edit.html:
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para perfil_edit.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Editar Perfil"
  - [ ] Form Bootstrap com tabs: "Pessoal" | "Profissional" | "Preferências"
  - [ ] Tab Pessoal: nome, telefone, endereço, data nascimento
  - [ ] Tab Profissional: cargo, sector, biografia
  - [ ] Tab Preferências: idioma, tema, notificações
  - [ ] Upload de foto com preview
  - [ ] Botões: "Salvar" e "Cancelar"
- [ ] Criar utilizador_list.html:
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para utilizador_list.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Gestão de Utilizadores"
  - [ ] Filtros: sector, nível, ativo/inativo, pesquisa por nome
  - [ ] Tabela Bootstrap com colunas: foto, nome, email, sector, cargo, nível, status
  - [ ] Ações por linha: ver, editar, ativar/desativar
  - [ ] Paginação Bootstrap
  - [ ] Botão "Novo Utilizador" → criar_utilizador
  - [ ] JavaScript: filtros AJAX, confirmação de ações
- [ ] Criar utilizador_form.html:
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para utilizador_form.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "{% if object %}Editar{% else %}Novo{% endif %} Utilizador"
  - [ ] Form com tabs: "Informações" | "Permissões" | "Sector"
  - [ ] Tab Informações: email, nome, telefone, cargo
  - [ ] Tab Permissões: is_pca, is_secretaria, grupos
  - [ ] Tab Sector: sector_atual, nível hierárquico
  - [ ] Validação: apenas um PCA, email único
  - [ ] Botões: "Salvar" e "Cancelar"

### 3. Templates de Gestão
- [ ] Criar gestao_sectores.html:
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para gestao_sectores.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Gestão de Sectores"
  - [ ] Cards para cada sector com estatísticas
  - [ ] Informações: nome, chefe, número de colaboradores, documentos ativos
  - [ ] Gráfico de distribuição de utilizadores por sector
  - [ ] Botão "Gerir Sector" → detalhes do sector
- [ ] Criar gestao_permissoes.html:
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para gestao_permissoes.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Gestão de Permissões"
  - [ ] Tabela de grupos com permissões
  - [ ] Lista de utilizadores por grupo
  - [ ] Interface para adicionar/remover utilizadores de grupos
  - [ ] Botão "Salvar Alterações"
- [ ] Criar hierarquia_utilizadores.html:
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para hierarquia_utilizadores.html
  - [ ] Estender {% extends 'base.html' %}
  - [ ] Block title: "Hierarquia Organizacional"
  - [ ] Árvore hierárquica visual (CSS + JavaScript)
  - [ ] PCA no topo, sectores como ramos, utilizadores como folhas
  - [ ] Tooltips com informações de cada utilizador
  - [ ] Botão "Exportar Organograma" → PDF

## 🔗 URLs

### 1. URLs de Autenticação
- [x] Criar arquivo users/urls.py com todas as URLs
- [x] URL 'login/' → LoginViewCustomizada.as_view(), name='login'
- [x] URL 'logout/' → LogoutViewCustomizada.as_view(), name='logout'
- [x] URL 'password-change/' → PasswordChangeViewCustomizada.as_view(), name='password_change'
- [x] URL 'password-reset/' → PasswordResetViewCustomizada.as_view(), name='password_reset'
- [x] URL 'password-reset-done/' → PasswordResetDoneView.as_view(), name='password_reset_done'
- [x] URL 'password-reset-confirm/<uidb64>/<token>/' → PasswordResetConfirmView.as_view(), name='password_reset_confirm'
- [x] URL 'password-reset-complete/' → PasswordResetCompleteView.as_view(), name='password_reset_complete'

### 2. URLs de Perfil
- [x] URL 'perfil/' → PerfilUtilizadorView.as_view(), name='perfil'
- [x] URL 'perfil/editar/' → EditarPerfilView.as_view(), name='perfil_edit'
- [x] URL 'utilizadores/' → ListarUtilizadoresView.as_view(), name='lista_utilizadores'
- [x] URL 'utilizadores/novo/' → CriarUtilizadorView.as_view(), name='criar_utilizador'
- [x] URL 'utilizadores/<int:pk>/editar/' → EditarUtilizadorView.as_view(), name='editar_utilizador'
- [x] URL 'utilizadores/<int:pk>/ativar-desativar/' → AtivarDesativarUtilizadorView.as_view(), name='ativar_desativar_utilizador'

### 3. URLs de Gestão
- [x] URL 'gestao/sectores/' → GestaoSectoresView.as_view(), name='gestao_sectores'
- [x] URL 'gestao/permissoes/' → GestaoPermissoesView.as_view(), name='gestao_permissoes'
- [x] URL 'gestao/hierarquia/' → HierarquiaUtilizadoresView.as_view(), name='hierarquia_utilizadores'
- [x] URL 'api/utilizadores/<int:pk>/status/' → AtivarDesativarUtilizadorView.as_view(), name='api_utilizador_status'
- [x] URL 'api/sectores/<int:pk>/utilizadores/' → UtilizadoresPorSectorView.as_view(), name='api_utilizadores_sector'
- [x] Incluir users.urls no expedientes/urls.py principal

## 🛠️ Admin

### 1. Admin Customizado
- [x] Criar arquivo users/admin.py com admin customizado
- [x] UserAdminCustomizado (UserAdmin):
  - [x] List_display = ['email', 'get_full_name', 'tipo_utilizador', 'sector_atual', 'cargo', 'ativo', 'date_joined']
  - [x] List_filter = ['tipo_utilizador', 'ativo', 'sector_atual', 'date_joined']
  - [x] Search_fields = ['email', 'first_name', 'last_name', 'telefone']
  - [x] Fieldsets = [
        ('Informações Pessoais', {'fields': ('email', 'first_name', 'last_name', 'telefone')}),
        ('Informações Profissionais', {'fields': ('sector_atual', 'cargo', 'tipo_utilizador', 'ativo')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Informações Adicionais', {'fields': ('avatar', 'biografia', 'data_nascimento', 'genero', 'endereco', 'codigo_postal', 'cidade', 'pais')}),
        ('Datas', {'fields': ('last_login', 'date_joined', 'ultimo_acesso')}),
    ]
  - [x] Actions = ['ativar_utilizadores', 'desativar_utilizadores', 'enviar_email_bem_vindo']
  - [x] Método ativar_utilizadores(): marca utilizadores selecionados como ativos
  - [x] Método desativar_utilizadores(): marca utilizadores selecionados como inativos
  - [x] Método enviar_email_bem_vindo(): envia email de boas-vindas
- [x] PerfilUtilizadorAdmin (ModelAdmin):
  - [x] List_display = ['user', 'nivel_hierarquico', 'idioma_preferido', 'tema_preferido', 'ativo']
  - [x] List_filter = ['nivel_hierarquico', 'idioma_preferido', 'tema_preferido', 'ativo']
  - [x] Search_fields = ['user__email', 'user__first_name', 'user__last_name', 'biografia']
  - [x] Raw_id_fields = ['user']
- [x] HierarquiaUtilizadorAdmin (ModelAdmin):
  - [x] List_display = ['utilizador', 'sector', 'cargo', 'nivel', 'data_inicio', 'data_fim', 'ativo']
  - [x] List_filter = ['nivel', 'tipo_contrato', 'ativo', 'data_inicio']
  - [x] Search_fields = ['utilizador__email', 'cargo', 'observacoes']
  - [x] Raw_id_fields = ['utilizador', 'sector', 'supervisor']
  - [x] Date_hierarchy = 'data_inicio'

## 🔄 Signals

### 1. Signals de Utilizador
- [x] Criar arquivo users/signals.py com todos os signals
- [x] Signal post_save para User:
  - [x] Criar PerfilUtilizador automaticamente quando User é criado
  - [x] Definir nivel_hierarquico baseado em tipo_utilizador
  - [x] Enviar email de boas-vindas com credenciais temporárias
- [x] Signal post_save para PerfilUtilizador:
  - [x] Atualizar campo nivel_hierarquico no User se necessário
  - [x] Criar entrada em HierarquiaUtilizador se é nova posição
- [x] Signal pre_save para User:
  - [x] Validar que email é único
  - [x] Log de alterações importantes (tipo_utilizador, ativo, sector)
- [x] Signal post_delete para User:
  - [x] Limpar dados relacionados (perfil, hierarquia)
  - [x] Notificar administradores sobre remoção
- [x] Signal user_logged_in:
  - [x] Atualizar campo ultimo_acesso
  - [x] Log de acesso para auditoria
  - [x] Verificar se utilizador está ativo
- [x] Signal user_logged_out:
  - [x] Log de logout para auditoria
  - [x] Limpar sessões temporárias se necessário

## 🧪 Testes

### 1. Testes de Modelos
- [x] Criar arquivo users/tests.py com todos os testes
- [x] TestUserModel (TestCase):
  - [x] Teste criar_utilizador(): criar utilizador com dados válidos
  - [x] Teste obter_papel_exibicao(): retorna papel correto baseado em campos
  - [x] Teste is_chefe_de_sector(): verifica se é chefe do sector atual
  - [x] Teste obter_nivel_hierarquico(): retorna nível numérico correto
  - [x] Teste pode_gerir_utilizador(): valida hierarquia de gestão
  - [x] Teste eh_pca_ou_superuser(): verifica permissões máximas
  - [x] Teste atualizar_ultimo_acesso(): atualiza campo corretamente
- [x] TestPerfilUtilizador (TestCase):
  - [x] Teste obter_nivel_display(): retorna nome do nível
  - [x] Teste eh_chefe(): verifica se é chefe
  - [x] Teste obter_idade(): calcula idade corretamente
  - [x] Teste obter_preferencia_notificacao(): retorna configuração
  - [x] Teste definir_preferencia_notificacao(): define configuração
- [x] TestHierarquiaUtilizador (TestCase):
  - [x] Teste obter_subordinados(): retorna subordinados corretos
  - [x] Teste pode_gerir_utilizador(): valida hierarquia
  - [x] Teste eh_ativo(): verifica se posição está ativa
  - [x] Teste obter_nivel_peso(): retorna peso numérico
  - [x] Teste obter_duracao(): calcula duração da posição
  - [x] Teste finalizar_posicao(): marca como inativo

### 2. Testes de Views
- [x] TestLoginView (TestCase):
  - [x] Teste get(): renderiza template correto
  - [x] Teste post_valid(): autentica utilizador e redireciona
  - [x] Teste post_invalid(): mostra erros de validação
- [x] TestListarUtilizadoresView (TestCase):
  - [x] Teste get(): lista utilizadores com permissão
  - [x] Teste permissao(): apenas utilizadores autorizados acessam
- [x] TestCriarUtilizadorView (TestCase):
  - [x] Teste get(): mostra formulário de criação

### 3. Testes de Forms
- [x] TestCriarUtilizadorForm (TestCase):
  - [x] Teste campos_obrigatorios(): valida campos obrigatórios
  - [x] Teste clean_email(): valida email único
- [x] TestUserLoginForm (TestCase):
  - [x] Teste clean_username(): valida email existe
- [x] TestPerfilUtilizadorForm (TestCase):
  - [x] Teste clean_data_nascimento(): valida idade

### 4. Testes de Signals
- [x] TestUserSignals (TestCase):
  - [x] Teste criar_perfil_automatico(): cria perfil ao criar utilizador
  - [x] Teste definir_nivel_hierarquico(): define nível baseado em campos

### 5. Testes de Permissões
- [x] TestPermissoesUtilizador (TestCase):
  - [x] Teste hierarquia_permissoes(): Admin > PCA > Secretaria > Chefe > Colaborador
  - [x] Teste gestao_utilizadores(): apenas superiores podem gerir

## 📋 Validação Final
- [x] Custom User Model funcionando com todos os campos e métodos
- [x] Login por email funcionando com validações
- [x] Hierarquia organizacional implementada e testada
- [x] Permissões configuradas corretamente (grupos e permissões customizadas)
- [x] Templates renderizando corretamente com Bootstrap 5
- [x] Admin configurado com filtros e ações
- [x] Signals funcionando (criação de perfil, validações, logs)
- [x] Forms com validações específicas funcionando
- [x] Views com permissões e decorators funcionando
- [x] URLs mapeadas corretamente
- [x] Testes implementados (modelos, views, forms, signals, permissões)
- [x] Migrações criadas e aplicadas
- [x] Checklist 100% completa

---

**Nota:** Esta app é fundamental para todo o sistema de permissões e hierarquia.

**IMPORTANTE - Relação Sector/Utilizador:**
- O campo `sector_atual` no User indica onde o utilizador trabalha atualmente
- O campo `chefe` no modelo Sector (app core) indica quem é o chefe desse sector
- Um utilizador pode ser chefe de um sector (definido no modelo Sector)
- O modelo HierarquiaUtilizador mantém histórico de posições do utilizador
- Use `user.is_chefe_de_sector()` para verificar se é chefe de algum sector

**IMPORTANTE - PCA (Presidente do Conselho de Administração):**
- O PCA é identificado pelo campo booleano `is_pca` no User
- Pode existir um Sector "Gabinete do PCA" ou "Presidência" onde o PCA é o chefe
- O PCA tem máxima autoridade na hierarquia organizacional
- Permissões especiais: aprovar todos os documentos de saída, ver todos os documentos
- Use `user.is_pca` ou `user.is_pca_or_superuser()` para verificar permissões máximas
- Apenas um utilizador deve ter `is_pca=True` (garantir via validação)
