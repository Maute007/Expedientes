from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from .models import ConfiguracaoRelatorio, ExecucaoRelatorio, Dashboard
from core.models import Sector, EstadoDocumento
from entrada.models import Expediente


@login_required
def dashboard_administrador(request):
    """
    Dashboard específico para administradores.
    """
    # Estatísticas globais do sistema
    total_documentos = Expediente.objects.filter(ativo=True).count()
    total_sectores = Sector.objects.filter(ativo=True).count()
    total_utilizadores = request.user._meta.model.objects.filter(is_active=True).count()
    
    # Documentos por estado
    documentos_estado = Expediente.objects.filter(ativo=True).values(
        'estado_atual__nome'
    ).annotate(
        total=Count('id')
    ).order_by('-total')
    
    # Documentos por sector
    documentos_sector = Expediente.objects.filter(ativo=True).values(
        'sector_responsavel__nome'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    # Performance por sector
    performance_sector = []
    for sector in Sector.objects.filter(ativo=True):
        total = Expediente.objects.filter(sector_responsavel=sector, ativo=True).count()
        concluidos = Expediente.objects.filter(
            sector_responsavel=sector, 
            ativo=True,
            estado_atual__nome='Concluído'
        ).count()
        
        taxa = (concluidos / total * 100) if total > 0 else 0
        
        performance_sector.append({
            'sector': sector.nome,
            'total': total,
            'concluidos': concluidos,
            'taxa': taxa
        })
    
    # Documentos recentes
    documentos_recentes = Expediente.objects.filter(ativo=True).select_related(
        'tipo', 'estado_atual', 'sector_responsavel'
    ).order_by('-data_criacao')[:10]
    
    # Relatórios mais executados
    relatorios_populares = ConfiguracaoRelatorio.objects.filter(
        ativo=True
    ).annotate(
        total_execucoes=Count('execucoes')
    ).order_by('-total_execucoes')[:5]
    
    context = {
        'titulo': 'Dashboard Administrador',
        'total_documentos': total_documentos,
        'total_sectores': total_sectores,
        'total_utilizadores': total_utilizadores,
        'documentos_estado': list(documentos_estado),
        'documentos_sector': list(documentos_sector),
        'performance_sector': performance_sector,
        'documentos_recentes': documentos_recentes,
        'relatorios_populares': relatorios_populares,
    }
    
    return render(request, 'relatorios/dashboard_administrador.html', context)


@login_required
def dashboard_pca_ca(request):
    """
    Dashboard específico para PCA/CA.
    """
    # Documentos pendentes de aprovação
    documentos_pendentes = Expediente.objects.filter(
        ativo=True,
        estado_atual__nome__in=['Recebido', 'Encaminhado', 'Em Tratamento']
    ).select_related('tipo', 'sector_responsavel').order_by('-data_criacao')
    
    # Documentos por sector
    documentos_sector = Expediente.objects.filter(ativo=True).values(
        'sector_responsavel__nome'
    ).annotate(
        total=Count('id')
    ).order_by('-total')
    
    # Tempo médio de resposta por sector
    tempo_resposta = []
    for sector in Sector.objects.filter(ativo=True):
        documentos = Expediente.objects.filter(
            sector_responsavel=sector, 
            ativo=True,
            estado_atual__nome='Concluído'
        )
        
        if documentos.exists():
            # Calcular tempo médio (simplificado)
            tempo_medio = 5  # dias (exemplo)
            tempo_resposta.append({
                'sector': sector.nome,
                'tempo_medio': tempo_medio,
                'documentos': documentos.count()
            })
    
    # Documentos em atraso (mais de 30 dias)
    data_limite = timezone.now().date() - timedelta(days=30)
    documentos_atraso = Expediente.objects.filter(
        ativo=True,
        data_criacao__date__lt=data_limite,
        estado_atual__nome__in=['Recebido', 'Encaminhado', 'Em Tratamento']
    ).count()
    
    # Documentos urgentes (mais de 15 dias)
    data_urgente = timezone.now().date() - timedelta(days=15)
    documentos_urgentes = Expediente.objects.filter(
        ativo=True,
        data_criacao__date__lt=data_urgente,
        estado_atual__nome__in=['Recebido', 'Encaminhado', 'Em Tratamento']
    ).count()
    
    context = {
        'titulo': 'Dashboard PCA/CA',
        'documentos_pendentes': documentos_pendentes,
        'documentos_sector': list(documentos_sector),
        'tempo_resposta': tempo_resposta,
        'documentos_atraso': documentos_atraso,
        'documentos_urgentes': documentos_urgentes,
    }
    
    return render(request, 'relatorios/dashboard_pca_ca.html', context)


@login_required
def dashboard_chefe_sector(request):
    """
    Dashboard específico para chefes de sector.
    """
    # Obter sector do utilizador
    sector_utilizador = getattr(request.user, 'sector_atual', None)
    
    if not sector_utilizador:
        messages.error(request, 'Utilizador não possui sector associado.')
        return redirect('relatorios:dashboard')
    
    # Documentos do sector
    documentos_sector = Expediente.objects.filter(
        sector_responsavel=sector_utilizador,
        ativo=True
    ).select_related('tipo', 'estado_atual')
    
    # Documentos por estado no sector
    documentos_estado = documentos_sector.values(
        'estado_atual__nome'
    ).annotate(
        total=Count('id')
    ).order_by('-total')
    
    # Colaboradores do sector
    colaboradores = request.user._meta.model.objects.filter(
        sector_atual=sector_utilizador,
        is_active=True
    )
    
    # Documentos recentes do sector
    documentos_recentes = documentos_sector.order_by('-data_criacao')[:10]
    
    # Performance do sector
    total_documentos = documentos_sector.count()
    documentos_concluidos = documentos_sector.filter(
        estado_atual__nome='Concluído'
    ).count()
    
    taxa_conclusao = (documentos_concluidos / total_documentos * 100) if total_documentos > 0 else 0
    
    # Documentos pendentes no sector
    documentos_pendentes = documentos_sector.filter(
        estado_atual__nome__in=['Recebido', 'Encaminhado', 'Em Tratamento']
    ).count()
    
    context = {
        'titulo': f'Dashboard - {sector_utilizador.nome}',
        'sector': sector_utilizador,
        'documentos_sector': documentos_sector,
        'documentos_estado': list(documentos_estado),
        'colaboradores': colaboradores,
        'documentos_recentes': documentos_recentes,
        'total_documentos': total_documentos,
        'documentos_concluidos': documentos_concluidos,
        'taxa_conclusao': taxa_conclusao,
        'documentos_pendentes': documentos_pendentes,
    }
    
    return render(request, 'relatorios/dashboard_chefe_sector.html', context)


@login_required
def dashboard_colaborador(request):
    """
    Dashboard específico para colaboradores.
    """
    # Tarefas atribuídas ao utilizador
    tarefas_atribuidas = Expediente.objects.filter(
        utilizador_atual=request.user,
        ativo=True
    ).select_related('tipo', 'estado_atual', 'sector_responsavel').order_by('-data_criacao')
    
    # Documentos em análise pelo utilizador
    documentos_analise = tarefas_atribuidas.filter(
        estado_atual__nome__in=['Em Tratamento', 'Em Análise']
    )
    
    # Documentos concluídos pelo utilizador
    documentos_concluidos = Expediente.objects.filter(
        utilizador_atual=request.user,
        ativo=True,
        estado_atual__nome='Concluído'
    ).order_by('-data_criacao')[:10]
    
    # Estatísticas pessoais
    total_tarefas = tarefas_atribuidas.count()
    tarefas_pendentes = documentos_analise.count()
    tarefas_concluidas = documentos_concluidos.count()
    
    # Tempo médio de conclusão (simplificado)
    tempo_medio_conclusao = 3  # dias (exemplo)
    
    # Documentos urgentes (mais de 7 dias)
    data_urgente = timezone.now().date() - timedelta(days=7)
    documentos_urgentes = documentos_analise.filter(
        data_criacao__date__lt=data_urgente
    ).count()
    
    context = {
        'titulo': 'Meu Dashboard',
        'tarefas_atribuidas': tarefas_atribuidas,
        'documentos_analise': documentos_analise,
        'documentos_concluidos': documentos_concluidos,
        'total_tarefas': total_tarefas,
        'tarefas_pendentes': tarefas_pendentes,
        'tarefas_concluidas': tarefas_concluidas,
        'tempo_medio_conclusao': tempo_medio_conclusao,
        'documentos_urgentes': documentos_urgentes,
    }
    
    return render(request, 'relatorios/dashboard_colaborador.html', context)
