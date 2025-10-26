"""
Comando para criar expedientes de teste para demonstrar os badges
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import EstadoDocumento, Sector
from entrada.models import Expediente, TipoDocumento
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria expedientes de teste para demonstrar os badges'

    def handle(self, *args, **options):
        self.stdout.write("=== CRIANDO EXPEDIENTES DE TESTE ===\n")
        
        # Verificar se existem dados necessários
        if not EstadoDocumento.objects.exists():
            self.stdout.write("❌ Estados de documento não encontrados!")
            return
        
        if not User.objects.exists():
            self.stdout.write("❌ Nenhum usuário encontrado!")
            return
        
        # Obter usuário admin
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write("❌ Nenhum usuário admin encontrado!")
            return
        
        # Obter estados
        estado_recebido = EstadoDocumento.objects.filter(nome='Recebido').first()
        estado_encaminhado = EstadoDocumento.objects.filter(nome='Encaminhado').first()
        estado_concluido = EstadoDocumento.objects.filter(nome='Concluído').first()
        
        # Criar tipo de documento se não existir
        tipo_documento, created = TipoDocumento.objects.get_or_create(
            nome='Memorando',
            defaults={
                'categoria': 'interno',
                'descricao': 'Memorando interno',
                'prazo_resposta': 5,
                'prioridade_padrao': 'normal',
                'requer_anexos': False,
                'ativo': True
            }
        )
        
        # Criar sector se não existir
        sector, created = Sector.objects.get_or_create(
            nome='Secretaria Geral',
            defaults={
                'descricao': 'Sector de secretaria geral',
                'ativo': True
            }
        )
        
        # Criar expedientes de teste
        expedientes_criados = 0
        
        # 3 expedientes pendentes (Recebido)
        for i in range(3):
            expediente = Expediente.objects.create(
                numero_protocolo=f'2025010000{i+1}',
                referencia=f'Memorando de teste {i+1}',
                tipo=tipo_documento,
                origem='quiosque',
                remetente=f'Remetente {i+1}',
                assunto=f'Assunto do memorando {i+1}',
                conteudo=f'Conteúdo do memorando {i+1}',
                estado_atual=estado_recebido,
                criado_por=admin_user,
                sector_responsavel=sector,
                data_criacao=timezone.now() - timedelta(days=i)
            )
            expedientes_criados += 1
            self.stdout.write(f"   ✅ Criado expediente pendente: {expediente.numero_protocolo}")
        
        # 2 expedientes enviados (Encaminhado)
        for i in range(2):
            expediente = Expediente.objects.create(
                numero_protocolo=f'2025010000{i+4}',
                referencia=f'Memorando enviado {i+1}',
                tipo=tipo_documento,
                origem='quiosque',
                remetente=f'Remetente enviado {i+1}',
                assunto=f'Assunto enviado {i+1}',
                conteudo=f'Conteúdo enviado {i+1}',
                estado_atual=estado_encaminhado,
                criado_por=admin_user,
                sector_responsavel=sector,
                data_criacao=timezone.now() - timedelta(days=i+3)
            )
            expedientes_criados += 1
            self.stdout.write(f"   ✅ Criado expediente enviado: {expediente.numero_protocolo}")
        
        # 4 expedientes processados (Concluído)
        for i in range(4):
            expediente = Expediente.objects.create(
                numero_protocolo=f'2025010000{i+6}',
                referencia=f'Memorando processado {i+1}',
                tipo=tipo_documento,
                origem='quiosque',
                remetente=f'Remetente processado {i+1}',
                assunto=f'Assunto processado {i+1}',
                conteudo=f'Conteúdo processado {i+1}',
                estado_atual=estado_concluido,
                criado_por=admin_user,
                sector_responsavel=sector,
                data_criacao=timezone.now() - timedelta(days=i+5)
            )
            expedientes_criados += 1
            self.stdout.write(f"   ✅ Criado expediente processado: {expediente.numero_protocolo}")
        
        self.stdout.write(f"\n=== RESUMO ===")
        self.stdout.write(f"Total de expedientes criados: {expedientes_criados}")
        self.stdout.write(f"- Pendentes (Recebido): 3")
        self.stdout.write(f"- Enviados (Encaminhado): 2")
        self.stdout.write(f"- Processados (Concluído): 4")
        
        self.stdout.write(f"\n✅ Dados de teste criados com sucesso!")
        self.stdout.write(f"Acesse: http://localhost:8000/ para ver os badges funcionando.")
