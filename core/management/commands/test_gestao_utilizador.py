from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.forms_admin import GestaoUtilizadorAdminForm
from users.models import PerfilUtilizador

User = get_user_model()

class Command(BaseCommand):
    help = 'Testa o formulário de gestão de utilizador'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧪 Testando formulário de gestão de utilizador...'))
        
        # Buscar um utilizador existente
        try:
            user = User.objects.first()
            if not user:
                self.stdout.write(self.style.ERROR('❌ Nenhum utilizador encontrado no sistema'))
                return
            
            self.stdout.write(f'👤 Testando com utilizador: {user.get_full_name()} ({user.email})')
            
            # Criar perfil se não existir
            perfil, created = PerfilUtilizador.objects.get_or_create(user=user)
            if created:
                self.stdout.write('✅ PerfilUtilizador criado')
            else:
                self.stdout.write('✅ PerfilUtilizador já existe')
            
            # Testar formulário
            form_data = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'telefone': '+258821234567',
                'tipo_utilizador': user.tipo_utilizador,
                'sector_atual': user.sector_atual.id if user.sector_atual else None,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'receber_notificacoes_email': True,
                'receber_notificacoes_push': True,
                'receber_newsletter': False,
                'perfil_publico': True,
                'mostrar_email': True,
                'mostrar_telefone': False,
                'tema_preferido': 'dark',
                'idioma_preferido': 'pt-pt',
                'timezone': 'Africa/Maputo',
                'horario_trabalho_inicio': '08:00',
                'horario_trabalho_fim': '17:00',
                'dias_trabalho': '1,2,3,4,5',
            }
            
            form = GestaoUtilizadorAdminForm(data=form_data, instance=user)
            
            if form.is_valid():
                self.stdout.write(self.style.SUCCESS('✅ Formulário é válido!'))
                
                # Salvar
                try:
                    saved_user = form.save()
                    self.stdout.write(f'✅ Utilizador salvo: {saved_user.get_full_name()}')
                    
                    # Verificar perfil
                    perfil_atualizado = PerfilUtilizador.objects.get(user=saved_user)
                    self.stdout.write(f'✅ Perfil atualizado:')
                    self.stdout.write(f'   - Notificações email: {perfil_atualizado.receber_notificacoes_email}')
                    self.stdout.write(f'   - Tema preferido: {perfil_atualizado.tema_preferido}')
                    self.stdout.write(f'   - Dias de trabalho: {perfil_atualizado.dias_trabalho}')
                except Exception as save_error:
                    self.stdout.write(f'❌ Erro ao salvar: {str(save_error)}')
                    import traceback
                    self.stdout.write(traceback.format_exc())
                
                self.stdout.write(self.style.SUCCESS('🎉 TESTE CONCLUÍDO COM SUCESSO!'))
                
            else:
                self.stdout.write(self.style.ERROR('❌ Formulário inválido:'))
                for field, errors in form.errors.items():
                    self.stdout.write(f'   - {field}: {errors}')
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro durante o teste: {str(e)}'))
