import os
import json
import csv
import io
from datetime import datetime, timedelta
from decimal import Decimal
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q, F
from django.db.models.functions import TruncDay, TruncMonth, TruncWeek
from django.core.files.base import ContentFile
from django.conf import settings
from core.models import Sector, EstadoDocumento
from entrada.models import Expediente, TipoDocumento
from .models import ExecucaoRelatorio
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch


class RelatorioGenerator:
    """
    Classe para geração de relatórios em diferentes formatos.
    """
    
    def __init__(self, execucao_relatorio):
        self.execucao = execucao_relatorio
        self.relatorio = execucao_relatorio.relatorio
        self.tipo_relatorio = self.relatorio.tipo_relatorio
        self.parametros = execucao_relatorio.parametros_utilizados
        self.filtros = execucao_relatorio.filtros_utilizados
    
    def gerar_relatorio(self):
        """
        Gera o relatório baseado no tipo e formato configurado.
        """
        try:
            # Atualizar status para processando
            self.execucao.status = 'processando'
            self.execucao.save(update_fields=['status'])
            
            # Obter dados
            dados = self._obter_dados()
            
            # Gerar ficheiro baseado no formato
            formato = self.parametros.get('formato', 'pdf')
            
            if formato == 'pdf':
                ficheiro = self._gerar_pdf(dados)
            elif formato == 'excel':
                ficheiro = self._gerar_excel(dados)
            elif formato == 'csv':
                ficheiro = self._gerar_csv(dados)
            elif formato == 'html':
                ficheiro = self._gerar_html(dados)
            else:
                raise ValueError(f"Formato '{formato}' não suportado.")
            
            # Salvar ficheiro
            nome_ficheiro = f"{self.relatorio.nome}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{formato}"
            self.execucao.ficheiro_gerado.save(nome_ficheiro, ficheiro)
            self.execucao.tamanho_ficheiro = self.execucao.ficheiro_gerado.size
            
            # Atualizar status para concluído
            self.execucao.status = 'concluido'
            self.execucao.data_conclusao = timezone.now()
            self.execucao.save(update_fields=['status', 'data_conclusao', 'tamanho_ficheiro'])
            
            return True
            
        except Exception as e:
            # Atualizar status para erro
            self.execucao.status = 'erro'
            self.execucao.erro = str(e)
            self.execucao.data_conclusao = timezone.now()
            self.execucao.save(update_fields=['status', 'erro', 'data_conclusao'])
            return False
    
    def _obter_dados(self):
        """
        Obtém os dados baseados no tipo de relatório.
        """
        tipo = self.tipo_relatorio.tipo_relatorio
        
        if tipo == 'documentos_sector':
            return self._dados_documentos_sector()
        elif tipo == 'tempo_resposta':
            return self._dados_tempo_resposta()
        elif tipo == 'estados_documentos':
            return self._dados_estados_documentos()
        elif tipo == 'comunicacao_sector':
            return self._dados_comunicacao_sector()
        elif tipo == 'atividade_utilizadores':
            return self._dados_atividade_utilizadores()
        elif tipo == 'eficiencia_sector':
            return self._dados_eficiencia_sector()
        elif tipo == 'utilizacao_sistema':
            return self._dados_utilizacao_sistema()
        elif tipo == 'documentos_periodo':
            return self._dados_documentos_periodo()
        elif tipo == 'performance_geral':
            return self._dados_performance_geral()
        else:
            return {}
    
    def _dados_documentos_sector(self):
        """
        Dados para relatório de documentos por sector.
        """
        queryset = Expediente.objects.filter(ativo=True)
        
        # Aplicar filtros
        if self.filtros.get('data_inicio'):
            queryset = queryset.filter(data_criacao__date__gte=self.filtros['data_inicio'])
        if self.filtros.get('data_fim'):
            queryset = queryset.filter(data_criacao__date__lte=self.filtros['data_fim'])
        if self.filtros.get('sector'):
            queryset = queryset.filter(sector_responsavel=self.filtros['sector'])
        if self.filtros.get('estado'):
            queryset = queryset.filter(estado_atual=self.filtros['estado'])
        
        # Agrupar por sector
        dados = queryset.values('sector_responsavel__nome').annotate(
            total=Count('id'),
            pendentes=Count('id', filter=Q(estado_atual__nome__in=['Recebido', 'Encaminhado', 'Em Tratamento'])),
            concluidos=Count('id', filter=Q(estado_atual__nome='Concluído')),
            arquivados=Count('id', filter=Q(estado_atual__nome='Arquivado'))
        ).order_by('-total')
        
        return {
            'titulo': 'Documentos por Sector',
            'dados': list(dados),
            'total_geral': queryset.count(),
            'periodo': self._obter_periodo()
        }
    
    def _dados_tempo_resposta(self):
        """
        Dados para relatório de tempo de resposta.
        """
        queryset = Expediente.objects.filter(
            ativo=True,
            data_submissao__isnull=False,
            data_aprovacao__isnull=False
        )
        
        # Aplicar filtros
        if self.filtros.get('data_inicio'):
            queryset = queryset.filter(data_criacao__date__gte=self.filtros['data_inicio'])
        if self.filtros.get('data_fim'):
            queryset = queryset.filter(data_criacao__date__lte=self.filtros['data_fim'])
        if self.filtros.get('sector'):
            queryset = queryset.filter(sector_responsavel=self.filtros['sector'])
        
        # Calcular tempo médio por sector
        dados = []
        for sector in Sector.objects.filter(ativo=True):
            sector_docs = queryset.filter(sector_responsavel=sector)
            if sector_docs.exists():
                tempos = []
                for doc in sector_docs:
                    if doc.data_submissao and doc.data_aprovacao:
                        tempo = (doc.data_aprovacao - doc.data_submissao).days
                        tempos.append(tempo)
                
                if tempos:
                    dados.append({
                        'sector': sector.nome,
                        'total_documentos': len(tempos),
                        'tempo_medio': sum(tempos) / len(tempos),
                        'tempo_minimo': min(tempos),
                        'tempo_maximo': max(tempos),
                        'em_atraso': len([t for t in tempos if t > 30])  # Mais de 30 dias
                    })
        
        return {
            'titulo': 'Tempo de Resposta por Sector',
            'dados': dados,
            'periodo': self._obter_periodo()
        }
    
    def _dados_estados_documentos(self):
        """
        Dados para relatório de estados de documentos.
        """
        queryset = Expediente.objects.filter(ativo=True)
        
        # Aplicar filtros
        if self.filtros.get('data_inicio'):
            queryset = queryset.filter(data_criacao__date__gte=self.filtros['data_inicio'])
        if self.filtros.get('data_fim'):
            queryset = queryset.filter(data_criacao__date__lte=self.filtros['data_fim'])
        if self.filtros.get('sector'):
            queryset = queryset.filter(sector_responsavel=self.filtros['sector'])
        
        # Agrupar por estado
        dados = queryset.values('estado_atual__nome').annotate(
            total=Count('id')
        ).order_by('-total')
        
        # Evolução temporal (últimos 12 meses)
        evolucao = queryset.annotate(
            mes=TruncMonth('data_criacao')
        ).values('mes', 'estado_atual__nome').annotate(
            total=Count('id')
        ).order_by('mes')
        
        return {
            'titulo': 'Estados de Documentos',
            'dados': list(dados),
            'evolucao': list(evolucao),
            'total_geral': queryset.count(),
            'periodo': self._obter_periodo()
        }
    
    def _dados_comunicacao_sector(self):
        """
        Dados para relatório de comunicação por sector.
        """
        # Este seria implementado quando houver sistema de mensagens
        return {
            'titulo': 'Comunicação por Sector',
            'dados': [],
            'periodo': self._obter_periodo()
        }
    
    def _dados_atividade_utilizadores(self):
        """
        Dados para relatório de atividade de utilizadores.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        queryset = Expediente.objects.filter(ativo=True)
        
        # Aplicar filtros
        if self.filtros.get('data_inicio'):
            queryset = queryset.filter(data_criacao__date__gte=self.filtros['data_inicio'])
        if self.filtros.get('data_fim'):
            queryset = queryset.filter(data_criacao__date__lte=self.filtros['data_fim'])
        if self.filtros.get('utilizador_criador'):
            queryset = queryset.filter(criado_por=self.filtros['utilizador_criador'])
        
        # Atividade por utilizador
        dados = queryset.values('criado_por__first_name', 'criado_por__last_name').annotate(
            documentos_criados=Count('id'),
            documentos_processados=Count('id', filter=Q(estado_atual__nome='Concluído')),
            documentos_pendentes=Count('id', filter=Q(estado_atual__nome__in=['Recebido', 'Encaminhado', 'Em Tratamento']))
        ).order_by('-documentos_criados')
        
        return {
            'titulo': 'Atividade de Utilizadores',
            'dados': list(dados),
            'periodo': self._obter_periodo()
        }
    
    def _dados_eficiencia_sector(self):
        """
        Dados para relatório de eficiência por sector.
        """
        dados = []
        
        for sector in Sector.objects.filter(ativo=True):
            sector_docs = Expediente.objects.filter(
                sector_responsavel=sector,
                ativo=True
            )
            
            if self.filtros.get('data_inicio'):
                sector_docs = sector_docs.filter(data_criacao__date__gte=self.filtros['data_inicio'])
            if self.filtros.get('data_fim'):
                sector_docs = sector_docs.filter(data_criacao__date__lte=self.filtros['data_fim'])
            
            total = sector_docs.count()
            concluidos = sector_docs.filter(estado_atual__nome='Concluído').count()
            pendentes = sector_docs.filter(estado_atual__nome__in=['Recebido', 'Encaminhado', 'Em Tratamento']).count()
            
            taxa_conclusao = (concluidos / total * 100) if total > 0 else 0
            
            dados.append({
                'sector': sector.nome,
                'total_documentos': total,
                'concluidos': concluidos,
                'pendentes': pendentes,
                'taxa_conclusao': round(taxa_conclusao, 2),
                'colaboradores': sector.obter_colaboradores().count()
            })
        
        return {
            'titulo': 'Eficiência por Sector',
            'dados': dados,
            'periodo': self._obter_periodo()
        }
    
    def _dados_utilizacao_sistema(self):
        """
        Dados para relatório de utilização do sistema.
        """
        # Este seria implementado com logs de acesso
        return {
            'titulo': 'Utilização do Sistema',
            'dados': [],
            'periodo': self._obter_periodo()
        }
    
    def _dados_documentos_periodo(self):
        """
        Dados para relatório de documentos por período.
        """
        queryset = Expediente.objects.filter(ativo=True)
        
        # Aplicar filtros
        if self.filtros.get('data_inicio'):
            queryset = queryset.filter(data_criacao__date__gte=self.filtros['data_inicio'])
        if self.filtros.get('data_fim'):
            queryset = queryset.filter(data_criacao__date__lte=self.filtros['data_fim'])
        if self.filtros.get('sector'):
            queryset = queryset.filter(sector_responsavel=self.filtros['sector'])
        
        # Agrupar por dia
        dados = queryset.annotate(
            dia=TruncDay('data_criacao')
        ).values('dia').annotate(
            total=Count('id')
        ).order_by('dia')
        
        return {
            'titulo': 'Documentos por Período',
            'dados': list(dados),
            'total_geral': queryset.count(),
            'periodo': self._obter_periodo()
        }
    
    def _dados_performance_geral(self):
        """
        Dados para relatório de performance geral.
        """
        queryset = Expediente.objects.filter(ativo=True)
        
        # Aplicar filtros
        if self.filtros.get('data_inicio'):
            queryset = queryset.filter(data_criacao__date__gte=self.filtros['data_inicio'])
        if self.filtros.get('data_fim'):
            queryset = queryset.filter(data_criacao__date__lte=self.filtros['data_fim'])
        
        # Estatísticas gerais
        total_documentos = queryset.count()
        documentos_concluidos = queryset.filter(estado_atual__nome='Concluído').count()
        documentos_pendentes = queryset.filter(estado_atual__nome__in=['Recebido', 'Encaminhado', 'Em Tratamento']).count()
        documentos_arquivados = queryset.filter(estado_atual__nome='Arquivado').count()
        
        taxa_conclusao = (documentos_concluidos / total_documentos * 100) if total_documentos > 0 else 0
        
        # Por sector
        por_sector = queryset.values('sector_responsavel__nome').annotate(
            total=Count('id'),
            concluidos=Count('id', filter=Q(estado_atual__nome='Concluído'))
        ).order_by('-total')
        
        # Por tipo de documento
        por_tipo = queryset.values('tipo__nome').annotate(
            total=Count('id')
        ).order_by('-total')
        
        return {
            'titulo': 'Performance Geral do Sistema',
            'estatisticas_gerais': {
                'total_documentos': total_documentos,
                'documentos_concluidos': documentos_concluidos,
                'documentos_pendentes': documentos_pendentes,
                'documentos_arquivados': documentos_arquivados,
                'taxa_conclusao': round(taxa_conclusao, 2)
            },
            'por_sector': list(por_sector),
            'por_tipo': list(por_tipo),
            'periodo': self._obter_periodo()
        }
    
    def _obter_periodo(self):
        """
        Retorna o período do relatório formatado.
        """
        inicio = self.filtros.get('data_inicio', 'N/A')
        fim = self.filtros.get('data_fim', 'N/A')
        
        if inicio != 'N/A' and fim != 'N/A':
            return f"{inicio} a {fim}"
        elif inicio != 'N/A':
            return f"A partir de {inicio}"
        elif fim != 'N/A':
            return f"Até {fim}"
        else:
            return "Todos os períodos"
    
    def _gerar_pdf(self, dados):
        """
        Gera relatório em formato PDF.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Estilo personalizado para título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Centralizado
        )
        
        # Conteúdo do documento
        story = []
        
        # Título
        story.append(Paragraph(dados['titulo'], title_style))
        story.append(Spacer(1, 12))
        
        # Período
        story.append(Paragraph(f"Período: {dados['periodo']}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Dados em tabela
        if 'dados' in dados and dados['dados']:
            # Cabeçalho da tabela
            headers = list(dados['dados'][0].keys())
            table_data = [headers]
            
            # Dados da tabela
            for item in dados['dados']:
                row = [str(item.get(key, '')) for key in headers]
                table_data.append(row)
            
            # Criar tabela
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        
        return ContentFile(buffer.getvalue())
    
    def _gerar_excel(self, dados):
        """
        Gera relatório em formato Excel.
        """
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = dados['titulo'][:31]  # Limite de caracteres do Excel
        
        # Estilos
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        
        # Título
        worksheet['A1'] = dados['titulo']
        worksheet['A1'].font = Font(size=16, bold=True)
        worksheet.merge_cells('A1:D1')
        
        # Período
        worksheet['A2'] = f"Período: {dados['periodo']}"
        worksheet['A2'].font = Font(size=12)
        
        # Dados em tabela
        if 'dados' in dados and dados['dados']:
            # Cabeçalho
            headers = list(dados['dados'][0].keys())
            for col, header in enumerate(headers, 1):
                cell = worksheet.cell(row=4, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal='center')
            
            # Dados
            for row, item in enumerate(dados['dados'], 5):
                for col, key in enumerate(headers, 1):
                    worksheet.cell(row=row, column=col, value=item.get(key, ''))
            
            # Ajustar largura das colunas
            for col in range(1, len(headers) + 1):
                column_letter = get_column_letter(col)
                worksheet.column_dimensions[column_letter].width = 20
        
        # Salvar em buffer
        buffer = io.BytesIO()
        workbook.save(buffer)
        buffer.seek(0)
        
        return ContentFile(buffer.getvalue())
    
    def _gerar_csv(self, dados):
        """
        Gera relatório em formato CSV.
        """
        buffer = io.StringIO()
        
        # Dados em CSV
        if 'dados' in dados and dados['dados']:
            headers = list(dados['dados'][0].keys())
            writer = csv.DictWriter(buffer, fieldnames=headers)
            writer.writeheader()
            
            for item in dados['dados']:
                writer.writerow(item)
        
        buffer.seek(0)
        return ContentFile(buffer.getvalue().encode('utf-8'))
    
    def _gerar_html(self, dados):
        """
        Gera relatório em formato HTML.
        """
        context = {
            'dados': dados,
            'relatorio': self.relatorio,
            'execucao': self.execucao
        }
        
        html_content = render_to_string('relatorios/templates/relatorio_html.html', context)
        return ContentFile(html_content.encode('utf-8'))


class ChartGenerator:
    """
    Classe para geração de gráficos usando Chart.js.
    """
    
    @staticmethod
    def gerar_grafico_barras(dados, titulo, labels_key='nome', values_key='total'):
        """
        Gera código JavaScript para gráfico de barras.
        """
        labels = [str(item[labels_key]) for item in dados]
        values = [item[values_key] for item in dados]
        
        chart_config = {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': titulo,
                    'data': values,
                    'backgroundColor': 'rgba(31, 41, 55, 0.8)',
                    'borderColor': 'rgba(31, 41, 55, 1)',
                    'borderWidth': 1
                }]
            },
            'options': {
                'responsive': True,
                'scales': {
                    'y': {
                        'beginAtZero': True
                    }
                },
                'plugins': {
                    'title': {
                        'display': True,
                        'text': titulo
                    }
                }
            }
        }
        
        return chart_config
    
    @staticmethod
    def gerar_grafico_pizza(dados, titulo, labels_key='nome', values_key='total'):
        """
        Gera código JavaScript para gráfico de pizza.
        """
        labels = [str(item[labels_key]) for item in dados]
        values = [item[values_key] for item in dados]
        
        # Cores para o gráfico
        colors = [
            'rgba(31, 41, 55, 0.8)',   # Cinza escuro
            'rgba(59, 130, 246, 0.8)',  # Azul
            'rgba(16, 185, 129, 0.8)',  # Verde
            'rgba(245, 158, 11, 0.8)',  # Amarelo
            'rgba(239, 68, 68, 0.8)',   # Vermelho
            'rgba(139, 92, 246, 0.8)',   # Roxo
            'rgba(236, 72, 153, 0.8)',   # Rosa
            'rgba(6, 182, 212, 0.8)'    # Ciano
        ]
        
        chart_config = {
            'type': 'pie',
            'data': {
                'labels': labels,
                'datasets': [{
                    'data': values,
                    'backgroundColor': colors[:len(values)],
                    'borderWidth': 1
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': titulo
                    },
                    'legend': {
                        'position': 'bottom'
                    }
                }
            }
        }
        
        return chart_config
    
    @staticmethod
    def gerar_grafico_linha(dados, titulo, labels_key='dia', values_key='total'):
        """
        Gera código JavaScript para gráfico de linha.
        """
        labels = [str(item[labels_key]) for item in dados]
        values = [item[values_key] for item in dados]
        
        chart_config = {
            'type': 'line',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': titulo,
                    'data': values,
                    'borderColor': 'rgba(31, 41, 55, 1)',
                    'backgroundColor': 'rgba(31, 41, 55, 0.1)',
                    'borderWidth': 2,
                    'fill': True,
                    'tension': 0.4
                }]
            },
            'options': {
                'responsive': True,
                'scales': {
                    'y': {
                        'beginAtZero': True
                    }
                },
                'plugins': {
                    'title': {
                        'display': True,
                        'text': titulo
                    }
                }
            }
        }
        
        return chart_config
    
    @staticmethod
    def gerar_grafico_area(dados, titulo, labels_key='mes', values_key='total'):
        """
        Gera código JavaScript para gráfico de área.
        """
        labels = [str(item[labels_key]) for item in dados]
        values = [item[values_key] for item in dados]
        
        chart_config = {
            'type': 'line',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': titulo,
                    'data': values,
                    'borderColor': 'rgba(31, 41, 55, 1)',
                    'backgroundColor': 'rgba(31, 41, 55, 0.3)',
                    'borderWidth': 2,
                    'fill': True,
                    'tension': 0.4
                }]
            },
            'options': {
                'responsive': True,
                'scales': {
                    'y': {
                        'beginAtZero': True
                    }
                },
                'plugins': {
                    'title': {
                        'display': True,
                        'text': titulo
                    }
                }
            }
        }
        
        return chart_config
