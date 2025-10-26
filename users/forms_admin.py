from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import User, PerfilUtilizador
from core.models import Sector


class GestaoUtilizadorAdminForm(forms.ModelForm):
    """
    Formulário completo para gestão de utilizador (apenas administradores).
    """
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'telefone', 'tipo_utilizador',
            'sector_atual', 'is_active', 'is_staff'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do utilizador'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sobrenome do utilizador'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+258 82 123 4567'
            }),
            'tipo_utilizador': forms.Select(attrs={
                'class': 'form-select'
            }),
            'sector_atual': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
    
    # Campos do PerfilUtilizador
    receber_notificacoes_email = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    receber_notificacoes_push = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    receber_newsletter = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    perfil_publico = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    mostrar_email = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    mostrar_telefone = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    tema_preferido = forms.ChoiceField(
        choices=[
            ('light', 'Claro'),
            ('dark', 'Escuro'),
            ('auto', 'Automático'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    idioma_preferido = forms.ChoiceField(
        choices=[
            ('pt-pt', 'Português'),
            ('en', 'English'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    timezone = forms.ChoiceField(
        choices=[
            ('Africa/Maputo', 'Maputo (GMT+2)'),
            ('UTC', 'UTC (GMT+0)'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    horario_trabalho_inicio = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    horario_trabalho_fim = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    dias_trabalho = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1,2,3,4,5 (Segunda a Sexta)'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Carregar dados do PerfilUtilizador se existir
        if self.instance and hasattr(self.instance, 'perfil'):
            perfil = self.instance.perfil
            self.fields['receber_notificacoes_email'].initial = perfil.receber_notificacoes_email
            self.fields['receber_notificacoes_push'].initial = perfil.receber_notificacoes_push
            self.fields['receber_newsletter'].initial = perfil.receber_newsletter
            self.fields['perfil_publico'].initial = perfil.perfil_publico
            self.fields['mostrar_email'].initial = perfil.mostrar_email
            self.fields['mostrar_telefone'].initial = perfil.mostrar_telefone
            self.fields['tema_preferido'].initial = perfil.tema_preferido
            self.fields['idioma_preferido'].initial = perfil.idioma_preferido
            self.fields['timezone'].initial = perfil.timezone
            self.fields['horario_trabalho_inicio'].initial = perfil.horario_trabalho_inicio
            self.fields['horario_trabalho_fim'].initial = perfil.horario_trabalho_fim
            self.fields['dias_trabalho'].initial = perfil.dias_trabalho
        
        # Adicionar help text
        self.fields['email'].help_text = 'Email único para login'
        self.fields['telefone'].help_text = 'Formato: +258 82 123 4567'
        self.fields['tipo_utilizador'].help_text = 'Define as permissões do utilizador'
        self.fields['sector_atual'].help_text = 'Sector onde o utilizador trabalha'
        self.fields['is_active'].help_text = 'Permitir que o utilizador faça login'
        self.fields['is_staff'].help_text = 'Permitir acesso ao painel administrativo'
        self.fields['dias_trabalho'].help_text = 'Dias da semana que trabalha (1=Segunda, 7=Domingo)'
        
        # Configurar choices para tipo_utilizador
        self.fields['tipo_utilizador'].choices = [
            ('admin', 'Administrador'),
            ('pca', 'PCA'),
            ('secretaria', 'Secretaria'),
            ('chefe', 'Chefe'),
            ('colaborador', 'Colaborador'),
            ('externo', 'Externo'),
        ]
        
        # Configurar choices para tema_preferido
        self.fields['tema_preferido'].choices = [
            ('light', 'Claro'),
            ('dark', 'Escuro'),
            ('auto', 'Automático'),
        ]
        
        # Configurar choices para idioma_preferido
        self.fields['idioma_preferido'].choices = [
            ('pt-pt', 'Português'),
            ('en', 'English'),
        ]
        
        # Configurar choices para timezone
        self.fields['timezone'].choices = [
            ('Africa/Maputo', 'Maputo (GMT+2)'),
            ('UTC', 'UTC (GMT+0)'),
        ]
    
    def clean_email(self):
        """
        Valida se email é único (exceto para o próprio utilizador).
        """
        email = self.cleaned_data.get('email')
        if email and self.instance.pk:
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Este email já está sendo usado por outro utilizador.')
        return email
    
    def clean_dias_trabalho(self):
        """
        Valida o formato dos dias de trabalho.
        """
        dias = self.cleaned_data.get('dias_trabalho')
        if dias:
            try:
                dias_list = [int(d.strip()) for d in dias.split(',')]
                for dia in dias_list:
                    if dia < 1 or dia > 7:
                        raise forms.ValidationError('Os dias devem estar entre 1 (Segunda) e 7 (Domingo).')
            except ValueError:
                raise forms.ValidationError('Formato inválido. Use: 1,2,3,4,5 (exemplo)')
        return dias
    
    def save(self, commit=True):
        """
        Salva o User e o PerfilUtilizador.
        """
        user = super().save(commit=commit)
        
        if commit:
            # Criar ou atualizar PerfilUtilizador
            perfil, created = PerfilUtilizador.objects.get_or_create(user=user)
            
            # Salvar campos do PerfilUtilizador
            perfil_fields = [
                'receber_notificacoes_email', 'receber_notificacoes_push', 'receber_newsletter',
                'perfil_publico', 'mostrar_email', 'mostrar_telefone', 'tema_preferido',
                'idioma_preferido', 'timezone', 'horario_trabalho_inicio', 'horario_trabalho_fim',
                'dias_trabalho'
            ]
            
            for field in perfil_fields:
                if field in self.cleaned_data:
                    setattr(perfil, field, self.cleaned_data[field])
            
            perfil.save()
        
        return user
