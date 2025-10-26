from django.urls import path
from . import views_anexos

app_name = 'anexos'

urlpatterns = [
    # URLs de Anexos Avançados
    path('baixar/<int:pk>/', views_anexos.BaixarAnexoView.as_view(), name='baixar_anexo'),
    path('visualizar/<int:pk>/', views_anexos.VisualizarAnexoView.as_view(), name='visualizar_anexo'),
    path('apagar/<int:pk>/', views_anexos.ApagarAnexoView.as_view(), name='apagar_anexo'),
    path('lista/<int:expediente_pk>/', views_anexos.ListarAnexosView.as_view(), name='lista_anexos'),
    path('verificar-integridade/<int:pk>/', views_anexos.VerificarIntegridadeAnexoView.as_view(), name='verificar_integridade_anexo'),
    path('scan-virus/<int:pk>/', views_anexos.ScanVirusAnexoView.as_view(), name='scan_virus_anexo'),
]
