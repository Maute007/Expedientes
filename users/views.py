from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import View, TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from django.core.exceptions import PermissionDenied
from core.mixins import BaseViewMixin, FormAlertMixin, AlertMixin
from core.views_base import BaseListView
from .models import PerfilUtilizador, HierarquiaUtilizador
from .forms import (
    UserRegistrationForm, UserLoginForm, PerfilUtilizadorForm, 
    PerfilConfiguracoesForm, CriarUtilizadorForm, EditarUtilizadorForm, PasswordChangeFormCustomizada,
    PasswordResetFormCustomizada, SetPasswordFormCustomizada, HierarquiaUtilizadorForm
)

User = get_user_model()


class PortalPublicoView(TemplateView):
    """
    Portal público para registo e login de utilizadores.
    """
    template_name = 'users/portal_publico.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['registration_form'] = UserRegistrationForm()
        context['login_form'] = UserLoginForm()
        return context


class UserRegistrationView(View):
    """
    View para registo de utilizadores.
    """
    
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'users/registro.html', {'form': form})
    
    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Requer ativação pelo admin
            user.save()
            
            # Criar perfil de utilizador
            PerfilUtilizador.objects.create(
                utilizador=user,
                receber_notificacoes_email=True,
                receber_notificacoes_push=True,
                tema_preferido='claro',
                idioma_preferido='pt-pt',
                timezone='Africa/Maputo'
            )
            
            messages.success(
                request, 
                'Registo realizado com sucesso! Aguarde aprovação do administrador.'
            )
            return redirect('users:portal_publico')
        
        return render(request, 'users/registro.html', {'form': form})


class UserLoginViewCustomizada(AlertMixin, View):
    """
    View customizada para login de utilizadores.
    """
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        
        form = UserLoginForm()
        return render(request, 'users/login_simples.html', {'form': form})
    
    def post(self, request):
        print("=== LOGIN POST RECEBIDO ===")
        print(f"POST data: {request.POST}")
        form = UserLoginForm(request.POST)
        print(f"Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        
        if form.is_valid():
            email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)
            
            # Autenticar usando email (USERNAME_FIELD = 'email' no modelo)
            user = authenticate(request, username=email, password=password)
            print(f"Email: {email}, Password length: {len(password)}")
            print(f"Authenticated user: {user}")
            
            if user is not None:
                print(f"User is active: {user.is_active}")
                if user.is_active:
                    print("Logging in user...")
                    login(request, user)
                    print("User logged in")
                    
                    # Configurar sessão
                    if not remember_me:
                        request.session.set_expiry(0)  # Sessão expira ao fechar browser
                    else:
                        request.session.set_expiry(1209600)  # 2 semanas
                    
                    # Redirecionar para próxima página ou dashboard
                    next_url = request.GET.get('next', 'core:dashboard')
                    self.success_alert(f'Bem-vindo, {user.get_full_name()}!')
                    return redirect(next_url)
                else:
                    self.error_alert('Conta desativada. Contacte o administrador.')
            else:
                self.error_alert('Email ou senha incorretos.')
        else:
            # Log dos erros para debug
            print(f"Form errors: {form.errors}")
            self.error_alert('Por favor, corrija os erros abaixo.')
        
        return render(request, 'users/login_simples.html', {'form': form})


class UserLogoutViewCustomizada(AlertMixin, View):
    """
    View customizada para logout de utilizadores.
    """
    
    def get(self, request):
        user_name = request.user.get_full_name() if request.user.is_authenticated else 'Utilizador'
        logout(request)
        self.info_alert(f'Até logo, {user_name}!')
        return redirect('users:portal_publico')


class PerfilUtilizadorView(BaseViewMixin, LoginRequiredMixin, View):
    """
    View para visualizar perfil do utilizador.
    """
    template_name = 'users/perfil.html'
    
    def get(self, request):
        try:
            perfil = request.user.perfil
        except PerfilUtilizador.DoesNotExist:
            perfil = PerfilUtilizador.objects.create(utilizador=request.user)
        
        context = {
            'perfil': perfil,
            'hierarquia': HierarquiaUtilizador.objects.filter(
                Q(superior=request.user) | Q(subordinado=request.user)
            ).select_related('superior', 'subordinado')
        }
        return render(request, self.template_name, context)


class EditarPerfilView(BaseViewMixin, LoginRequiredMixin, View):
    """
    View para editar perfil do utilizador.
    """
    template_name = 'users/perfil_editar.html'
    
    def get(self, request):
        form = PerfilUtilizadorForm(instance=request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = PerfilUtilizadorForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Perfil de {request.user.get_full_name()} atualizado com sucesso!')
            return redirect('users:perfil')
        
        return render(request, self.template_name, {'form': form})


class ConfiguracoesPerfilView(BaseViewMixin, LoginRequiredMixin, View):
    """
    View para configurações do perfil.
    """
    template_name = 'users/perfil_configuracoes.html'
    
    def get(self, request):
        try:
            perfil = request.user.perfil
        except PerfilUtilizador.DoesNotExist:
            perfil = PerfilUtilizador.objects.create(utilizador=request.user)
        
        form = PerfilConfiguracoesForm(instance=perfil)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        try:
            perfil = request.user.perfil
        except PerfilUtilizador.DoesNotExist:
            perfil = PerfilUtilizador.objects.create(utilizador=request.user)
        
        form = PerfilConfiguracoesForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, f'⚙️ Configurações de {request.user.get_full_name()} salvas com sucesso!')
            return redirect('users:perfil_configuracoes')
        
        return render(request, self.template_name, {'form': form})


class ListarUtilizadoresView(BaseListView, LoginRequiredMixin):
    """
    View para listar utilizadores (APENAS ADMINISTRADORES).
    """
    model = User
    template_name = 'users/lista_utilizadores.html'
    context_object_name = 'utilizadores'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        """
        Verificar se o utilizador é administrador.
        """
        if not (request.user.is_superuser or request.user.tipo_utilizador == 'admin'):
            messages.error(request, '🚫 Acesso negado: Apenas administradores podem ver a lista de utilizadores.')
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = User.objects.select_related('sector_atual', 'perfil').all()
        
        # Filtros
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(cargo__icontains=search)
            )
        
        sector = self.request.GET.get('sector')
        if sector:
            queryset = queryset.filter(sector_atual_id=sector)
        
        status = self.request.GET.get('status')
        if status == 'ativo':
            queryset = queryset.filter(ativo=True)
        elif status == 'inativo':
            queryset = queryset.filter(ativo=False)
        
        # Ordenação
        order = self.request.GET.get('order', 'date_joined')
        if order in ['first_name', 'last_name', 'email', 'cargo', 'date_joined']:
            queryset = queryset.order_by(order)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from core.models import Sector
        
        context['sectores'] = Sector.objects.filter(ativo=True)
        context['search'] = self.request.GET.get('search', '')
        context['sector'] = self.request.GET.get('sector', '')
        context['status'] = self.request.GET.get('status', '')
        context['order'] = self.request.GET.get('order', 'date_joined')
        
        return context


class CriarUtilizadorView(FormAlertMixin, BaseViewMixin, LoginRequiredMixin, CreateView):
    """
    View para criar novo utilizador interno (APENAS ADMINISTRADORES).
    """
    model = User
    form_class = CriarUtilizadorForm
    template_name = 'users/criar_utilizador.html'
    success_url = reverse_lazy('users:lista_utilizadores')
    
    def dispatch(self, request, *args, **kwargs):
        """
        Verificar se o utilizador é administrador.
        """
        if not (request.user.is_superuser or request.user.tipo_utilizador == 'admin'):
            messages.error(request, 'Apenas administradores podem criar utilizadores internos.')
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        """
        Passar request para o form para validação.
        """
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_success_message(self):
        return f'Utilizador {self.object.get_full_name()} criado com sucesso!'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from core.models import Sector
        context['sectores'] = Sector.objects.filter(ativo=True)
        context['titulo_pagina'] = 'Criar Utilizador Interno'
        context['descricao_pagina'] = 'Apenas administradores podem criar utilizadores internos. Utilizadores externos devem registar-se no portal público.'
        return context


class EditarUtilizadorView(FormAlertMixin, BaseViewMixin, LoginRequiredMixin, UpdateView):
    """
    View para editar utilizador (APENAS ADMINISTRADORES).
    """
    model = User
    form_class = EditarUtilizadorForm
    template_name = 'users/editar_utilizador.html'
    success_url = reverse_lazy('users:lista_utilizadores')
    
    def dispatch(self, request, *args, **kwargs):
        """
        Verificar se o utilizador é administrador.
        """
        if not (request.user.is_superuser or request.user.tipo_utilizador == 'admin'):
            messages.error(request, 'Apenas administradores podem editar utilizadores.')
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        """
        Passar request para o form para validação.
        """
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_success_message(self):
        return f'Utilizador {self.object.get_full_name()} atualizado com sucesso!'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from core.models import Sector
        context['sectores'] = Sector.objects.filter(ativo=True)
        context['titulo_pagina'] = 'Editar Utilizador'
        return context


class AtivarDesativarUtilizadorView(LoginRequiredMixin, View):
    """
    View para ativar/desativar utilizador (AJAX).
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, pk):
        if not request.user.is_staff:
            return JsonResponse({'error': 'Sem permissão'}, status=403)
        
        try:
            user = User.objects.get(pk=pk)
            user.ativo = not user.ativo
            user.save()
            
            return JsonResponse({
                'success': True,
                'ativo': user.ativo,
                'message': f'Utilizador {"ativado" if user.ativo else "desativado"} com sucesso!'
            })
        except User.DoesNotExist:
            return JsonResponse({'error': 'Utilizador não encontrado'}, status=404)


class PasswordChangeViewCustomizada(BaseViewMixin, LoginRequiredMixin, View):
    """
    View customizada para alteração de senha.
    """
    template_name = 'users/alterar_senha.html'
    
    def get(self, request):
        form = PasswordChangeFormCustomizada(user=request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = PasswordChangeFormCustomizada(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'🔐 Senha de {request.user.get_full_name()} alterada com sucesso!')
            return redirect('users:perfil')
        
        return render(request, self.template_name, {'form': form})


class PasswordResetViewCustomizada(PasswordResetView):
    """
    View customizada para reset de senha.
    """
    form_class = PasswordResetFormCustomizada
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = reverse_lazy('users:password_reset_done')


class PasswordResetDoneViewCustomizada(PasswordResetDoneView):
    """
    View customizada para confirmação de reset de senha.
    """
    template_name = 'users/password_reset_done.html'


class PasswordResetConfirmViewCustomizada(PasswordResetConfirmView):
    """
    View customizada para confirmação de nova senha.
    """
    form_class = SetPasswordFormCustomizada
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class PasswordResetCompleteViewCustomizada(PasswordResetCompleteView):
    """
    View customizada para confirmação de senha alterada.
    """
    template_name = 'users/password_reset_complete.html'


class GestaoSectoresView(BaseViewMixin, LoginRequiredMixin, ListView):
    """
    View para gestão de sectores (admin).
    """
    template_name = 'users/gestao_sectores.html'
    context_object_name = 'sectores'
    paginate_by = 20
    
    def get_queryset(self):
        from core.models import Sector
        return Sector.objects.select_related('chefe', 'chefe_substituto').all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['utilizadores_por_sector'] = User.objects.values('sector_atual__nome').annotate(
            total=Count('id')
        )
        return context


class GestaoPermissoesView(BaseViewMixin, LoginRequiredMixin, View):
    """
    View para gestão de permissões (admin).
    """
    template_name = 'users/gestao_permissoes.html'
    
    def get(self, request):
        grupos = Group.objects.prefetch_related('permissions', 'user_set').all()
        permissoes = Permission.objects.select_related('content_type').all()
        
        context = {
            'grupos': grupos,
            'permissoes': permissoes,
            'utilizadores_por_grupo': User.objects.values('groups__name').annotate(
                total=Count('id')
            )
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        # Lógica para atualizar permissões de grupos
        grupo_id = request.POST.get('grupo_id')
        permissao_ids = request.POST.getlist('permissoes')
        
        try:
            grupo = Group.objects.get(id=grupo_id)
            grupo.permissions.set(permissao_ids)
            messages.success(request, f'Permissões do grupo {grupo.name} atualizadas!')
        except Group.DoesNotExist:
            messages.error(request, 'Grupo não encontrado!')
        
        return redirect('users:gestao_permissoes')


class HierarquiaUtilizadoresView(BaseViewMixin, LoginRequiredMixin, View):
    """
    View para gestão de hierarquia de utilizadores.
    """
    template_name = 'users/hierarquia_utilizadores.html'
    
    def get(self, request):
        hierarquia = HierarquiaUtilizador.objects.select_related(
            'superior', 'subordinado'
        ).all()
        
        # Construir árvore hierárquica
        arvore = self._construir_arvore_hierarquica()
        
        context = {
            'hierarquia': hierarquia,
            'arvore': arvore,
            'form': HierarquiaUtilizadorForm()
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = HierarquiaUtilizadorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Relação hierárquica criada com sucesso!')
            return redirect('users:hierarquia_utilizadores')
        
        # Se houver erro, recarregar a página com o form
        hierarquia = HierarquiaUtilizador.objects.select_related(
            'superior', 'subordinado'
        ).all()
        arvore = self._construir_arvore_hierarquica()
        
        context = {
            'hierarquia': hierarquia,
            'arvore': arvore,
            'form': form
        }
        return render(request, self.template_name, context)
    
    def _construir_arvore_hierarquica(self):
        """
        Constrói árvore hierárquica para visualização.
        """
        # Encontrar PCA (nível mais alto)
        pca = User.objects.filter(is_pca=True).first()
        if not pca:
            return {}
        
        arvore = {
            'utilizador': pca,
            'subordinados': []
        }
        
        # Construir árvore recursivamente
        self._adicionar_subordinados(arvore)
        
        return arvore
    
    def _adicionar_subordinados(self, no):
        """
        Adiciona subordinados ao nó da árvore.
        """
        subordinados = HierarquiaUtilizador.objects.filter(
            superior=no['utilizador']
        ).select_related('subordinado')
        
        for relacao in subordinados:
            subordinado_no = {
                'utilizador': relacao.subordinado,
                'tipo_relacao': relacao.tipo_relacao,
                'subordinados': []
            }
            self._adicionar_subordinados(subordinado_no)
            no['subordinados'].append(subordinado_no)


class UtilizadoresPorSectorView(LoginRequiredMixin, View):
    """
    API view para obter utilizadores por sector (AJAX).
    """
    
    def get(self, request, pk):
        try:
            from core.models import Sector
            sector = Sector.objects.get(pk=pk)
            utilizadores = User.objects.filter(sector_atual=sector).values(
                'id', 'first_name', 'last_name', 'email', 'cargo', 'ativo'
            )
            
            return JsonResponse({
                'success': True,
                'sector': sector.nome,
                'utilizadores': list(utilizadores)
            })
        except Sector.DoesNotExist:
            return JsonResponse({'error': 'Sector não encontrado'}, status=404)


# ===== GESTÃO DE PERFIS DE UTILIZADOR (APENAS ADMINISTRADORES) =====

class ListarPerfisView(BaseListView, LoginRequiredMixin):
    """
    View para listar perfis de utilizadores (apenas administradores).
    """
    model = PerfilUtilizador
    template_name = 'users/lista_perfis.html'
    context_object_name = 'perfis'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        # Apenas administradores podem acessar
        if not request.user.is_authenticated:
            return redirect('users:login')
        if not (request.user.is_superuser or getattr(request.user, 'tipo_utilizador', None) == 'admin'):
            messages.error(request, 'Apenas administradores podem acessar esta página.')
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return PerfilUtilizador.objects.select_related('user').order_by('-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo_pagina': 'Perfis de Utilizadores',
        })
        return context


class EditarPerfilAdminView(BaseViewMixin, LoginRequiredMixin, View):
    """
    View para editar perfil de utilizador (apenas administradores).
    """
    template_name = 'users/gestao_utilizador_admin.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Apenas administradores podem acessar
        if not request.user.is_authenticated:
            return redirect('users:login')
        if not (request.user.is_superuser or getattr(request.user, 'tipo_utilizador', None) == 'admin'):
            messages.error(request, 'Apenas administradores podem acessar esta página.')
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, user_id):
        from .forms_admin import GestaoUtilizadorAdminForm
        
        user = get_object_or_404(User, id=user_id)
        perfil, created = PerfilUtilizador.objects.get_or_create(user=user)
        form = GestaoUtilizadorAdminForm(instance=user)
        
        context = {
            'form': form,
            'user': user,
            'perfil': perfil,
            'titulo_pagina': f'Gestão de Utilizador - {user.get_full_name()}',
        }
        return render(request, self.template_name, context)
    
    def post(self, request, user_id):
        from .forms_admin import GestaoUtilizadorAdminForm
        
        user = get_object_or_404(User, id=user_id)
        perfil, created = PerfilUtilizador.objects.get_or_create(user=user)
        form = GestaoUtilizadorAdminForm(request.POST, instance=user)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Configurações de {user.get_full_name()} atualizadas com sucesso!')
            return redirect('users:lista_perfis')
        
        context = {
            'form': form,
            'user': user,
            'perfil': perfil,
            'titulo_pagina': f'Gestão de Utilizador - {user.get_full_name()}',
        }
        return render(request, self.template_name, context)


# ===== GESTÃO DE HIERARQUIA DE UTILIZADORES (APENAS ADMINISTRADORES) =====

class ListarHierarquiaView(BaseListView, LoginRequiredMixin):
    """
    View para listar hierarquia de utilizadores (apenas administradores).
    """
    model = HierarquiaUtilizador
    template_name = 'users/lista_hierarquia.html'
    context_object_name = 'hierarquias'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        # Apenas administradores podem acessar
        if not (request.user.is_superuser or request.user.tipo_utilizador == 'admin'):
            messages.error(request, 'Apenas administradores podem acessar esta página.')
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return HierarquiaUtilizador.objects.select_related('superior', 'subordinado').filter(ativo=True).order_by('-data_inicio')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo_pagina': 'Hierarquia de Utilizadores',
        })
        return context


class CriarHierarquiaView(BaseViewMixin, LoginRequiredMixin, View):
    """
    View para criar nova relação hierárquica (apenas administradores).
    """
    template_name = 'users/criar_hierarquia.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Apenas administradores podem acessar
        if not (request.user.is_superuser or request.user.tipo_utilizador == 'admin'):
            messages.error(request, 'Apenas administradores podem acessar esta página.')
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        form = HierarquiaUtilizadorForm()
        context = {
            'form': form,
            'titulo_pagina': 'Criar Relação Hierárquica',
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = HierarquiaUtilizadorForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Relação hierárquica criada com sucesso!')
            return redirect('users:lista_hierarquia')
        
        context = {
            'form': form,
            'titulo_pagina': 'Criar Relação Hierárquica',
        }
        return render(request, self.template_name, context)


class EditarHierarquiaView(BaseViewMixin, LoginRequiredMixin, View):
    """
    View para editar relação hierárquica (apenas administradores).
    """
    template_name = 'users/editar_hierarquia.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Apenas administradores podem acessar
        if not (request.user.is_superuser or request.user.tipo_utilizador == 'admin'):
            messages.error(request, 'Apenas administradores podem acessar esta página.')
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, pk):
        hierarquia = get_object_or_404(HierarquiaUtilizador, pk=pk)
        form = HierarquiaUtilizadorForm(instance=hierarquia)
        
        context = {
            'form': form,
            'hierarquia': hierarquia,
            'titulo_pagina': 'Editar Relação Hierárquica',
        }
        return render(request, self.template_name, context)
    
    def post(self, request, pk):
        hierarquia = get_object_or_404(HierarquiaUtilizador, pk=pk)
        form = HierarquiaUtilizadorForm(request.POST, instance=hierarquia)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Relação hierárquica atualizada com sucesso!')
            return redirect('users:lista_hierarquia')
        
        context = {
            'form': form,
            'hierarquia': hierarquia,
            'titulo_pagina': 'Editar Relação Hierárquica',
        }
        return render(request, self.template_name, context)


class ApagarHierarquiaView(LoginRequiredMixin, View):
    """
    View para apagar relação hierárquica (apenas administradores).
    """
    
    def dispatch(self, request, *args, **kwargs):
        # Apenas administradores podem acessar
        if not (request.user.is_superuser or request.user.tipo_utilizador == 'admin'):
            messages.error(request, 'Apenas administradores podem acessar esta página.')
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, pk):
        hierarquia = get_object_or_404(HierarquiaUtilizador, pk=pk)
        hierarquia.ativo = False
        hierarquia.data_fim = timezone.now()
        hierarquia.save()
        
        messages.success(request, 'Relação hierárquica desativada com sucesso!')
        return redirect('users:lista_hierarquia')