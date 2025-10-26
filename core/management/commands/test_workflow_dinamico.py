from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from entrada.models import Expediente
from core.models import EstadoDocumento

User = get_user_model()

class Command(BaseCommand):
    help = 'Testa sistema de workflow dinâmico'

    def handle(self, *args, **options):
        # Testar com diferentes tipos de utilizadores
        users = {
            'pca': User.objects.filter(tipo_utilizador='pca').first(),
            'secretaria': User.objects.filter(tipo_utilizador='secretaria').first(),
            'chefe': User.objects.filter(tipo_utilizador='chefe').first(),
            'colaborador': User.objects.filter(tipo_utilizador='colaborador').first(),
        }
        
        # Testar com diferentes estados
        expediente = Expediente.objects.first()
        
        if not expediente:
            self.stdout.write(self.style.ERROR('Nenhum expediente encontrado'))
            return
        
        estados = EstadoDocumento.objects.filter(ativo=True)
        
        for estado in estados:
            expediente.estado_atual = estado
            expediente.save()
            
            self.stdout.write(self.style.SUCCESS(f'\n=== ESTADO: {estado.nome} ==='))
            
            for tipo, user in users.items():
                if user:
                    acoes = expediente.obter_acoes_disponiveis(user)
                    self.stdout.write(f'{tipo.upper()}: {len(acoes)} ações')
                    for acao in acoes:
                        self.stdout.write(f'  - {acao["label"]}')
