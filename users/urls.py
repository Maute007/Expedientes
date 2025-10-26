from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from .test_login import test_login_view

app_name = 'users'

urlpatterns = [
    # Portal Público
    path('', views.PortalPublicoView.as_view(), name='portal_publico'),
    
    # Autenticação
    path('login/', views.UserLoginViewCustomizada.as_view(), name='login'),
    path('login-test/', test_login_view, name='login_test'),
    path('logout/', views.UserLogoutViewCustomizada.as_view(), name='logout'),
    path('registro/', views.UserRegistrationView.as_view(), name='registro'),
    
    # Alteração de Senha
    path('password-change/', views.PasswordChangeViewCustomizada.as_view(), name='password_change'),
    
    # Reset de Senha
    path('password-reset/', views.PasswordResetViewCustomizada.as_view(), name='password_reset'),
    path('password-reset-done/', views.PasswordResetDoneViewCustomizada.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.PasswordResetConfirmViewCustomizada.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', views.PasswordResetCompleteViewCustomizada.as_view(), name='password_reset_complete'),
    
    # Perfil do Utilizador
    path('perfil/', views.PerfilUtilizadorView.as_view(), name='perfil'),
    path('perfil/editar/', views.EditarPerfilView.as_view(), name='perfil_edit'),
    path('perfil/configuracoes/', views.ConfiguracoesPerfilView.as_view(), name='perfil_configuracoes'),
    
    # Gestão de Utilizadores
    path('utilizadores/', views.ListarUtilizadoresView.as_view(), name='lista_utilizadores'),
    path('utilizadores/novo/', views.CriarUtilizadorView.as_view(), name='criar_utilizador'),
    path('utilizadores/<int:pk>/editar/', views.EditarUtilizadorView.as_view(), name='editar_utilizador'),
    path('utilizadores/<int:pk>/ativar-desativar/', views.AtivarDesativarUtilizadorView.as_view(), name='ativar_desativar_utilizador'),
    
    # Gestão de Perfis (apenas administradores)
    path('perfis/', views.ListarPerfisView.as_view(), name='lista_perfis'),
    path('perfis/<int:user_id>/editar/', views.EditarPerfilAdminView.as_view(), name='editar_perfil_admin'),
    
    # Gestão de Hierarquia (apenas administradores)
    path('hierarquia/', views.ListarHierarquiaView.as_view(), name='lista_hierarquia'),
    path('hierarquia/criar/', views.CriarHierarquiaView.as_view(), name='criar_hierarquia'),
    path('hierarquia/<int:pk>/editar/', views.EditarHierarquiaView.as_view(), name='editar_hierarquia'),
    path('hierarquia/<int:pk>/apagar/', views.ApagarHierarquiaView.as_view(), name='apagar_hierarquia'),
    
    # Gestão Administrativa
    path('gestao/sectores/', views.GestaoSectoresView.as_view(), name='gestao_sectores'),
    path('gestao/permissoes/', views.GestaoPermissoesView.as_view(), name='gestao_permissoes'),
    path('gestao/hierarquia/', views.HierarquiaUtilizadoresView.as_view(), name='hierarquia_utilizadores'),
    
    # APIs
    path('api/utilizadores/<int:pk>/status/', views.AtivarDesativarUtilizadorView.as_view(), name='api_utilizador_status'),
    path('api/sectores/<int:pk>/utilizadores/', views.UtilizadoresPorSectorView.as_view(), name='api_utilizadores_sector'),
]
