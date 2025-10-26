from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from .models import ConfiguracaoSistema


def validate_file_size(file: UploadedFile) -> None:
    """
    Valida o tamanho do arquivo baseado na configuração do sistema.
    
    Args:
        file: Arquivo enviado
        
    Raises:
        ValidationError: Se o arquivo exceder o tamanho máximo
    """
    try:
        # Obter tamanho máximo configurado (em MB)
        tamanho_maximo_mb = ConfiguracaoSistema.obter_configuracao(
            'tamanho_maximo_arquivo', 
            valor_padrao=10
        )
        
        # Converter para bytes
        tamanho_maximo_bytes = tamanho_maximo_mb * 1024 * 1024
        
        # Verificar tamanho do arquivo
        if file.size > tamanho_maximo_bytes:
            raise ValidationError(
                f'O arquivo excede o tamanho máximo permitido de {tamanho_maximo_mb}MB. '
                f'Tamanho atual: {file.size / (1024 * 1024):.2f}MB'
            )
            
    except Exception as e:
        # Em caso de erro ao obter configuração, usar valor padrão
        tamanho_maximo_bytes = 10 * 1024 * 1024  # 10MB padrão
        
        if file.size > tamanho_maximo_bytes:
            raise ValidationError(
                f'O arquivo excede o tamanho máximo permitido de 10MB. '
                f'Tamanho atual: {file.size / (1024 * 1024):.2f}MB'
            )


def get_max_file_size_mb() -> int:
    """
    Retorna o tamanho máximo de arquivo configurado em MB.
    
    Returns:
        int: Tamanho máximo em MB
    """
    return ConfiguracaoSistema.obter_configuracao(
        'tamanho_maximo_arquivo', 
        valor_padrao=10
    )


def get_max_file_size_bytes() -> int:
    """
    Retorna o tamanho máximo de arquivo configurado em bytes.
    
    Returns:
        int: Tamanho máximo em bytes
    """
    return get_max_file_size_mb() * 1024 * 1024
