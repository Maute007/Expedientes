from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.views.generic import ListView, View, DeleteView, RedirectView, CreateView, UpdateView, TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
import json

from .models import Notificacao, Sector, ConfiguracaoSistema
from .forms import SectorForm
from .utils import enviar_notificacao
from .views_base import BaseListView, DashboardViewBase
from .mixins import FormAlertMixin


class ListarNotificacoesView(LoginRequiredMixin, ListView):
    """
    View para listar todas as notificações do utilizador.
    """
    model = Notificacao
    template_name = 'core/notificacoes_lista.html'
    context_object_name = 'notificacoes'
    paginate_by = 20
    
    def get_queryset(self):
        """
        Retorna notificações do utilizador logado com filtros.
        """
        queryset = Notificacao.objects.filter(destinatario=self.request.user)
        
        # Filtro por tipo
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Filtro por lida/não lida
        lida = self.request.GET.get('lida')
        if lida == 'true':
            queryset = queryset.filter(lida=True)
        elif lida == 'false':
            queryset = queryset.filter(lida=False)
        
        # Filtro por prioridade
        prioridade = self.request.GET.get('prioridade')
        if prioridade:
            queryset = queryset.filter(prioridade=prioridade)
        
        # Filtro por data
        data_inicio = self.request.GET.get('data_inicio')
        if data_inicio:
            queryset = queryset.filter(data_criacao__date__gte=data_inicio)
        
        data_fim = self.request.GET.get('data_fim')
        if data_fim:
            queryset = queryset.filter(data_criacao__date__lte=data_fim)
        
        return queryset.order_by('-data_criacao')
    
    def get_context_data(self, **kwargs):
        """
        Adiciona dados de contexto para filtros e estatísticas.
        """
        context = super().get_context_data(**kwargs)
        
        # Estatísticas
        queryset = self.get_queryset()
        context['total_notificacoes'] = queryset.count()
        context['nao_lidas'] = queryset.filter(lida=False).count()
        context['lidas'] = queryset.filter(lida=True).count()
        context['urgentes'] = queryset.filter(prioridade='urgente').count()
        
        # Filtros disponíveis
        context['tipos_notificacao'] = Notificacao.TIPOS_NOTIFICACAO
        context['prioridades'] = Notificacao.PRIORIDADES
        
        # Filtros ativos
        context['filtro_tipo'] = self.request.GET.get('tipo', '')
        context['filtro_lida'] = self.request.GET.get('lida', '')
        context['filtro_prioridade'] = self.request.GET.get('prioridade', '')
        context['filtro_data_inicio'] = self.request.GET.get('data_inicio', '')
        context['filtro_data_fim'] = self.request.GET.get('data_fim', '')
        
        return context


class MarcarNotificacaoLidaView(LoginRequiredMixin, View):
    """
    View para marcar uma notificação como lida via AJAX.
    """
    
    @require_http_methods(["POST"])
    def post(self, request, pk):
        """
        Marca notificação como lida.
        """
        try:
            notificacao = get_object_or_404(
                Notificacao, 
                pk=pk, 
                destinatario=request.user
            )
            
            notificacao.marcar_como_lida()
            
            return JsonResponse({
                'success': True,
                'message': 'Notificação marcada como lida.',
                'data_lida': notificacao.data_lida.strftime('%d/%m/%Y %H:%M') if notificacao.data_lida else None
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao marcar notificação como lida: {str(e)}'
            }, status=400)


class MarcarTodasLidasView(LoginRequiredMixin, View):
    """
    View para marcar todas as notificações como lidas via AJAX.
    """
    
    @require_http_methods(["POST"])
    def post(self, request):
        """
        Marca todas as notificações do utilizador como lidas.
        """
        try:
            count = Notificacao.marcar_todas_lidas(request.user)
            
            return JsonResponse({
                'success': True,
                'message': f'{count} notificações marcadas como lidas.',
                'count': count
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao marcar notificações como lidas: {str(e)}'
            }, status=400)


class ApagarNotificacaoView(LoginRequiredMixin, DeleteView):
    """
    View para apagar uma notificação.
    """
    model = Notificacao
    template_name = 'core/notificacao_confirmar_apagar.html'
    success_url = reverse_lazy('core:lista_notificacoes')
    
    def get_queryset(self):
        """
        Apenas notificações do utilizador logado.
        """
        return Notificacao.objects.filter(destinatario=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """
        Apaga a notificação e mostra mensagem de sucesso.
        """
        notificacao = self.get_object()
        notificacao.delete()
        
        messages.success(
            request, 
            f'Notificação "{notificacao.titulo}" apagada com sucesso.'
        )
        
        return redirect(self.success_url)


class NotificacoesDropdownView(LoginRequiredMixin, View):
    """
    View AJAX para dropdown de notificações no navbar.
    """
    
    def get(self, request):
        """
        Retorna dados para dropdown de notificações.
        """
        try:
            # Últimas 5 notificações NÃO LIDAS
            notificacoes_recentes = Notificacao.objects.filter(
                destinatario=request.user,
                lida=False
            )[:5]
            
            # Contar não lidas
            total_nao_lidas = Notificacao.objects.filter(
                destinatario=request.user,
                lida=False
            ).count()
            
            # Preparar dados
            notificacoes_data = []
            for notif in notificacoes_recentes:
                notificacoes_data.append({
                    'id': notif.id,
                    'titulo': notif.titulo,
                    'mensagem': notif.mensagem[:100] + '...' if len(notif.mensagem) > 100 else notif.mensagem,
                    'tipo': notif.tipo,
                    'prioridade': notif.prioridade,
                    'lida': notif.lida,
                    'data_criacao': notif.data_criacao.strftime('%d/%m/%Y %H:%M'),
                    'icone': notif.obter_icone(),
                    'url': notif.obter_url(),
                    'eh_urgente': notif.eh_urgente()
                })
            
            return JsonResponse({
                'success': True,
                'notificacoes': notificacoes_data,
                'total_nao_lidas': total_nao_lidas
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao carregar notificações: {str(e)}'
            }, status=500)


class RedirecionarNotificacaoView(LoginRequiredMixin, RedirectView):
    """
    View para redirecionar para o documento relacionado e marcar como lida.
    """
    
    def get_redirect_url(self, *args, **kwargs):
        """
        Marca notificação como lida e redireciona para o documento.
        """
        pk = kwargs.get('pk')
        
        try:
            notificacao = get_object_or_404(
                Notificacao, 
                pk=pk, 
                destinatario=self.request.user
            )
            
            # Marcar como lida
            notificacao.marcar_como_lida()
            
            # Retornar URL do documento relacionado
            return notificacao.obter_url()
            
        except Exception as e:
            messages.error(
                self.request, 
                f'Erro ao redirecionar notificação: {str(e)}'
            )
            return reverse_lazy('core:lista_notificacoes')


class DashboardView(DashboardViewBase):
    """
    View principal do dashboard usando a view base.
    """
    
    def get_dashboard_statistics(self):
        """
        Estatísticas específicas do dashboard principal.
        """
        user = self.request.user
        
        return {
            'total_notificacoes': Notificacao.objects.filter(destinatario=user).count(),
            'notificacoes_nao_lidas': Notificacao.objects.filter(
                destinatario=user, 
                lida=False
            ).count(),
            'notificacoes_urgentes': Notificacao.objects.filter(
                destinatario=user, 
                prioridade='urgente',
                lida=False
            ).count(),
            'total_sectores': Sector.objects.filter(ativo=True).count(),
        }
    
    def get_recent_data(self):
        """
        Dados recentes para o dashboard.
        """
        user = self.request.user
        
        return {
            'notificacoes_recentes': Notificacao.objects.filter(
                destinatario=user,
                lida=False
            )[:5],
            'sectores_ativos': Sector.objects.filter(ativo=True)[:5],
        }
    
    def get_alerts(self):
        """
        Alertas e avisos para o dashboard.
        """
        user = self.request.user
        alerts = []
        warnings = []
        
        # Verificar notificações urgentes
        notificacoes_urgentes = Notificacao.objects.filter(
            destinatario=user,
            prioridade='urgente',
            lida=False
        ).count()
        
        if notificacoes_urgentes > 0:
            warnings.append({
                'type': 'urgent',
                'message': f'Você tem {notificacoes_urgentes} notificação(ões) urgente(s) pendente(s).',
                'icon': 'bi-exclamation-triangle',
                'url': reverse_lazy('core:lista_notificacoes')
            })
        
        return {
            'alerts': alerts,
            'warnings': warnings,
        }


# Manter a função dashboard_view para compatibilidade
@login_required
def dashboard_view(request):
    """
    View principal do dashboard.
    Redireciona para o dashboard específico baseado no tipo de utilizador.
    """
    user = request.user
    
    # Redirecionar baseado no tipo de utilizador
    if user.is_superuser or user.tipo_utilizador == 'admin':
        return redirect('core:dashboard_admin')
    elif user.tipo_utilizador == 'pca':
        return redirect('core:dashboard_pca')
    elif user.tipo_utilizador == 'secretaria':
        return redirect('core:dashboard_secretaria')
    elif user.tipo_utilizador == 'chefe':
        return redirect('core:dashboard_chefe')
    elif user.tipo_utilizador == 'externo':
        return redirect('core:dashboard_externo')
    else:  # colaborador ou outro
        return redirect('core:dashboard_colaborador')


# ===== VIEWS DE GESTÃO DE SECTORES =====

class ListarSectoresView(BaseListView):
    """
    View para listar todos os sectores seguindo o layout de lista fornecido.
    """
    model = Sector
    template_name = 'core/sectores_lista.html'
    context_object_name = 'sectores'
    search_fields = ['nome', 'descricao', 'chefe__first_name', 'chefe__last_name', 'chefe__email']
    filter_fields = {
        'ativo': 'ativo',
    }
    ordering = ['nome']
    
    def get_queryset(self):
        """
        Retorna sectores com filtros específicos.
        """
        queryset = super().get_queryset()
        
        # Filtro por nome (específico)
        nome = self.request.GET.get('nome')
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        
        # Filtro por chefe (específico)
        chefe = self.request.GET.get('chefe')
        if chefe:
            queryset = queryset.filter(
                Q(chefe__first_name__icontains=chefe) | 
                Q(chefe__last_name__icontains=chefe) |
                Q(chefe__email__icontains=chefe)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Adiciona dados de contexto específicos para sectores.
        """
        context = super().get_context_data(**kwargs)
        
        # Filtros ativos específicos
        context['filtro_nome'] = self.request.GET.get('nome', '')
        context['filtro_chefe'] = self.request.GET.get('chefe', '')
        context['filtro_ativo'] = self.request.GET.get('ativo', '')
        
        return context
    
    def get_statistics(self):
        """
        Estatísticas específicas para sectores.
        """
        queryset = self.get_queryset()
        return {
            'total_sectores': queryset.count(),
            'sectores_ativos': queryset.filter(ativo=True).count(),
            'sectores_inativos': queryset.filter(ativo=False).count(),
        }
    
    def serialize_object(self, obj):
        """
        Serializa um sector para JSON.
        """
        return {
            'id': obj.id,
            'nome': obj.nome,
            'descricao': obj.descricao,
            'chefe': obj.chefe.get_full_name() if obj.chefe else '',
            'ativo': obj.ativo,
            'data_criacao': obj.data_criacao.strftime('%d/%m/%Y'),
        }


class CriarSectorView(FormAlertMixin, LoginRequiredMixin, CreateView):
    """
    View para criar novo sector seguindo o layout de formulário fornecido.
    """
    model = Sector
    form_class = SectorForm
    template_name = 'core/sector_form.html'
    success_url = reverse_lazy('core:lista_sectores')
    
    def get_success_message(self):
        return f'Sector "{self.object.nome}" criado com sucesso!'


class EditarSectorView(FormAlertMixin, LoginRequiredMixin, UpdateView):
    """
    View para editar sector existente seguindo o layout de formulário fornecido.
    """
    model = Sector
    form_class = SectorForm
    template_name = 'core/sector_form.html'
    success_url = reverse_lazy('core:lista_sectores')
    
    def get_success_message(self):
        return f'Sector "{self.object.nome}" atualizado com sucesso!'


class ApagarSectorView(LoginRequiredMixin, DeleteView):
    """
    View para apagar sector.
    """
    model = Sector
    template_name = 'core/sector_confirmar_apagar.html'
    success_url = reverse_lazy('core:lista_sectores')
    
    def delete(self, request, *args, **kwargs):
        """
        Apaga o sector e mostra mensagem de sucesso.
        """
        sector = self.get_object()
        nome = sector.nome
        sector.delete()
        
        messages.success(
            request, 
            f'Sector "{nome}" apagado com sucesso.'
        )
        
        return redirect(self.success_url)


class DetalhesSectorView(LoginRequiredMixin, View):
    """
    View para mostrar detalhes de um sector.
    """
    template_name = 'core/sector_detalhes.html'
    
    def get(self, request, pk):
        """
        Mostra detalhes do sector.
        """
        sector = get_object_or_404(Sector, pk=pk)
        
        # Obter colaboradores do sector
        colaboradores = sector.obter_colaboradores()
        
        context = {
            'sector': sector,
            'colaboradores': colaboradores,
            'total_colaboradores': colaboradores.count(),
        }
        
        return render(request, self.template_name, context)


# ===== DASHBOARDS ESPECÍFICOS POR TIPO DE UTILIZADOR =====

class DashboardAdminView(LoginRequiredMixin, TemplateView):
    """
    Dashboard do Administrador do Sistema.
    Mostra estatísticas gerais, gestão de utilizadores e sectores.
    """
    template_name = 'core/dashboards/dashboard_admin.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        User = get_user_model()
        
        # Estatísticas gerais
        context.update({
            'titulo_pagina': 'Dashboard - Administrador',
            'total_utilizadores': User.objects.count(),
            'utilizadores_ativos': User.objects.filter(ativo=True).count(),
            'utilizadores_pendentes': User.objects.filter(is_active=False).count(),
            'utilizadores_inativos': User.objects.filter(ativo=False).count(),
            'total_sectores': Sector.objects.count(),
            'sectores_ativos': Sector.objects.filter(ativo=True).count(),
            'total_notificacoes': Notificacao.objects.filter(destinatario=self.request.user).count(),
            'notificacoes_nao_lidas': Notificacao.objects.filter(
                destinatario=self.request.user,
                lida=False
            ).count(),
            
            # Utilizadores recentes
            'utilizadores_recentes': User.objects.order_by('-date_joined')[:5],
            
            # Sectores
            'sectores_lista': Sector.objects.filter(ativo=True).order_by('nome')[:10],
            
            # Estatísticas por tipo de utilizador
            'stats_por_tipo': {
                'admin': User.objects.filter(tipo_utilizador='admin').count(),
                'pca': User.objects.filter(tipo_utilizador='pca').count(),
                'secretaria': User.objects.filter(tipo_utilizador='secretaria').count(),
                'chefe': User.objects.filter(tipo_utilizador='chefe').count(),
                'colaborador': User.objects.filter(tipo_utilizador='colaborador').count(),
                'externo': User.objects.filter(tipo_utilizador='externo').count(),
            },
        })
        
        return context


class DashboardDataView(LoginRequiredMixin, View):
    """
    View AJAX para buscar dados atualizados do dashboard.
    """
    def get(self, request, *args, **kwargs):
        User = get_user_model()
        
        # Estatísticas gerais
        data = {
            'total_utilizadores': User.objects.count(),
            'utilizadores_ativos': User.objects.filter(ativo=True).count(),
            'utilizadores_pendentes': User.objects.filter(is_active=False).count(),
            'utilizadores_inativos': User.objects.filter(ativo=False).count(),
            'total_sectores': Sector.objects.count(),
            'sectores_ativos': Sector.objects.filter(ativo=True).count(),
            'total_notificacoes': Notificacao.objects.filter(destinatario=self.request.user).count(),
            'notificacoes_nao_lidas': Notificacao.objects.filter(
                destinatario=request.user,
                lida=False
            ).count(),
            
            # Estatísticas por tipo de utilizador
            'stats_por_tipo': {
                'admin': User.objects.filter(tipo_utilizador='admin').count(),
                'pca': User.objects.filter(tipo_utilizador='pca').count(),
                'secretaria': User.objects.filter(tipo_utilizador='secretaria').count(),
                'chefe': User.objects.filter(tipo_utilizador='chefe').count(),
                'colaborador': User.objects.filter(tipo_utilizador='colaborador').count(),
                'externo': User.objects.filter(tipo_utilizador='externo').count(),
            },
        }
        
        return JsonResponse(data)


class DashboardSecretariaView(LoginRequiredMixin, TemplateView):
    """
    Dashboard da Secretaria.
    Mostra documentos de entrada, saída e estatísticas gerais.
    """
    template_name = 'core/dashboards/dashboard_secretaria.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        User = get_user_model()
        
        # Importar modelos da app entrada
        try:
            from entrada.models import Expediente, MovimentacaoDocumento
            correspondencias_recentes = Expediente.objects.filter(
                ativo=True
            ).order_by('-data_criacao')[:10]
            
            # Atividades recentes baseadas em movimentações
            atividades_recentes = MovimentacaoDocumento.objects.filter(
                documento__ativo=True
            ).select_related(
                'documento', 'de_utilizador', 'para_utilizador', 'de_sector', 'para_sector'
            ).order_by('-data_movimentacao')[:5]
            
            # Estatísticas de documentos
            total_documentos = Expediente.objects.filter(ativo=True).count()
            documentos_pendentes = Expediente.objects.filter(
                ativo=True,
                estado_atual__nome__in=['Recebido', 'Encaminhado', 'Em Tratamento', 'Devolvido']
            ).count()
            documentos_processados = Expediente.objects.filter(
                ativo=True,
                estado_atual__nome='Concluído'
            ).count()
            documentos_arquivados = Expediente.objects.filter(
                ativo=True,
                estado_atual__nome='Arquivado'
            ).count()
            
            # Documentos com estado prolongado (mais de 5 dias sem atualização e em estados pendentes)
            from django.utils import timezone
            from datetime import timedelta
            data_limite = timezone.now() - timedelta(days=5)
            documentos_prolongados = Expediente.objects.filter(
                ativo=True,
                estado_atual__nome__in=['Recebido', 'Encaminhado', 'Em Tratamento', 'Devolvido'],
                data_atualizacao__lt=data_limite
            ).order_by('data_atualizacao')[:5]
            total_prolongados = Expediente.objects.filter(
                ativo=True,
                estado_atual__nome__in=['Recebido', 'Encaminhado', 'Em Tratamento', 'Devolvido'],
                data_atualizacao__lt=data_limite
            ).count()
            
        except ImportError:
            # Se a app entrada não estiver disponível
            correspondencias_recentes = []
            atividades_recentes = []
            total_documentos = 0
            documentos_pendentes = 0
            documentos_processados = 0
            documentos_arquivados = 0
            documentos_prolongados = []
            total_prolongados = 0
        
        # Estatísticas gerais (similar ao admin mas com foco em documentos)
        context.update({
            'titulo_pagina': 'Dashboard - Secretaria',
            'total_utilizadores': User.objects.count(),
            'utilizadores_ativos': User.objects.filter(ativo=True).count(),
            'total_sectores': Sector.objects.count(),
            'sectores_ativos': Sector.objects.filter(ativo=True).count(),
            'total_notificacoes': Notificacao.objects.filter(destinatario=self.request.user).count(),
            'notificacoes_nao_lidas': Notificacao.objects.filter(
                destinatario=self.request.user,
                lida=False
            ).count(),
            
            # Documentos reais da app entrada
            'correspondencias_recentes': correspondencias_recentes,
            'atividades_recentes': atividades_recentes,
            'total_documentos': total_documentos,
            'documentos_pendentes': documentos_pendentes,
            'documentos_processados': documentos_processados,
            'documentos_arquivados': documentos_arquivados,
            'documentos_prolongados': documentos_prolongados,
            'total_prolongados': total_prolongados,
            
            # Sectores
            'sectores_lista': Sector.objects.filter(ativo=True).order_by('nome')[:10],
        })
        
        return context


class DashboardPCAView(LoginRequiredMixin, TemplateView):
    """
    Dashboard do Presidente do Conselho de Administração (PCA).
    Mostra visão executiva de todos os sectores e documentos importantes.
    """
    template_name = 'core/dashboards/dashboard_pca.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        User = get_user_model()
        
        # Importar modelos da app entrada
        try:
            from entrada.models import Expediente, MovimentacaoDocumento
            # PCA vê apenas documentos onde é utilizador_atual
            correspondencias_recentes = Expediente.objects.filter(
                ativo=True,
                utilizador_atual=self.request.user
            ).order_by('-data_criacao')[:10]
            
            # Atividades recentes baseadas em movimentações
            atividades_recentes = MovimentacaoDocumento.objects.filter(
                documento__ativo=True
            ).select_related(
                'documento', 'de_utilizador', 'para_utilizador', 'de_sector', 'para_sector'
            ).order_by('-data_movimentacao')[:5]
            
            # Estatísticas de documentos (filtradas para o PCA)
            base_queryset = Expediente.objects.filter(
                ativo=True,
                utilizador_atual=self.request.user
            )
            
            total_documentos = base_queryset.count()
            documentos_pendentes = base_queryset.filter(
                estado_atual__nome__in=['Recebido', 'Encaminhado', 'Em Tratamento', 'Devolvido']
            ).count()
            documentos_processados = base_queryset.filter(
                estado_atual__nome='Concluído'
            ).count()
            documentos_arquivados = base_queryset.filter(
                estado_atual__nome='Arquivado'
            ).count()
            
            # Documentos com estado prolongado (mais de 5 dias sem atualização e em estados pendentes)
            from django.utils import timezone
            from datetime import timedelta
            data_limite = timezone.now() - timedelta(days=5)
            documentos_prolongados = base_queryset.filter(
                estado_atual__nome__in=['Recebido', 'Encaminhado', 'Em Tratamento', 'Devolvido'],
                data_atualizacao__lt=data_limite
            ).order_by('data_atualizacao')[:5]
            total_prolongados = base_queryset.filter(
                estado_atual__nome__in=['Recebido', 'Encaminhado', 'Em Tratamento', 'Devolvido'],
                data_atualizacao__lt=data_limite
            ).count()
            
        except ImportError:
            # Se a app entrada não estiver disponível
            correspondencias_recentes = []
            atividades_recentes = []
            total_documentos = 0
            documentos_pendentes = 0
            documentos_processados = 0
            documentos_arquivados = 0
            documentos_prolongados = []
            total_prolongados = 0
        
        # Estatísticas gerais (similar ao admin mas com foco em documentos)
        context.update({
            'titulo_pagina': 'Dashboard - PCA',
            'total_utilizadores': User.objects.count(),
            'utilizadores_ativos': User.objects.filter(ativo=True).count(),
            'total_sectores': Sector.objects.count(),
            'sectores_ativos': Sector.objects.filter(ativo=True).count(),
            'total_notificacoes': Notificacao.objects.filter(destinatario=self.request.user).count(),
            'notificacoes_nao_lidas': Notificacao.objects.filter(
                destinatario=self.request.user,
                lida=False
            ).count(),
            
            # Documentos reais da app entrada (filtrados para o PCA)
            'correspondencias_recentes': correspondencias_recentes,
            'atividades_recentes': atividades_recentes,
            'total_documentos': total_documentos,
            'documentos_pendentes': documentos_pendentes,
            'documentos_processados': documentos_processados,
            'documentos_arquivados': documentos_arquivados,
            'documentos_prolongados': documentos_prolongados,
            'total_prolongados': total_prolongados,
            
            # Sectores
            'sectores_lista': Sector.objects.filter(ativo=True).order_by('nome')[:10],
        })
        
        return context


class DashboardChefeView(LoginRequiredMixin, TemplateView):
    """
    Dashboard do Chefe de Sector.
    Mostra documentos e equipa do seu sector.
    """
    template_name = 'core/dashboards/dashboard_chefe.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Obter sector do chefe
        sector = Sector.objects.filter(chefe=user, ativo=True).first()
        
        # Importar modelos da app entrada
        try:
            from entrada.models import Expediente, MovimentacaoDocumento
            from django.db.models import Q
            
            # Chefe vê apenas documentos onde é utilizador_atual
            correspondencias_recentes = Expediente.objects.filter(
                ativo=True,
                utilizador_atual=user
            ).order_by('-data_criacao')[:10]
            
            # Atividades recentes baseadas em movimentações
            atividades_recentes = MovimentacaoDocumento.objects.filter(
                documento__ativo=True
            ).select_related(
                'documento', 'de_utilizador', 'para_utilizador', 'de_sector', 'para_sector'
            ).order_by('-data_movimentacao')[:5]
            
            # Estatísticas de documentos (filtradas para o chefe)
            base_queryset = Expediente.objects.filter(
                ativo=True,
                utilizador_atual=user
            )
            
            total_documentos = base_queryset.count()
            documentos_pendentes = base_queryset.filter(
                estado_atual__nome__in=['Recebido', 'Encaminhado', 'Em Tratamento', 'Devolvido']
            ).count()
            documentos_processados = base_queryset.filter(
                estado_atual__nome='Concluído'
            ).count()
            documentos_arquivados = base_queryset.filter(
                estado_atual__nome='Arquivado'
            ).count()
            
        except ImportError:
            # Se a app entrada não estiver disponível
            correspondencias_recentes = []
            atividades_recentes = []
            total_documentos = 0
            documentos_pendentes = 0
            documentos_processados = 0
            documentos_arquivados = 0
        
        # Estatísticas gerais
        total_notificacoes = Notificacao.objects.filter(
            destinatario=user,
            lida=False
        ).count()
        
        # Colaboradores do sector
        colaboradores = sector.obter_colaboradores() if sector else []
        colaboradores_count = colaboradores.count()
        
        context.update({
            'titulo_pagina': 'Dashboard - Chefe de Sector',
            'sector': sector,
            'colaboradores': colaboradores,
            'colaboradores_count': colaboradores_count,
            'total_notificacoes': total_notificacoes,
            'correspondencias_recentes': correspondencias_recentes,
            'atividades_recentes': atividades_recentes,
            'total_documentos': total_documentos,
            'documentos_pendentes': documentos_pendentes,
            'documentos_processados': documentos_processados,
            'documentos_arquivados': documentos_arquivados,
        })
        
        return context


class DashboardColaboradorView(LoginRequiredMixin, TemplateView):
    """
    Dashboard do Colaborador.
    Mostra tarefas e documentos atribuídos.
    """
    template_name = 'core/dashboards/dashboard_colaborador.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Importar modelos da app entrada
        try:
            from entrada.models import Expediente, MovimentacaoDocumento
            from django.db.models import Q
            
            # Colaborador vê apenas documentos onde é utilizador_atual
            correspondencias_recentes = Expediente.objects.filter(
                ativo=True,
                utilizador_atual=user
            ).order_by('-data_criacao')[:10]
            
            # Atividades recentes baseadas em movimentações
            atividades_recentes = MovimentacaoDocumento.objects.filter(
                documento__ativo=True
            ).select_related(
                'documento', 'de_utilizador', 'para_utilizador', 'de_sector', 'para_sector'
            ).order_by('-data_movimentacao')[:5]
            
            # Estatísticas de documentos (filtradas para o colaborador)
            base_queryset = Expediente.objects.filter(
                ativo=True,
                utilizador_atual=user
            )
            
            total_documentos = base_queryset.count()
            documentos_pendentes = base_queryset.filter(
                estado_atual__nome__in=['Recebido', 'Encaminhado', 'Em Tratamento', 'Devolvido']
            ).count()
            documentos_processados = base_queryset.filter(
                estado_atual__nome='Concluído'
            ).count()
            documentos_arquivados = base_queryset.filter(
                estado_atual__nome='Arquivado'
            ).count()
            
        except ImportError:
            # Se a app entrada não estiver disponível
            correspondencias_recentes = []
            atividades_recentes = []
            total_documentos = 0
            documentos_pendentes = 0
            documentos_processados = 0
            documentos_arquivados = 0
        
        # Estatísticas gerais
        total_notificacoes = Notificacao.objects.filter(
            destinatario=user,
            lida=False
        ).count()
        
        context.update({
            'titulo_pagina': 'Dashboard - Colaborador',
            'sector': user.sector_atual,
            'total_notificacoes': total_notificacoes,
            'correspondencias_recentes': correspondencias_recentes,
            'atividades_recentes': atividades_recentes,
            'total_documentos': total_documentos,
            'documentos_atribuidos': total_documentos,  # Alias para compatibilidade
            'tarefas_pendentes': documentos_pendentes,  # Alias para compatibilidade
            'documentos_pendentes': documentos_pendentes,
            'documentos_processados': documentos_processados,
            'documentos_arquivados': documentos_arquivados,
        })
        
        return context


class DashboardExternoView(LoginRequiredMixin, TemplateView):
    """
    Dashboard do Utilizador Externo.
    Mostra submissões e status de documentos externos.
    """
    template_name = 'core/dashboards/dashboard_externo.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context.update({
            'titulo_pagina': 'Dashboard - Portal Externo',
            'total_notificacoes': Notificacao.objects.filter(
                destinatario=user,
                lida=False,
            ).count(),
            
            # Submissões (será implementado quando app externa estiver pronta)
            'minhas_submissoes': 0,  # Placeholder
            'submissoes_pendentes': 0,  # Placeholder
            'submissoes_aprovadas': 0,  # Placeholder
        })
        
        return context


# ===== CONFIGURAÇÕES DO SISTEMA =====

class ConfiguracoesSistemaView(LoginRequiredMixin, TemplateView):
    """
    View para configurações do sistema (apenas administradores, secretarias e PCA).
    """
    template_name = 'core/configuracoes_sistema.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Apenas administradores, secretarias e PCA podem acessar
        if not (request.user.is_superuser or 
                request.user.tipo_utilizador in ['admin', 'secretaria', 'pca']):
            messages.error(request, '🚫 Acesso negado: Apenas administradores, secretarias e PCA podem acessar as configurações do sistema.')
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        User = get_user_model()
        
        # Estatísticas do sistema
        context.update({
            'titulo_pagina': 'Configurações do Sistema',
            'total_utilizadores': User.objects.count(),
            'utilizadores_pendentes': User.objects.filter(ativo=False).count(),
            'utilizadores_inativos': User.objects.filter(is_active=False).count(),
            'total_sectores': Sector.objects.count(),
            'sectores_ativos': Sector.objects.filter(ativo=True).count(),
            'total_tipos_documento': 0,  # Será implementado quando a app entrada estiver completa
            'total_notificacoes': Notificacao.objects.filter(destinatario=self.request.user).count(),
        })
        
        return context


class SalvarConfiguracoesGeraisView(LoginRequiredMixin, View):
    """
    View para salvar configurações gerais do sistema.
    """
    
    def dispatch(self, request, *args, **kwargs):
        # Apenas administradores, secretarias e PCA podem acessar
        if not (request.user.is_superuser or 
                request.user.tipo_utilizador in ['admin', 'secretaria', 'pca']):
            return JsonResponse({'error': 'Acesso negado'}, status=403)
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        try:
            # Obter ou criar configurações
            nome_sistema, created = ConfiguracaoSistema.objects.get_or_create(
                chave='nome_sistema',
                defaults={'valor': 'FTC - Sistema de Processos', 'tipo': 'string'}
            )
            tamanho_arquivo, created = ConfiguracaoSistema.objects.get_or_create(
                chave='tamanho_maximo_arquivo',
                defaults={'valor': '10', 'tipo': 'int'}
            )
            timeout_sessao, created = ConfiguracaoSistema.objects.get_or_create(
                chave='timeout_sessao',
                defaults={'valor': '30', 'tipo': 'int'}
            )
            
            # Atualizar valores
            nome_sistema.definir_valor(request.POST.get('nome_sistema', 'FTC - Sistema de Processos'))
            tamanho_arquivo.definir_valor(int(request.POST.get('tamanho_arquivo', 10)))
            timeout_sessao.definir_valor(int(request.POST.get('timeout_sessao', 30)))
            
            return JsonResponse({'success': True, 'message': 'Configurações salvas com sucesso!'})
            
        except Exception as e:
            return JsonResponse({'error': f'Erro ao salvar configurações: {str(e)}'}, status=500)


class SalvarConfiguracoesNotificacoesView(LoginRequiredMixin, View):
    """
    View para salvar configurações de notificações.
    """
    
    def dispatch(self, request, *args, **kwargs):
        # Apenas administradores, secretarias e PCA podem acessar
        if not (request.user.is_superuser or 
                request.user.tipo_utilizador in ['admin', 'secretaria', 'pca']):
            return JsonResponse({'error': 'Acesso negado'}, status=403)
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        try:
            # Obter ou criar configurações de notificação
            email_notificacoes, created = ConfiguracaoSistema.objects.get_or_create(
                chave='email_notificacoes',
                defaults={'valor': 'true', 'tipo': 'bool'}
            )
            frequencia_notificacoes, created = ConfiguracaoSistema.objects.get_or_create(
                chave='frequencia_notificacoes',
                defaults={'valor': 'imediata', 'tipo': 'string'}
            )
            
            # Atualizar valores
            email_notificacoes.definir_valor(request.POST.get('email_notificacoes', 'true') == 'true')
            frequencia_notificacoes.definir_valor(request.POST.get('frequencia_notificacoes', 'imediata'))
            
            return JsonResponse({'success': True, 'message': 'Configurações de notificação salvas com sucesso!'})
            
        except Exception as e:
            return JsonResponse({'error': f'Erro ao salvar configurações: {str(e)}'}, status=500)