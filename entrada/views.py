from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, View, FormView
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
import json

from .models import Expediente, TipoDocumento, AnexoExpediente, HistoricoExpediente, MovimentacaoDocumento, ParecerExpediente
from .forms import (
    TipoDocumentoForm, Etapa1Form, Etapa2Form, Etapa3Form, 
    Etapa4Form, AnexoForm, ExpedienteSearchForm, ExpedienteFilterForm,
    DocumentoEntradaForm, DocumentoEntradaUpdateForm, EncaminhamentoForm,
    PortalExpedienteForm, MultiAnexoForm, EditarExpedienteForm, ParecerExpedienteForm, ImplementarParecerForm
)
from .mixins import ProgressoEtapasMixin
from core.models import Sector
from core.mixins import FormAlertMixin
from core.views_base import BaseViewMixin
from core.utils import enviar_notificacao
from django.contrib.auth import get_user_model

User = get_user_model()


class ListarExpedientesView(LoginRequiredMixin, ListView):
    """
    View para listar expedientes com filtros e busca
    """
    model = Expediente
    template_name = 'entrada/lista_expedientes.html'
    context_object_name = 'expedientes'
    paginate_by = 15
    
    def get_queryset(self):
        # Secretaria vê todos os expedientes, outros utilizadores veem apenas os seus
        if self.request.user.tipo_utilizador == 'secretaria':
            queryset = Expediente.objects.select_related(
                'tipo', 'criado_por', 'sector_responsavel', 'estado_atual'
            ).prefetch_related('anexos')
        else:
            # Todos os outros utilizadores veem apenas documentos onde são utilizador_atual
            queryset = Expediente.objects.select_related(
                'tipo', 'criado_por', 'sector_responsavel', 'estado_atual'
            ).prefetch_related('anexos').filter(
                utilizador_atual=self.request.user
            )
        
        # Filtros
        search_form = ExpedienteSearchForm(self.request.GET)
        if search_form.is_valid():
            numero = search_form.cleaned_data.get('numero_protocolo')
            if numero:
                # Pesquisa em múltiplos campos
                queryset = queryset.filter(
                    Q(numero_protocolo__icontains=numero) |
                    Q(referencia__icontains=numero) |
                    Q(remetente__icontains=numero) |
                    Q(assunto__icontains=numero)
                )
            
            tipo = search_form.cleaned_data.get('tipo')
            if tipo:
                queryset = queryset.filter(tipo=tipo)
            
            status = search_form.cleaned_data.get('status')
            if status:
                queryset = queryset.filter(estado_atual=status)
            
            data_inicio = search_form.cleaned_data.get('data_inicio')
            if data_inicio:
                queryset = queryset.filter(data_criacao__date__gte=data_inicio)
            
            data_fim = search_form.cleaned_data.get('data_fim')
            if data_fim:
                queryset = queryset.filter(data_criacao__date__lte=data_fim)
            
            sector = search_form.cleaned_data.get('sector')
            if sector:
                queryset = queryset.filter(sector_responsavel=sector)
        
        # Ordenação
        filter_form = ExpedienteFilterForm(self.request.GET)
        if filter_form.is_valid():
            ordenar_por = filter_form.cleaned_data.get('ordenar_por', '-data_criacao')
            queryset = queryset.order_by(ordenar_por)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ExpedienteSearchForm(self.request.GET)
        context['filter_form'] = ExpedienteFilterForm(self.request.GET)
        
        # Adicionar estados disponíveis para o filtro
        from core.models import EstadoDocumento
        context['estados_disponiveis'] = EstadoDocumento.objects.filter(ativo=True)
        
        return context


class CriarExpedienteView(LoginRequiredMixin, CreateView):
    """
    View principal para criar expediente (redireciona para etapa 1)
    """
    model = Expediente
    template_name = 'entrada/criar_expediente.html'
    
    def get(self, request, *args, **kwargs):
        return redirect('entrada:etapa1')


class Etapa1View(LoginRequiredMixin, ProgressoEtapasMixin, CreateView):
    """
    View para Etapa 1: Informações Básicas
    """
    model = Expediente
    form_class = Etapa1Form
    template_name = 'entrada/etapa1.html'
    
    def form_valid(self, form):
        expediente = form.save(commit=False)
        expediente.criado_por = self.request.user
        
        # Verificar se o usuário tem sector_atual
        if hasattr(self.request.user, 'sector_atual') and self.request.user.sector_atual:
            expediente.sector_responsavel = self.request.user.sector_atual
        
        expediente.estado_atual = self.get_estado_inicial()
        
        # Usar o número de protocolo do formulário ou gerar um novo
        if form.cleaned_data.get('numero_protocolo'):
            expediente.numero_protocolo = form.cleaned_data['numero_protocolo']
        else:
            expediente.numero_protocolo = expediente.gerar_numero_protocolo()
        
        try:
            expediente.save()
            
            # Adicionar criador aos membros envolvidos
            expediente.membros_envolvidos.add(self.request.user)
            
            # Salvar na sessão para as próximas etapas
            self.request.session['expediente_id'] = expediente.id
            self.request.session['etapa_atual'] = 1
            
            messages.success(self.request, '✅ Etapa 1 concluída! Dados básicos do expediente salvos. Prosseguindo para anexos...')
            return redirect('entrada:etapa2')
        except Exception as e:
            print(f"Erro ao salvar expediente: {e}")
            messages.error(self.request, f'❌ Erro ao salvar expediente na Etapa 1: {str(e)}. Verifique os dados inseridos e tente novamente.')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        print(f"Form errors: {form.errors}")
        
        # Preservar o número de protocolo se foi gerado
        if not form.initial.get('numero_protocolo') and not form.data.get('numero_protocolo'):
            temp_expediente = Expediente()
            form.initial['numero_protocolo'] = temp_expediente.gerar_numero_protocolo()
        
        # Não mostrar mensagem genérica - o template mostra os erros específicos
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Gerar número de protocolo automaticamente para exibição
        if not context['form'].initial.get('numero_protocolo'):
            # Criar uma instância temporária para gerar o número
            temp_expediente = Expediente()
            context['form'].initial['numero_protocolo'] = temp_expediente.gerar_numero_protocolo()
        
        return context
    
    def get_estado_inicial(self):
        """Retorna o estado inicial dos expedientes"""
        from core.models import EstadoDocumento
        return EstadoDocumento.objects.filter(nome='Recebido').first()


class Etapa2View(LoginRequiredMixin, ProgressoEtapasMixin, UpdateView):
    """
    View para Etapa 2: Detalhes
    """
    model = Expediente
    form_class = Etapa2Form
    template_name = 'entrada/etapa2.html'
    
    def dispatch(self, request, *args, **kwargs):
        expediente_id = request.session.get('expediente_id')
        if not expediente_id:
            messages.error(request, '⏰ Sessão expirada. Por favor, inicie novamente o processo de criação do expediente.')
            return redirect('entrada:etapa1')
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self):
        expediente_id = self.request.session.get('expediente_id')
        return get_object_or_404(Expediente, id=expediente_id)
    
    def form_valid(self, form):
        expediente = form.save()
        
        # Processar anexos múltiplos
        anexos = self.request.FILES.getlist('anexos')
        if anexos:
            for anexo in anexos:
                if anexo:  # Verificar se o arquivo não está vazio
                    AnexoExpediente.objects.create(
                        expediente=expediente,
                        arquivo=anexo,
                        nome_original=anexo.name,
                        tamanho=anexo.size,
                        tipo_mime=anexo.content_type,
                        descricao=f'Anexo: {anexo.name}',
                        upload_por=self.request.user
                    )
        
        self.request.session['etapa_atual'] = 2
        messages.success(self.request, '✅ Etapa 2 concluída! Anexos adicionados com sucesso. Prosseguindo para membros envolvidos...')
        return redirect('entrada:etapa3')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expediente = self.get_object()
        context['anexos'] = expediente.anexos.all() if expediente else []
        return context


class Etapa3View(LoginRequiredMixin, ProgressoEtapasMixin, FormView):
    """
    View para Etapa 3: Membros
    """
    form_class = Etapa3Form
    template_name = 'entrada/etapa3.html'
    
    def dispatch(self, request, *args, **kwargs):
        expediente_id = request.session.get('expediente_id')
        if not expediente_id:
            messages.error(request, '⏰ Sessão expirada. Por favor, inicie novamente o processo de criação do expediente.')
            return redirect('entrada:etapa1')
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self):
        expediente_id = self.request.session.get('expediente_id')
        return get_object_or_404(Expediente, id=expediente_id)
    
    def form_valid(self, form):
        expediente = self.get_object()
        
        # Processar dados do formulário
        sector_selecionado = form.cleaned_data.get('sector')
        membros_selecionados = form.cleaned_data.get('membros', [])
        
        # Atualizar sectores envolvidos
        if sector_selecionado:
            expediente.sectores_envolvidos.add(sector_selecionado)
        
        # Atualizar membros envolvidos
        if membros_selecionados:
            # Adicionar membros selecionados sem remover os existentes (como PCA)
            for membro in membros_selecionados:
                expediente.membros_envolvidos.add(membro)
        
        self.request.session['etapa_atual'] = 3
        messages.success(self.request, '✅ Etapa 3 concluída! Membros envolvidos definidos. Prosseguindo para revisão final...')
        return redirect('entrada:etapa4')
    
    def get_initial(self):
        """
        Inicializar o formulário com dados do expediente
        """
        initial = super().get_initial()
        expediente = self.get_object()
        
        # Definir sector inicial baseado no sector responsável do expediente
        if expediente and expediente.sector_responsavel:
            initial['sector'] = expediente.sector_responsavel
        
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expediente = self.get_object()
        context['expediente'] = expediente
        context['sectores_envolvidos'] = expediente.sectores_envolvidos.all() if expediente else []
        context['membros_envolvidos'] = expediente.membros_envolvidos.all() if expediente else []
        
        # Adicionar sectores disponíveis para busca
        from core.models import Sector
        context['sectores_disponiveis'] = Sector.objects.filter(ativo=True).order_by('nome')
        
        return context


class Etapa4View(LoginRequiredMixin, ProgressoEtapasMixin, DetailView):
    """
    View para Etapa 4: Revisão Final
    """
    model = Expediente
    template_name = 'entrada/etapa4.html'
    
    def dispatch(self, request, *args, **kwargs):
        expediente_id = request.session.get('expediente_id')
        if not expediente_id:
            messages.error(request, '⏰ Sessão expirada. Por favor, inicie novamente o processo de criação do expediente.')
            return redirect('entrada:etapa1')
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self):
        expediente_id = self.request.session.get('expediente_id')
        return get_object_or_404(Expediente, id=expediente_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expediente = self.get_object()
        if expediente:
            context['anexos'] = expediente.anexos.all()
            context['sectores_envolvidos'] = expediente.sectores_envolvidos.all()
            context['membros_envolvidos'] = expediente.membros_envolvidos.all()
        return context


@login_required
def finalizar_expediente(request):
    """
    View para finalizar o expediente após revisão
    """
    expediente_id = request.session.get('expediente_id')
    if not expediente_id:
        messages.error(request, '⏰ Sessão expirada. Por favor, inicie novamente o processo de criação do expediente.')
        return redirect('entrada:criar_expediente')
    
    expediente = get_object_or_404(Expediente, id=expediente_id)
    
    if request.method == 'POST':
        # Marcar como submetido
        expediente.marcar_como_submetido()
        
        # Criar entrada no histórico
        HistoricoExpediente.objects.create(
            expediente=expediente,
            acao='Expediente submetido',
            descricao='Expediente submetido para análise',
            usuario=request.user,
            estado_anterior='rascunho',
            estado_novo='submetido'
        )
        
        # Limpar sessão
        del request.session['expediente_id']
        del request.session['etapa_atual']
        
        messages.success(request, f'Expediente {expediente.numero_protocolo} submetido com sucesso!')
        return redirect('entrada:lista_expedientes')
    
    return redirect('entrada:etapa4')


@login_required
def guardar_rascunho(request):
    """
    View para guardar rascunho do expediente
    """
    expediente_id = request.session.get('expediente_id')
    if not expediente_id:
        messages.error(request, '⏰ Sessão expirada. Por favor, inicie novamente o processo de criação do expediente.')
        return redirect('entrada:criar_expediente')
    
    expediente = get_object_or_404(Expediente, id=expediente_id)
    expediente.rascunho = True
    expediente.save()
    
    messages.success(request, f'💾 Rascunho do expediente {expediente.numero_protocolo} guardado com sucesso! Você pode continuar editando mais tarde.')
    return redirect('entrada:etapa4')


@login_required
def adicionar_membro(request):
    """
    View AJAX para adicionar membro ao expediente
    """
    if request.method == 'POST':
        expediente_id = request.session.get('expediente_id')
        if not expediente_id:
            return JsonResponse({'success': False, 'message': 'Sessão expirada'})
        
        expediente = get_object_or_404(Expediente, id=expediente_id)
        sector_id = request.POST.get('sector_id')
        membro_id = request.POST.get('membro_id')
        
        if sector_id:
            sector = get_object_or_404(Sector, id=sector_id)
            expediente.sectores_envolvidos.add(sector)
        
        if membro_id:
            membro = get_object_or_404(User, id=membro_id)
            expediente.membros_envolvidos.add(membro)
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


@login_required
def remover_membro(request):
    """
    View AJAX para remover membro do expediente
    """
    if request.method == 'POST':
        expediente_id = request.session.get('expediente_id')
        if not expediente_id:
            return JsonResponse({'success': False, 'message': 'Sessão expirada'})
        
        expediente = get_object_or_404(Expediente, id=expediente_id)
        sector_id = request.POST.get('sector_id')
        membro_id = request.POST.get('membro_id')
        
        if sector_id:
            sector = get_object_or_404(Sector, id=sector_id)
            expediente.sectores_envolvidos.remove(sector)
        
        if membro_id:
            membro = get_object_or_404(User, id=membro_id)
            expediente.membros_envolvidos.remove(membro)
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


@login_required
def obter_membros_sector(request):
    """
    View AJAX para obter membros de um sector
    """
    if request.method == 'POST':
        sector_id = request.POST.get('sector_id')
        if sector_id:
            sector = get_object_or_404(Sector, id=sector_id)
            membros = User.objects.filter(
                sector_atual=sector,
                ativo=True
            ).values('id', 'first_name', 'last_name', 'email', 'tipo_utilizador')
            
            # Formatar dados para o JavaScript
            membros_formatados = []
            for membro in membros:
                membros_formatados.append({
                    'id': membro['id'],
                    'nome': f"{membro['first_name']} {membro['last_name']}".strip(),
                    'email': membro['email'],
                    'tipo_utilizador': membro['tipo_utilizador']
                })
            
            # Obter chefe do sector
            chefe_sector = sector.obter_chefe()
            chefe_formatado = None
            if chefe_sector:
                chefe_formatado = {
                    'id': chefe_sector.id,
                    'nome': chefe_sector.get_full_name(),
                    'email': chefe_sector.email,
                    'tipo_utilizador': chefe_sector.tipo_utilizador
                }
            
            return JsonResponse({
                'success': True,
                'membros': membros_formatados,
                'chefe_sector': chefe_formatado
            })
    
    return JsonResponse({'success': False, 'message': 'Sector não encontrado'})


@login_required
def buscar_membros(request):
    """
    View AJAX para buscar membros para adicionar
    """
    if request.method == 'POST':
        sector_id = request.POST.get('sector_id')
        tipo_utilizador = request.POST.get('tipo_utilizador')
        nome = request.POST.get('nome', '')
        
        # Construir queryset base
        queryset = User.objects.filter(ativo=True)
        
        # Filtrar por sector se especificado
        if sector_id:
            queryset = queryset.filter(sector_atual_id=sector_id)
        
        # Filtrar por tipo de utilizador se especificado
        if tipo_utilizador:
            queryset = queryset.filter(tipo_utilizador=tipo_utilizador)
        
        # Filtrar por nome se especificado
        if nome:
            queryset = queryset.filter(
                Q(first_name__icontains=nome) | 
                Q(last_name__icontains=nome) |
                Q(email__icontains=nome)
            )
        
        # Formatar dados para o JavaScript
        membros = []
        for membro in queryset[:50]:  # Limitar a 50 resultados
            membros.append({
                'id': membro.id,
                'nome': membro.get_full_name() or membro.username,
                'email': membro.email,
                'tipo_utilizador': membro.tipo_utilizador,
                'sector': membro.sector_atual.nome if membro.sector_atual else 'Sem sector'
            })
        
        return JsonResponse({
            'success': True,
            'membros': membros
        })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})

@login_required
def upload_anexo(request):
    """
    View AJAX para upload de anexos
    """
    if request.method == 'POST':
        expediente_id = request.session.get('expediente_id')
        if not expediente_id:
            return JsonResponse({'success': False, 'message': 'Sessão expirada'})
        
        expediente = get_object_or_404(Expediente, id=expediente_id)
        
        form = AnexoForm(request.POST, request.FILES)
        if form.is_valid():
            anexo = form.save(commit=False)
            anexo.expediente = expediente
            anexo.upload_por = request.user
            anexo.save()
            
            return JsonResponse({
                'success': True,
                'anexo': {
                    'id': anexo.id,
                    'nome': anexo.nome_original,
                    'tamanho': anexo.tamanho_humanizado,
                    'data': anexo.data_upload.strftime('%d/%m/%Y %H:%M')
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro no formulário',
                'errors': form.errors
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


class DetalharExpedienteView(LoginRequiredMixin, DetailView):
    """
    View para detalhar expediente
    """
    model = Expediente
    template_name = 'entrada/detalhar_expediente.html'
    context_object_name = 'expediente'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expediente = self.get_object()
        
        # Verificar permissões
        if not expediente.pode_visualizar(self.request.user):
            raise PermissionDenied("Você não tem permissão para visualizar este documento.")
        
        # Adicionar propriedades para facilitar uso no template
        context['pode_visualizar'] = expediente.pode_visualizar(self.request.user)
        context['pode_encaminhar'] = expediente.pode_encaminhar(self.request.user)
        context['pode_marcar_recebido'] = expediente.pode_marcar_recebido(self.request.user)
        context['pode_editar'] = expediente.pode_editar(self.request.user)
        
        # NOVO: Adicionar ações disponíveis
        context['acoes_disponiveis'] = expediente.obter_acoes_disponiveis(self.request.user)
        
        # NOVO: Adicionar cor do estado atual
        if expediente.estado_atual:
            context['cor_estado_atual'] = expediente.estado_atual.cor
        else:
            context['cor_estado_atual'] = '#6c757d'  # Cor padrão cinza
        
        anexos = expediente.anexos.all()
        # Adicionar propriedade para cada anexo indicando se pode ser assinado pelo usuário atual
        anexos_com_info = []
        for anexo in anexos:
            anexo.pode_ser_assinado_por_usuario = (
                self.request.user.tipo_utilizador in ['pca', 'secretaria', 'chefe'] and
                anexo.pode_ser_assinado() and
                anexo.pode_assinador_acessar(self.request.user)
            )
            anexos_com_info.append(anexo)
        
        context['anexos'] = anexos_com_info
        context['historico'] = expediente.historico.all()[:10]
        context['sectores_envolvidos'] = expediente.sectores_envolvidos.all()
        context['membros_envolvidos'] = expediente.membros_envolvidos.all()
        context['movimentacoes'] = expediente.movimentacoes.all().order_by('-data_movimentacao')
        
        # Adicionar contexto para assinatura digital
        context['pode_assinar_anexo'] = self.request.user.tipo_utilizador in ['pca', 'secretaria', 'chefe']
        context['user'] = self.request.user  # Adicionar user ao contexto para usar nos templates
        
        return context


class EditarExpedienteView(LoginRequiredMixin, UpdateView):
    """
    View para editar expediente
    """
    model = Expediente
    form_class = EditarExpedienteForm
    template_name = 'entrada/editar_expediente.html'
    success_url = reverse_lazy('entrada:lista_expedientes')
    
    def form_valid(self, form):
        expediente = form.save()
        
        # Criar entrada no histórico
        HistoricoExpediente.objects.create(
            expediente=expediente,
            acao='Expediente editado',
            descricao='Dados do expediente foram alterados',
            usuario=self.request.user,
            estado_anterior=expediente.status,
            estado_novo=expediente.status
        )
        
        messages.success(self.request, f'✅ Expediente {expediente.numero_protocolo} atualizado com sucesso! As alterações foram salvas.')
        return super().form_valid(form)


class DeletarExpedienteView(LoginRequiredMixin, DeleteView):
    """
    View para deletar expediente
    """
    model = Expediente
    template_name = 'entrada/confirmar_deletar_expediente.html'
    success_url = reverse_lazy('entrada:lista_expedientes')
    
    def delete(self, request, *args, **kwargs):
        expediente = self.get_object()
        
        # Criar entrada no histórico
        HistoricoExpediente.objects.create(
            expediente=expediente,
            acao='Expediente deletado',
            descricao='Expediente foi removido do sistema',
            usuario=request.user,
            estado_anterior=expediente.status,
            estado_novo='deletado'
        )
        
        messages.success(request, f'Expediente {expediente.numero_protocolo} deletado com sucesso!')
        return super().delete(request, *args, **kwargs)


# Views para Tipos de Documento
class ListarTiposDocumentoView(LoginRequiredMixin, ListView):
    """
    View para listar tipos de documento
    """
    model = TipoDocumento
    template_name = 'entrada/lista_tipos_documento.html'
    context_object_name = 'tipos'
    paginate_by = 20


class CriarTipoDocumentoView(FormAlertMixin, LoginRequiredMixin, CreateView):
    """
    View para criar tipo de documento
    """
    model = TipoDocumento
    form_class = TipoDocumentoForm
    template_name = 'entrada/criar_tipo_documento.html'
    success_url = reverse_lazy('entrada:lista_tipos_documento')
    
    def get_success_message(self):
        return f'Tipo de documento "{self.object.nome}" criado com sucesso!'


class EditarTipoDocumentoView(FormAlertMixin, LoginRequiredMixin, UpdateView):
    """
    View para editar tipo de documento
    """
    model = TipoDocumento
    form_class = TipoDocumentoForm
    template_name = 'entrada/editar_tipo_documento.html'
    success_url = reverse_lazy('entrada:lista_tipos_documento')
    
    def get_success_message(self):
        return f'Tipo de documento "{self.object.nome}" atualizado com sucesso!'


class DeletarTipoDocumentoView(LoginRequiredMixin, DeleteView):
    """
    View para deletar tipo de documento
    """
    model = TipoDocumento
    template_name = 'entrada/confirmar_deletar_tipo_documento.html'
    success_url = reverse_lazy('entrada:lista_tipos_documento')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, f'🗑️ Tipo de documento "{self.get_object().nome}" deletado com sucesso!')
        return super().delete(request, *args, **kwargs)


# Views de Encaminhamento conforme checklist
class EncaminharPCAParaSectorView(LoginRequiredMixin, View):
    """
    View para PCA e Secretaria encaminharem documento para sector
    """
    def get(self, request, pk):
        documento = get_object_or_404(Expediente, pk=pk)
        if not documento.pode_encaminhar(request.user):
            messages.error(request, f'❌ Acesso negado: Você não tem permissão para encaminhar o expediente {documento.numero_protocolo}. Apenas PCA, Secretaria e Chefes de Setor podem encaminhar documentos.')
            return redirect('entrada:lista_expedientes')
        
        form = EncaminhamentoForm()
        context = {
            'documento': documento,
            'form': form,
            'titulo': 'Encaminhar para Sector'
        }
        return render(request, 'entrada/encaminhamento_form.html', context)
    
    def post(self, request, pk):
        documento = get_object_or_404(Expediente, pk=pk)
        if not documento.pode_encaminhar(request.user):
            messages.error(request, f'❌ Acesso negado: Você não tem permissão para encaminhar o expediente {documento.numero_protocolo}. Apenas PCA, Secretaria e Chefes de Setor podem encaminhar documentos.')
            return redirect('entrada:lista_expedientes')
        
        form = EncaminhamentoForm(request.POST)
        if form.is_valid():
            # Implementar lógica de encaminhamento
            sector_destino = form.cleaned_data.get('sector_destino')
            observacoes = form.cleaned_data.get('observacoes', '')
            
            # Buscar o chefe do sector de destino
            chefe_sector = None
            if sector_destino and sector_destino.chefe:
                chefe_sector = sector_destino.chefe
            
            # Criar movimentação
            from .models import MovimentacaoDocumento
            from core.models import EstadoDocumento
            from core.utils import enviar_notificacao
            
            # Buscar estado "Encaminhado"
            estado_encaminhado = EstadoDocumento.objects.filter(nome='Encaminhado').first()
            if estado_encaminhado:
                documento.estado_atual = estado_encaminhado
                documento.sector_responsavel = sector_destino
            # Definir chefe do sector como responsável atual
            if chefe_sector:
                documento.utilizador_atual = chefe_sector
            documento.save()
            
            # ADICIONAR ESTAS LINHAS APÓS O SAVE:
            if chefe_sector:
                documento.membros_envolvidos.add(chefe_sector)
            
            # Criar movimentação
            MovimentacaoDocumento.objects.create(
                documento=documento,
                de_utilizador=request.user,
                de_sector=request.user.sector_atual,
                para_sector=sector_destino,
                para_utilizador=chefe_sector,
                estado_anterior=documento.estado_atual,
                estado_novo=estado_encaminhado,
                observacoes=observacoes,
                tipo_movimentacao='encaminhamento'
            )
            
            # Enviar notificação para o chefe do sector
            if chefe_sector:
                enviar_notificacao(
                    destinatario=chefe_sector,
                    titulo="Documento Encaminhado",
                    mensagem=f"O documento {documento.numero_protocolo} foi encaminhado para o seu sector ({sector_destino.nome})",
                    tipo='documento_encaminhado',
                    documento=documento,
                    prioridade='normal'
                )
            
            messages.success(request, f'📤 Expediente {documento.numero_protocolo} encaminhado para {sector_destino.nome} com sucesso! O chefe do sector receberá uma notificação.')
            return redirect('entrada:detalhar_expediente', pk=pk)
        
        context = {
            'documento': documento,
            'form': form,
            'titulo': 'Encaminhar para Sector'
        }
        return render(request, 'entrada/encaminhamento_form.html', context)


class EncaminharChefeParaColaboradorView(LoginRequiredMixin, View):
    """
    View para Chefe encaminhar documento para colaborador do seu sector
    OU para Colaborador encaminhar para seu chefe
    """
    def get(self, request, pk):
        documento = get_object_or_404(Expediente, pk=pk)
        if not documento.pode_encaminhar(request.user):
            messages.error(request, f'❌ Acesso negado: Você não tem permissão para encaminhar o expediente {documento.numero_protocolo}. Apenas PCA, Secretaria e Chefes de Setor podem encaminhar documentos.')
            return redirect('entrada:lista_expedientes')
        
        # Determinar opções de encaminhamento baseado no tipo de usuário
        if request.user.tipo_utilizador == 'chefe':
            # Chefe pode encaminhar para colaboradores do seu sector OU devolver ao PCA
            from django.db.models import Q
            colaboradores = User.objects.filter(
                Q(sector_atual=request.user.sector_atual, tipo_utilizador='colaborador', ativo=True) |
                Q(tipo_utilizador='pca', ativo=True)
            )
            titulo = 'Encaminhar para Colaborador ou PCA'
        elif request.user.tipo_utilizador == 'colaborador':
            # Colaborador pode encaminhar apenas para seu chefe
            chefe = User.objects.filter(
                sector_atual=request.user.sector_atual,
                tipo_utilizador='chefe',
                ativo=True
            ).first()
            colaboradores = User.objects.filter(pk=chefe.pk) if chefe else User.objects.none()
            titulo = 'Encaminhar para Chefe'
        else:
            # PCA/Secretaria podem encaminhar para qualquer um
            colaboradores = User.objects.filter(ativo=True)
            titulo = 'Encaminhar Documento'
        
        form = EncaminhamentoForm()
        form.fields['utilizador_destino'].queryset = colaboradores
        
        context = {
            'documento': documento,
            'form': form,
            'titulo': titulo
        }
        return render(request, 'entrada/encaminhamento_form.html', context)
    
    def post(self, request, pk):
        documento = get_object_or_404(Expediente, pk=pk)
        if not documento.pode_encaminhar(request.user):
            messages.error(request, f'❌ Acesso negado: Você não tem permissão para encaminhar o expediente {documento.numero_protocolo}. Apenas PCA, Secretaria e Chefes de Setor podem encaminhar documentos.')
            return redirect('entrada:lista_expedientes')
        
        form = EncaminhamentoForm(request.POST)
        if form.is_valid():
            utilizador_destino = form.cleaned_data.get('utilizador_destino')
            observacoes = form.cleaned_data.get('observacoes', '')
            
            # Verificar se utilizador_destino foi selecionado
            if not utilizador_destino:
                messages.error(request, '❌ Por favor, selecione um destinatário para o encaminhamento.')
                return redirect('entrada:encaminhar_chefe_colaborador', pk=pk)
            
            # Validações específicas por tipo de usuário
            if request.user.tipo_utilizador == 'chefe':
                # Chefe pode encaminhar para colaboradores OU PCA
                if utilizador_destino.tipo_utilizador == 'colaborador':
                    if utilizador_destino.sector_atual != request.user.sector_atual:
                        messages.error(request, 'Você só pode encaminhar para colaboradores do seu sector.')
                        return redirect('entrada:encaminhar_chefe_colaborador', pk=pk)
                elif utilizador_destino.tipo_utilizador != 'pca':
                    messages.error(request, 'Você só pode encaminhar para colaboradores do seu sector ou devolver ao PCA.')
                    return redirect('entrada:encaminhar_chefe_colaborador', pk=pk)
                    
            elif request.user.tipo_utilizador == 'colaborador':
                # Colaborador só pode encaminhar para seu chefe
                if utilizador_destino.tipo_utilizador != 'chefe':
                    messages.error(request, 'Você só pode encaminhar para seu chefe.')
                    return redirect('entrada:encaminhar_chefe_colaborador', pk=pk)
                if utilizador_destino.sector_atual != request.user.sector_atual:
                    messages.error(request, 'Você só pode encaminhar para o chefe do seu sector.')
                    return redirect('entrada:encaminhar_chefe_colaborador', pk=pk)
            
            # Atualizar documento
            documento.utilizador_atual = utilizador_destino
            documento.sector_responsavel = utilizador_destino.sector_atual
            documento.save()
            
            # Criar movimentação
            from .models import MovimentacaoDocumento
            
            MovimentacaoDocumento.objects.create(
                documento=documento,
                de_utilizador=request.user,
                de_sector=request.user.sector_atual,
                para_utilizador=utilizador_destino,
                para_sector=utilizador_destino.sector_atual,
                observacoes=observacoes,
                tipo_movimentacao='encaminhamento'
            )
            
            # Adicionar destinatário e remetente aos membros envolvidos
            documento.membros_envolvidos.add(utilizador_destino)
            documento.membros_envolvidos.add(request.user)
            
            # Enviar notificações
            from core.utils import enviar_notificacao
            
            # Notificar o destinatário
            enviar_notificacao(
                destinatario=utilizador_destino,
                titulo="Documento Encaminhado",
                mensagem=f"O documento {documento.numero_protocolo} foi encaminhado para você por {request.user.get_full_name()}",
                tipo='documento_encaminhado',
                documento=documento,
                prioridade='normal'
            )
            
            # Notificar o usuário atual (confirmação)
            enviar_notificacao(
                destinatario=request.user,
                titulo="Encaminhamento Confirmado",
                mensagem=f"O documento {documento.numero_protocolo} foi encaminhado com sucesso para {utilizador_destino.get_full_name()}",
                tipo='documento_encaminhado',
                documento=documento,
                prioridade='normal'
            )
            
            messages.success(request, f'👤 Expediente {documento.numero_protocolo} encaminhado para {utilizador_destino.get_full_name()} com sucesso! O utilizador receberá uma notificação.')
            return redirect('entrada:detalhar_expediente', pk=pk)
        
        # Determinar título baseado no tipo de usuário
        titulo = 'Encaminhar para Colaborador' if request.user.tipo_utilizador == 'chefe' else 'Encaminhar para Chefe'
        
        context = {
            'documento': documento,
            'form': form,
            'titulo': titulo
        }
        return render(request, 'entrada/encaminhamento_form.html', context)


class DevolverDocumentoView(LoginRequiredMixin, View):
    """
    View para devolver documento ao PCA ou Chefe
    """
    def get(self, request, pk):
        documento = get_object_or_404(Expediente, pk=pk)
        form = EncaminhamentoForm()
        context = {
            'documento': documento,
            'form': form,
            'titulo': 'Devolver Documento'
        }
        return render(request, 'entrada/encaminhamento_form.html', context)
    
    def post(self, request, pk):
        documento = get_object_or_404(Expediente, pk=pk)
        form = EncaminhamentoForm(request.POST)
        if form.is_valid():
            observacoes = form.cleaned_data.get('observacoes', '')
            
            # Determinar destino da devolução
            if request.user.tipo_utilizador == 'colaborador':
                # Colaborador devolve para o chefe
                chefe_sector = User.objects.filter(
                    sector_atual=request.user.sector_atual,
                    tipo_utilizador='chefe'
                ).first()
                if chefe_sector:
                    destino_utilizador = chefe_sector
                    destino_sector = chefe_sector.sector_atual
                else:
                    messages.error(request, 'Chefe do sector não encontrado.')
                    return redirect('entrada:detalhar_expediente', pk=pk)
            else:
                # Chefe devolve para PCA
                pca = User.objects.filter(tipo_utilizador='pca').first()
                if pca:
                    destino_utilizador = pca
                    destino_sector = pca.sector_atual
                else:
                    messages.error(request, 'PCA não encontrado.')
                    return redirect('entrada:detalhar_expediente', pk=pk)
            
            # Transferir posse do documento
            documento.utilizador_atual = destino_utilizador
            documento.sector_responsavel = destino_sector
            
            # Mudar estado para Encaminhado após devolução
            from .models import EstadoDocumento
            estado_encaminhado = EstadoDocumento.objects.get(nome='Encaminhado')
            documento.estado_atual = estado_encaminhado
            
            documento.save()
            
            # Adicionar destinatário e remetente aos membros envolvidos
            documento.membros_envolvidos.add(destino_utilizador)
            documento.membros_envolvidos.add(request.user)
            
            # Criar movimentação
            from .models import MovimentacaoDocumento
            
            MovimentacaoDocumento.objects.create(
                documento=documento,
                de_utilizador=request.user,
                de_sector=request.user.sector_atual,
                para_utilizador=destino_utilizador,
                para_sector=destino_sector,
                observacoes=observacoes,
                tipo_movimentacao='devolucao'
            )
            
            # Enviar notificação para o destinatário
            from core.utils import enviar_notificacao
            
            enviar_notificacao(
                destinatario=destino_utilizador,
                titulo=f'📄 Documento Devolvido: {documento.numero_protocolo}',
                mensagem=f'O documento "{documento.assunto}" foi devolvido por {request.user.get_full_name()}. Você é agora o responsável pelo tratamento.',
                tipo='devolucao',
                documento=documento,
                remetente=request.user,
                prioridade='normal'
            )
            
            messages.success(request, f'↩️ Expediente {documento.numero_protocolo} devolvido para {destino_utilizador.get_full_name()} com sucesso! O documento voltou ao responsável anterior.')
            return redirect('entrada:detalhar_expediente', pk=pk)
        
        context = {
            'documento': documento,
            'form': form,
            'titulo': 'Devolver Documento'
        }
        return render(request, 'entrada/encaminhamento_form.html', context)


class DevolverDocumentoInstantaneoView(LoginRequiredMixin, View):
    """
    View AJAX para devolver documento instantaneamente ao PCA ou Chefe sem formulário
    """
    def post(self, request, pk):
        documento = get_object_or_404(Expediente, pk=pk)
        try:
            # Determinar destino da devolução
            if request.user.tipo_utilizador == 'colaborador':
                # Colaborador devolve para o chefe
                chefe_sector = User.objects.filter(
                    sector_atual=request.user.sector_atual,
                    tipo_utilizador='chefe'
                ).first()
                if chefe_sector:
                    destino_utilizador = chefe_sector
                    destino_sector = chefe_sector.sector_atual
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Chefe do sector não encontrado.'
                    }, status=404)
            else:
                # Chefe ou Secretaria devolve para PCA
                pca = User.objects.filter(tipo_utilizador='pca').first()
                if pca:
                    destino_utilizador = pca
                    destino_sector = pca.sector_atual
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'PCA não encontrado.'
                    }, status=404)
            
            # Transferir posse do documento
            documento.utilizador_atual = destino_utilizador
            documento.sector_responsavel = destino_sector
            
            # Mudar estado para Encaminhado após devolução
            from .models import EstadoDocumento
            estado_encaminhado = EstadoDocumento.objects.get(nome='Encaminhado')
            documento.estado_atual = estado_encaminhado
            
            documento.save()
            
            # Adicionar destinatário e remetente aos membros envolvidos
            documento.membros_envolvidos.add(destino_utilizador)
            documento.membros_envolvidos.add(request.user)
            
            # Criar movimentação
            from .models import MovimentacaoDocumento
            
            MovimentacaoDocumento.objects.create(
                documento=documento,
                de_utilizador=request.user,
                de_sector=request.user.sector_atual,
                para_utilizador=destino_utilizador,
                para_sector=destino_sector,
                observacoes='Documento devolvido instantaneamente',
                tipo_movimentacao='devolucao'
            )
            
            # Enviar notificação para o destinatário
            from core.utils import enviar_notificacao
            import logging
            logger = logging.getLogger(__name__)
            
            try:
                logger.info(f"Enviando notificação de devolução para {destino_utilizador.get_full_name()} (ID: {destino_utilizador.id})")
                
                notificacao = enviar_notificacao(
                    destinatario=destino_utilizador,
                    titulo=f'📄 Documento Devolvido: {documento.numero_protocolo}',
                    mensagem=f'O documento "{documento.assunto}" foi devolvido por {request.user.get_full_name()}. Você é agora o responsável pelo tratamento.',
                    tipo='documento_devolvido',
                    documento=documento,
                    remetente=request.user,
                    prioridade='normal'
                )
                
                logger.info(f"Notificação criada com sucesso: ID {notificacao.id}")
            except Exception as e:
                logger.error(f"Erro ao enviar notificação: {e}")
                import traceback
                logger.error(traceback.format_exc())
            
            return JsonResponse({
                'success': True,
                'message': f'↩️ Documento devolvido para {destino_utilizador.get_full_name()} com sucesso! Notificação enviada.',
                'novo_membro_atual': destino_utilizador.get_full_name(),
                'novo_estado': documento.estado_atual.nome
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao devolver documento: {str(e)}'
            }, status=500)


@login_required
def marcar_como_recebido(request, pk):
    """
    View para marcar documento como recebido
    """
    documento = get_object_or_404(Expediente, pk=pk)
    
    if not documento.pode_visualizar(request.user):
        messages.error(request, f'❌ Acesso negado: Você não tem permissão para visualizar o expediente {documento.numero_protocolo}. Verifique suas permissões de acesso.')
        return redirect('entrada:lista_expedientes')
    
    # Marcar como recebido
    documento.marcar_como_recebido(request.user)
    
    # Criar movimentação
    from .models import MovimentacaoDocumento
    from core.models import EstadoDocumento
    
    estado_recebido = EstadoDocumento.objects.filter(nome='Recebido').first()
    if estado_recebido:
        documento.estado_atual = estado_recebido
        documento.save()
    
    MovimentacaoDocumento.objects.create(
        documento=documento,
        para_utilizador=request.user,
        para_sector=request.user.sector_atual,
        estado_novo=estado_recebido,
        observacoes='Documento marcado como recebido',
        tipo_movimentacao='recebimento'
    )
    
    messages.success(request, f'✅ Expediente {documento.numero_protocolo} marcado como recebido! O documento está agora sob sua responsabilidade.')
    return redirect('entrada:detalhar_expediente', pk=pk)


# Views de Portal Externo
class PortalExpedienteView(View):
    """
    View para portal externo de submissão de expedientes
    """
    def get(self, request):
        form = PortalExpedienteForm()
        context = {
            'form': form,
            'titulo': 'Portal de Expedientes'
        }
        return render(request, 'entrada/portal_expediente.html', context)
    
    def post(self, request):
        form = PortalExpedienteForm(request.POST, request.FILES)
        if form.is_valid():
            # Criar expediente
            expediente = Expediente.objects.create(
                tipo=form.cleaned_data['tipo_documento'],
                origem='portal',
                remetente=form.cleaned_data['nome_remetente'],
                assunto=form.cleaned_data['assunto'],
                conteudo=form.cleaned_data['conteudo'],
                telefone=form.cleaned_data.get('telefone', ''),
                prioridade='normal',
                requer_resposta=True,
                confidencial=False,
                criado_por=None,  # Usuário externo
                sector_responsavel=None,  # Será definido pelo PCA
                estado_atual=None,  # Será definido pelo sistema
                status='submetido'
            )
            
            # Processar anexos se houver
            anexos = request.FILES.getlist('anexos')
            for anexo in anexos:
                AnexoExpediente.objects.create(
                    expediente=expediente,
                    arquivo=anexo,
                    nome_original=anexo.name,
                    tamanho=anexo.size,
                    tipo_mime=anexo.content_type,
                    upload_por=None  # Usuário externo
                )
            
            messages.success(request, f'Expediente {expediente.numero_protocolo} submetido com sucesso!')
            return redirect('entrada:portal_success', pk=expediente.pk)
        
        context = {
            'form': form,
            'titulo': 'Portal de Expedientes'
        }
        return render(request, 'entrada/portal_expediente.html', context)


class PortalSuccessView(DetailView):
    """
    View para página de sucesso do portal
    """
    model = Expediente
    template_name = 'entrada/portal_success.html'
    context_object_name = 'expediente'


# Views de Tratamento de Documentos
class IniciarTratamentoDocumentoView(LoginRequiredMixin, View):
    """
    View para iniciar tratamento de documento
    """
    def post(self, request, pk):
        expediente = get_object_or_404(Expediente, pk=pk)
        
        # Verificar permissões
        if not expediente.pode_visualizar(request.user):
            messages.error(request, f'❌ Acesso negado: Você não tem permissão para tratar o expediente {expediente.numero_protocolo}. Apenas usuários autorizados podem iniciar tratamento.')
            return redirect('entrada:lista_expedientes')
        
        try:
            # Buscar estado "Em Tratamento"
            from core.models import EstadoDocumento
            estado_tratamento = EstadoDocumento.objects.filter(nome='Em Tratamento').first()
            
            if estado_tratamento:
                # Mudar para estado "Em Tratamento"
                expediente.estado_atual = estado_tratamento
                expediente.utilizador_atual = request.user
                expediente.data_ultima_atualizacao = timezone.now()
                expediente.save()
                
                # Adicionar utilizador aos membros envolvidos
                expediente.membros_envolvidos.add(request.user)
                
                # Criar movimentação
                MovimentacaoDocumento.objects.create(
                    documento=expediente,
                    de_utilizador=request.user,
                    de_sector=request.user.sector_atual,
                    tipo_movimentacao='recebimento',
                    observacoes='Início do tratamento',
                    automatica=False
                )
                
                messages.success(request, f'✅ Expediente {expediente.numero_protocolo} iniciado em tratamento! O documento está agora sob sua responsabilidade.')
            else:
                messages.error(request, 'Estado "Em Tratamento" não encontrado.')
            
        except Exception as e:
            messages.error(request, f'Erro ao iniciar tratamento: {str(e)}')
        
        return redirect('entrada:detalhar_expediente', pk=pk)


class ConcluirDocumentoView(LoginRequiredMixin, View):
    """
    View para concluir tratamento de documento
    """
    def post(self, request, pk):
        expediente = get_object_or_404(Expediente, pk=pk)
        
        # Verificar permissões
        if not expediente.pode_visualizar(request.user):
            messages.error(request, 'Você não tem permissão para concluir este documento.')
            return redirect('entrada:lista_expedientes')
        
        try:
            # Buscar estado "Concluído"
            from core.models import EstadoDocumento
            estado_concluido = EstadoDocumento.objects.filter(nome='Concluído').first()
            
            if estado_concluido:
                # Mudar para estado "Concluído"
                expediente.estado_atual = estado_concluido
                expediente.data_aprovacao = timezone.now()
                expediente.data_ultima_atualizacao = timezone.now()
                expediente.save()
                
                # Criar movimentação
                MovimentacaoDocumento.objects.create(
                    documento=expediente,
                    de_utilizador=request.user,
                    de_sector=request.user.sector_atual,
                    tipo_movimentacao='conclusao',
                    observacoes='Documento concluído',
                    automatica=False
                )
                
                messages.success(request, f'✅ Expediente {expediente.numero_protocolo} concluído com sucesso! O documento foi finalizado e está pronto para arquivamento.')
            else:
                messages.error(request, 'Estado "Concluído" não encontrado.')
            
            # Notificar PCA
            usuarios_pca = User.objects.filter(tipo_utilizador='pca', ativo=True)
            for pca in usuarios_pca:
                enviar_notificacao(
                    destinatario=pca,
                    titulo="Documento Concluído",
                    mensagem=f"O expediente {expediente.numero_protocolo} foi concluído por {request.user.get_full_name()}",
                    tipo='documento_concluido',
                    documento=expediente,
                    prioridade='normal'
                )
            
        except Exception as e:
            messages.error(request, f'Erro ao concluir documento: {str(e)}')
        
        return redirect('entrada:detalhar_expediente', pk=pk)


class ReabrirDocumentoView(LoginRequiredMixin, View):
    """
    View para reabrir documento arquivado ou concluído
    """
    def post(self, request, pk):
        expediente = get_object_or_404(Expediente, pk=pk)
        
        # Verificar permissões (apenas PCA e Secretaria)
        if request.user.tipo_utilizador not in ['pca', 'secretaria']:
            messages.error(request, 'Você não tem permissão para reabrir este documento.')
            return redirect('entrada:detalhar_expediente', pk=pk)
        
        try:
            # Buscar estado "Em Tratamento"
            from core.models import EstadoDocumento
            estado_tratamento = EstadoDocumento.objects.filter(nome='Em Tratamento').first()
            
            if estado_tratamento:
                # Mudar para estado "Em Tratamento"
                expediente.estado_atual = estado_tratamento
                expediente.utilizador_atual = request.user
                expediente.data_ultima_atualizacao = timezone.now()
                expediente.save()
                
                # Adicionar utilizador aos membros envolvidos
                expediente.membros_envolvidos.add(request.user)
                
                # Criar movimentação
                MovimentacaoDocumento.objects.create(
                    expediente=expediente,
                    utilizador_origem=request.user,
                    utilizador_destino=request.user,
                    acao='reabrir',
                    observacoes=f'Documento reaberto por {request.user.get_full_name()}'
                )
                
                messages.success(request, f'🔄 Expediente {expediente.numero_protocolo} reaberto com sucesso! O documento voltou ao estado "Em Tratamento" e pode ser processado novamente.')
            else:
                messages.error(request, 'Estado "Em Tratamento" não encontrado.')
                
        except Exception as e:
            messages.error(request, f'Erro ao reabrir documento: {str(e)}')
        
        return redirect('entrada:detalhar_expediente', pk=pk)


class ArquivarDocumentoView(LoginRequiredMixin, View):
    """
    View para arquivar documento (PCA e Secretaria)
    """
    def post(self, request, pk):
        expediente = get_object_or_404(Expediente, pk=pk)
        
        # Verificar se é PCA ou Secretaria
        if request.user.tipo_utilizador not in ['pca', 'secretaria']:
            messages.error(request, 'Apenas o PCA e Secretaria podem arquivar documentos.')
            return redirect('entrada:lista_expedientes')
        
        try:
            # Marcar como arquivado
            expediente.status = 'arquivado'
            expediente.utilizador_atual = None
            
            # Buscar estado "Arquivado"
            from core.models import EstadoDocumento
            estado_arquivado = EstadoDocumento.objects.filter(nome='Arquivado').first()
            if estado_arquivado:
                expediente.estado_atual = estado_arquivado
            
            expediente.save()
            
            # Criar movimentação
            MovimentacaoDocumento.objects.create(
                documento=expediente,
                de_utilizador=request.user,
                de_sector=request.user.sector_atual,
                tipo_movimentacao='arquivamento',
                observacoes='Documento arquivado pelo PCA',
                automatica=False
            )
            
            messages.success(request, f'✅ Expediente {expediente.numero_protocolo} arquivado com sucesso! O documento foi movido para o arquivo permanente.')
            
        except Exception as e:
            messages.error(request, f'Erro ao arquivar documento: {str(e)}')
        
        return redirect('entrada:lista_expedientes')


class HistoricoMovimentacaoView(LoginRequiredMixin, DetailView):
    """
    View para visualizar histórico de movimentações
    """
    model = Expediente
    template_name = 'entrada/historico_movimentacao.html'
    context_object_name = 'expediente'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expediente = self.get_object()
        
        # Verificar permissões
        if not expediente.pode_visualizar(self.request.user):
            raise PermissionDenied("Você não tem permissão para visualizar este documento.")
        
        context['movimentacoes'] = expediente.movimentacoes.all().order_by('-data_movimentacao')
        return context


# Views para Pareceres
class CriarParecerView(LoginRequiredMixin, View):
    """
    View para criar parecer sobre expediente
    """
    def get(self, request, pk):
        expediente = get_object_or_404(Expediente, pk=pk)
        
        # Verificar se pode criar parecer
        if not expediente.pode_visualizar(request.user):
            messages.error(request, f'❌ Acesso negado: Você não tem permissão para criar parecer no expediente {expediente.numero_protocolo}. Verifique suas permissões de acesso.')
            return redirect('entrada:detalhar_expediente', pk=pk)
        
        form = ParecerExpedienteForm()
        context = {
            'expediente': expediente,
            'form': form,
            'titulo': 'Criar Parecer'
        }
        return render(request, 'entrada/parecer_form.html', context)
    
    def post(self, request, pk):
        expediente = get_object_or_404(Expediente, pk=pk)
        
        # Verificar se pode criar parecer
        if not expediente.pode_visualizar(request.user):
            messages.error(request, f'❌ Acesso negado: Você não tem permissão para criar parecer no expediente {expediente.numero_protocolo}. Verifique suas permissões de acesso.')
            return redirect('entrada:detalhar_expediente', pk=pk)
        
        form = ParecerExpedienteForm(request.POST)
        if form.is_valid():
            parecer = form.save(commit=False)
            parecer.expediente = expediente
            parecer.parecerista = request.user
            parecer.save()
            
            # Criar movimentação
            MovimentacaoDocumento.objects.create(
                documento=expediente,
                de_utilizador=request.user,
                de_sector=request.user.sector_atual,
                observacoes=f"Parecer criado: {parecer.titulo}",
                tipo_movimentacao='parecer'
            )
            
            # Enviar notificações
            # Notificar PCA e Secretaria
            usuarios_admin = User.objects.filter(tipo_utilizador__in=['pca', 'secretaria'], ativo=True)
            for admin in usuarios_admin:
                enviar_notificacao(
                    destinatario=admin,
                    titulo="Novo Parecer Criado",
                    mensagem=f"Foi criado um parecer para o expediente {expediente.numero_protocolo} por {request.user.get_full_name()}",
                    tipo='documento_novo',
                    documento=expediente,
                    prioridade='normal'
                )
            
            # Notificar chefe do sector (se diferente do parecerista)
            if expediente.sector_responsavel and expediente.sector_responsavel.chefe != request.user:
                enviar_notificacao(
                    destinatario=expediente.sector_responsavel.chefe,
                    titulo="Novo Parecer no Sector",
                    mensagem=f"Foi criado um parecer para o expediente {expediente.numero_protocolo} no seu sector",
                    tipo='documento_novo',
                    documento=expediente,
                    prioridade='normal'
                )
            
            messages.success(request, f'💬 Parecer sobre expediente {expediente.numero_protocolo} criado com sucesso! O parecer foi registrado e notificações enviadas.')
            return redirect('entrada:detalhar_expediente', pk=pk)
        
        context = {
            'expediente': expediente,
            'form': form,
            'titulo': 'Criar Parecer'
        }
        return render(request, 'entrada/parecer_form.html', context)


class EditarParecerView(LoginRequiredMixin, View):
    """
    View para editar parecer
    """
    def get(self, request, pk, parecer_id):
        expediente = get_object_or_404(Expediente, pk=pk)
        parecer = get_object_or_404(ParecerExpediente, pk=parecer_id, expediente=expediente)
        
        # Verificar permissões
        if not parecer.pode_editar(request.user):
            messages.error(request, 'Você não tem permissão para editar este parecer.')
            return redirect('entrada:detalhar_expediente', pk=pk)
        
        form = ParecerExpedienteForm(instance=parecer)
        context = {
            'expediente': expediente,
            'parecer': parecer,
            'form': form,
            'titulo': 'Editar Parecer'
        }
        return render(request, 'entrada/parecer_form.html', context)
    
    def post(self, request, pk, parecer_id):
        expediente = get_object_or_404(Expediente, pk=pk)
        parecer = get_object_or_404(ParecerExpediente, pk=parecer_id, expediente=expediente)
        
        # Verificar permissões
        if not parecer.pode_editar(request.user):
            messages.error(request, 'Você não tem permissão para editar este parecer.')
            return redirect('entrada:detalhar_expediente', pk=pk)
        
        form = ParecerExpedienteForm(request.POST, instance=parecer)
        if form.is_valid():
            form.save()
            messages.success(request, f'✏️ Parecer sobre expediente {expediente.numero_protocolo} atualizado com sucesso! As alterações foram salvas.')
            return redirect('entrada:detalhar_expediente', pk=pk)
        
        context = {
            'expediente': expediente,
            'parecer': parecer,
            'form': form,
            'titulo': 'Editar Parecer'
        }
        return render(request, 'entrada/parecer_form.html', context)


class ImplementarParecerView(LoginRequiredMixin, View):
    """
    View para implementar parecer
    """
    def get(self, request, pk, parecer_id):
        expediente = get_object_or_404(Expediente, pk=pk)
        parecer = get_object_or_404(ParecerExpediente, pk=parecer_id, expediente=expediente)
        
        # Verificar permissões
        if not parecer.pode_implementar(request.user):
            messages.error(request, 'Você não tem permissão para implementar este parecer.')
            return redirect('entrada:detalhar_expediente', pk=pk)
        
        if parecer.implementado:
            messages.error(request, 'Este parecer já foi implementado.')
            return redirect('entrada:detalhar_expediente', pk=pk)
        
        form = ImplementarParecerForm()
        context = {
            'expediente': expediente,
            'parecer': parecer,
            'form': form,
            'titulo': 'Implementar Parecer'
        }
        return render(request, 'entrada/implementar_parecer_form.html', context)
    
    def post(self, request, pk, parecer_id):
        expediente = get_object_or_404(Expediente, pk=pk)
        parecer = get_object_or_404(ParecerExpediente, pk=parecer_id, expediente=expediente)
        
        # Verificar permissões
        if not parecer.pode_implementar(request.user):
            messages.error(request, 'Você não tem permissão para implementar este parecer.')
            return redirect('entrada:detalhar_expediente', pk=pk)
        
        if parecer.implementado:
            messages.error(request, 'Este parecer já foi implementado.')
            return redirect('entrada:detalhar_expediente', pk=pk)
        
        form = ImplementarParecerForm(request.POST)
        if form.is_valid():
            parecer.implementado = True
            parecer.data_implementacao = form.cleaned_data['data_implementacao']
            parecer.implementado_por = request.user
            parecer.save()
            
            # Criar movimentação
            MovimentacaoDocumento.objects.create(
                documento=expediente,
                de_utilizador=request.user,
                de_sector=request.user.sector_atual,
                observacoes=f"Parecer implementado: {parecer.titulo}",
                tipo_movimentacao='parecer'
            )
            
            # Enviar notificações
            # Notificar parecerista
            enviar_notificacao(
                destinatario=parecer.parecerista,
                titulo="Parecer Implementado",
                mensagem=f"Seu parecer '{parecer.titulo}' foi implementado por {request.user.get_full_name()}",
                tipo='documento_concluido',
                documento=expediente,
                prioridade='normal'
            )
            
            # Notificar PCA e Secretaria
            usuarios_admin = User.objects.filter(tipo_utilizador__in=['pca', 'secretaria'], ativo=True)
            for admin in usuarios_admin:
                enviar_notificacao(
                    destinatario=admin,
                    titulo="Parecer Implementado",
                    mensagem=f"O parecer '{parecer.titulo}' foi implementado por {request.user.get_full_name()}",
                    tipo='documento_concluido',
                    documento=expediente,
                    prioridade='normal'
                )
            
            messages.success(request, f'🎯 Parecer sobre expediente {expediente.numero_protocolo} implementado com sucesso! O parecer foi marcado como executado.')
            return redirect('entrada:detalhar_expediente', pk=pk)
        
        context = {
            'expediente': expediente,
            'parecer': parecer,
            'form': form,
            'titulo': 'Implementar Parecer'
        }
        return render(request, 'entrada/implementar_parecer_form.html', context)


class HistoricoPareceresView(LoginRequiredMixin, View):
    """
    View para visualizar histórico de pareceres
    """
    def get(self, request, pk):
        expediente = get_object_or_404(Expediente, pk=pk)
        
        # Verificar permissões
        if not expediente.pode_visualizar(request.user):
            messages.error(request, 'Você não tem permissão para visualizar pareceres deste documento.')
            return redirect('entrada:detalhar_expediente', pk=pk)
        
        # Obter todos os pareceres ativos do expediente
        pareceres = expediente.pareceres.filter(ativo=True).order_by('-data_parecer')
        
        # Filtrar pareceres que o usuário pode visualizar
        pareceres_permitidos = [p for p in pareceres if p.pode_visualizar(request.user)]
        
        # Debug: log para verificar dados
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f'Expediente {pk}: Total de pareceres ativos: {pareceres.count()}, Permitidos: {len(pareceres_permitidos)}')
        
        context = {
            'expediente': expediente,
            'pareceres': pareceres_permitidos,
            'titulo': 'Histórico de Pareceres'
        }
        return render(request, 'entrada/historico_pareceres.html', context)