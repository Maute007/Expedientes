from django.urls import path
from . import views

app_name = 'externa'

urlpatterns = [
    path('minhas-submissoes/', views.MinhasSubmissoesView.as_view(), name='minhas_submissoes'),
    path('nova-submissao/', views.NovaSubmissaoView.as_view(), name='nova_submissao'),
]
