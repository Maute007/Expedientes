from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Expediente, TipoDocumento, AnexoExpediente, MovimentacaoDocumento, ParecerExpediente
from core.models import Sector, EstadoDocumento

User = get_user_model()


class TipoDocumentoForm(forms.ModelForm):
    """
    Form para criar/editar tipos de documento
    """
    class Meta:
        model = TipoDocumento
        fields = ['nome', 'categoria', 'descricao', 'prazo_resposta', 'prioridade_padrao', 'requer_anexos', 'template_resposta', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Solicitação Interna'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição do tipo de documento'
            }),
            'prazo_resposta': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 365
            }),
            'prioridade_padrao': forms.Select(attrs={
                'class': 'form-select'
            }),
            'requer_anexos': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'template_resposta': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Template para resposta padrão (opcional)'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class Etapa1Form(forms.ModelForm):
    """
    Form para Etapa 1: Informações Básicas
    """
    class Meta:
        model = Expediente
        fields = ['numero_protocolo', 'referencia', 'tipo', 'origem', 'remetente']
        widgets = {
            'numero_protocolo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'AAAAMMXXXXX',
                'readonly': True,
                'style': 'background-color: #f8f9fa;'
            }),
            'referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Ofício nº 123/2025'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Selecionar tipo...'
            }),
            'origem': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Selecionar origem...'
            }),
            'remetente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do remetente'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas tipos ativos
        self.fields['tipo'].queryset = TipoDocumento.objects.filter(ativo=True)
        self.fields['tipo'].empty_label = "Selecionar tipo..."


class Etapa2Form(forms.ModelForm):
    """
    Form para Etapa 2: Detalhes
    """
    # anexos removido - agora gerenciado via JavaScript/modal
    
    class Meta:
        model = Expediente
        fields = ['assunto', 'descricao', 'telefone', 'prioridade', 'data_limite', 'requer_resposta', 'confidencial']
        widgets = {
            'assunto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Resumo do assunto do processo'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrição detalhada do processo (opcional)'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+258 82 123 4567'
            }),
            'prioridade': forms.Select(attrs={
                'class': 'form-select'
            }),
            'data_limite': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'requer_resposta': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'confidencial': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Definir prioridade padrão como 'normal'
        self.fields['prioridade'].initial = 'normal'
        # Tornar campos opcionais
        self.fields['data_limite'].required = False
        self.fields['requer_resposta'].required = False
        self.fields['confidencial'].required = False
        self.fields['descricao'].required = False
        self.fields['telefone'].required = False
    
    def clean_anexos(self):
        anexos = self.files.getlist('anexos')
        if anexos:
            for anexo in anexos:
                if anexo.size > 10 * 1024 * 1024:  # 10MB
                    raise forms.ValidationError(f'O arquivo {anexo.name} é muito grande. Tamanho máximo: 10MB')
                
                # Verificar extensão
                extensoes_permitidas = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif', '.xls', '.xlsx', '.txt', '.zip']
                if not any(anexo.name.lower().endswith(ext) for ext in extensoes_permitidas):
                    raise forms.ValidationError(f'O arquivo {anexo.name} tem formato não suportado.')
        
        return anexos


class Etapa3Form(forms.Form):
    """
    Form para Etapa 3: Membros
    """
    sector = forms.ModelChoiceField(
        queryset=Sector.objects.filter(ativo=True),
        empty_label="Selecionar sector...",
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'sector-select'
        })
    )
    
    membros = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(ativo=True),
        required=False,
        widget=forms.MultipleHiddenInput()
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicializar com membros vazios
        self.fields['membros'].queryset = User.objects.filter(ativo=True)


class Etapa4Form(forms.ModelForm):
    """
    Form para Etapa 4: Revisão Final
    """
    class Meta:
        model = Expediente
        fields = []  # Apenas para revisão, sem campos editáveis
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Este form é apenas para revisão, não tem campos editáveis


class AnexoForm(forms.ModelForm):
    """
    Form para upload de anexos
    """
    class Meta:
        model = AnexoExpediente
        fields = ['arquivo', 'descricao']
        widgets = {
            'arquivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            }),
            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição do anexo (opcional)'
            })
        }
    
    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')
        if arquivo:
            # Verificar tamanho (10MB máximo)
            if arquivo.size > 10 * 1024 * 1024:
                raise forms.ValidationError("O arquivo deve ter no máximo 10MB.")
            
            # Verificar extensão
            extensoes_permitidas = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            if not any(arquivo.name.lower().endswith(ext) for ext in extensoes_permitidas):
                raise forms.ValidationError(
                    "Formato não suportado. Use: PDF, DOC, DOCX, JPG, PNG"
                )
        
        return arquivo


class ExpedienteSearchForm(forms.Form):
    """
    Form para busca de expedientes
    """
    numero_protocolo = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de protocolo...'
        })
    )
    
    tipo = forms.ModelChoiceField(
        queryset=TipoDocumento.objects.filter(ativo=True),
        required=False,
        empty_label="Todos os tipos",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    status = forms.ModelChoiceField(
        queryset=EstadoDocumento.objects.filter(ativo=True),
        required=False,
        empty_label="Todos os status",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    sector = forms.ModelChoiceField(
        queryset=Sector.objects.filter(ativo=True),
        required=False,
        empty_label="Todos os sectores",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )


class ExpedienteFilterForm(forms.Form):
    """
    Form para filtros avançados de expedientes
    """
    SORT_CHOICES = [
        ('-data_criacao', 'Mais recente'),
        ('data_criacao', 'Mais antigo'),
        ('numero_protocolo', 'Número de protocolo'),
        ('assunto', 'Assunto'),
        ('tipo__nome', 'Tipo'),
        ('status', 'Status'),
    ]
    
    ordenar_por = forms.ChoiceField(
        choices=SORT_CHOICES,
        initial='-data_criacao',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    por_pagina = forms.ChoiceField(
        choices=[(10, '10 por página'), (25, '25 por página'), (50, '50 por página')],
        initial=25,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )


# Forms da checklist DocumentoEntrada
class ParecerExpedienteForm(forms.ModelForm):
    """
    Formulário para criar/editar pareceres de expedientes
    """
    class Meta:
        model = ParecerExpediente
        fields = [
            'tipo_parecer', 'titulo', 'conteudo', 'recomendacoes', 
            'observacoes', 'prioridade', 'data_limite'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o título do parecer'
            }),
            'conteudo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Digite o conteúdo do parecer...'
            }),
            'recomendacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Digite as recomendações (opcional)...'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Digite observações adicionais (opcional)...'
            }),
            'tipo_parecer': forms.Select(attrs={
                'class': 'form-select'
            }),
            'prioridade': forms.Select(attrs={
                'class': 'form-select'
            }),
            'data_limite': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar data_limite opcional
        self.fields['data_limite'].required = False
        self.fields['recomendacoes'].required = False
        self.fields['observacoes'].required = False


class ImplementarParecerForm(forms.Form):
    """
    Formulário para implementar pareceres
    """
    observacoes_implementacao = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Digite observações sobre a implementação...'
        }),
        required=False,
        label="Observações da Implementação"
    )
    
    data_implementacao = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        label="Data de Implementação",
        initial=timezone.now
    )


class DocumentoEntradaForm(forms.ModelForm):
    """
    Form para criar documento de entrada conforme checklist
    """
    class Meta:
        model = Expediente
        fields = ['tipo', 'assunto', 'conteudo', 'prioridade', 'data_limite', 'requer_resposta', 'confidencial']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'assunto': forms.TextInput(attrs={'class': 'form-control'}),
            'conteudo': forms.Textarea(attrs={'rows': 8, 'class': 'form-control'}),
            'prioridade': forms.Select(attrs={'class': 'form-select'}),
            'data_limite': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'requer_resposta': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'confidencial': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
    
    def clean_assunto(self):
        assunto = self.cleaned_data.get('assunto')
        if not assunto:
            raise forms.ValidationError("Assunto é obrigatório.")
        return assunto
    
    def clean_data_limite(self):
        data_limite = self.cleaned_data.get('data_limite')
        if data_limite:
            from datetime import date
            if data_limite < date.today():
                raise forms.ValidationError("Data limite não pode ser no passado.")
        return data_limite


class DocumentoEntradaUpdateForm(forms.ModelForm):
    """
    Form para editar documento de entrada conforme checklist
    """
    class Meta:
        model = Expediente
        fields = ['assunto', 'conteudo', 'prioridade', 'data_limite', 'observacoes']
        widgets = {
            'assunto': forms.TextInput(attrs={'class': 'form-control'}),
            'conteudo': forms.Textarea(attrs={'rows': 8, 'class': 'form-control'}),
            'prioridade': forms.Select(attrs={'class': 'form-select'}),
            'data_limite': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'})
        }


class EncaminhamentoForm(forms.Form):
    """
    Form para encaminhamento de documentos conforme checklist
    """
    destinatario_tipo = forms.ChoiceField(
        choices=[('sector', 'Sector'), ('utilizador', 'Utilizador')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    sector_destino = forms.ModelChoiceField(
        queryset=Sector.objects.filter(ativo=True),
        required=False,
        empty_label="Selecionar sector...",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    utilizador_destino = forms.ModelChoiceField(
        queryset=User.objects.filter(ativo=True),
        required=False,
        empty_label="Selecionar utilizador...",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    observacoes = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
    )
    adicionar_despacho = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    tipo_despacho = forms.ChoiceField(
        choices=[
            ('aprovacao', 'Aprovação'),
            ('rejeicao', 'Rejeição'),
            ('observacao', 'Observação'),
            ('devolucao', 'Devolução'),
            ('arquivamento', 'Arquivamento')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    conteudo_despacho = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        destinatario_tipo = cleaned_data.get('destinatario_tipo')
        sector_destino = cleaned_data.get('sector_destino')
        utilizador_destino = cleaned_data.get('utilizador_destino')
        
        if destinatario_tipo == 'sector' and not sector_destino:
            raise forms.ValidationError("Selecione um sector de destino.")
        elif destinatario_tipo == 'utilizador' and not utilizador_destino:
            raise forms.ValidationError("Selecione um utilizador de destino.")
        
        return cleaned_data
    
    def clean_sector_destino(self):
        sector = self.cleaned_data.get('sector_destino')
        if sector and not sector.ativo:
            raise forms.ValidationError("Sector selecionado não está ativo.")
        return sector
    
    def clean_utilizador_destino(self):
        utilizador = self.cleaned_data.get('utilizador_destino')
        if utilizador and not utilizador.ativo:
            raise forms.ValidationError("Utilizador selecionado não está ativo.")
        return utilizador


class PortalExpedienteForm(forms.Form):
    """
    Form para portal externo conforme checklist
    """
    nome_remetente = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu nome completo'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'})
    )
    telefone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+258 82 123 4567'})
    )
    assunto = forms.CharField(
        max_length=300,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Assunto do expediente'})
    )
    conteudo = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'class': 'form-control', 'placeholder': 'Descreva detalhadamente sua solicitação'})
    )
    tipo_documento = forms.ModelChoiceField(
        queryset=TipoDocumento.objects.filter(ativo=True),
        empty_label="Selecionar tipo de documento...",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    anexos = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
        })
    )


class EditarExpedienteForm(forms.ModelForm):
    """
    Form para editar expediente existente
    """
    class Meta:
        model = Expediente
        fields = ['tipo', 'origem', 'remetente', 'assunto', 'descricao', 'telefone']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Selecionar tipo...'
            }),
            'origem': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Selecionar origem...'
            }),
            'remetente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do remetente'
            }),
            'assunto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Resumo do assunto do processo'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrição detalhada do processo (opcional)'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+258 82 123 4567'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas tipos ativos
        self.fields['tipo'].queryset = TipoDocumento.objects.filter(ativo=True)
        self.fields['tipo'].empty_label = "Selecionar tipo..."
        
        # Adicionar classes Bootstrap aos labels
        for field_name, field in self.fields.items():
            field.label_class = 'form-label fw-semibold'


class MultiAnexoForm(forms.Form):
    """
    Form para upload múltiplo de anexos conforme checklist
    """
    ficheiros = forms.FileField(
        label='Ficheiros',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png,.gif,.xls,.xlsx,.txt,.zip'
        })
    )
    descricao_geral = forms.CharField(
        label='Descrição Geral',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    def clean_ficheiros(self):
        ficheiros = self.files.getlist('ficheiros')
        if not ficheiros:
            raise forms.ValidationError("Selecione pelo menos um ficheiro.")
        
        for ficheiro in ficheiros:
            # Verificar tamanho (10MB máximo)
            if ficheiro.size > 10 * 1024 * 1024:
                raise forms.ValidationError(f"Ficheiro {ficheiro.name} excede 10MB.")
            
            # Verificar extensão
            extensoes_permitidas = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif', '.xls', '.xlsx', '.txt', '.zip']
            if not any(ficheiro.name.lower().endswith(ext) for ext in extensoes_permitidas):
                raise forms.ValidationError(f"Formato não suportado para {ficheiro.name}.")
        
        return ficheiros
