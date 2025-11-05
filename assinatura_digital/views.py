from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, ListView, TemplateView
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.db.models import Q
import base64
import json
import os

from entrada.models import AnexoExpediente
from .models import AssinaturaDocumento, AssinaturaUtilizador
from .forms import (
    AssinaturaCanvasForm, PosicionamentoAssinaturaForm,
    SalvarAssinaturaPadraoForm, ConfirmarAssinaturaForm
)
from .decorators import assinatura_permitida, AssinaturaPermitidaMixin
from .utils import (
    criar_backup_arquivo, inserir_assinatura_pdf,
    inserir_assinatura_imagem, inserir_assinatura_docx
)


class AssinarAnexoView(AssinaturaPermitidaMixin, LoginRequiredMixin, TemplateView):
    """
    View para visualizar documento e iniciar processo de assinatura
    """
    template_name = 'assinatura_digital/documento_viewer.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        anexo_id = self.kwargs.get('pk')
        anexo = get_object_or_404(AnexoExpediente, pk=anexo_id, ativo=True)
        
        # Verificar permissões
        if not anexo.pode_assinador_acessar(self.request.user):
            raise PermissionDenied("Você não tem permissão para assinar este anexo.")
        
        if not anexo.pode_ser_assinado():
            messages.error(self.request, "Este formato de arquivo não pode ser assinado.")
            return redirect('entrada:detalhar_expediente', pk=anexo.expediente.pk)
        
        # Verificar se usuário tem assinatura padrão
        try:
            assinatura_padrao = AssinaturaUtilizador.objects.get(utilizador=self.request.user, ativo=True)
            context['tem_assinatura_padrao'] = True
            context['assinatura_padrao_url'] = assinatura_padrao.assinatura_imagem.url
        except AssinaturaUtilizador.DoesNotExist:
            context['tem_assinatura_padrao'] = False
        
        context['anexo'] = anexo
        context['expediente'] = anexo.expediente
        context['anexo_url'] = anexo.arquivo.url
        
        # Determinar tipo de visualização
        if anexo.tipo_mime == 'application/pdf':
            context['tipo_visualizacao'] = 'pdf'
        elif anexo.tipo_mime.startswith('image/'):
            context['tipo_visualizacao'] = 'imagem'
        elif 'word' in anexo.tipo_mime or anexo.nome_original.lower().endswith(('.doc', '.docx')):
            context['tipo_visualizacao'] = 'documento'
        else:
            context['tipo_visualizacao'] = 'outro'
        
        return context


class CriarAssinaturaCanvasView(AssinaturaPermitidaMixin, LoginRequiredMixin, TemplateView):
    """
    View para criar assinatura no canvas
    """
    template_name = 'assinatura_digital/assinatura_canvas.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        anexo_id = self.kwargs.get('anexo_id')
        anexo = get_object_or_404(AnexoExpediente, pk=anexo_id, ativo=True)
        
        # Verificar permissões
        if not anexo.pode_assinador_acessar(self.request.user):
            raise PermissionDenied("Você não tem permissão para assinar este anexo.")
        
        context['anexo'] = anexo
        context['expediente'] = anexo.expediente
        
        return context


@login_required
@assinatura_permitida
def salvar_assinatura_padrao(request):
    """
    View para salvar assinatura padrão do utilizador
    """
    if request.method == 'POST':
        try:
            # Obter dados do POST (pode vir de form ou AJAX)
            signature_data = request.POST.get('signature_data')
            
            if not signature_data:
                return JsonResponse({
                    'success': False, 
                    'message': 'Dados da assinatura não fornecidos.'
                })
            
            # Converter base64 para imagem
            try:
                # Remover data:image/png;base64, se presente
                if ',' in signature_data:
                    header, encoded = signature_data.split(',', 1)
                else:
                    encoded = signature_data
                
                image_data = base64.b64decode(encoded)
            except Exception as e:
                return JsonResponse({
                    'success': False, 
                    'message': f'Erro ao decodificar imagem: {str(e)}'
                })
            
            # Verificar se os dados da imagem são válidos
            if len(image_data) == 0:
                return JsonResponse({
                    'success': False, 
                    'message': 'Imagem da assinatura está vazia.'
                })
            
            # Criar ou atualizar assinatura padrão
            try:
                assinatura, created = AssinaturaUtilizador.objects.get_or_create(
                    utilizador=request.user,
                    defaults={'ativo': True}
                )
                
                # Atualizar ativo se já existia mas estava inativo
                if not created and not assinatura.ativo:
                    assinatura.ativo = True
                
                # Salvar imagem
                file_name = f'assinatura_padrao_{request.user.id}_{timezone.now().strftime("%Y%m%d%H%M%S")}.png'
                assinatura.assinatura_imagem.save(
                    file_name,
                    ContentFile(image_data),
                    save=True
                )
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Assinatura padrão salva com sucesso!',
                    'image_url': assinatura.get_signature_url()
                })
            except Exception as e:
                return JsonResponse({
                    'success': False, 
                    'message': f'Erro ao salvar assinatura: {str(e)}'
                })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'Erro ao processar requisição: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


class PosicionarAssinaturaView(AssinaturaPermitidaMixin, LoginRequiredMixin, TemplateView):
    """
    View para posicionar assinatura no documento
    """
    template_name = 'assinatura_digital/posicionar_assinatura.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        anexo_id = self.kwargs.get('anexo_id')
        anexo = get_object_or_404(AnexoExpediente, pk=anexo_id, ativo=True)
        
        # Verificar permissões
        if not anexo.pode_assinador_acessar(self.request.user):
            raise PermissionDenied("Você não tem permissão para assinar este anexo.")
        
        # Obter dados da assinatura da sessão ou GET
        signature_data = self.request.GET.get('signature_data', '')
        usar_padrao = self.request.GET.get('usar_padrao', 'false') == 'true'
        
        context['anexo'] = anexo
        context['expediente'] = anexo.expediente
        context['anexo_url'] = anexo.arquivo.url
        context['signature_data'] = signature_data
        context['usar_padrao'] = usar_padrao
        
        # Verificar assinatura padrão
        try:
            assinatura_padrao = AssinaturaUtilizador.objects.get(utilizador=self.request.user, ativo=True)
            context['assinatura_padrao_url'] = assinatura_padrao.assinatura_imagem.url
        except AssinaturaUtilizador.DoesNotExist:
            context['assinatura_padrao_url'] = None
        
        return context


@login_required
@assinatura_permitida
def confirmar_assinatura(request, pk):
    """
    View para confirmar e processar assinatura no documento
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método não permitido'})
    
    anexo = get_object_or_404(AnexoExpediente, pk=pk, ativo=True)
    
    # Verificar permissões
    if not anexo.pode_assinador_acessar(request.user):
        return JsonResponse({'success': False, 'message': 'Sem permissão para assinar este anexo.'})
    
    form = ConfirmarAssinaturaForm(request.POST)
    
    if not form.is_valid():
        return JsonResponse({'success': False, 'errors': form.errors})
    
    try:
        # Obter dados do formulário
        posicao_x = form.cleaned_data['posicao_x']
        posicao_y = form.cleaned_data['posicao_y']
        pagina = form.cleaned_data['pagina']
        observacoes = form.cleaned_data.get('observacoes', '')
        
        # Converter usar_assinatura_padrao para boolean (pode vir como string "true" ou "false")
        usar_padrao_raw = form.cleaned_data.get('usar_assinatura_padrao', False)
        if isinstance(usar_padrao_raw, str):
            usar_padrao = usar_padrao_raw.lower() in ('true', '1', 'yes', 'on')
        else:
            usar_padrao = bool(usar_padrao_raw)
        
        # Validar se tem assinatura (padrão ou do canvas)
        if not usar_padrao:
            signature_data = form.cleaned_data.get('signature_data', '')
            if not signature_data:
                return JsonResponse({
                    'success': False, 
                    'message': 'É necessário fornecer uma assinatura (padrão ou desenhar no canvas).'
                })
        
        # Obter imagem da assinatura
        if usar_padrao:
            try:
                assinatura_padrao = AssinaturaUtilizador.objects.get(utilizador=request.user, ativo=True)
                signature_image_file = assinatura_padrao.assinatura_imagem
                tipo_assinatura = 'padrao'
                # Criar ContentFile a partir da imagem salva
                signature_image_file.open('rb')
                signature_image_data = signature_image_file.read()
                signature_image_file.close()
                signature_image = ContentFile(signature_image_data, name=os.path.basename(signature_image_file.name))
            except AssinaturaUtilizador.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Assinatura padrão não encontrada.'})
        else:
            signature_data = form.cleaned_data.get('signature_data', '')
            if not signature_data:
                return JsonResponse({
                    'success': False, 
                    'message': 'Dados da assinatura não fornecidos. Por favor, desenhe uma assinatura ou use a assinatura padrão.'
                })
            
            # Converter base64 para imagem
            try:
                # Remover data:image/png;base64, se presente
                if ',' in signature_data:
                    header, encoded = signature_data.split(',', 1)
                else:
                    encoded = signature_data
                
                image_data = base64.b64decode(encoded)
                
                if len(image_data) == 0:
                    return JsonResponse({
                        'success': False, 
                        'message': 'Imagem da assinatura está vazia.'
                    })
            except Exception as e:
                return JsonResponse({
                    'success': False, 
                    'message': f'Erro ao decodificar assinatura: {str(e)}'
                })
            
            # Salvar temporariamente
            signature_image = ContentFile(image_data, name=f'assinatura_{request.user.id}_{timezone.now().timestamp()}.png')
            tipo_assinatura = 'canvas'
        
        # Criar backup do arquivo original
        backup_path = criar_backup_arquivo(anexo.arquivo)
        
        try:
            # Processar arquivo baseado no tipo
            if anexo.tipo_mime == 'application/pdf':
                arquivo_modificado = inserir_assinatura_pdf(
                    anexo.arquivo, signature_image, posicao_x, posicao_y, pagina
                )
            elif anexo.tipo_mime.startswith('image/'):
                arquivo_modificado = inserir_assinatura_imagem(
                    anexo.arquivo, signature_image, posicao_x, posicao_y
                )
            elif 'word' in anexo.tipo_mime or anexo.nome_original.lower().endswith(('.doc', '.docx')):
                arquivo_modificado = inserir_assinatura_docx(
                    anexo.arquivo, signature_image, posicao_x, posicao_y
                )
            else:
                return JsonResponse({'success': False, 'message': 'Formato de arquivo não suportado.'})
            
            # Garantir que o arquivo modificado está no início
            if hasattr(arquivo_modificado, 'seek'):
                arquivo_modificado.seek(0)
            
            # Ler o conteúdo do arquivo modificado
            if hasattr(arquivo_modificado, 'read'):
                arquivo_modificado_content = arquivo_modificado.read()
            else:
                arquivo_modificado_content = arquivo_modificado
            
            # Verificar se o conteúdo foi lido corretamente
            if not arquivo_modificado_content or len(arquivo_modificado_content) == 0:
                return JsonResponse({
                    'success': False, 
                    'message': 'Erro: Arquivo modificado está vazio.'
                })
            
            # Substituir arquivo original
            # Limitar tamanho do nome do arquivo para evitar problemas
            nome_original = os.path.basename(anexo.arquivo.name)
            if len(nome_original) > 200:
                # Truncar nome se muito longo (mantendo extensão)
                nome_base, ext = os.path.splitext(nome_original)
                nome_original = nome_base[:190] + ext
            
            # Fechar o arquivo antes de salvar (se estiver aberto)
            if hasattr(anexo.arquivo, 'close'):
                try:
                    anexo.arquivo.close()
                except:
                    pass
            
            # Salvar o novo arquivo
            anexo.arquivo.save(nome_original, ContentFile(arquivo_modificado_content), save=True)
            anexo.save()  # Salvar o anexo para garantir que as mudanças são persistidas
        except Exception as e:
            # Mensagens de erro mais amigáveis
            error_message = str(e)
            if 'value too long' in error_message.lower():
                error_message = 'Erro: O nome do arquivo ou caminho é muito longo. Tente renomear o arquivo com um nome mais curto.'
            elif 'read of closed file' in error_message.lower():
                error_message = 'Erro: Problema ao acessar o arquivo. Tente novamente.'
            elif 'permission denied' in error_message.lower():
                error_message = 'Erro: Você não tem permissão para realizar esta ação.'
            elif 'not found' in error_message.lower():
                error_message = 'Erro: Arquivo não encontrado. O arquivo pode ter sido removido.'
            else:
                # Mensagem genérica mais amigável
                error_message = f'Erro ao processar assinatura: {error_message}'
            
            return JsonResponse({
                'success': False, 
                'message': error_message
            })
        
        # Salvar imagem da assinatura para o registro
        if usar_padrao:
            # Usar a imagem padrão diretamente
            assinatura_imagem_ref = assinatura_padrao.assinatura_imagem
        else:
            # Salvar a assinatura do canvas
            assinatura_imagem_ref = signature_image
        
        # Criar registro de assinatura
        # Truncar user_agent se muito longo (limite do modelo é 500)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if len(user_agent) > 500:
            user_agent = user_agent[:500]
        
        # Truncar observacoes se muito longas (por segurança)
        if observacoes and len(observacoes) > 1000:
            observacoes = observacoes[:1000]
        
        assinatura = AssinaturaDocumento.objects.create(
            anexo=anexo,
            utilizador=request.user,
            tipo_assinatura=tipo_assinatura,
            assinatura_imagem=assinatura_imagem_ref,
            posicao_x=posicao_x,
            posicao_y=posicao_y,
            pagina=pagina,
            ip_address=get_client_ip(request),
            user_agent=user_agent,
            observacoes=observacoes,
            arquivo_original_backup=backup_path[:500] if backup_path and len(backup_path) > 500 else backup_path
        )
        
        messages.success(request, f"Documento '{anexo.nome_original}' assinado com sucesso!")
        
        return JsonResponse({
            'success': True,
            'message': 'Assinatura aplicada com sucesso!',
            'redirect_url': f"/entrada/detalhar/{anexo.expediente.pk}/"
        })
        
    except Exception as e:
        # Mensagens de erro mais amigáveis
        error_message = str(e)
        if 'value too long' in error_message.lower() or 'character varying' in error_message.lower():
            error_message = 'O nome do arquivo ou caminho é muito longo. Tente renomear o arquivo com um nome mais curto.'
        elif 'read of closed file' in error_message.lower():
            error_message = 'Problema ao acessar o arquivo. Tente novamente.'
        elif 'permission denied' in error_message.lower():
            error_message = 'Você não tem permissão para realizar esta ação.'
        elif 'not found' in error_message.lower():
            error_message = 'Arquivo não encontrado. O arquivo pode ter sido removido.'
        elif 'not installed' in error_message.lower() or 'import' in error_message.lower():
            error_message = 'Biblioteca necessária não está instalada. Entre em contato com o administrador.'
        else:
            # Mensagem genérica mais amigável
            error_message = 'Erro ao processar assinatura. Por favor, tente novamente. Se o problema persistir, entre em contato com o suporte.'
        
        return JsonResponse({
            'success': False, 
            'message': error_message
        })


def get_client_ip(request):
    """Obtém o IP do cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class MinhasAssinaturasView(AssinaturaPermitidaMixin, LoginRequiredMixin, ListView):
    """
    View para listar histórico de assinaturas do utilizador
    """
    model = AssinaturaDocumento
    template_name = 'assinatura_digital/minhas_assinaturas.html'
    context_object_name = 'assinaturas'
    paginate_by = 20
    
    def get_queryset(self):
        return AssinaturaDocumento.objects.filter(
            utilizador=self.request.user,
            ativo=True
        ).select_related('anexo', 'anexo__expediente').order_by('-data_assinatura')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_assinaturas'] = self.get_queryset().count()
        return context


class ListarAnexosPendentesView(AssinaturaPermitidaMixin, LoginRequiredMixin, ListView):
    """
    View para listar anexos que o usuário pode assinar mas ainda não assinou
    """
    template_name = 'assinatura_digital/anexos_pendentes_assinatura.html'
    context_object_name = 'anexos'
    paginate_by = 20
    
    def get_queryset(self):
        # Buscar todos os anexos que o usuário pode visualizar
        anexos_acessiveis = AnexoExpediente.objects.filter(
            ativo=True,
            expediente__ativo=True
        ).select_related('expediente')
        
        # Filtrar apenas os que o usuário pode acessar
        anexos_filtrados = [
            anexo for anexo in anexos_acessiveis
            if anexo.pode_assinador_acessar(self.request.user)
            and anexo.pode_ser_assinado()
        ]
        
        # Buscar IDs dos anexos que já têm assinatura do usuário
        anexos_assinados = AssinaturaDocumento.objects.filter(
            utilizador=self.request.user,
            ativo=True
        ).values_list('anexo_id', flat=True)
        
        # Filtrar apenas os que ainda não foram assinados
        anexos_pendentes = [
            anexo for anexo in anexos_filtrados
            if anexo.pk not in anexos_assinados
        ]
        
        return anexos_pendentes
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_pendentes'] = len(self.get_queryset())
        return context
