from django.urls import path
from . import views

app_name = 'externa'

urlpatterns = [
    path('', views.MinhasSubmissoesView.as_view(), name='minhas_submissoes'),
    path('nova/', views.NovaSubmissaoView.as_view(), name='nova_submissao'),
    # Adicionar mais URLs conforme necessário
]
