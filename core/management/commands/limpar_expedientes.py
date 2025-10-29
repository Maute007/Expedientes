from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
import os
import shutil


class Command(BaseCommand):
    help = 'Limpa todos os dados de expedientes e movimentações, preservando configurações'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Executar sem pedir confirmação interativa',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra estatísticas sem apagar dados',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        confirm = options['confirm']

        # Importar modelos necessários
        from core.models import (
            Notificacao, 
            DespachoDocumento, 
            AnexoDespacho
        )
        from entrada.models import (
            Expediente,
            AnexoExpediente,
            ParecerExpediente,
            MovimentacaoDocumento,
            HistoricoExpediente
        )

        # Dicionário com modelos a limpar na ordem correta
        modelos_limpar = [
            ('AnexoDespacho', AnexoDespacho),
            ('DespachoDocumento', DespachoDocumento),
            ('HistoricoExpediente', HistoricoExpediente),
            ('MovimentacaoDocumento', MovimentacaoDocumento),
            ('ParecerExpediente', ParecerExpediente),
            ('AnexoExpediente', AnexoExpediente),
            ('Expediente', Expediente),
            ('Notificacao', Notificacao),
        ]

        self.stdout.write(self.style.WARNING('\n' + '='*80))
        self.stdout.write(self.style.WARNING('🧹 LIMPEZA DE DADOS DE EXPEDIENTES'))
        self.stdout.write(self.style.WARNING('='*80 + '\n'))

        # Contar registros
        estatisticas = {}
        total_apagar = 0

        for nome, modelo in modelos_limpar:
            count = modelo.objects.count()
            estatisticas[nome] = count
            total_apagar += count

        # Mostrar estatísticas
        self.stdout.write('📊 ESTATÍSTICAS ATUAIS:\n')
        for nome, count in estatisticas.items():
            self.stdout.write(f'  - {nome}: {count:,} registros')

        self.stdout.write(f'\n📈 Total de registros a apagar: {total_apagar:,}')

        # Mostrar tabelas preservadas
        self.stdout.write(self.style.SUCCESS('\n✅ TABELAS PRESERVADAS:'))
        self.stdout.write('  - Utilizadores (User)')
        self.stdout.write('  - Perfis de Utilizador')
        self.stdout.write('  - Hierarquia de Utilizadores')
        self.stdout.write('  - Sectores')
        self.stdout.write('  - Estados de Documento')
        self.stdout.write('  - Configurações do Sistema')
        self.stdout.write('  - Tipos de Documento\n')

        # Modo dry-run
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 MODO DRY-RUN: Nenhum dado será apagado\n'))
            return

        # Confirmar operação
        if not confirm:
            self.stdout.write(self.style.ERROR('\n⚠️  ATENÇÃO: Esta operação é IRREVERSÍVEL!\n'))
            resposta = input('Digite "CONFIRMAR" para prosseguir: ')
            
            if resposta != 'CONFIRMAR':
                self.stdout.write(self.style.WARNING('❌ Operação cancelada pelo usuário'))
                return

        # Executar limpeza
        self.stdout.write(self.style.SUCCESS('\n🚀 Iniciando limpeza...\n'))

        try:
            with transaction.atomic():
                registros_apagados = {}
                total_apagado = 0

                # Apagar dados na ordem correta
                for nome, modelo in modelos_limpar:
                    count = modelo.objects.count()
                    
                    if count > 0:
                        resultado = modelo.objects.all().delete()
                        apagados = resultado[0]
                        
                        registros_apagados[nome] = apagados
                        total_apagado += apagados
                        
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ {nome}: {apagados:,} registros apagados')
                        )

                self.stdout.write(f'\n📊 Total apagado: {total_apagado:,} registros')

            # Limpar arquivos de mídia
            self.stdout.write('\n🧹 Limpando arquivos de mídia...')
            self.limpar_arquivos_media()

            self.stdout.write(self.style.SUCCESS('\n✅ Limpeza concluída com sucesso!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Erro durante a limpeza: {str(e)}'))
            raise

    def limpar_arquivos_media(self):
        """Limpa arquivos físicos de anexos"""
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        
        if not media_root:
            self.stdout.write('⚠️  MEDIA_ROOT não configurado')
            return

        # Diretórios a limpar
        diretorios_limpar = [
            os.path.join(media_root, 'expedientes', 'anexos'),
            os.path.join(media_root, 'despachos'),
        ]

        arquivos_apagados = 0
        diretorios_apagados = 0

        for diretorio in diretorios_limpar:
            if os.path.exists(diretorio):
                # Contar arquivos
                for root, dirs, files in os.walk(diretorio):
                    arquivos_apagados += len(files)
                    diretorios_apagados += len(dirs)

                # Apagar todo o conteúdo mas manter estrutura
                for root, dirs, files in os.walk(diretorio, topdown=False):
                    for nome in files:
                        try:
                            os.remove(os.path.join(root, nome))
                        except Exception as e:
                            self.stdout.write(f'⚠️  Erro ao apagar {nome}: {e}')
                    
                    # Apagar diretórios vazios (exceto o diretório raiz)
                    for nome in dirs:
                        try:
                            dir_path = os.path.join(root, nome)
                            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                                shutil.rmtree(dir_path)
                        except Exception as e:
                            self.stdout.write(f'⚠️  Erro ao apagar diretório: {e}')

        if arquivos_apagados > 0:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Arquivos de mídia limpos: {arquivos_apagados:,} arquivos')
            )
        else:
            self.stdout.write('ℹ️  Nenhum arquivo de mídia encontrado')

