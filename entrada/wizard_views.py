"""
Implementação de Wizard para formulários multi-etapas usando django-formtools
Esta é uma implementação mais robusta e seguindo as melhores práticas.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django import forms
from .models import Expediente, AnexoExpediente
from .forms import Etapa1Form, Etapa2Form, Etapa3Form, Etapa4Form
from core.models import EstadoDocumento


class ExpedienteWizardView(LoginRequiredMixin, TemplateView):
    """
    Wizard para criação de expedientes em múltiplas etapas.
    Implementa o padrão Wizard seguindo as melhores práticas do Django.
    """
    template_name = 'entrada/wizard.html'
    
    # Definição das etapas
    STEPS = [
        'etapa1',  # Informações Básicas
        'etapa2',  # Detalhes
        'etapa3',  # Membros
        'etapa4',  # Revisão
    ]
    
    def dispatch(self, request, *args, **kwargs):
        # Inicializar dados do wizard na sessão
        if 'wizard_data' not in request.session:
            request.session['wizard_data'] = {}
            request.session['wizard_step'] = 0
            request.session['wizard_expediente_id'] = None
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        current_step = self.get_current_step()
        context.update({
            'current_step': current_step,
            'total_steps': len(self.STEPS),
            'step_number': current_step + 1,
            'progress_percentage': ((current_step + 1) / len(self.STEPS)) * 100,
            'can_go_back': current_step > 0,
            'can_go_forward': current_step < len(self.STEPS) - 1,
            'is_last_step': current_step == len(self.STEPS) - 1,
        })
        
        return context
    
    def get_current_step(self):
        """Retorna o índice da etapa atual"""
        return self.request.session.get('wizard_step', 0)
    
    def get_current_step_name(self):
        """Retorna o nome da etapa atual"""
        step_index = self.get_current_step()
        return self.STEPS[step_index] if step_index < len(self.STEPS) else None
    
    def get_form_class(self):
        """Retorna a classe do formulário para a etapa atual"""
        step_name = self.get_current_step_name()
        
        form_classes = {
            'etapa1': Etapa1Form,
            'etapa2': Etapa2Form,
            'etapa3': Etapa3Form,
            'etapa4': Etapa4Form,
        }
        
        return form_classes.get(step_name)
    
    def get_form(self):
        """Retorna uma instância do formulário para a etapa atual"""
        form_class = self.get_form_class()
        if not form_class:
            return None
        
        # Carregar dados da sessão se existirem
        wizard_data = self.request.session.get('wizard_data', {})
        step_data = wizard_data.get(self.get_current_step_name(), {})
        
        if self.request.method == 'POST':
            return form_class(data=self.request.POST, initial=step_data)
        else:
            return form_class(initial=step_data)
    
    def get(self, request, *args, **kwargs):
        form = self.get_form()
        if form is None:
            messages.error(request, 'Etapa inválida.')
            return redirect('entrada:lista_expedientes')
        
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form is None:
            messages.error(request, 'Etapa inválida.')
            return redirect('entrada:lista_expedientes')
        
        if form.is_valid():
            return self.process_valid_form(form)
        else:
            return self.process_invalid_form(form)
    
    def process_valid_form(self, form):
        """Processa um formulário válido"""
        current_step_name = self.get_current_step_name()
        wizard_data = self.request.session.get('wizard_data', {})
        
        # Salvar dados da etapa atual
        wizard_data[current_step_name] = form.cleaned_data
        
        # Processar arquivos se for etapa 2
        if current_step_name == 'etapa2' and 'anexos' in self.request.FILES:
            anexos_files = self.request.FILES.getlist('anexos')
            etapa2_files = []
            for anexo in anexos_files:
                etapa2_files.append({
                    'arquivo': anexo,
                    'nome_original': anexo.name,
                    'tamanho': anexo.size,
                    'tipo_mime': anexo.content_type
                })
            wizard_data['etapa2_files'] = etapa2_files
        
        self.request.session['wizard_data'] = wizard_data
        
        # Se for a última etapa, criar o objeto final
        if self.get_current_step() == len(self.STEPS) - 1:
            return self.finish_wizard()
        else:
            # Avançar para próxima etapa
            self.request.session['wizard_step'] = self.get_current_step() + 1
            messages.success(self.request, f'Etapa {self.get_current_step() + 1} concluída!')
            return redirect('entrada:wizard')
    
    def process_invalid_form(self, form):
        """Processa um formulário inválido"""
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)
    
    def finish_wizard(self):
        """Finaliza o wizard criando o objeto final"""
        try:
            wizard_data = self.request.session.get('wizard_data', {})
            
            # Criar o expediente com todos os dados
            expediente = self.create_expediente(wizard_data)
            
            # Limpar dados do wizard
            self.clear_wizard_data()
            
            messages.success(self.request, 'Expediente criado com sucesso!')
            return redirect('entrada:detalhar_expediente', pk=expediente.id)
            
        except Exception as e:
            messages.error(self.request, f'Erro ao criar expediente: {str(e)}')
            return redirect('entrada:wizard')
    
    def create_expediente(self, wizard_data):
        """Cria o expediente final com todos os dados das etapas"""
        # Dados da etapa 1
        etapa1_data = wizard_data.get('etapa1', {})
        
        expediente = Expediente(
            numero_protocolo=etapa1_data.get('numero_protocolo') or self.generate_protocol_number(),
            referencia=etapa1_data.get('referencia', ''),
            tipo=etapa1_data.get('tipo'),
            origem=etapa1_data.get('origem', ''),
            remetente=etapa1_data.get('remetente', ''),
            criado_por=self.request.user,
            estado_atual=self.get_estado_inicial(),
        )
        
        # Verificar se o usuário tem sector_atual
        if hasattr(self.request.user, 'sector_atual') and self.request.user.sector_atual:
            expediente.sector_responsavel = self.request.user.sector_atual
        
        # Dados da etapa 2
        etapa2_data = wizard_data.get('etapa2', {})
        if etapa2_data:
            expediente.assunto = etapa2_data.get('assunto', '')
            expediente.descricao = etapa2_data.get('descricao', '')
            expediente.telefone = etapa2_data.get('telefone', '')
            expediente.prioridade = etapa2_data.get('prioridade', 'normal')
            expediente.data_limite = etapa2_data.get('data_limite')
            expediente.requer_resposta = etapa2_data.get('requer_resposta', False)
            expediente.confidencial = etapa2_data.get('confidencial', False)
            expediente.numero_paginas = etapa2_data.get('numero_paginas', 0)
            expediente.valor_monetario = etapa2_data.get('valor_monetario', 0)
            expediente.observacoes = etapa2_data.get('observacoes', '')
        
        # Salvar o expediente
        expediente.save()
        
        # Processar anexos da etapa 2
        etapa2_files = wizard_data.get('etapa2_files', [])
        for anexo_data in etapa2_files:
            AnexoExpediente.objects.create(
                expediente=expediente,
                arquivo=anexo_data['arquivo'],
                nome_original=anexo_data['nome_original'],
                tamanho=anexo_data['tamanho'],
                tipo_mime=anexo_data['tipo_mime'],
                upload_por=self.request.user
            )
        
        # Dados da etapa 3 (membros e sectores)
        etapa3_data = wizard_data.get('etapa3', {})
        if etapa3_data:
            # Adicionar sectores envolvidos
            sectores_envolvidos = etapa3_data.get('sectores_envolvidos', [])
            expediente.sectores_envolvidos.set(sectores_envolvidos)
            
            # Adicionar membros envolvidos
            membros_envolvidos = etapa3_data.get('membros_envolvidos', [])
            expediente.membros_envolvidos.set(membros_envolvidos)
        
        return expediente
    
    def generate_protocol_number(self):
        """Gera um número de protocolo"""
        temp_expediente = Expediente()
        return temp_expediente.gerar_numero_protocolo()
    
    def get_estado_inicial(self):
        """Retorna o estado inicial dos expedientes"""
        return EstadoDocumento.objects.filter(nome='Recebido').first()
    
    def clear_wizard_data(self):
        """Limpa os dados do wizard da sessão"""
        self.request.session.pop('wizard_data', None)
        self.request.session.pop('wizard_step', None)
        self.request.session.pop('wizard_expediente_id', None)
    
    def go_back(self):
        """Volta para a etapa anterior"""
        current_step = self.get_current_step()
        if current_step > 0:
            self.request.session['wizard_step'] = current_step - 1
            return redirect('entrada:wizard')
        return redirect('entrada:wizard')
    
    def reset_wizard(self):
        """Reinicia o wizard"""
        self.clear_wizard_data()
        return redirect('entrada:wizard')


class WizardStepView(ExpedienteWizardView):
    """
    View para navegar entre etapas do wizard
    """
    
    def get(self, request, *args, **kwargs):
        step_name = kwargs.get('step')
        
        if step_name == 'back':
            return self.go_back()
        elif step_name == 'reset':
            return self.reset_wizard()
        else:
            # Definir etapa específica
            try:
                step_index = self.STEPS.index(step_name)
                self.request.session['wizard_step'] = step_index
            except ValueError:
                messages.error(request, 'Etapa inválida.')
                return redirect('entrada:wizard')
        
        return super().get(request, *args, **kwargs)
