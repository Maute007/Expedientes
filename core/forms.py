from django import forms
from django.core.exceptions import ValidationError
from .models import ConfiguracaoSistema, Sector


class BaseForm(forms.Form):
    """
    Form base com estilos comuns para todo o sistema.
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
            elif isinstance(field.widget, forms.DateTimeInput):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'type': 'datetime-local'
                })
            elif isinstance(field.widget, forms.TimeInput):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'type': 'time'
                })
            elif isinstance(field.widget, forms.NumberInput):
                field.widget.attrs.update({
                    'class': 'form-control'
                })
            elif isinstance(field.widget, forms.EmailInput):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'type': 'email'
                })
            elif isinstance(field.widget, forms.URLInput):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'type': 'url'
                })
            elif isinstance(field.widget, forms.PasswordInput):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'type': 'password'
                })
    
    def add_error_class(self, field_name, error_class='is-invalid'):
        """
        Adiciona classe de erro a um campo específico.
        """
        if field_name in self.fields:
            current_class = self.fields[field_name].widget.attrs.get('class', '')
            if error_class not in current_class:
                self.fields[field_name].widget.attrs['class'] = f"{current_class} {error_class}".strip()
    
    def remove_error_class(self, field_name, error_class='is-invalid'):
        """
        Remove classe de erro de um campo específico.
        """
        if field_name in self.fields:
            current_class = self.fields[field_name].widget.attrs.get('class', '')
            self.fields[field_name].widget.attrs['class'] = current_class.replace(error_class, '').strip()
    
    def clean(self):
        """
        Validação geral do form.
        """
        cleaned_data = super().clean()
        
        # Adicionar validações comuns aqui se necessário
        return cleaned_data


class ConfiguracaoSistemaForm(forms.ModelForm):
    """
    Form para configurações do sistema.
    """
    
    class Meta:
        model = ConfiguracaoSistema
        fields = ['chave', 'valor', 'descricao', 'tipo']
        widgets = {
            'chave': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: max_upload_size',
                'maxlength': 100
            }),
            'valor': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Valor da configuração'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Descrição da configuração'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adicionar help text
        self.fields['chave'].help_text = 'Chave única para identificar a configuração (ex: max_upload_size)'
        self.fields['valor'].help_text = 'Valor da configuração (será convertido conforme o tipo)'
        self.fields['descricao'].help_text = 'Descrição opcional da configuração'
        self.fields['tipo'].help_text = 'Tipo de dados para conversão do valor'
    
    def clean_chave(self):
        """
        Valida se a chave é única e tem formato válido.
        """
        chave = self.cleaned_data.get('chave')
        
        if chave:
            # Verificar se contém apenas caracteres válidos
            import re
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', chave):
                raise ValidationError(
                    'A chave deve começar com letra ou underscore e conter apenas letras, números e underscores.'
                )
            
            # Verificar se já existe (exceto se estiver editando o mesmo objeto)
            queryset = ConfiguracaoSistema.objects.filter(chave=chave)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise ValidationError('Já existe uma configuração com esta chave.')
        
        return chave
    
    def clean_valor(self):
        """
        Valida o valor baseado no tipo selecionado.
        """
        valor = self.cleaned_data.get('valor')
        tipo = self.cleaned_data.get('tipo')
        
        if valor and tipo:
            try:
                if tipo == 'int':
                    int(valor)
                elif tipo == 'bool':
                    if valor.lower() not in ('true', 'false', '1', '0', 'yes', 'no', 'sim', 'não'):
                        raise ValidationError('Para tipo booleano, use: true/false, 1/0, yes/no, sim/não')
                elif tipo == 'json':
                    import json
                    json.loads(valor)
            except (ValueError, json.JSONDecodeError) as e:
                raise ValidationError(f'Valor inválido para tipo {tipo}: {str(e)}')
        
        return valor
    
    def clean(self):
        """
        Validação cruzada entre campos.
        """
        cleaned_data = super().clean()
        chave = cleaned_data.get('chave')
        valor = cleaned_data.get('valor')
        tipo = cleaned_data.get('tipo')
        
        # Se tipo é 'json', valor deve ser JSON válido
        if tipo == 'json' and valor:
            try:
                import json
                json.loads(valor)
            except json.JSONDecodeError:
                self.add_error('valor', 'Valor deve ser um JSON válido para tipo JSON.')
        
        return cleaned_data


class SectorForm(forms.ModelForm):
    """
    Form para gestão de sectores seguindo o layout de formulário fornecido.
    """
    
    class Meta:
        model = Sector
        fields = ['nome', 'descricao', 'chefe', 'chefe_substituto', 'ativo', 'observacoes']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do sector (ex: Secretaria, Gabinete do PCA)',
                'maxlength': 100
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrição detalhada do sector e suas responsabilidades'
            }),
            'chefe': forms.Select(attrs={
                'class': 'form-select'
            }),
            'chefe_substituto': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais sobre o sector'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adicionar help text
        self.fields['nome'].help_text = 'Nome único do sector (obrigatório)'
        self.fields['descricao'].help_text = 'Descrição detalhada das responsabilidades do sector'
        self.fields['chefe'].help_text = 'Utilizador responsável pelo sector (obrigatório)'
        self.fields['chefe_substituto'].help_text = 'Utilizador que substitui o chefe em ausências (opcional)'
        self.fields['ativo'].help_text = 'Sector ativo pode receber documentos'
        self.fields['observacoes'].help_text = 'Informações adicionais sobre o sector'
        
        # Filtrar utilizadores ativos para chefes
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.fields['chefe'].queryset = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
        self.fields['chefe_substituto'].queryset = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
    
    def clean_nome(self):
        """
        Valida se o nome é único.
        """
        nome = self.cleaned_data.get('nome')
        
        if nome:
            # Verificar se já existe (exceto se estiver editando o mesmo objeto)
            queryset = Sector.objects.filter(nome=nome)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise ValidationError('Já existe um sector com este nome.')
        
        return nome
    
    def clean_chefe_substituto(self):
        """
        Valida se o chefe substituto é diferente do chefe.
        """
        chefe = self.cleaned_data.get('chefe')
        chefe_substituto = self.cleaned_data.get('chefe_substituto')
        
        if chefe and chefe_substituto and chefe == chefe_substituto:
            raise ValidationError('O chefe substituto deve ser diferente do chefe principal.')
        
        return chefe_substituto
    
    def clean(self):
        """
        Validação cruzada entre campos.
        """
        cleaned_data = super().clean()
        chefe = cleaned_data.get('chefe')
        chefe_substituto = cleaned_data.get('chefe_substituto')
        
        # Se chefe substituto está definido, deve ser diferente do chefe
        if chefe and chefe_substituto and chefe == chefe_substituto:
            self.add_error('chefe_substituto', 'O chefe substituto deve ser diferente do chefe principal.')
        
        return cleaned_data
