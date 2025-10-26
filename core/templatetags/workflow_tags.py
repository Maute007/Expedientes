from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    """
    Template filter para acessar valor de dicionário por chave.
    Uso: {{ cores_estados|get:expediente.estado_atual.nome }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)
