from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy


class BaseViewMixin:
    """
    Mixin base para views com funcionalidades comuns.
    """
    pass


class AlertMixin:
    """
    Mixin para adicionar alertas ao sistema de notificações.
    """
    
    def add_alert(self, message, alert_type='success'):
        """
        Adiciona um alerta que será exibido via JavaScript.
        """
        messages.add_message(
            self.request, 
            messages.INFO, 
            f'ALERT:{alert_type}:{message}'
        )
    
    def success_alert(self, message):
        """Adiciona alerta de sucesso."""
        self.add_alert(message, 'success')
    
    def error_alert(self, message):
        """Adiciona alerta de erro."""
        self.add_alert(message, 'error')
    
    def warning_alert(self, message):
        """Adiciona alerta de aviso."""
        self.add_alert(message, 'warning')
    
    def info_alert(self, message):
        """Adiciona alerta de informação."""
        self.add_alert(message, 'info')


class FormAlertMixin(AlertMixin):
    """
    Mixin para formulários com alertas.
    """
    
    def form_valid(self, form):
        """Processa formulário válido com alerta."""
        response = super().form_valid(form)
        if hasattr(self, 'get_success_message'):
            self.success_alert(self.get_success_message())
        else:
            # Mensagem contextual baseada no tipo de operação
            if hasattr(self, 'model'):
                model_name = self.model._meta.verbose_name
                if 'create' in str(type(self)).lower():
                    self.success_alert(f'{model_name} criado com sucesso!')
                elif 'update' in str(type(self)).lower():
                    self.success_alert(f'{model_name} atualizado com sucesso!')
                else:
                    self.success_alert(f'{model_name} processado com sucesso!')
            else:
                self.success_alert('Operação realizada com sucesso!')
        return response
    
    def form_invalid(self, form):
        """Processa formulário inválido com alerta."""
        # Mensagem contextual baseada no tipo de operação
        if hasattr(self, 'model'):
            model_name = self.model._meta.verbose_name
            if 'create' in str(type(self)).lower():
                self.error_alert(f'Erro ao criar {model_name}. Verifique os dados informados.')
            elif 'update' in str(type(self)).lower():
                self.error_alert(f'Erro ao atualizar {model_name}. Verifique os dados informados.')
            else:
                self.error_alert(f'Erro ao processar {model_name}. Verifique os dados informados.')
        else:
            self.error_alert('Por favor, corrija os erros no formulário.')
        return super().form_invalid(form)