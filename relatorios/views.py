from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
import json
import threading
from datetime import datetime, timedelta

from .models import (
    ConfiguracaoRelatorio, TipoRelatorio, ExecucaoRelatorio, 
    Dashboard, WidgetDashboard
)
from .forms import (
    RelatorioForm, ParametrosRelatorioForm, FiltrosRelatorioForm,
    DashboardForm, WidgetForm, ExecucaoRelatorioForm
)
from .utils import RelatorioGenerator, ChartGenerator
from core.models import Sector, EstadoDocumento
from entrada.models import Expediente

# Importar views dos dashboards por perfil
from .views_dashboards import (
    dashboard_administrador, dashboard_pca_ca, 
    dashboard_chefe_sector, dashboard_colaborador
)


@login_required
def dashboard_relatorios(request):
    """
    Dashboard principal de relatórios.
    """
    # Estatísticas gerais
    total_relatorios = ConfiguracaoRelatorio.objects.filter(ativo=True).count()
    total_execucoes = ExecucaoRelatorio.objects.count()
    execucoes_hoje = ExecucaoRelatorio.objects.filter(
        data_execucao__date=timezone.now().date()
    ).count()
    
    # Relatórios recentes
    relatorios_recentes = ConfiguracaoRelatorio.objects.filter(
        Q(publico=True) | Q(utilizador_criador=request.user),
        ativo=True
    ).order_by('-data_criacao')[:5]
    
    # Execuções recentes
    execucoes_recentes = ExecucaoRelatorio.objects.filter(
        utilizador=request.user
    ).order_by('-data_execucao')[:5]
    
    # Dashboards do utilizador
    dashboards = Dashboard.objects.filter(
        Q(publico=True) | Q(utilizador_criador=request.user),
        ativo=True
    ).order_by('-data_criacao')[:3]
    
    context = {
        'total_relatorios': total_relatorios,
        'total_execucoes': total_execucoes,
        'execucoes_hoje': execucoes_hoje,
        'relatorios_recentes': relatorios_recentes,
        'execucoes_recentes': execucoes_recentes,
        'dashboards': dashboards,
    }
    
    return render(request, 'relatorios/dashboard.html', context)


@login_required
def lista_relatorios(request):
    """
    Lista todos os relatórios disponíveis.
    """
    # Filtros
    search = request.GET.get('search', '')
    tipo = request.GET.get('tipo', '')
    sector = request.GET.get('sector', '')
    status = request.GET.get('status', '')
    
    # Query base
    queryset = ConfiguracaoRelatorio.objects.filter(
        Q(publico=True) | Q(utilizador_criador=request.user),
        ativo=True
    )
    
    # Aplicar filtros
    if search:
        queryset = queryset.filter(
            Q(nome__icontains=search) | 
            Q(descricao__icontains=search)
        )
    
    if tipo:
        queryset = queryset.filter(tipo_relatorio__tipo_relatorio=tipo)
    
    if sector:
        queryset = queryset.filter(sector=sector)
    
    if status == 'meus':
        queryset = queryset.filter(utilizador_criador=request.user)
    elif status == 'publicos':
        queryset = queryset.filter(publico=True)
    
    # Paginação
    paginator = Paginator(queryset.order_by('-data_criacao'), 12)
    page_number = request.GET.get('page')
    relatorios = paginator.get_page(page_number)
    
    # Filtros para o formulário
    tipos_relatorio = TipoRelatorio.objects.filter(ativo=True)
    sectores = Sector.objects.filter(ativo=True)
    
    context = {
        'relatorios': relatorios,
        'tipos_relatorio': tipos_relatorio,
        'sectores': sectores,
        'filtros': {
            'search': search,
            'tipo': tipo,
            'sector': sector,
            'status': status,
        }
    }
    
    return render(request, 'relatorios/relatorio_list.html', context)


@login_required
def detalhar_relatorio(request, pk):
    """
    Detalhes de um relatório específico.
    """
    relatorio = get_object_or_404(
        ConfiguracaoRelatorio,
        pk=pk
    )
    
    # Verificar permissões
    if not (relatorio.publico or relatorio.utilizador_criador == request.user):
        raise Http404("Relatório não encontrado.")
    
    # Execuções do relatório
    execucoes = relatorio.execucoes.filter(utilizador=request.user).order_by('-data_execucao')[:10]
    
    # Formulário para execução rápida
    form_execucao = ExecucaoRelatorioForm(relatorio)
    
    context = {
        'relatorio': relatorio,
        'execucoes': execucoes,
        'form_execucao': form_execucao,
    }
    
    return render(request, 'relatorios/relatorio_detail.html', context)


@login_required
def criar_relatorio(request):
    """
    Criação de novo relatório.
    """
    if request.method == 'POST':
        form = RelatorioForm(request.POST, user=request.user)
        if form.is_valid():
            relatorio = form.save()
            messages.success(request, f'Relatório "{relatorio.nome}" criado com sucesso!')
            return redirect('relatorios:detalhar_relatorio', pk=relatorio.pk)
    else:
        form = RelatorioForm(user=request.user)
    
    context = {
        'form': form,
        'titulo': 'Criar Novo Relatório'
    }
    
    return render(request, 'relatorios/relatorio_form.html', context)


@login_required
def editar_relatorio(request, pk):
    """
    Edição de relatório existente.
    """
    relatorio = get_object_or_404(
        ConfiguracaoRelatorio,
        pk=pk,
        utilizador_criador=request.user
    )
    
    if request.method == 'POST':
        form = RelatorioForm(request.POST, instance=relatorio, user=request.user)
        if form.is_valid():
            relatorio = form.save()
            messages.success(request, f'Relatório "{relatorio.nome}" atualizado com sucesso!')
            return redirect('relatorios:detalhar_relatorio', pk=relatorio.pk)
    else:
        form = RelatorioForm(instance=relatorio, user=request.user)
    
    context = {
        'form': form,
        'relatorio': relatorio,
        'titulo': f'Editar Relatório: {relatorio.nome}'
    }
    
    return render(request, 'relatorios/relatorio_form.html', context)


@login_required
def executar_relatorio(request, pk):
    """
    Execução de um relatório.
    """
    relatorio = get_object_or_404(
        ConfiguracaoRelatorio,
        pk=pk
    )
    
    # Verificar permissões
    if not (relatorio.publico or relatorio.utilizador_criador == request.user):
        raise Http404("Relatório não encontrado.")
    
    if request.method == 'POST':
        form = ExecucaoRelatorioForm(relatorio, request.POST)
        if form.is_valid():
            # Criar execução
            execucao = relatorio.execute(request.user)
            
            # Atualizar parâmetros se fornecidos
            parametros_atualizados = {}
            for field_name, value in form.cleaned_data.items():
                if field_name.startswith('param_'):
                    param_name = field_name.replace('param_', '')
                    parametros_atualizados[param_name] = value
            
            if parametros_atualizados:
                execucao.parametros_utilizados.update(parametros_atualizados)
                execucao.save(update_fields=['parametros_utilizados'])
            
            # Executar em background
            def executar_background():
                generator = RelatorioGenerator(execucao)
                generator.gerar_relatorio()
            
            thread = threading.Thread(target=executar_background)
            thread.start()
            
            messages.success(request, 'Relatório em execução! Você será notificado quando estiver pronto.')
            return redirect('relatorios:detalhar_relatorio', pk=relatorio.pk)
    else:
        form = ExecucaoRelatorioForm(relatorio)
    
    context = {
        'relatorio': relatorio,
        'form': form,
    }
    
    return render(request, 'relatorios/relatorio_execute.html', context)


@login_required
def download_relatorio(request, pk):
    """
    Download de relatório executado.
    """
    execucao = get_object_or_404(
        ExecucaoRelatorio,
        pk=pk,
        utilizador=request.user,
        status='concluido'
    )
    
    if not execucao.ficheiro_gerado:
        raise Http404("Ficheiro não encontrado.")
    
    response = HttpResponse(
        execucao.ficheiro_gerado.read(),
        content_type='application/octet-stream'
    )
    response['Content-Disposition'] = f'attachment; filename="{execucao.ficheiro_gerado.name}"'
    
    return response


@login_required
def lista_dashboards(request):
    """
    Lista todos os dashboards disponíveis.
    """
    # Filtros
    search = request.GET.get('search', '')
    sector = request.GET.get('sector', '')
    status = request.GET.get('status', '')
    
    # Query base
    queryset = Dashboard.objects.filter(
        Q(publico=True) | Q(utilizador_criador=request.user),
        ativo=True
    )
    
    # Aplicar filtros
    if search:
        queryset = queryset.filter(
            Q(nome__icontains=search) | 
            Q(descricao__icontains=search)
        )
    
    if sector:
        queryset = queryset.filter(sector=sector)
    
    if status == 'meus':
        queryset = queryset.filter(utilizador_criador=request.user)
    elif status == 'publicos':
        queryset = queryset.filter(publico=True)
    
    # Paginação
    paginator = Paginator(queryset.order_by('-data_criacao'), 12)
    page_number = request.GET.get('page')
    dashboards = paginator.get_page(page_number)
    
    # Filtros para o formulário
    sectores = Sector.objects.filter(ativo=True)
    
    context = {
        'dashboards': dashboards,
        'sectores': sectores,
        'filtros': {
            'search': search,
            'sector': sector,
            'status': status,
        }
    }
    
    return render(request, 'relatorios/dashboard_list.html', context)


@login_required
def visualizar_dashboard(request, pk):
    """
    Visualização de um dashboard específico.
    """
    dashboard = get_object_or_404(
        Dashboard,
        pk=pk
    )
    
    # Verificar permissões
    if not (dashboard.publico or dashboard.utilizador_criador == request.user):
        raise Http404("Dashboard não encontrado.")
    
    # Renderizar widgets
    widgets_data = []
    for widget_config in dashboard.widgets:
        widget_data = {
            'id': widget_config.get('id'),
            'tipo': widget_config.get('tipo'),
            'titulo': widget_config.get('titulo'),
            'parametros': widget_config.get('parametros', {}),
            'posicao': widget_config.get('posicao', {}),
            'tamanho': widget_config.get('tamanho', {})
        }
        
        # Obter dados do widget
        dados = _obter_dados_widget(widget_data, request.user)
        widget_data['dados'] = dados
        
        widgets_data.append(widget_data)
    
    context = {
        'dashboard': dashboard,
        'widgets': widgets_data,
    }
    
    return render(request, 'relatorios/dashboard_view.html', context)


@login_required
def criar_dashboard(request):
    """
    Criação de novo dashboard.
    """
    if request.method == 'POST':
        form = DashboardForm(request.POST, user=request.user)
        if form.is_valid():
            dashboard = form.save()
            messages.success(request, f'Dashboard "{dashboard.nome}" criado com sucesso!')
            return redirect('relatorios:visualizar_dashboard', pk=dashboard.pk)
    else:
        form = DashboardForm(user=request.user)
    
    context = {
        'form': form,
        'titulo': 'Criar Novo Dashboard'
    }
    
    return render(request, 'relatorios/dashboard_form.html', context)


@login_required
def editar_dashboard(request, pk):
    """
    Edição de dashboard existente.
    """
    dashboard = get_object_or_404(
        Dashboard,
        pk=pk,
        utilizador_criador=request.user
    )
    
    if request.method == 'POST':
        form = DashboardForm(request.POST, instance=dashboard, user=request.user)
        if form.is_valid():
            dashboard = form.save()
            messages.success(request, f'Dashboard "{dashboard.nome}" atualizado com sucesso!')
            return redirect('relatorios:visualizar_dashboard', pk=dashboard.pk)
    else:
        form = DashboardForm(instance=dashboard, user=request.user)
    
    context = {
        'form': form,
        'dashboard': dashboard,
        'titulo': f'Editar Dashboard: {dashboard.nome}'
    }
    
    return render(request, 'relatorios/dashboard_form.html', context)


@login_required
def configurar_widget(request, dashboard_pk):
    """
    Configuração de widgets do dashboard.
    """
    dashboard = get_object_or_404(
        Dashboard,
        pk=dashboard_pk,
        utilizador_criador=request.user
    )
    
    if request.method == 'POST':
        widget_data = json.loads(request.body)
        
        # Adicionar widget ao dashboard
        if not dashboard.widgets:
            dashboard.widgets = []
        
        widget_data['id'] = len(dashboard.widgets) + 1
        dashboard.widgets.append(widget_data)
        dashboard.save(update_fields=['widgets'])
        
        return JsonResponse({'success': True, 'widget_id': widget_data['id']})
    
    # Tipos de widgets disponíveis
    tipos_widgets = [
        {'value': 'contador', 'label': 'Contador'},
        {'value': 'grafico_barras', 'label': 'Gráfico de Barras'},
        {'value': 'grafico_pizza', 'label': 'Gráfico de Pizza'},
        {'value': 'grafico_linha', 'label': 'Gráfico de Linha'},
        {'value': 'grafico_area', 'label': 'Gráfico de Área'},
        {'value': 'tabela', 'label': 'Tabela'},
        {'value': 'lista', 'label': 'Lista'},
        {'value': 'metricas', 'label': 'Métricas'},
    ]
    
    context = {
        'dashboard': dashboard,
        'tipos_widgets': tipos_widgets,
    }
    
    return render(request, 'relatorios/widget_config.html', context)


@login_required
def remover_widget(request, dashboard_pk, widget_id):
    """
    Remove um widget do dashboard.
    """
    dashboard = get_object_or_404(
        Dashboard,
        pk=dashboard_pk,
        utilizador_criador=request.user
    )
    
    if request.method == 'POST':
        dashboard.remove_widget(widget_id)
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})


@login_required
def obter_dados_widget(request, widget_id):
    """
    API para obter dados de um widget específico.
    """
    widget_data = json.loads(request.body)
    dados = _obter_dados_widget(widget_data, request.user)
    
    return JsonResponse({'dados': dados})


def _obter_dados_widget(widget_config, user):
    """
    Função auxiliar para obter dados de um widget.
    """
    tipo = widget_config.get('tipo')
    parametros = widget_config.get('parametros', {})
    
    if tipo == 'contador':
        return _dados_contador(parametros, user)
    elif tipo == 'grafico_barras':
        return _dados_grafico_barras(parametros, user)
    elif tipo == 'grafico_pizza':
        return _dados_grafico_pizza(parametros, user)
    elif tipo == 'grafico_linha':
        return _dados_grafico_linha(parametros, user)
    elif tipo == 'grafico_area':
        return _dados_grafico_area(parametros, user)
    elif tipo == 'tabela':
        return _dados_tabela(parametros, user)
    elif tipo == 'lista':
        return _dados_lista(parametros, user)
    elif tipo == 'metricas':
        return _dados_metricas(parametros, user)
    else:
        return {}


def _dados_contador(parametros, user):
    """
    Dados para widget de contador.
    """
    tipo = parametros.get('tipo', 'documentos_total')
    
    if tipo == 'documentos_total':
        count = Expediente.objects.filter(ativo=True).count()
        label = 'Total de Documentos'
    elif tipo == 'documentos_pendentes':
        count = Expediente.objects.filter(
            ativo=True,
            estado_atual__nome__in=['Recebido', 'Encaminhado', 'Em Tratamento']
        ).count()
        label = 'Documentos Pendentes'
    elif tipo == 'documentos_concluidos':
        count = Expediente.objects.filter(
            ativo=True,
            estado_atual__nome='Concluído'
        ).count()
        label = 'Documentos Concluídos'
    elif tipo == 'sectores_ativos':
        count = Sector.objects.filter(ativo=True).count()
        label = 'Sectores Ativos'
    else:
        count = 0
        label = 'Contador'
    
    return {
        'valor': count,
        'label': label,
        'icone': parametros.get('icone', 'bi-file-earmark-text')
    }


def _dados_grafico_barras(parametros, user):
    """
    Dados para widget de gráfico de barras.
    """
    tipo = parametros.get('tipo', 'documentos_sector')
    
    if tipo == 'documentos_sector':
        dados = Expediente.objects.filter(ativo=True).values(
            'sector_responsavel__nome'
        ).annotate(
            total=Count('id')
        ).order_by('-total')[:10]
        
        chart_config = ChartGenerator.gerar_grafico_barras(
            list(dados), 
            'Documentos por Sector',
            'sector_responsavel__nome',
            'total'
        )
    elif tipo == 'documentos_estado':
        dados = Expediente.objects.filter(ativo=True).values(
            'estado_atual__nome'
        ).annotate(
            total=Count('id')
        ).order_by('-total')
        
        chart_config = ChartGenerator.gerar_grafico_barras(
            list(dados), 
            'Documentos por Estado',
            'estado_atual__nome',
            'total'
        )
    else:
        chart_config = {}
    
    return chart_config


def _dados_grafico_pizza(parametros, user):
    """
    Dados para widget de gráfico de pizza.
    """
    tipo = parametros.get('tipo', 'documentos_estado')
    
    if tipo == 'documentos_estado':
        dados = Expediente.objects.filter(ativo=True).values(
            'estado_atual__nome'
        ).annotate(
            total=Count('id')
        ).order_by('-total')
        
        chart_config = ChartGenerator.gerar_grafico_pizza(
            list(dados), 
            'Distribuição por Estado',
            'estado_atual__nome',
            'total'
        )
    elif tipo == 'documentos_tipo':
        dados = Expediente.objects.filter(ativo=True).values(
            'tipo__nome'
        ).annotate(
            total=Count('id')
        ).order_by('-total')[:8]
        
        chart_config = ChartGenerator.gerar_grafico_pizza(
            list(dados), 
            'Distribuição por Tipo',
            'tipo__nome',
            'total'
        )
    else:
        chart_config = {}
    
    return chart_config


def _dados_grafico_linha(parametros, user):
    """
    Dados para widget de gráfico de linha.
    """
    tipo = parametros.get('tipo', 'documentos_periodo')
    
    if tipo == 'documentos_periodo':
        # Últimos 30 dias
        from django.db.models.functions import TruncDay
        dados = Expediente.objects.filter(
            ativo=True,
            data_criacao__date__gte=timezone.now().date() - timedelta(days=30)
        ).annotate(
            dia=TruncDay('data_criacao')
        ).values('dia').annotate(
            total=Count('id')
        ).order_by('dia')
        
        chart_config = ChartGenerator.gerar_grafico_linha(
            list(dados), 
            'Documentos por Período',
            'dia',
            'total'
        )
    else:
        chart_config = {}
    
    return chart_config


def _dados_grafico_area(parametros, user):
    """
    Dados para widget de gráfico de área.
    """
    tipo = parametros.get('tipo', 'documentos_mensal')
    
    if tipo == 'documentos_mensal':
        # Últimos 12 meses
        from django.db.models.functions import TruncMonth
        dados = Expediente.objects.filter(
            ativo=True,
            data_criacao__date__gte=timezone.now().date() - timedelta(days=365)
        ).annotate(
            mes=TruncMonth('data_criacao')
        ).values('mes').annotate(
            total=Count('id')
        ).order_by('mes')
        
        chart_config = ChartGenerator.gerar_grafico_area(
            list(dados), 
            'Documentos por Mês',
            'mes',
            'total'
        )
    else:
        chart_config = {}
    
    return chart_config


def _dados_tabela(parametros, user):
    """
    Dados para widget de tabela.
    """
    tipo = parametros.get('tipo', 'documentos_recentes')
    
    if tipo == 'documentos_recentes':
        dados = Expediente.objects.filter(ativo=True).select_related(
            'tipo', 'estado_atual', 'sector_responsavel'
        ).order_by('-data_criacao')[:10]
        
        return {
            'titulo': 'Documentos Recentes',
            'colunas': ['Protocolo', 'Tipo', 'Estado', 'Sector', 'Data'],
            'dados': [
                {
                    'protocolo': doc.numero_protocolo,
                    'tipo': doc.tipo.nome,
                    'estado': doc.estado_atual.nome,
                    'sector': doc.sector_responsavel.nome,
                    'data': doc.data_criacao.strftime('%d/%m/%Y')
                }
                for doc in dados
            ]
        }
    elif tipo == 'sectores_performance':
        dados = []
        for sector in Sector.objects.filter(ativo=True):
            total = Expediente.objects.filter(sector_responsavel=sector, ativo=True).count()
            concluidos = Expediente.objects.filter(
                sector_responsavel=sector, 
                ativo=True,
                estado_atual__nome='Concluído'
            ).count()
            
            taxa = (concluidos / total * 100) if total > 0 else 0
            
            dados.append({
                'sector': sector.nome,
                'total': total,
                'concluidos': concluidos,
                'taxa': f"{taxa:.1f}%"
            })
        
        return {
            'titulo': 'Performance por Sector',
            'colunas': ['Sector', 'Total', 'Concluídos', 'Taxa'],
            'dados': dados
        }
    else:
        return {}


def _dados_lista(parametros, user):
    """
    Dados para widget de lista.
    """
    tipo = parametros.get('tipo', 'documentos_pendentes')
    
    if tipo == 'documentos_pendentes':
        dados = Expediente.objects.filter(
            ativo=True,
            estado_atual__nome__in=['Recebido', 'Encaminhado', 'Em Tratamento']
        ).select_related('tipo', 'sector_responsavel').order_by('-data_criacao')[:10]
        
        return {
            'titulo': 'Documentos Pendentes',
            'itens': [
                {
                    'titulo': f"{doc.numero_protocolo} - {doc.tipo.nome}",
                    'subtitulo': doc.sector_responsavel.nome,
                    'data': doc.data_criacao.strftime('%d/%m/%Y'),
                    'estado': doc.estado_atual.nome
                }
                for doc in dados
            ]
        }
    else:
        return {}


def _dados_metricas(parametros, user):
    """
    Dados para widget de métricas.
    """
    tipo = parametros.get('tipo', 'geral')
    
    if tipo == 'geral':
        total_documentos = Expediente.objects.filter(ativo=True).count()
        documentos_pendentes = Expediente.objects.filter(
            ativo=True,
            estado_atual__nome__in=['Recebido', 'Encaminhado', 'Em Tratamento']
        ).count()
        documentos_concluidos = Expediente.objects.filter(
            ativo=True,
            estado_atual__nome='Concluído'
        ).count()
        sectores_ativos = Sector.objects.filter(ativo=True).count()
        
        return {
            'titulo': 'Métricas Gerais',
            'metricas': [
                {'label': 'Total de Documentos', 'valor': total_documentos, 'icone': 'bi-file-earmark-text'},
                {'label': 'Documentos Pendentes', 'valor': documentos_pendentes, 'icone': 'bi-clock'},
                {'label': 'Documentos Concluídos', 'valor': documentos_concluidos, 'icone': 'bi-check-circle'},
                {'label': 'Sectores Ativos', 'valor': sectores_ativos, 'icone': 'bi-building'},
            ]
        }
    else:
        return {}


# Relatórios de Comunicação
@login_required
def relatorio_mensagens_sector(request):
    """
    Relatório de mensagens por sector.
    """
    # Filtros
    sector_id = request.GET.get('sector', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    # Query base para mensagens (simulado - adaptar conforme modelo real)
    mensagens_query = Expediente.objects.filter(ativo=True)
    
    # Aplicar filtros
    if sector_id:
        mensagens_query = mensagens_query.filter(sector_responsavel_id=sector_id)
    
    if data_inicio:
        mensagens_query = mensagens_query.filter(data_criacao__date__gte=data_inicio)
    
    if data_fim:
        mensagens_query = mensagens_query.filter(data_criacao__date__lte=data_fim)
    
    # Agrupar por sector
    mensagens_sector = mensagens_query.values(
        'sector_responsavel__nome'
    ).annotate(
        total=Count('id'),
        pendentes=Count('id', filter=Q(estado_atual__nome__in=['Recebido', 'Encaminhado', 'Em Tratamento'])),
        concluidos=Count('id', filter=Q(estado_atual__nome='Concluído'))
    ).order_by('-total')
    
    # Estatísticas gerais
    total_mensagens = mensagens_query.count()
    mensagens_pendentes = mensagens_query.filter(
        estado_atual__nome__in=['Recebido', 'Encaminhado', 'Em Tratamento']
    ).count()
    mensagens_concluidas = mensagens_query.filter(
        estado_atual__nome='Concluído'
    ).count()
    
    # Tempo médio de resposta (simulado)
    tempo_medio_resposta = 5.2  # dias
    
    context = {
        'titulo': 'Relatório de Mensagens por Sector',
        'mensagens_sector': list(mensagens_sector),
        'total_mensagens': total_mensagens,
        'mensagens_pendentes': mensagens_pendentes,
        'mensagens_concluidas': mensagens_concluidas,
        'tempo_medio_resposta': tempo_medio_resposta,
        'filtros': {
            'sector': sector_id,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
        },
        'sectores': Sector.objects.filter(ativo=True),
    }
    
    return render(request, 'relatorios/relatorio_mensagens_sector.html', context)


@login_required
def relatorio_atividade_utilizadores(request):
    """
    Relatório de atividade de utilizadores.
    """
    # Filtros
    sector_id = request.GET.get('sector', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    # Query base para utilizadores
    utilizadores_query = request.user._meta.model.objects.filter(is_active=True)
    
    # Aplicar filtros
    if sector_id:
        utilizadores_query = utilizadores_query.filter(utilizador__sector_id=sector_id)
    
    # Estatísticas por utilizador
    utilizadores_atividade = []
    for user in utilizadores_query:
        # Documentos atribuídos
        documentos_atribuidos = Expediente.objects.filter(
            utilizador_atual=user,
            ativo=True
        ).count()
        
        # Documentos concluídos
        documentos_concluidos = Expediente.objects.filter(
            utilizador_atual=user,
            ativo=True,
            estado_atual__nome='Concluído'
        ).count()
        
        # Documentos pendentes
        documentos_pendentes = documentos_atribuidos - documentos_concluidos
        
        # Taxa de conclusão
        taxa_conclusao = (documentos_concluidos / documentos_atribuidos * 100) if documentos_atribuidos > 0 else 0
        
        utilizadores_atividade.append({
            'utilizador': user.get_full_name() or user.username,
            'sector': getattr(user, 'sector_atual', None),
            'documentos_atribuidos': documentos_atribuidos,
            'documentos_concluidos': documentos_concluidos,
            'documentos_pendentes': documentos_pendentes,
            'taxa_conclusao': taxa_conclusao,
        })
    
    # Ordenar por atividade
    utilizadores_atividade.sort(key=lambda x: x['documentos_atribuidos'], reverse=True)
    
    # Estatísticas gerais
    total_utilizadores = len(utilizadores_atividade)
    utilizadores_ativos = len([u for u in utilizadores_atividade if u['documentos_atribuidos'] > 0])
    utilizadores_inativos = total_utilizadores - utilizadores_ativos
    
    context = {
        'titulo': 'Relatório de Atividade de Utilizadores',
        'utilizadores_atividade': utilizadores_atividade,
        'total_utilizadores': total_utilizadores,
        'utilizadores_ativos': utilizadores_ativos,
        'utilizadores_inativos': utilizadores_inativos,
        'filtros': {
            'sector': sector_id,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
        },
        'sectores': Sector.objects.filter(ativo=True),
    }
    
    return render(request, 'relatorios/relatorio_atividade_utilizadores.html', context)


@login_required
def relatorio_tempo_resposta(request):
    """
    Relatório de tempo de resposta.
    """
    # Filtros
    sector_id = request.GET.get('sector', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    # Query base para documentos concluídos
    documentos_query = Expediente.objects.filter(
        ativo=True,
        estado_atual__nome='Concluído'
    )
    
    # Aplicar filtros
    if sector_id:
        documentos_query = documentos_query.filter(sector_responsavel_id=sector_id)
    
    if data_inicio:
        documentos_query = documentos_query.filter(data_criacao__date__gte=data_inicio)
    
    if data_fim:
        documentos_query = documentos_query.filter(data_criacao__date__lte=data_fim)
    
    # Tempo médio por sector
    tempo_sector = []
    for sector in Sector.objects.filter(ativo=True):
        docs_sector = documentos_query.filter(sector_responsavel=sector)
        
        if docs_sector.exists():
            # Calcular tempo médio (simplificado)
            tempo_medio = 4.5  # dias (exemplo)
            tempo_sector.append({
                'sector': sector.nome,
                'tempo_medio': tempo_medio,
                'documentos': docs_sector.count(),
                'mais_rapido': 2.1,
                'mais_lento': 8.3,
            })
    
    # Tempo médio por tipo de documento
    tempo_tipo = documentos_query.values('tipo__nome').annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    # Adicionar tempo médio simulado
    for item in tempo_tipo:
        item['tempo_medio'] = 3.2  # dias (exemplo)
    
    # Estatísticas gerais
    total_documentos = documentos_query.count()
    tempo_medio_geral = 4.1  # dias
    documentos_rapidos = len([t for t in tempo_sector if t['tempo_medio'] < 3])
    documentos_lentos = len([t for t in tempo_sector if t['tempo_medio'] > 7])
    
    context = {
        'titulo': 'Relatório de Tempo de Resposta',
        'tempo_sector': tempo_sector,
        'tempo_tipo': list(tempo_tipo),
        'total_documentos': total_documentos,
        'tempo_medio_geral': tempo_medio_geral,
        'documentos_rapidos': documentos_rapidos,
        'documentos_lentos': documentos_lentos,
        'filtros': {
            'sector': sector_id,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
        },
        'sectores': Sector.objects.filter(ativo=True),
    }
    
    return render(request, 'relatorios/relatorio_tempo_resposta.html', context)