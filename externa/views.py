from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class MinhasSubmissoesView(LoginRequiredMixin, TemplateView):
    """
    View para utilizadores externos verem suas submissões
    """
    template_name = 'externa/minhas_submissoes.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Minhas Submissões'
        return context

class NovaSubmissaoView(LoginRequiredMixin, TemplateView):
    """
    View para utilizadores externos criarem nova submissão
    """
    template_name = 'externa/nova_submissao.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Nova Submissão'
        return context
