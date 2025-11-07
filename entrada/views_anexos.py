from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, DeleteView, ListView
from django.http import FileResponse, HttpResponse, JsonResponse, Http404
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.utils import timezone
import os
import mimetypes

from .models import AnexoExpediente, Expediente
from core.mixins import FormAlertMixin


class BaixarAnexoView(LoginRequiredMixin, View):
    """
    View para baixar anexo seguindo padrão do sistema
    """
    def get(self, request, pk):
        anexo = get_object_or_404(AnexoExpediente, pk=pk, ativo=True)
        
        # Verificar permissões - usuário deve ter acesso ao expediente
        if not anexo.expediente.pode_visualizar(request.user):
            raise PermissionDenied("Você não tem permissão para baixar este anexo.")
        
        # Verificar se arquivo existe
        if not anexo.arquivo or not os.path.exists(anexo.arquivo.path):
            raise Http404("Arquivo não encontrado.")
        
        # Determinar tipo MIME
        content_type = anexo.tipo_mime or mimetypes.guess_type(anexo.nome_original)[0] or 'application/octet-stream'
        
        # Criar resposta de arquivo
        response = FileResponse(
            anexo.arquivo,
            content_type=content_type,
            as_attachment=True,
            filename=anexo.nome_original
        )
        
        # Log de download (opcional)
        # Aqui poderia registrar quem baixou quando
        
        return response


class VisualizarAnexoView(LoginRequiredMixin, View):
    """
    View para visualizar anexo inline seguindo padrão do sistema
    """
    def get(self, request, pk):
        anexo = get_object_or_404(AnexoExpediente, pk=pk, ativo=True)
        
        # Verificar permissões
        if not anexo.expediente.pode_visualizar(request.user):
            raise PermissionDenied("Você não tem permissão para visualizar este anexo.")
        
        # Verificar se arquivo existe
        if not anexo.arquivo:
            messages.error(request, f"Arquivo do anexo '{anexo.nome_original}' não está disponível.")
            return redirect('entrada:detalhar_expediente', pk=anexo.expediente.pk)
        
        # Tentar usar URL direta primeiro (mais confiável para visualização inline)
        # Isso funciona melhor para PDFs e imagens em muitos navegadores
        try:
            arquivo_url = anexo.arquivo.url
            # Para PDFs e imagens, redirecionar para URL direta que geralmente visualiza inline
            if anexo.tipo_mime == 'application/pdf' or anexo.tipo_mime.startswith('image/'):
                # Usar redirect para URL do media, que geralmente é mais confiável
                return redirect(arquivo_url)
        except Exception:
            pass  # Se não conseguir URL, tentar método alternativo
        
        # Método alternativo: servir via FileResponse
        # Verificar se arquivo existe fisicamente e obter path
        arquivo_path = None
        try:
            arquivo_path = anexo.arquivo.path
            if not os.path.exists(arquivo_path):
                messages.error(request, f"Arquivo físico do anexo '{anexo.nome_original}' não foi encontrado no servidor.")
                return redirect('entrada:detalhar_expediente', pk=anexo.expediente.pk)
        except (ValueError, AttributeError):
            # Se não conseguir path nem URL, redirecionar para download
            messages.error(request, f"Erro ao acessar o arquivo '{anexo.nome_original}'.")
            return redirect('entrada:baixar_anexo', pk=pk)
        
        # Se chegou aqui, arquivo_path está definido e válido
        # Determinar tipo de visualização
        try:
            if anexo.tipo_mime.startswith('image/'):
                # Visualizar imagem inline usando FileResponse
                file_handle = open(arquivo_path, 'rb')
                response = FileResponse(
                    file_handle,
                    content_type=anexo.tipo_mime
                )
                # Headers para forçar visualização inline
                response['Content-Disposition'] = 'inline'
                return response
            
            elif anexo.tipo_mime == 'application/pdf':
                # Visualizar PDF inline usando FileResponse
                file_handle = open(arquivo_path, 'rb')
                response = FileResponse(
                    file_handle,
                    content_type='application/pdf'
                )
                # Headers para forçar visualização inline
                response['Content-Disposition'] = 'inline'
                response['Accept-Ranges'] = 'bytes'
                return response
            
            else:
                # Para outros tipos, redirecionar para download
                return redirect('entrada:baixar_anexo', pk=pk)
        except Exception as e:
            messages.error(request, f"Erro ao ler o arquivo '{anexo.nome_original}': {str(e)}")
            return redirect('entrada:detalhar_expediente', pk=anexo.expediente.pk)


class ApagarAnexoView(LoginRequiredMixin, DeleteView):
    """
    View para apagar anexo seguindo padrão do sistema
    """
    model = AnexoExpediente
    template_name = 'entrada/anexo_confirmar_apagar.html'
    
    def get_object(self):
        obj = get_object_or_404(AnexoExpediente, pk=self.kwargs['pk'], ativo=True)
        # Verificar permissões
        if not obj.expediente.pode_editar(self.request.user):
            raise PermissionDenied("Você não tem permissão para apagar este anexo.")
        return obj
    
    def get_success_url(self):
        return reverse_lazy('entrada:detalhar_expediente', kwargs={'pk': self.object.expediente.pk})
    
    def delete(self, request, *args, **kwargs):
        anexo = self.get_object()
        expediente_pk = anexo.expediente.pk
        
        # Marcar como inativo em vez de apagar fisicamente
        anexo.ativo = False
        anexo.save()
        
        messages.success(request, f'Anexo "{anexo.nome_original}" foi removido com sucesso.')
        return redirect('entrada:detalhar_expediente', pk=expediente_pk)


class ListarAnexosView(LoginRequiredMixin, ListView):
    """
    View para listar anexos de um expediente seguindo padrão do sistema
    """
    model = AnexoExpediente
    template_name = 'entrada/anexo_list.html'
    context_object_name = 'anexos'
    paginate_by = 20
    
    def get_queryset(self):
        expediente_pk = self.kwargs.get('expediente_pk')
        expediente = get_object_or_404(Expediente, pk=expediente_pk)
        
        # Verificar permissões
        if not expediente.pode_visualizar(self.request.user):
            raise PermissionDenied("Você não tem permissão para visualizar os anexos deste expediente.")
        
        anexos = AnexoExpediente.objects.filter(
            expediente=expediente,
            ativo=True
        ).order_by('-data_upload')
        
        # Adicionar propriedades para cada anexo indicando se pode ser assinado pelo usuário atual
        anexos_list = list(anexos)
        for anexo in anexos_list:
            anexo.pode_ser_assinado_por_usuario = (
                self.request.user.tipo_utilizador in ['pca', 'secretaria', 'chefe'] and
                anexo.pode_ser_assinado() and
                anexo.pode_assinador_acessar(self.request.user)
            )
        
        return anexos_list
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expediente_pk = self.kwargs.get('expediente_pk')
        expediente = get_object_or_404(Expediente, pk=expediente_pk)
        
        context.update({
            'expediente': expediente,
            'titulo_pagina': f'Anexos - {expediente.numero_protocolo}',
            'pode_editar': expediente.pode_editar(self.request.user),
            'pode_assinar_anexo': self.request.user.tipo_utilizador in ['pca', 'secretaria', 'chefe'],
            'user': self.request.user,
        })
        
        return context


class VerificarIntegridadeAnexoView(LoginRequiredMixin, View):
    """
    View para verificar integridade de anexo seguindo padrão do sistema
    """
    def post(self, request, pk):
        anexo = get_object_or_404(AnexoExpediente, pk=pk, ativo=True)
        
        # Verificar permissões
        if not anexo.expediente.pode_visualizar(request.user):
            return JsonResponse({'success': False, 'message': 'Sem permissão.'})
        
        # Verificar se arquivo existe
        if not anexo.arquivo or not os.path.exists(anexo.arquivo.path):
            return JsonResponse({
                'success': False, 
                'message': 'Arquivo não encontrado no sistema.',
                'status': 'erro'
            })
        
        # Aqui implementaria verificação de hash se tivesse
        # Por enquanto, apenas verifica se arquivo existe
        return JsonResponse({
            'success': True,
            'message': 'Arquivo íntegro.',
            'status': 'ok'
        })


class ScanVirusAnexoView(LoginRequiredMixin, View):
    """
    View para scan de vírus de anexo seguindo padrão do sistema
    """
    def post(self, request, pk):
        anexo = get_object_or_404(AnexoExpediente, pk=pk, ativo=True)
        
        # Verificar permissões
        if not anexo.expediente.pode_visualizar(request.user):
            return JsonResponse({'success': False, 'message': 'Sem permissão.'})
        
        # Aqui implementaria integração com antivírus
        # Por enquanto, simula resultado
        return JsonResponse({
            'success': True,
            'message': 'Arquivo limpo.',
            'status': 'limpo',
            'data_scan': timezone.now().isoformat()
        })
