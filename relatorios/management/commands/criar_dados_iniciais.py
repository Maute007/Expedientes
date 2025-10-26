from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import json

from relatorios.models import ConfiguracaoRelatorio, TipoRelatorio, ExecucaoRelatorio, Dashboard, WidgetDashboard
from core.models import Sector, EstadoDocumento
from entrada.models import Expediente, TipoDocumento

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria dados iniciais para o sistema de relatórios'

    def handle(self, *args, **options):
        self.stdout.write('Criando dados iniciais para o sistema de relatórios...')
        
        # Criar tipos de relatório
        self.criar_tipos_relatorio()
        
        # Criar configurações de relatório
        self.criar_configuracoes_relatorio()
        
        # Criar dashboards
        self.criar_dashboards()
        
        # Criar execuções de relatório
        self.criar_execucoes_relatorio()
        
        self.stdout.write(
            self.style.SUCCESS('Dados iniciais criados com sucesso!')
        )

    def criar_tipos_relatorio(self):
        """Cria tipos de relatório padrão."""
        tipos = [
            {
                'nome': 'Documentos por Sector',
                'descricao': 'Relatório de documentos agrupados por sector',
                'tipo_relatorio': 'documentos_sector',
                'template': 'relatorios/documentos_sector.html',
                'parametros_obrigatorios': ['data_inicio', 'data_fim'],
                'formato_saida': 'pdf',
                'ativo': True
            },
            {
                'nome': 'Tempo de Resposta',
                'descricao': 'Relatório de tempo médio de resposta por sector',
                'tipo_relatorio': 'tempo_resposta',
                'template': 'relatorios/tempo_resposta.html',
                'parametros_obrigatorios': ['data_inicio', 'data_fim'],
                'formato_saida': 'excel',
                'ativo': True
            },
            {
                'nome': 'Estados de Documentos',
                'descricao': 'Relatório de distribuição de documentos por estado',
                'tipo_relatorio': 'estados_documentos',
                'template': 'relatorios/estados_documentos.html',
                'parametros_obrigatorios': [],
                'formato_saida': 'csv',
                'ativo': True
            },
            {
                'nome': 'Atividade de Utilizadores',
                'descricao': 'Relatório de atividade dos utilizadores do sistema',
                'tipo_relatorio': 'atividade_utilizadores',
                'template': 'relatorios/atividade_utilizadores.html',
                'parametros_obrigatorios': ['sector'],
                'formato_saida': 'pdf',
                'ativo': True
            },
            {
                'nome': 'Performance por Sector',
                'descricao': 'Relatório de performance e eficiência por sector',
                'tipo_relatorio': 'performance_sector',
                'template': 'relatorios/performance_sector.html',
                'parametros_obrigatorios': ['data_inicio', 'data_fim'],
                'formato_saida': 'excel',
                'ativo': True
            }
        ]
        
        for tipo_data in tipos:
            tipo, created = TipoRelatorio.objects.get_or_create(
                nome=tipo_data['nome'],
                defaults=tipo_data
            )
            if created:
                self.stdout.write(f'  ✓ Tipo de relatório criado: {tipo.nome}')

    def criar_configuracoes_relatorio(self):
        """Cria configurações de relatório padrão."""
        # Obter tipos de relatório
        tipo_documentos = TipoRelatorio.objects.get(nome='Documentos por Sector')
        tipo_tempo = TipoRelatorio.objects.get(nome='Tempo de Resposta')
        tipo_estados = TipoRelatorio.objects.get(nome='Estados de Documentos')
        tipo_atividade = TipoRelatorio.objects.get(nome='Atividade de Utilizadores')
        tipo_performance = TipoRelatorio.objects.get(nome='Performance por Sector')
        
        # Obter sector padrão
        sector_padrao = Sector.objects.first()
        
        # Obter utilizador admin
        admin_user = User.objects.filter(is_superuser=True).first()
        
        configuracoes = [
            {
                'nome': 'Relatório Mensal de Documentos',
                'descricao': 'Relatório mensal de documentos por sector',
                'tipo_relatorio': tipo_documentos,
                'parametros': {
                    'data_inicio': '2024-01-01',
                    'data_fim': '2024-01-31',
                    'incluir_graficos': True,
                    'incluir_estatisticas': True
                },
                'sector': sector_padrao,
                'utilizador_criador': admin_user,
                'ativo': True,
                'publico': True
            },
            {
                'nome': 'Análise de Tempo de Resposta',
                'descricao': 'Análise detalhada do tempo de resposta por sector',
                'tipo_relatorio': tipo_tempo,
                'parametros': {
                    'data_inicio': '2024-01-01',
                    'data_fim': '2024-01-31',
                    'incluir_comparacao': True,
                    'incluir_tendencias': True
                },
                'sector': sector_padrao,
                'utilizador_criador': admin_user,
                'ativo': True,
                'publico': True
            },
            {
                'nome': 'Dashboard de Estados',
                'descricao': 'Relatório de distribuição de estados de documentos',
                'tipo_relatorio': tipo_estados,
                'parametros': {
                    'incluir_graficos': True,
                    'incluir_historico': True
                },
                'sector': sector_padrao,
                'utilizador_criador': admin_user,
                'ativo': True,
                'publico': True
            },
            {
                'nome': 'Relatório de Atividade',
                'descricao': 'Relatório de atividade dos utilizadores',
                'tipo_relatorio': tipo_atividade,
                'parametros': {
                    'sector': 'todos',
                    'incluir_metricas': True,
                    'incluir_ranking': True
                },
                'sector': sector_padrao,
                'utilizador_criador': admin_user,
                'ativo': True,
                'publico': False
            },
            {
                'nome': 'Performance Trimestral',
                'descricao': 'Relatório trimestral de performance por sector',
                'tipo_relatorio': tipo_performance,
                'parametros': {
                    'data_inicio': '2024-01-01',
                    'data_fim': '2024-03-31',
                    'incluir_benchmarking': True,
                    'incluir_recomendacoes': True
                },
                'sector': sector_padrao,
                'utilizador_criador': admin_user,
                'ativo': True,
                'publico': True
            }
        ]
        
        for config_data in configuracoes:
            config, created = ConfiguracaoRelatorio.objects.get_or_create(
                nome=config_data['nome'],
                defaults=config_data
            )
            if created:
                self.stdout.write(f'  ✓ Configuração de relatório criada: {config.nome}')

    def criar_dashboards(self):
        """Cria dashboards padrão."""
        # Obter sector padrão
        sector_padrao = Sector.objects.first()
        
        # Obter utilizador admin
        admin_user = User.objects.filter(is_superuser=True).first()
        
        dashboards = [
            {
                'nome': 'Dashboard Principal',
                'descricao': 'Dashboard principal com visão geral do sistema',
                'sector': sector_padrao,
                'utilizador_criador': admin_user,
                'widgets': [
                    {
                        'id': 1,
                        'tipo': 'contador',
                        'titulo': 'Total de Documentos',
                        'parametros': {'tipo': 'documentos_total'},
                        'posicao': {'x': 0, 'y': 0},
                        'tamanho': {'width': 2, 'height': 1}
                    },
                    {
                        'id': 2,
                        'tipo': 'contador',
                        'titulo': 'Documentos Pendentes',
                        'parametros': {'tipo': 'documentos_pendentes'},
                        'posicao': {'x': 2, 'y': 0},
                        'tamanho': {'width': 2, 'height': 1}
                    },
                    {
                        'id': 3,
                        'tipo': 'grafico_barras',
                        'titulo': 'Documentos por Sector',
                        'parametros': {'tipo': 'documentos_sector'},
                        'posicao': {'x': 0, 'y': 1},
                        'tamanho': {'width': 4, 'height': 2}
                    },
                    {
                        'id': 4,
                        'tipo': 'grafico_pizza',
                        'titulo': 'Distribuição por Estado',
                        'parametros': {'tipo': 'documentos_estado'},
                        'posicao': {'x': 4, 'y': 1},
                        'tamanho': {'width': 2, 'height': 2}
                    },
                    {
                        'id': 5,
                        'tipo': 'tabela',
                        'titulo': 'Documentos Recentes',
                        'parametros': {'tipo': 'documentos_recentes'},
                        'posicao': {'x': 0, 'y': 3},
                        'tamanho': {'width': 6, 'height': 2}
                    }
                ],
                'layout': 'grid',
                'ativo': True,
                'publico': True
            },
            {
                'nome': 'Dashboard de Performance',
                'descricao': 'Dashboard focado em métricas de performance',
                'sector': sector_padrao,
                'utilizador_criador': admin_user,
                'widgets': [
                    {
                        'id': 1,
                        'tipo': 'metricas',
                        'titulo': 'Métricas Gerais',
                        'parametros': {'tipo': 'geral'},
                        'posicao': {'x': 0, 'y': 0},
                        'tamanho': {'width': 6, 'height': 2}
                    },
                    {
                        'id': 2,
                        'tipo': 'grafico_linha',
                        'titulo': 'Tendência de Documentos',
                        'parametros': {'tipo': 'documentos_periodo'},
                        'posicao': {'x': 0, 'y': 2},
                        'tamanho': {'width': 6, 'height': 2}
                    }
                ],
                'layout': 'grid',
                'ativo': True,
                'publico': False
            }
        ]
        
        for dashboard_data in dashboards:
            dashboard, created = Dashboard.objects.get_or_create(
                nome=dashboard_data['nome'],
                defaults=dashboard_data
            )
            if created:
                self.stdout.write(f'  ✓ Dashboard criado: {dashboard.nome}')

    def criar_execucoes_relatorio(self):
        """Cria execuções de relatório de exemplo."""
        # Obter configurações de relatório
        configs = ConfiguracaoRelatorio.objects.all()[:3]
        
        # Obter utilizador admin
        admin_user = User.objects.filter(is_superuser=True).first()
        
        for config in configs:
            # Criar algumas execuções de exemplo
            for i in range(3):
                execucao = ExecucaoRelatorio.objects.create(
                    relatorio=config,
                    utilizador=admin_user,
                    data_execucao=timezone.now() - timedelta(days=i*7),
                    status='concluido',
                    parametros_utilizados=config.parametros,
                    erro=''
                )
                
                # Simular ficheiro gerado
                execucao.ficheiro_gerado = f'relatorios/{config.nome}_{i+1}.pdf'
                execucao.save()
                
                self.stdout.write(f'  ✓ Execução criada: {config.nome} - {execucao.data_execucao.strftime("%d/%m/%Y")}')
