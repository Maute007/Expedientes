from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from .models import ConfiguracaoRelatorio, TipoRelatorio, Dashboard, WidgetDashboard
from core.models import Sector

User = get_user_model()


class RelatorioForm(forms.ModelForm):
    """
    Formulário para criação e edição de configurações de relatórios.
    """
    
    class Meta:
        model = ConfiguracaoRelatorio
        fields = [
            'nome', 'descricao', 'tipo_relatorio', 'sector', 
            'publico', 'ativo'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do relatório'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição do relatório'
            }),
            'tipo_relatorio': forms.Select(attrs={
                'class': 'form-select'
            }),
            'sector': forms.Select(attrs={
                'class': 'form-select'
            }),
            'publico': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar tipos de relatórios ativos
        self.fields['tipo_relatorio'].queryset = TipoRelatorio.objects.filter(ativo=True)
        
        # Filtrar sectores ativos
        self.fields['sector'].queryset = Sector.objects.filter(ativo=True)
        self.fields['sector'].empty_label = "Todos os sectores"
        
        # Adicionar campos dinâmicos baseados no tipo de relatório
        if self.instance.pk and self.instance.tipo_relatorio:
            self._add_dynamic_fields()
    
    def _add_dynamic_fields(self):
        """Adiciona campos dinâmicos baseados no tipo de relatório."""
        tipo_relatorio = self.instance.tipo_relatorio
        
        # Adicionar campos para parâmetros obrigatórios
        for param in tipo_relatorio.parametros_obrigatorios:
            field_name = f"param_{param}"
            if param == 'data_inicio':
                self.fields[field_name] = forms.DateField(
                    label=f"Data de Início",
                    widget=forms.DateInput(attrs={
                        'class': 'form-control',
                        'type': 'date'
                    }),
                    required=True
                )
            elif param == 'data_fim':
                self.fields[field_name] = forms.DateField(
                    label=f"Data de Fim",
                    widget=forms.DateInput(attrs={
                        'class': 'form-control',
                        'type': 'date'
                    }),
                    required=True
                )
            elif param == 'sector_id':
                self.fields[field_name] = forms.ModelChoiceField(
                    label="Sector",
                    queryset=Sector.objects.filter(ativo=True),
                    widget=forms.Select(attrs={'class': 'form-select'}),
                    required=True,
                    empty_label="Selecione um sector"
                )
            elif param == 'estado_id':
                from core.models import EstadoDocumento
                self.fields[field_name] = forms.ModelChoiceField(
                    label="Estado",
                    queryset=EstadoDocumento.objects.filter(ativo=True),
                    widget=forms.Select(attrs={'class': 'form-select'}),
                    required=True,
                    empty_label="Selecione um estado"
                )
            else:
                self.fields[field_name] = forms.CharField(
                    label=param.replace('_', ' ').title(),
                    widget=forms.TextInput(attrs={'class': 'form-control'}),
                    required=True
                )
        
        # Adicionar campos para parâmetros opcionais
        for param in tipo_relatorio.parametros_opcionais:
            field_name = f"param_{param}"
            if param == 'formato':
                self.fields[field_name] = forms.ChoiceField(
                    label="Formato de Saída",
                    choices=[
                        ('pdf', 'PDF'),
                        ('excel', 'Excel'),
                        ('csv', 'CSV'),
                        ('html', 'HTML')
                    ],
                    widget=forms.Select(attrs={'class': 'form-select'}),
                    required=False,
                    initial='pdf'
                )
            elif param == 'incluir_graficos':
                self.fields[field_name] = forms.BooleanField(
                    label="Incluir Gráficos",
                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
                    required=False,
                    initial=True
                )
            else:
                self.fields[field_name] = forms.CharField(
                    label=param.replace('_', ' ').title(),
                    widget=forms.TextInput(attrs={'class': 'form-control'}),
                    required=False
                )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validar datas
        data_inicio = cleaned_data.get('param_data_inicio')
        data_fim = cleaned_data.get('param_data_fim')
        
        if data_inicio and data_fim:
            if data_inicio > data_fim:
                raise ValidationError("A data de início deve ser anterior à data de fim.")
            
            # Verificar se não é muito antigo (mais de 2 anos)
            dois_anos_atras = timezone.now().date() - timedelta(days=730)
            if data_inicio < dois_anos_atras:
                raise ValidationError("A data de início não pode ser anterior a 2 anos.")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.user:
            instance.utilizador_criador = self.user
        
        # Salvar parâmetros dinâmicos
        parametros = {}
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('param_'):
                param_name = field_name.replace('param_', '')
                parametros[param_name] = value
        
        instance.parametros = parametros
        
        if commit:
            instance.save()
        
        return instance


class ParametrosRelatorioForm(forms.Form):
    """
    Formulário para configuração de parâmetros de relatórios.
    """
    
    def __init__(self, tipo_relatorio, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tipo_relatorio = tipo_relatorio
        
        # Adicionar campos baseados no tipo de relatório
        self._add_fields()
    
    def _add_fields(self):
        """Adiciona campos baseados no tipo de relatório."""
        
        # Campos comuns para todos os relatórios
        self.fields['data_inicio'] = forms.DateField(
            label="Data de Início",
            widget=forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            initial=timezone.now().date() - timedelta(days=30)
        )
        
        self.fields['data_fim'] = forms.DateField(
            label="Data de Fim",
            widget=forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            initial=timezone.now().date()
        )
        
        self.fields['formato'] = forms.ChoiceField(
            label="Formato de Saída",
            choices=[
                ('pdf', 'PDF'),
                ('excel', 'Excel'),
                ('csv', 'CSV'),
                ('html', 'HTML')
            ],
            widget=forms.Select(attrs={'class': 'form-select'}),
            initial='pdf'
        )
        
        # Campos específicos por tipo de relatório
        if self.tipo_relatorio.tipo_relatorio == 'documentos_sector':
            self.fields['sector'] = forms.ModelChoiceField(
                label="Sector",
                queryset=Sector.objects.filter(ativo=True),
                widget=forms.Select(attrs={'class': 'form-select'}),
                required=False,
                empty_label="Todos os sectores"
            )
            
            self.fields['estado'] = forms.ModelChoiceField(
                label="Estado",
                queryset=EstadoDocumento.objects.filter(ativo=True),
                widget=forms.Select(attrs={'class': 'form-select'}),
                required=False,
                empty_label="Todos os estados"
            )
        
        elif self.tipo_relatorio.tipo_relatorio == 'tempo_resposta':
            self.fields['incluir_graficos'] = forms.BooleanField(
                label="Incluir Gráficos",
                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
                required=False,
                initial=True
            )
            
            self.fields['agrupar_por'] = forms.ChoiceField(
                label="Agrupar por",
                choices=[
                    ('sector', 'Sector'),
                    ('tipo_documento', 'Tipo de Documento'),
                    ('mes', 'Mês'),
                    ('semana', 'Semana')
                ],
                widget=forms.Select(attrs={'class': 'form-select'}),
                initial='sector'
            )
        
        elif self.tipo_relatorio.tipo_relatorio == 'atividade_utilizadores':
            self.fields['utilizador'] = forms.ModelChoiceField(
                label="Utilizador",
                queryset=User.objects.filter(is_active=True),
                widget=forms.Select(attrs={'class': 'form-select'}),
                required=False,
                empty_label="Todos os utilizadores"
            )
            
            self.fields['tipo_atividade'] = forms.ChoiceField(
                label="Tipo de Atividade",
                choices=[
                    ('todos', 'Todas'),
                    ('criacao', 'Criação de Documentos'),
                    ('processamento', 'Processamento'),
                    ('aprovacao', 'Aprovação'),
                    ('arquivamento', 'Arquivamento')
                ],
                widget=forms.Select(attrs={'class': 'form-select'}),
                initial='todos'
            )


class FiltrosRelatorioForm(forms.Form):
    """
    Formulário para filtros avançados de relatórios.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtros básicos
        self.fields['data_inicio'] = forms.DateField(
            label="Data de Início",
            widget=forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            required=False
        )
        
        self.fields['data_fim'] = forms.DateField(
            label="Data de Fim",
            widget=forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            required=False
        )
        
        self.fields['sector'] = forms.ModelChoiceField(
            label="Sector",
            queryset=Sector.objects.filter(ativo=True),
            widget=forms.Select(attrs={'class': 'form-select'}),
            required=False,
            empty_label="Todos os sectores"
        )
        
        self.fields['estado'] = forms.ModelChoiceField(
            label="Estado",
            queryset=EstadoDocumento.objects.filter(ativo=True),
            widget=forms.Select(attrs={'class': 'form-select'}),
            required=False,
            empty_label="Todos os estados"
        )
        
        self.fields['prioridade'] = forms.ChoiceField(
            label="Prioridade",
            choices=[
                ('', 'Todas'),
                ('baixa', 'Baixa'),
                ('normal', 'Normal'),
                ('alta', 'Alta'),
                ('urgente', 'Urgente')
            ],
            widget=forms.Select(attrs={'class': 'form-select'}),
            required=False
        )
        
        self.fields['origem'] = forms.ChoiceField(
            label="Origem",
            choices=[
                ('', 'Todas'),
                ('secretaria', 'Secretaria'),
                ('portal', 'Portal Online'),
                ('quiosque', 'Quiosque'),
                ('email', 'Email'),
                ('fax', 'Fax'),
                ('correio', 'Correio'),
                ('pessoal', 'Entrega Pessoal')
            ],
            widget=forms.Select(attrs={'class': 'form-select'}),
            required=False
        )
        
        # Filtros avançados
        self.fields['utilizador_criador'] = forms.ModelChoiceField(
            label="Criado por",
            queryset=User.objects.filter(is_active=True),
            widget=forms.Select(attrs={'class': 'form-select'}),
            required=False,
            empty_label="Todos os utilizadores"
        )
        
        self.fields['utilizador_atual'] = forms.ModelChoiceField(
            label="Utilizador Atual",
            queryset=User.objects.filter(is_active=True),
            widget=forms.Select(attrs={'class': 'form-select'}),
            required=False,
            empty_label="Todos os utilizadores"
        )
        
        self.fields['incluir_rascunhos'] = forms.BooleanField(
            label="Incluir Rascunhos",
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            required=False,
            initial=False
        )
        
        self.fields['incluir_arquivados'] = forms.BooleanField(
            label="Incluir Arquivados",
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            required=False,
            initial=True
        )


class DashboardForm(forms.ModelForm):
    """
    Formulário para criação e edição de dashboards.
    """
    
    class Meta:
        model = Dashboard
        fields = ['nome', 'descricao', 'sector', 'publico', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do dashboard'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição do dashboard'
            }),
            'sector': forms.Select(attrs={
                'class': 'form-select'
            }),
            'publico': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar sectores ativos
        self.fields['sector'].queryset = Sector.objects.filter(ativo=True)
        self.fields['sector'].empty_label = "Todos os sectores"
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.user:
            instance.utilizador_criador = self.user
        
        if commit:
            instance.save()
        
        return instance


class WidgetForm(forms.ModelForm):
    """
    Formulário para criação e edição de widgets.
    """
    
    class Meta:
        model = WidgetDashboard
        fields = ['tipo_widget', 'titulo', 'parametros', 'tamanho', 'ativo', 'ordem']
        widgets = {
            'tipo_widget': forms.Select(attrs={
                'class': 'form-select'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título do widget'
            }),
            'parametros': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Parâmetros em JSON'
            }),
            'tamanho': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '{"width": 4, "height": 3}'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'ordem': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            })
        }
    
    def clean_parametros(self):
        """Valida se os parâmetros são JSON válido."""
        parametros = self.cleaned_data.get('parametros')
        if parametros:
            try:
                import json
                json.loads(parametros)
            except json.JSONDecodeError:
                raise ValidationError("Parâmetros devem ser um JSON válido.")
        return parametros
    
    def clean_tamanho(self):
        """Valida se o tamanho é JSON válido."""
        tamanho = self.cleaned_data.get('tamanho')
        if tamanho:
            try:
                import json
                tamanho_dict = json.loads(tamanho)
                if 'width' not in tamanho_dict or 'height' not in tamanho_dict:
                    raise ValidationError("Tamanho deve conter 'width' e 'height'.")
            except json.JSONDecodeError:
                raise ValidationError("Tamanho deve ser um JSON válido.")
        return tamanho


class ExecucaoRelatorioForm(forms.Form):
    """
    Formulário para execução rápida de relatórios.
    """
    
    def __init__(self, relatorio, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.relatorio = relatorio
        
        # Adicionar campos baseados nos parâmetros do relatório
        self._add_fields()
    
    def _add_fields(self):
        """Adiciona campos baseados nos parâmetros do relatório."""
        
        # Campos básicos
        self.fields['formato'] = forms.ChoiceField(
            label="Formato de Saída",
            choices=[
                ('pdf', 'PDF'),
                ('excel', 'Excel'),
                ('csv', 'CSV'),
                ('html', 'HTML')
            ],
            widget=forms.Select(attrs={'class': 'form-select'}),
            initial=self.relatorio.tipo_relatorio.formato_saida
        )
        
        # Adicionar campos para parâmetros do relatório
        for param, value in self.relatorio.parametros.items():
            if param == 'data_inicio':
                self.fields[param] = forms.DateField(
                    label="Data de Início",
                    widget=forms.DateInput(attrs={
                        'class': 'form-control',
                        'type': 'date'
                    }),
                    initial=value
                )
            elif param == 'data_fim':
                self.fields[param] = forms.DateField(
                    label="Data de Fim",
                    widget=forms.DateInput(attrs={
                        'class': 'form-control',
                        'type': 'date'
                    }),
                    initial=value
                )
            elif param == 'sector_id':
                self.fields[param] = forms.ModelChoiceField(
                    label="Sector",
                    queryset=Sector.objects.filter(ativo=True),
                    widget=forms.Select(attrs={'class': 'form-select'}),
                    initial=value,
                    empty_label="Selecione um sector"
                )
            else:
                self.fields[param] = forms.CharField(
                    label=param.replace('_', ' ').title(),
                    widget=forms.TextInput(attrs={'class': 'form-control'}),
                    initial=value
                )
