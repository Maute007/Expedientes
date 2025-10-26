from django.urls import path, include
from . import views
from . import wizard_views
from . import views_anexos

app_name = 'entrada'

urlpatterns = [
    # Expedientes
    path('', views.ListarExpedientesView.as_view(), name='lista_expedientes'),
    path('criar/', views.CriarExpedienteView.as_view(), name='criar_expediente'),
    
    # Wizard (Nova implementação recomendada)
    path('wizard/', wizard_views.ExpedienteWizardView.as_view(), name='wizard'),
    path('wizard/<str:step>/', wizard_views.WizardStepView.as_view(), name='wizard_step'),
    
    # Etapas individuais (implementação atual - manter para compatibilidade)
    path('etapa1/', views.Etapa1View.as_view(), name='etapa1'),
    path('etapa2/', views.Etapa2View.as_view(), name='etapa2'),
    path('etapa3/', views.Etapa3View.as_view(), name='etapa3'),
    path('etapa4/', views.Etapa4View.as_view(), name='etapa4'),
    path('finalizar/', views.finalizar_expediente, name='finalizar_expediente'),
    path('guardar-rascunho/', views.guardar_rascunho, name='guardar_rascunho'),
    path('detalhar/<int:pk>/', views.DetalharExpedienteView.as_view(), name='detalhar_expediente'),
    path('editar/<int:pk>/', views.EditarExpedienteView.as_view(), name='editar_expediente'),
    path('deletar/<int:pk>/', views.DeletarExpedienteView.as_view(), name='deletar_expediente'),
    
    # Ações AJAX
    path('adicionar-membro/', views.adicionar_membro, name='adicionar_membro'),
    path('remover-membro/', views.remover_membro, name='remover_membro'),
    path('obter-membros-sector/', views.obter_membros_sector, name='obter_membros_sector'),
    path('buscar-membros/', views.buscar_membros, name='buscar_membros'),
    path('upload-anexo/', views.upload_anexo, name='upload_anexo'),
    
    # Tipos de Documento
    path('tipos/', views.ListarTiposDocumentoView.as_view(), name='lista_tipos_documento'),
    path('tipos/criar/', views.CriarTipoDocumentoView.as_view(), name='criar_tipo_documento'),
    path('tipos/editar/<int:pk>/', views.EditarTipoDocumentoView.as_view(), name='editar_tipo_documento'),
    path('tipos/deletar/<int:pk>/', views.DeletarTipoDocumentoView.as_view(), name='deletar_tipo_documento'),
    
    # Encaminhamento
    path('encaminhar-pca-sector/<int:pk>/', views.EncaminharPCAParaSectorView.as_view(), name='encaminhar_pca_sector'),
    path('encaminhar-chefe-colaborador/<int:pk>/', views.EncaminharChefeParaColaboradorView.as_view(), name='encaminhar_chefe_colaborador'),
    path('devolver/<int:pk>/', views.DevolverDocumentoView.as_view(), name='devolver_documento'),
    path('api/devolver-instantaneo/<int:pk>/', views.DevolverDocumentoInstantaneoView.as_view(), name='devolver_instantaneo'),
    path('marcar-recebido/<int:pk>/', views.marcar_como_recebido, name='marcar_recebido'),
    
    # Tratamento de Documentos
    path('iniciar-tratamento/<int:pk>/', views.IniciarTratamentoDocumentoView.as_view(), name='iniciar_tratamento'),
    path('concluir/<int:pk>/', views.ConcluirDocumentoView.as_view(), name='concluir_documento'),
    path('arquivar/<int:pk>/', views.ArquivarDocumentoView.as_view(), name='arquivar_documento'),
    path('reabrir/<int:pk>/', views.ReabrirDocumentoView.as_view(), name='reabrir_documento'),
    path('historico/<int:pk>/', views.HistoricoMovimentacaoView.as_view(), name='historico_movimentacao'),
    
    # Portal Externo
    path('portal/', views.PortalExpedienteView.as_view(), name='portal_expediente'),
    path('portal/success/<int:pk>/', views.PortalSuccessView.as_view(), name='portal_success'),
    
    # URLs de Anexos Avançados
    path('anexos/baixar/<int:pk>/', views_anexos.BaixarAnexoView.as_view(), name='baixar_anexo'),
    path('anexos/visualizar/<int:pk>/', views_anexos.VisualizarAnexoView.as_view(), name='visualizar_anexo'),
    path('anexos/apagar/<int:pk>/', views_anexos.ApagarAnexoView.as_view(), name='apagar_anexo'),
    path('anexos/lista/<int:expediente_pk>/', views_anexos.ListarAnexosView.as_view(), name='lista_anexos'),
    path('anexos/verificar-integridade/<int:pk>/', views_anexos.VerificarIntegridadeAnexoView.as_view(), name='verificar_integridade_anexo'),
    path('anexos/scan-virus/<int:pk>/', views_anexos.ScanVirusAnexoView.as_view(), name='scan_virus_anexo'),
    
    # URLs para Pareceres
    path('parecer/criar/<int:pk>/', views.CriarParecerView.as_view(), name='criar_parecer'),
    path('parecer/editar/<int:pk>/<int:parecer_id>/', views.EditarParecerView.as_view(), name='editar_parecer'),
    path('parecer/implementar/<int:pk>/<int:parecer_id>/', views.ImplementarParecerView.as_view(), name='implementar_parecer'),
    path('parecer/historico/<int:pk>/', views.HistoricoPareceresView.as_view(), name='historico_pareceres'),
]
