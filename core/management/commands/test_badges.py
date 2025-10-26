"""
Comando para testar os badges de estatísticas no navbar
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.context_processors import estatisticas_documentos_contexto
from core.models import EstadoDocumento
from entrada.models import Expediente

User = get_user_model()


class Command(BaseCommand):
    help = 'Testa os badges de estatísticas no navbar'

    def handle(self, *args, **options):
        self.stdout.write("=== TESTE DOS BADGES DE ESTATÍSTICAS ===\n")
        
        # Verificar se existem estados de documento
        self.stdout.write("1. Verificando estados de documento:")
        estados = EstadoDocumento.objects.all()
        for estado in estados:
            self.stdout.write(f"   - {estado.nome} (ID: {estado.id})")
        
        if not estados.exists():
            self.stdout.write("   ❌ Nenhum estado encontrado! Execute: python manage.py loaddata core/fixtures/estados_documento.json")
            return
        
        # Verificar se existem expedientes
        self.stdout.write("\n2. Verificando expedientes:")
        total_expedientes = Expediente.objects.count()
        self.stdout.write(f"   - Total de expedientes: {total_expedientes}")
        
        if total_expedientes == 0:
            self.stdout.write("   ⚠️  Nenhum expediente encontrado. Os badges mostrarão 0.")
        
        # Verificar contagem por estado
        self.stdout.write("\n3. Contagem por estado:")
        estado_recebido = EstadoDocumento.objects.filter(nome='Recebido').first()
        estado_encaminhado = EstadoDocumento.objects.filter(nome='Encaminhado').first()
        estado_concluido = EstadoDocumento.objects.filter(nome='Concluído').first()
        
        if estado_recebido:
            count_recebido = Expediente.objects.filter(estado_atual=estado_recebido).count()
            self.stdout.write(f"   - Recebido (Pendentes): {count_recebido}")
        
        if estado_encaminhado:
            count_encaminhado = Expediente.objects.filter(estado_atual=estado_encaminhado).count()
            self.stdout.write(f"   - Encaminhado (Enviadas): {count_encaminhado}")
        
        if estado_concluido:
            count_concluido = Expediente.objects.filter(estado_atual=estado_concluido).count()
            self.stdout.write(f"   - Concluído (Processadas): {count_concluido}")
        
        # Testar context processor
        self.stdout.write("\n4. Testando context processor:")
        try:
            # Simular request
            class MockRequest:
                def __init__(self, user):
                    self.user = user
            
            # Testar com usuário admin
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                request = MockRequest(admin_user)
                context = estatisticas_documentos_contexto(request)
                
                self.stdout.write(f"   - total_processadas: {context['total_processadas']}")
                self.stdout.write(f"   - total_enviadas: {context['total_enviadas']}")
                self.stdout.write(f"   - total_pendentes: {context['total_pendentes']}")
                
                if context['total_processadas'] > 0 or context['total_enviadas'] > 0 or context['total_pendentes'] > 0:
                    self.stdout.write("   ✅ Context processor funcionando!")
                else:
                    self.stdout.write("   ⚠️  Context processor funcionando, mas sem dados para mostrar.")
            else:
                self.stdout.write("   ❌ Nenhum usuário admin encontrado!")
                
        except Exception as e:
            self.stdout.write(f"   ❌ Erro no context processor: {e}")
        
        # Sugestões
        self.stdout.write("\n5. Sugestões:")
        if total_expedientes == 0:
            self.stdout.write("   - Crie alguns expedientes para testar os badges")
            self.stdout.write("   - Acesse: http://localhost:8000/entrada/etapa1/")
        
        if not estados.exists():
            self.stdout.write("   - Carregue os estados: python manage.py loaddata core/fixtures/estados_documento.json")
        
        self.stdout.write("\n=== FIM DO TESTE ===")
