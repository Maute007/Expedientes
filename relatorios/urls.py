from django.urls import path
from . import views
from . import views_simples

app_name = 'relatorios'

urlpatterns = [
    # Dashboard simples (nova versão)
    path('', views_simples.dashboard_simples, name='dashboard'),
    path('simples/', views_simples.dashboard_simples, name='dashboard_simples'),
    path('exportar/<str:formato>/', views_simples.exportar_relatorio, name='exportar'),
    
    # Dashboard complexo (versão antiga)
    path('complexo/', views.dashboard_relatorios, name='dashboard_complexo'),
    
    # Relatórios
    path('relatorios/', views.lista_relatorios, name='lista_relatorios'),
    path('relatorios/criar/', views.criar_relatorio, name='criar_relatorio'),
    path('relatorios/<int:pk>/', views.detalhar_relatorio, name='detalhar_relatorio'),
    path('relatorios/<int:pk>/editar/', views.editar_relatorio, name='editar_relatorio'),
    path('relatorios/<int:pk>/executar/', views.executar_relatorio, name='executar_relatorio'),
    path('execucoes/<int:pk>/download/', views.download_relatorio, name='download_relatorio'),
    
    # Dashboards
    path('dashboards/', views.lista_dashboards, name='lista_dashboards'),
    path('dashboards/criar/', views.criar_dashboard, name='criar_dashboard'),
    path('dashboards/<int:pk>/', views.visualizar_dashboard, name='visualizar_dashboard'),
    path('dashboards/<int:pk>/editar/', views.editar_dashboard, name='editar_dashboard'),
    
    # Widgets
    path('dashboards/<int:dashboard_pk>/widgets/', views.configurar_widget, name='configurar_widget'),
    path('dashboards/<int:dashboard_pk>/widgets/<int:widget_id>/remover/', views.remover_widget, name='remover_widget'),
    path('api/widgets/dados/', views.obter_dados_widget, name='obter_dados_widget'),
    
    # Dashboards por Perfil
    path('dashboard/admin/', views.dashboard_administrador, name='dashboard_admin'),
    path('dashboard/pca-ca/', views.dashboard_pca_ca, name='dashboard_pca_ca'),
    path('dashboard/chefe-sector/', views.dashboard_chefe_sector, name='dashboard_chefe_sector'),
    path('dashboard/colaborador/', views.dashboard_colaborador, name='dashboard_colaborador'),
    
    # Relatórios de Comunicação
    path('relatorios/mensagens-sector/', views.relatorio_mensagens_sector, name='relatorio_mensagens_sector'),
    path('relatorios/atividade-utilizadores/', views.relatorio_atividade_utilizadores, name='relatorio_atividade_utilizadores'),
    path('relatorios/tempo-resposta/', views.relatorio_tempo_resposta, name='relatorio_tempo_resposta'),
]