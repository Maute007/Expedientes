from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Notificacao


class Command(BaseCommand):
    help = 'Limpa notificações antigas do sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=30,
            help='Número de dias para manter notificações (padrão: 30)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra quantas notificações seriam removidas sem removê-las',
        )

    def handle(self, *args, **options):
        dias = options['dias']
        dry_run = options['dry_run']

        self.stdout.write(
            self.style.SUCCESS(f'🧹 Limpando notificações com mais de {dias} dias...')
        )

        # Calcular data limite
        data_limite = timezone.now() - timedelta(days=dias)
        
        # Buscar notificações antigas
        notificacoes_antigas = Notificacao.objects.filter(
            data_criacao__lt=data_limite
        )

        total_antigas = notificacoes_antigas.count()
        
        if total_antigas == 0:
            self.stdout.write('✅ Nenhuma notificação antiga encontrada')
            return

        # Separar por tipo
        lidas = notificacoes_antigas.filter(lida=True).count()
        nao_lidas = notificacoes_antigas.filter(lida=False).count()

        self.stdout.write(f'📊 Estatísticas:')
        self.stdout.write(f'  📧 Total de notificações antigas: {total_antigas}')
        self.stdout.write(f'  ✅ Notificações lidas: {lidas}')
        self.stdout.write(f'  ❌ Notificações não lidas: {nao_lidas}')

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'🔍 DRY RUN: {total_antigas} notificações seriam removidas')
            )
            return

        # Confirmar remoção
        if total_antigas > 0:
            confirmar = input(f'⚠️  Remover {total_antigas} notificações antigas? (s/N): ')
            if confirmar.lower() != 's':
                self.stdout.write('❌ Operação cancelada')
                return

        # Remover notificações antigas
        removidas = notificacoes_antigas.delete()[0]
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {removidas} notificações removidas com sucesso')
        )

        # Mostrar estatísticas finais
        total_restantes = Notificacao.objects.count()
        self.stdout.write(f'📊 Notificações restantes no sistema: {total_restantes}')
