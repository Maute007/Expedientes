from django import forms
from django.core.exceptions import ValidationError
from .upload_validators import validate_file_size, get_max_file_size_mb


class FileUploadMixin:
    """
    Mixin para formulários que fazem upload de arquivos.
    Aplica validação de tamanho baseada nas configurações do sistema.
    """
    
    def clean(self):
        """
        Valida arquivos enviados baseado nas configurações do sistema.
        """
        cleaned_data = super().clean()
        
        # Verificar todos os campos de arquivo
        for field_name, field in self.fields.items():
            if isinstance(field, forms.FileField):
                file = self.cleaned_data.get(field_name)
                if file and hasattr(file, 'size'):
                    try:
                        validate_file_size(file)
                    except ValidationError as e:
                        self.add_error(field_name, e)
        
        return cleaned_data
    
    def get_max_file_size_mb(self):
        """
        Retorna o tamanho máximo de arquivo em MB para uso nos templates.
        """
        return get_max_file_size_mb()
    
    def get_max_file_size_display(self):
        """
        Retorna o tamanho máximo formatado para exibição.
        """
        size_mb = self.get_max_file_size_mb()
        if size_mb >= 1024:
            return f"{size_mb / 1024:.1f}GB"
        return f"{size_mb}MB"
