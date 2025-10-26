from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from .models import PerfilUtilizador, HierarquiaUtilizador
from core.form_mixins import FileUploadMixin

User = get_user_model()


class BaseUserForm(forms.Form):
    """
    Form base para utilizadores com estilos comuns.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplicar classes Bootstrap 5 a todos os campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': field.label or ''
                })
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'rows': 4
                })
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({
                    'class': 'form-select'
                })
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class': 'form-check-input'
                })
            elif isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.update({
                    'class': 'form-check-input'
                })
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({
                    'class': 'form-check-input'
                })
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({
                    'class': 'form-control'
                })
            elif isinstance(field.widget, forms.DateInput):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'type': 'date'
                })
            elif isinstance(field.widget, forms.EmailInput):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'type': 'email'
                })
            elif isinstance(field.widget, forms.PasswordInput):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'type': 'password'
                })


class UserRegistrationForm(UserCreationForm):
    """
    Form de registo APENAS para utilizadores externos no portal público.
    """
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'telefone', 'password1', 'password2']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'seu.email@exemplo.com',
                'autocomplete': 'email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu nome',
                'autocomplete': 'given-name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu sobrenome',
                'autocomplete': 'family-name'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+258 82 123 4567',
                'autocomplete': 'tel'
            }),
        }
    
    def save(self, commit=True):
        """
        Salva o utilizador como EXTERNO automaticamente.
        """
        user = super().save(commit=False)
        user.tipo_utilizador = 'externo'  # Sempre externo no registo público
        user.username = user.email  # Usar email como username
        if commit:
            user.save()
        return user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar campos de senha
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Crie uma senha segura',
            'autocomplete': 'new-password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme sua senha',
            'autocomplete': 'new-password'
        })
        
        # Adicionar help text
        self.fields['email'].help_text = 'Email único para login no sistema'
        self.fields['password1'].help_text = 'Mínimo 8 caracteres com letras e números'
        self.fields['password2'].help_text = 'Digite a mesma senha para confirmação'
        self.fields['telefone'].help_text = 'Formato: +258 82 123 4567'
    
    def clean_email(self):
        """
        Valida se email é único.
        """
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('Já existe um utilizador com este email.')
        return email
    
    def clean_telefone(self):
        """
        Valida formato do telefone.
        """
        telefone = self.cleaned_data.get('telefone')
        if telefone:
            # Validar formato moçambicano
            import re
            pattern = r'^\+?258\s?\d{2}\s?\d{3}\s?\d{3}$'
            if not re.match(pattern, telefone.replace(' ', '')):
                raise ValidationError('Formato de telefone inválido. Use: +258 82 123 4567')
        return telefone


class UserLoginForm(forms.Form):
    """
    Form de login de utilizador (simplificado, sem AuthenticationForm).
    """
    
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu.email@exemplo.com',
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sua senha',
            'autocomplete': 'current-password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label="Lembrar-me"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Email"
        self.fields['password'].label = "Senha"


class PerfilUtilizadorForm(forms.ModelForm):
    """
    Form para editar perfil do utilizador.
    """
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'telefone', 'cargo',
            'data_nascimento', 'genero', 'endereco', 'codigo_postal',
            'cidade', 'pais', 'biografia', 'avatar'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu nome'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu sobrenome'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'seu.email@exemplo.com'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+258 82 123 4567'
            }),
            'cargo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu cargo na empresa'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'genero': forms.Select(attrs={
                'class': 'form-select'
            }),
            'endereco': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'codigo_postal': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'pais': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'biografia': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Conte um pouco sobre você...'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adicionar help text
        self.fields['email'].help_text = 'Email único para login'
        self.fields['telefone'].help_text = 'Formato: +258 82 123 4567'
        self.fields['avatar'].help_text = 'Imagem JPG, PNG ou GIF (máx. 2MB)'
        self.fields['data_nascimento'].help_text = 'Data de nascimento (opcional)'
    
    def clean_email(self):
        """
        Valida se email é único (exceto para o próprio utilizador).
        """
        email = self.cleaned_data.get('email')
        if email and self.instance.pk:
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Já existe um utilizador com este email.')
        return email


class PerfilConfiguracoesForm(forms.ModelForm):
    """
    Form para configurações do perfil.
    """
    
    class Meta:
        model = PerfilUtilizador
        fields = [
            'receber_notificacoes_email', 'receber_notificacoes_push',
            'receber_newsletter', 'tema_preferido', 'idioma_preferido',
            'timezone', 'perfil_publico', 'mostrar_email', 'mostrar_telefone',
            'horario_trabalho_inicio', 'horario_trabalho_fim', 'dias_trabalho'
        ]
        widgets = {
            'tema_preferido': forms.Select(attrs={
                'class': 'form-select'
            }),
            'idioma_preferido': forms.Select(attrs={
                'class': 'form-select'
            }),
            'timezone': forms.Select(attrs={
                'class': 'form-select'
            }),
            'horario_trabalho_inicio': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'horario_trabalho_fim': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'dias_trabalho': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1,2,3,4,5 (Segunda a Sexta)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adicionar help text
        self.fields['dias_trabalho'].help_text = 'Dias da semana separados por vírgula (1=Segunda, 7=Domingo)'
        self.fields['timezone'].help_text = 'Fuso horário para exibição de datas'


class CriarUtilizadorForm(FileUploadMixin, forms.ModelForm):
    """
    Form para criar novo utilizador interno (APENAS ADMINISTRADORES).
    Utilizadores externos devem usar o portal público.
    """
    
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha temporária'
        })
    )
    password2 = forms.CharField(
        label="Confirmar Senha",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a senha'
        })
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'telefone', 'sector_atual',
            'cargo', 'tipo_utilizador', 'ativo', 'data_nascimento',
            'genero', 'endereco', 'codigo_postal', 'cidade', 'pais'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sobrenome'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+258 82 123 4567'
            }),
            'sector_atual': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cargo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cargo'
            }),
            'tipo_utilizador': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'genero': forms.Select(attrs={
                'class': 'form-select'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
    
    def clean_password2(self):
        """
        Valida se as senhas coincidem.
        """
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('As senhas não coincidem.')
        return password2
    
    def clean_tipo_utilizador(self):
        """
        Valida que apenas administradores podem criar utilizadores internos.
        """
        tipo_utilizador = self.cleaned_data.get('tipo_utilizador')
        
        # Verificar se o utilizador atual é administrador
        if self.request and self.request.user.is_authenticated:
            if not (self.request.user.is_superuser or self.request.user.tipo_utilizador == 'admin'):
                raise ValidationError("Apenas administradores podem criar utilizadores internos.")
        
        # Não permitir criação de externos via admin (devem usar portal público)
        if tipo_utilizador == 'externo':
            raise ValidationError("Utilizadores externos devem registar-se através do portal público.")
        
        return tipo_utilizador
    
    def save(self, commit=True):
        """
        Salva o utilizador com senha.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.username = user.email  # Usar email como username
        if commit:
            user.save()
        return user


class PasswordChangeFormCustomizada(PasswordChangeForm):
    """
    Form customizado para alteração de senha.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplicar classes Bootstrap
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control'
            })


class PasswordResetFormCustomizada(PasswordResetForm):
    """
    Form customizado para reset de senha.
    """
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu.email@exemplo.com'
        })
    )


class SetPasswordFormCustomizada(SetPasswordForm):
    """
    Form customizado para definir nova senha.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplicar classes Bootstrap
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control'
            })


class EditarUtilizadorForm(forms.ModelForm):
    """
    Form para editar utilizador existente (APENAS ADMINISTRADORES).
    Não inclui campos de senha.
    """
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'telefone', 'sector_atual',
            'cargo', 'tipo_utilizador', 'ativo', 'data_nascimento',
            'genero', 'endereco', 'codigo_postal', 'cidade', 'pais'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sobrenome'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+258 82 123 4567'
            }),
            'sector_atual': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cargo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cargo'
            }),
            'tipo_utilizador': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'genero': forms.Select(attrs={
                'class': 'form-select'
            }),
            'endereco': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Endereço completo'
            }),
            'codigo_postal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código postal'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade'
            }),
            'pais': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'País'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
    
    def clean_email(self):
        """
        Valida se email é único (exceto para o próprio utilizador).
        """
        email = self.cleaned_data.get('email')
        if email and self.instance.pk:
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Já existe um utilizador com este email.')
        return email
    
    def clean_tipo_utilizador(self):
        """
        Valida que apenas administradores podem editar utilizadores internos.
        """
        tipo_utilizador = self.cleaned_data.get('tipo_utilizador')
        
        # Verificar se o utilizador atual é administrador
        if self.request and self.request.user.is_authenticated:
            if not (self.request.user.is_superuser or self.request.user.tipo_utilizador == 'admin'):
                raise ValidationError("Apenas administradores podem editar utilizadores internos.")
        
        return tipo_utilizador


class HierarquiaUtilizadorForm(forms.ModelForm):
    """
    Form para gestão de hierarquia de utilizadores.
    """
    
    class Meta:
        model = HierarquiaUtilizador
        fields = ['superior', 'subordinado', 'tipo_relacao', 'observacoes']
        widgets = {
            'superior': forms.Select(attrs={
                'class': 'form-select'
            }),
            'subordinado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo_relacao': forms.Select(attrs={
                'class': 'form-select'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre a relação hierárquica...'
            })
        }
    
    def clean(self):
        """
        Valida se superior e subordinado são diferentes.
        """
        cleaned_data = super().clean()
        superior = cleaned_data.get('superior')
        subordinado = cleaned_data.get('subordinado')
        
        if superior and subordinado and superior == subordinado:
            raise ValidationError('O superior e subordinado devem ser diferentes.')
        
        return cleaned_data
