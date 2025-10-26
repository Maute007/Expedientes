from django.core.management.base import BaseCommand
from relatorios.models import TipoRelatorio


class Command(BaseCommand):
    help = 'Cria tipos de relatórios iniciais'

    def handle(self, *args, **options):
        tipos_relatorio = [
            {
                'nome': 'Documentos por Sector',
                'descricao': 'Relatório de documentos agrupados por sector',
                'tipo_relatorio': 'documentos_sector',
                'template': 'documentos_sector.html',
                'parametros_obrigatorios': ['data_inicio', 'data_fim'],
                'parametros_opcionais': ['sector_id', 'estado_id', 'formato', 'incluir_graficos'],
                'formato_saida': 'pdf',
                'ordem': 1
            },
            {
                'nome': 'Tempo de Resposta',
                'descricao': 'Relatório de tempo médio de resposta por sector',
                'tipo_relatorio': 'tempo_resposta',
                'template': 'tempo_resposta.html',
                'parametros_obrigatorios': ['data_inicio', 'data_fim'],
                'parametros_opcionais': ['sector_id', 'agrupar_por', 'incluir_graficos'],
                'formato_saida': 'pdf',
                'ordem': 2
            },
            {
                'nome': 'Estados de Documentos',
                'descricao': 'Relatório de distribuição de documentos por estado',
                'tipo_relatorio': 'estados_documentos',
                'template': 'estados_documentos.html',
                'parametros_obrigatorios': ['data_inicio', 'data_fim'],
                'parametros_opcionais': ['sector_id', 'formato', 'incluir_graficos'],
                'formato_saida': 'pdf',
                'ordem': 3
            },
            {
                'nome': 'Atividade de Utilizadores',
                'descricao': 'Relatório de atividade dos utilizadores do sistema',
                'tipo_relatorio': 'atividade_utilizadores',
                'template': 'atividade_utilizadores.html',
                'parametros_obrigatorios': ['data_inicio', 'data_fim'],
                'parametros_opcionais': ['utilizador_id', 'tipo_atividade', 'formato'],
                'formato_saida': 'pdf',
                'ordem': 4
            },
            {
                'nome': 'Eficiência por Sector',
                'descricao': 'Relatório de eficiência e performance por sector',
                'tipo_relatorio': 'eficiencia_sector',
                'template': 'eficiencia_sector.html',
                'parametros_obrigatorios': ['data_inicio', 'data_fim'],
                'parametros_opcionais': ['sector_id', 'formato', 'incluir_graficos'],
                'formato_saida': 'pdf',
                'ordem': 5
            },
            {
                'nome': 'Performance Geral',
                'descricao': 'Relatório geral de performance do sistema',
                'tipo_relatorio': 'performance_geral',
                'template': 'performance_geral.html',
                'parametros_obrigatorios': ['data_inicio', 'data_fim'],
                'parametros_opcionais': ['formato', 'incluir_graficos'],
                'formato_saida': 'pdf',
                'ordem': 6
            },
            {
                'nome': 'Documentos por Período',
                'descricao': 'Relatório de documentos agrupados por período',
                'tipo_relatorio': 'documentos_periodo',
                'template': 'documentos_periodo.html',
                'parametros_obrigatorios': ['data_inicio', 'data_fim'],
                'parametros_opcionais': ['sector_id', 'agrupar_por', 'formato'],
                'formato_saida': 'pdf',
                'ordem': 7
            }
        ]

        for tipo_data in tipos_relatorio:
            tipo, created = TipoRelatorio.objects.get_or_create(
                nome=tipo_data['nome'],
                defaults=tipo_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Criado tipo de relatório: {tipo.nome}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Tipo de relatório já existe: {tipo.nome}')
                )

        self.stdout.write(
            self.style.SUCCESS('Tipos de relatórios criados com sucesso!')
        )
