from django.urls import path
from . import views

app_name = 'assinatura_digital'

urlpatterns = [
    # Visualizar documento e iniciar assinatura
    path('assinar/<int:pk>/', views.AssinarAnexoView.as_view(), name='assinar_anexo'),
    
    # Criar assinatura no canvas
    path('criar-assinatura/<int:anexo_id>/', views.CriarAssinaturaCanvasView.as_view(), name='criar_assinatura'),
    
    # Salvar assinatura padrão
    path('salvar-assinatura-padrao/', views.salvar_assinatura_padrao, name='salvar_assinatura_padrao'),
    
    # Posicionar assinatura no documento
    path('posicionar/<int:anexo_id>/', views.PosicionarAssinaturaView.as_view(), name='posicionar_assinatura'),
    
    # Confirmar e processar assinatura
    path('confirmar/<int:pk>/', views.confirmar_assinatura, name='confirmar_assinatura'),
    
    # Histórico de assinaturas
    path('minhas-assinaturas/', views.MinhasAssinaturasView.as_view(), name='minhas_assinaturas'),
    
    # Lista de anexos pendentes
    path('anexos-pendentes/', views.ListarAnexosPendentesView.as_view(), name='anexos_pendentes'),
]
