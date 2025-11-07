from django import forms
from django.core.exceptions import ValidationError
from .models import AssinaturaDocumento, AssinaturaUtilizador


class AssinaturaCanvasForm(forms.Form):
    """
    Form para capturar assinatura do canvas
    """
    signature_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=True,
        help_text="Dados da assinatura em base64"
    )
    
    def clean_signature_data(self):
        data = self.cleaned_data.get('signature_data')
        if not data:
            raise ValidationError("Assinatura é obrigatória.")
        
        # Verificar se é base64 válido
        if not data.startswith('data:image'):
            raise ValidationError("Formato de assinatura inválido.")
        
        return data


class PosicionamentoAssinaturaForm(forms.ModelForm):
    """
    Form para posicionar assinatura no documento
    """
    class Meta:
        model = AssinaturaDocumento
        fields = ['posicao_x', 'posicao_y', 'pagina', 'observacoes']
        widgets = {
            'posicao_x': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'required': True
            }),
            'posicao_y': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'required': True
            }),
            'pagina': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 1,
                'required': True
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre a assinatura (opcional)'
            }),
        }
    
    def clean_pagina(self):
        pagina = self.cleaned_data.get('pagina')
        if pagina < 1:
            raise ValidationError("A página deve ser maior ou igual a 1.")
        return pagina


class SalvarAssinaturaPadraoForm(forms.ModelForm):
    """
    Form para salvar assinatura padrão do utilizador
    """
    signature_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=True,
        help_text="Dados da assinatura em base64"
    )
    
    class Meta:
        model = AssinaturaUtilizador
        fields = ['assinatura_imagem']
        widgets = {
            'assinatura_imagem': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def clean_signature_data(self):
        data = self.cleaned_data.get('signature_data')
        if not data:
            raise ValidationError("Assinatura é obrigatória.")
        
        if not data.startswith('data:image'):
            raise ValidationError("Formato de assinatura inválido.")
        
        return data


class ConfirmarAssinaturaForm(forms.Form):
    """
    Form para confirmar assinatura antes de aplicar no documento
    """
    posicao_x = forms.FloatField(
        required=True,
        widget=forms.HiddenInput()
    )
    posicao_y = forms.FloatField(
        required=True,
        widget=forms.HiddenInput()
    )
    pagina = forms.IntegerField(
        required=True,
        min_value=1,
        widget=forms.HiddenInput()
    )
    signature_data = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    observacoes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Observações sobre a assinatura (opcional)'
        })
    )
    usar_assinatura_padrao = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput()
    )

