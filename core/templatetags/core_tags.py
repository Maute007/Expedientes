from django import template
from django.utils.safestring import mark_safe
from django.utils import timezone
from datetime import timedelta
from core.models import EstadoDocumento, Notificacao
from core.utils import ICONES_NOTIFICACAO

register = template.Library()


@register.simple_tag
def estado_badge(estado, tamanho='sm'):
    """
    Renderiza um badge com o estado do documento e sua cor.
    
    Args:
        estado: EstadoDocumento ou string com nome do estado
        tamanho: tamanho do badge ('sm', 'md', 'lg')
    
    Returns:
        HTML do badge Bootstrap
    """
    if isinstance(estado, str):
        try:
            estado_obj = EstadoDocumento.objects.get(nome=estado)
        except EstadoDocumento.DoesNotExist:
            return mark_safe('<span class="badge bg-secondary">Estado não encontrado</span>')
    else:
        estado_obj = estado
    
    if not estado_obj:
        return mark_safe('<span class="badge bg-secondary">Sem estado</span>')
    
    tamanho_class = f'badge-{tamanho}' if tamanho != 'sm' else ''
    
    badge_html = f'''
    <span class="badge {tamanho_class}" style="background-color: {estado_obj.cor}; color: white;">
        {estado_obj.nome}
    </span>
    '''
    
    return mark_safe(badge_html)


@register.simple_tag
def estado_cor(estado):
    """
    Retorna apenas a cor do estado.
    
    Args:
        estado: EstadoDocumento ou string com nome do estado
    
    Returns:
        String com a cor hex
    """
    if isinstance(estado, str):
        try:
            estado_obj = EstadoDocumento.objects.get(nome=estado)
        except EstadoDocumento.DoesNotExist:
            return '#6c757d'  # Cor padrão
    else:
        estado_obj = estado
    
    if not estado_obj:
        return '#6c757d'
    
    return estado_obj.cor


@register.simple_tag
def progresso_workflow(documento):
    """
    Renderiza uma barra de progresso do workflow do documento.
    
    Args:
        documento: Documento com campo estado_atual
    
    Returns:
        HTML da barra de progresso Bootstrap
    """
    if not documento or not hasattr(documento, 'estado_atual'):
        return mark_safe('<div class="progress"><div class="progress-bar" style="width: 0%"></div></div>')
    
    estado_atual = documento.estado_atual
    if not estado_atual:
        return mark_safe('<div class="progress"><div class="progress-bar" style="width: 0%"></div></div>')
    
    # Obter todos os estados ordenados
    estados = EstadoDocumento.objects.filter(ativo=True).order_by('ordem')
    total_estados = estados.count()
    
    if total_estados == 0:
        return mark_safe('<div class="progress"><div class="progress-bar" style="width: 0%"></div></div>')
    
    # Calcular progresso baseado na ordem do estado atual
    progresso = (estado_atual.ordem / total_estados) * 100
    
    progress_html = f'''
    <div class="progress" style="height: 8px;">
        <div class="progress-bar" 
             role="progressbar" 
             style="width: {progresso:.1f}%; background-color: {estado_atual.cor};"
             aria-valuenow="{progresso:.1f}" 
             aria-valuemin="0" 
             aria-valuemax="100">
        </div>
    </div>
    <small class="text-muted">{estado_atual.nome} ({progresso:.1f}%)</small>
    '''
    
    return mark_safe(progress_html)


@register.simple_tag
def proximos_estados(documento):
    """
    Renderiza os próximos estados possíveis para um documento.
    
    Args:
        documento: Documento com campo estado_atual
    
    Returns:
        HTML com badges dos próximos estados
    """
    if not documento or not hasattr(documento, 'estado_atual'):
        return mark_safe('<span class="text-muted">Sem estado atual</span>')
    
    estado_atual = documento.estado_atual
    if not estado_atual:
        return mark_safe('<span class="text-muted">Sem estado atual</span>')
    
    proximos = estado_atual.obter_proximos_estados()
    
    if not proximos.exists():
        return mark_safe('<span class="text-muted">Nenhum próximo estado disponível</span>')
    
    badges_html = []
    for estado in proximos:
        badge_html = f'''
        <span class="badge bg-light text-dark me-1" 
              style="border: 1px solid {estado.cor}; color: {estado.cor};">
            {estado.nome}
        </span>
        '''
        badges_html.append(badge_html)
    
    return mark_safe(''.join(badges_html))


@register.simple_tag
def contador_notificacoes(user):
    """
    Renderiza um badge com o contador de notificações não lidas.
    
    Args:
        user: Utilizador autenticado
    
    Returns:
        HTML do badge com contador
    """
    if not user or not user.is_authenticated:
        return mark_safe('')
    
    try:
        total_nao_lidas = Notificacao.objects.filter(
            destinatario=user, 
            lida=False
        ).count()
        
        if total_nao_lidas == 0:
            return mark_safe('')
        
        badge_html = f'''
        <span class="position-relative">
            <i class="bi bi-bell fs-5"></i>
            <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                {total_nao_lidas}
                <span class="visually-hidden">notificações não lidas</span>
            </span>
        </span>
        '''
        
        return mark_safe(badge_html)
        
    except Exception:
        return mark_safe('')


@register.simple_tag
def lista_notificacoes_recentes(user, limite=5):
    """
    Renderiza uma lista das notificações recentes do utilizador.
    
    Args:
        user: Utilizador autenticado
        limite: número máximo de notificações a mostrar
    
    Returns:
        HTML da lista de notificações
    """
    if not user or not user.is_authenticated:
        return mark_safe('<p class="text-muted">Faça login para ver notificações</p>')
    
    try:
        notificacoes = Notificacao.objects.filter(
            destinatario=user
        ).order_by('-data_criacao')[:limite]
        
        if not notificacoes.exists():
            return mark_safe('<p class="text-muted">Nenhuma notificação</p>')
        
        lista_html = ['<div class="list-group list-group-flush">']
        
        for notificacao in notificacoes:
            classe_lida = '' if notificacao.lida else 'list-group-item-warning'
            icone = notificacao.obter_icone()
            urgente = 'text-danger' if notificacao.eh_urgente() else ''
            
            item_html = f'''
            <div class="list-group-item {classe_lida}">
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">
                        <i class="bi {icone} me-2"></i>
                        <span class="{urgente}">{notificacao.titulo}</span>
                    </h6>
                    <small>{notificacao.data_criacao|timesince} atrás</small>
                </div>
                <p class="mb-1">{notificacao.mensagem|truncatewords:15}</p>
            </div>
            '''
            lista_html.append(item_html)
        
        lista_html.append('</div>')
        
        return mark_safe(''.join(lista_html))
        
    except Exception:
        return mark_safe('<p class="text-danger">Erro ao carregar notificações</p>')


@register.simple_tag
def badge_notificacao(notificacao, tamanho='sm'):
    """
    Renderiza um badge para uma notificação específica.
    
    Args:
        notificacao: Objeto Notificacao
        tamanho: tamanho do badge ('sm', 'md', 'lg')
    
    Returns:
        HTML do badge
    """
    if not notificacao:
        return mark_safe('')
    
    icone = notificacao.obter_icone()
    cor_classe = 'bg-danger' if notificacao.eh_urgente() else 'bg-primary'
    tamanho_class = f'badge-{tamanho}' if tamanho != 'sm' else ''
    
    badge_html = f'''
    <span class="badge {cor_classe} {tamanho_class}">
        <i class="bi {icone} me-1"></i>
        {notificacao.get_tipo_display()}
    </span>
    '''
    
    return mark_safe(badge_html)


@register.simple_tag
def card_notificacao(notificacao, show_actions=True):
    """
    Renderiza um card completo para uma notificação.
    
    Args:
        notificacao: Objeto Notificacao
        show_actions: se deve mostrar botões de ação
    
    Returns:
        HTML do card Bootstrap
    """
    if not notificacao:
        return mark_safe('')
    
    icone = notificacao.obter_icone()
    classe_lida = 'border-light' if notificacao.lida else 'border-warning'
    urgente = 'text-danger' if notificacao.eh_urgente() else ''
    
    card_html = f'''
    <div class="card mb-3 {classe_lida}">
        <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <h6 class="card-title {urgente}">
                        <i class="bi {icone} me-2"></i>
                        {notificacao.titulo}
                    </h6>
                    <p class="card-text">{notificacao.mensagem}</p>
                    <small class="text-muted">
                        {notificacao.data_criacao|timesince} atrás
                        {badge_notificacao(notificacao)}
                    </small>
                </div>
    '''
    
    if show_actions and not notificacao.lida:
        card_html += f'''
                <div class="ms-3">
                    <button class="btn btn-sm btn-outline-success" 
                            onclick="marcarComoLida({notificacao.id})">
                        <i class="bi bi-check"></i>
                    </button>
                </div>
        '''
    
    card_html += '''
            </div>
        </div>
    </div>
    '''
    
    return mark_safe(card_html)


@register.simple_tag
def icone_notificacao(tipo):
    """
    Retorna o ícone Bootstrap para um tipo de notificação.
    
    Args:
        tipo: tipo da notificação
    
    Returns:
        String com a classe CSS do ícone
    """
    return ICONES_NOTIFICACAO.get(tipo, 'bi-bell')


@register.simple_tag
def cor_prioridade(prioridade):
    """
    Retorna a cor Bootstrap para uma prioridade.
    
    Args:
        prioridade: prioridade da notificação ('normal' ou 'urgente')
    
    Returns:
        String com a classe CSS da cor
    """
    cores = {
        'normal': 'text-primary',
        'urgente': 'text-danger'
    }
    return cores.get(prioridade, 'text-secondary')


@register.simple_tag
def status_utilizador(user):
    """
    Renderiza o status do utilizador (PCA, Chefe, Colaborador).
    
    Args:
        user: Utilizador
    
    Returns:
        HTML com badge do status
    """
    if not user or not user.is_authenticated:
        return mark_safe('')
    
    if hasattr(user, 'is_pca') and user.is_pca:
        return mark_safe('<span class="badge bg-danger">PCA</span>')
    
    if user.sector_atual and user.sector_atual.eh_chefe(user):
        return mark_safe('<span class="badge bg-warning text-dark">Chefe</span>')
    
    return mark_safe('<span class="badge bg-secondary">Colaborador</span>')


@register.simple_tag
def sector_badge(sector):
    """
    Renderiza um badge para um sector.
    
    Args:
        sector: Objeto Sector
    
    Returns:
        HTML do badge
    """
    if not sector:
        return mark_safe('<span class="badge bg-secondary">Sem sector</span>')
    
    badge_html = f'''
    <span class="badge bg-info text-dark">
        <i class="bi bi-building me-1"></i>
        {sector.nome}
    </span>
    '''
    
    return mark_safe(badge_html)


@register.filter
def tempo_pt(value):
    """
    Filtro para formatar tempo relativo em português.
    Mostra semanas, dias, horas e minutos quando aplicável.
    
    Args:
        value: datetime object
    
    Returns:
        string com tempo formatado em português
    """
    if not value:
        return ''
    
    now = timezone.now()
    if timezone.is_aware(value):
        diff = now - value
    else:
        diff = timezone.now() - timezone.make_aware(value)
    
    total_seconds = int(diff.total_seconds())
    
    if total_seconds < 60:
        if total_seconds < 1:
            return 'agora mesmo'
        return f'{total_seconds} segundo{"s" if total_seconds > 1 else ""}'
    
    # Calcular semanas, dias, horas e minutos
    semanas = total_seconds // 604800
    resto_apos_semanas = total_seconds % 604800
    
    dias = resto_apos_semanas // 86400
    resto_apos_dias = resto_apos_semanas % 86400
    
    horas = resto_apos_dias // 3600
    resto_apos_horas = resto_apos_dias % 3600
    
    minutos = resto_apos_horas // 60
    
    # Construir string com múltiplas unidades
    partes = []
    
    if semanas > 0:
        partes.append(f'{semanas} semana{"s" if semanas > 1 else ""}')
    
    if dias > 0:
        partes.append(f'{dias} dia{"s" if dias > 1 else ""}')
    
    # Mostrar horas se for menos de 4 semanas ou se não houver semanas
    if horas > 0 and (semanas == 0 or semanas < 4):
        partes.append(f'{horas} hora{"s" if horas > 1 else ""}')
    
    # Mostrar minutos se for menos de 1 semana ou se não houver semanas
    if minutos > 0 and semanas == 0:
        partes.append(f'{minutos} minuto{"s" if minutos > 1 else ""}')
    
    if not partes:
        return 'agora mesmo'
    
    # Juntar as partes com vírgulas e "e" antes da última
    if len(partes) == 1:
        return partes[0]
    elif len(partes) == 2:
        return f'{partes[0]} e {partes[1]}'
    else:
        return ', '.join(partes[:-1]) + f' e {partes[-1]}'
