from django.contrib.auth.mixins import LoginRequiredMixin


class ProgressoEtapasMixin:
    """
    Mixin para gerenciar o progresso dinâmico das etapas do formulário multi-etapas
    """
    
    def get_progresso_context(self):
        """
        Retorna o contexto do progresso baseado na etapa atual
        """
        # SEMPRE detectar pela URL primeiro (fonte confiável)
        url_name = self.request.resolver_match.url_name
        if 'etapa1' in url_name:
            etapa_atual = 1
        elif 'etapa2' in url_name:
            etapa_atual = 2
        elif 'etapa3' in url_name:
            etapa_atual = 3
        elif 'etapa4' in url_name:
            etapa_atual = 4
        else:
            # Fallback: tentar obter da sessão
            etapa_atual = self.request.session.get('etapa_atual', 1)
        
        # Atualizar sessão com o valor correto
        self.request.session['etapa_atual'] = etapa_atual
        
        etapas = [
            {
                'numero': 1,
                'nome': 'Informações Básicas',
                'subtitulo': 'Dados principais da correspondência',
                'url': 'entrada:etapa1'
            },
            {
                'numero': 2,
                'nome': 'Detalhes',
                'subtitulo': 'Conteúdo e anexos',
                'url': 'entrada:etapa2'
            },
            {
                'numero': 3,
                'nome': 'Membros',
                'subtitulo': 'Pessoas envolvidas',
                'url': 'entrada:etapa3'
            },
            {
                'numero': 4,
                'nome': 'Revisão',
                'subtitulo': 'Confirmar dados',
                'url': 'entrada:etapa4'
            }
        ]
        
        # Determinar o estado de cada etapa
        for i, etapa in enumerate(etapas, 1):
            if i < etapa_atual:
                # Etapas anteriores: concluídas com check
                etapa['estado'] = 'completed'
                etapa['icone'] = 'bi-check'
            elif i == etapa_atual:
                # Etapa atual: ativa com seta
                etapa['estado'] = 'active'
                etapa['icone'] = 'bi-arrow-right'
            else:
                # Etapas futuras: pendentes com número
                etapa['estado'] = 'pending'
                etapa['icone'] = str(i)
        
        return {
            'etapas': etapas,
            'etapa_atual': etapa_atual
        }
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_progresso_context())
        return context
