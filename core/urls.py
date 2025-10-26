from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Dashboard Principal (redirecionamento)
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard_redirect'),
    
    # Dashboards Específicos por Tipo de Utilizador
    path('dashboard/admin/', views.DashboardAdminView.as_view(), name='dashboard_admin'),
    path('dashboard/secretaria/', views.DashboardSecretariaView.as_view(), name='dashboard_secretaria'),
    path('dashboard/pca/', views.DashboardPCAView.as_view(), name='dashboard_pca'),
    path('dashboard/chefe/', views.DashboardChefeView.as_view(), name='dashboard_chefe'),
    path('dashboard/colaborador/', views.DashboardColaboradorView.as_view(), name='dashboard_colaborador'),
    path('dashboard/externo/', views.DashboardExternoView.as_view(), name='dashboard_externo'),
    
    # API para dados do dashboard
    path('api/dashboard/data/', views.DashboardDataView.as_view(), name='dashboard_data'),
    
    # Notificações - Páginas principais
    path('notificacoes/', views.ListarNotificacoesView.as_view(), name='lista_notificacoes'),
    path('notificacoes/apagar/<int:pk>/', views.ApagarNotificacaoView.as_view(), name='apagar_notificacao'),
    path('notificacoes/redirecionar/<int:pk>/', views.RedirecionarNotificacaoView.as_view(), name='redirecionar_notificacao'),
    
    # Notificações - APIs AJAX
    path('api/notificacoes/marcar-lida/<int:pk>/', views.MarcarNotificacaoLidaView.as_view(), name='marcar_notificacao_lida'),
    path('api/notificacoes/marcar-todas-lidas/', views.MarcarTodasLidasView.as_view(), name='marcar_todas_lidas'),
    path('api/notificacoes/dropdown/', views.NotificacoesDropdownView.as_view(), name='notificacoes_dropdown'),
    
    # Gestão de Sectores
    path('sectores/', views.ListarSectoresView.as_view(), name='lista_sectores'),
    path('sectores/criar/', views.CriarSectorView.as_view(), name='criar_sector'),
    path('sectores/editar/<int:pk>/', views.EditarSectorView.as_view(), name='editar_sector'),
    path('sectores/apagar/<int:pk>/', views.ApagarSectorView.as_view(), name='apagar_sector'),
    path('sectores/detalhes/<int:pk>/', views.DetalhesSectorView.as_view(), name='detalhes_sector'),
    
    # Configurações do Sistema
    path('configuracoes/', views.ConfiguracoesSistemaView.as_view(), name='configuracoes'),
    path('api/configuracoes/gerais/', views.SalvarConfiguracoesGeraisView.as_view(), name='salvar_configuracoes_gerais'),
    path('api/configuracoes/notificacoes/', views.SalvarConfiguracoesNotificacoesView.as_view(), name='salvar_configuracoes_notificacoes'),
]
