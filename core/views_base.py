from django.views.generic import ListView, TemplateView
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .mixins import BaseViewMixin


class BaseListView(BaseViewMixin, ListView):
    """
    ListView base com funcionalidades comuns de paginação e filtros.
    """
    paginate_by = 20
    search_fields = []
    filter_fields = {}
    ordering = ['-id']
    
    def get_queryset(self):
        """
        Aplica filtros e busca na queryset.
        """
        queryset = super().get_queryset()
        
        # Aplicar busca
        search_query = self.request.GET.get('search', '').strip()
        if search_query and self.search_fields:
            search_filter = Q()
            for field in self.search_fields:
                search_filter |= Q(**{f"{field}__icontains": search_query})
            queryset = queryset.filter(search_filter)
        
        # Aplicar filtros específicos
        for filter_name, filter_field in self.filter_fields.items():
            filter_value = self.request.GET.get(filter_name)
            if filter_value:
                queryset = queryset.filter(**{filter_field: filter_value})
        
        # Aplicar ordenação
        ordering = self.request.GET.get('ordering', self.ordering)
        if ordering:
            if isinstance(ordering, str):
                ordering = [ordering]
            queryset = queryset.order_by(*ordering)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Adiciona dados de contexto para filtros e paginação.
        """
        context = super().get_context_data(**kwargs)
        
        # Adicionar parâmetros de busca e filtros
        context['search_query'] = self.request.GET.get('search', '')
        context['current_ordering'] = self.request.GET.get('ordering', '')
        
        # Adicionar opções de ordenação
        context['ordering_options'] = self.get_ordering_options()
        
        # Adicionar estatísticas
        context.update(self.get_statistics())
        
        return context
    
    def get_ordering_options(self):
        """
        Retorna opções de ordenação disponíveis.
        """
        return [
            {'value': '-id', 'label': 'Mais Recente'},
            {'value': 'id', 'label': 'Mais Antigo'},
            {'value': 'nome', 'label': 'Nome A-Z'},
            {'value': '-nome', 'label': 'Nome Z-A'},
        ]
    
    def get_statistics(self):
        """
        Retorna estatísticas da lista (sobrescrever nas subclasses).
        """
        return {}
    
    @method_decorator(require_http_methods(["POST"]))
    def post(self, request, *args, **kwargs):
        """
        Processa filtros via AJAX.
        """
        try:
            # Aplicar filtros
            queryset = self.get_queryset()
            
            # Paginar resultados
            paginator = Paginator(queryset, self.paginate_by)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)
            
            # Preparar dados para resposta JSON
            data = {
                'success': True,
                'results': [],
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'has_previous': page_obj.has_previous(),
                    'has_next': page_obj.has_next(),
                }
            }
            
            # Adicionar objetos da página
            for obj in page_obj:
                data['results'].append(self.serialize_object(obj))
            
            return JsonResponse(data)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao processar filtros: {str(e)}'
            }, status=500)
    
    def serialize_object(self, obj):
        """
        Serializa um objeto para JSON (sobrescrever nas subclasses).
        """
        return {
            'id': obj.id,
            'nome': str(obj),
        }


class DashboardViewBase(BaseViewMixin, TemplateView):
    """
    View base para dashboards com funcionalidades comuns.
    """
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        """
        Adiciona dados comuns do dashboard.
        """
        context = super().get_context_data(**kwargs)
        
        # Estatísticas básicas
        context.update(self.get_dashboard_statistics())
        
        # Dados recentes
        context.update(self.get_recent_data())
        
        # Alertas e notificações
        context.update(self.get_alerts())
        
        return context
    
    def get_dashboard_statistics(self):
        """
        Retorna estatísticas do dashboard (sobrescrever nas subclasses).
        """
        return {
            'total_items': 0,
            'active_items': 0,
            'pending_items': 0,
        }
    
    def get_recent_data(self):
        """
        Retorna dados recentes (sobrescrever nas subclasses).
        """
        return {
            'recent_items': [],
        }
    
    def get_alerts(self):
        """
        Retorna alertas e notificações (sobrescrever nas subclasses).
        """
        return {
            'alerts': [],
            'warnings': [],
        }


class FilteredListView(BaseListView):
    """
    ListView com filtros avançados e busca.
    """
    filter_form_class = None
    
    def get_context_data(self, **kwargs):
        """
        Adiciona formulário de filtros ao contexto.
        """
        context = super().get_context_data(**kwargs)
        
        if self.filter_form_class:
            context['filter_form'] = self.filter_form_class(self.request.GET)
        
        return context
    
    def get_queryset(self):
        """
        Aplica filtros do formulário.
        """
        queryset = super().get_queryset()
        
        if self.filter_form_class:
            filter_form = self.filter_form_class(self.request.GET)
            if filter_form.is_valid():
                queryset = self.apply_filters(queryset, filter_form.cleaned_data)
        
        return queryset
    
    def apply_filters(self, queryset, cleaned_data):
        """
        Aplica filtros específicos (sobrescrever nas subclasses).
        """
        return queryset
