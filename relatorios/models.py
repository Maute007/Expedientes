from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from core.models import Sector, EstadoDocumento
from entrada.models import Expediente, TipoDocumento
import json

User = get_user_model()


class TipoRelatorio(models.Model):
    """
    Modelo para definir tipos de relatórios disponíveis no sistema.
    """
    TIPOS_RELATORIO = [
        ('documentos_sector', 'Documentos por Sector'),
        ('tempo_resposta', 'Tempo de Resposta'),
        ('estados_documentos', 'Estados de Documentos'),
        ('comunicacao_sector', 'Comunicação por Sector'),
        ('atividade_utilizadores', 'Atividade de Utilizadores'),
        ('eficiencia_sector', 'Eficiência por Sector'),
        ('utilizacao_sistema', 'Utilização do Sistema'),
        ('documentos_periodo', 'Documentos por Período'),
        ('performance_geral', 'Performance Geral'),
        ('customizado', 'Relatório Customizado')
    ]
    
    FORMATOS_SAIDA = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('html', 'HTML'),
        ('json', 'JSON')
    ]
    
    nome = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome do Tipo"
    )
    descricao = models.TextField(
        verbose_name="Descrição"
    )
    tipo_relatorio = models.CharField(
        max_length=30,
        choices=TIPOS_RELATORIO,
        verbose_name="Tipo de Relatório"
    )
    template = models.CharField(
        max_length=200,
        verbose_name="Template",
        help_text="Caminho para o template do relatório"
    )
    parametros_obrigatorios = models.JSONField(
        default=list,
        verbose_name="Parâmetros Obrigatórios",
        help_text="Lista de parâmetros obrigatórios para este tipo de relatório"
    )
    parametros_opcionais = models.JSONField(
        default=list,
        verbose_name="Parâmetros Opcionais",
        help_text="Lista de parâmetros opcionais para este tipo de relatório"
    )
    formato_saida = models.CharField(
        max_length=10,
        choices=FORMATOS_SAIDA,
        default='pdf',
        verbose_name="Formato de Saída"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem"
    )
    
    class Meta:
        ordering = ['ordem', 'nome']
        verbose_name = "Tipo de Relatório"
        verbose_name_plural = "Tipos de Relatórios"
    
    def __str__(self):
        return self.nome
    
    def get_template_path(self):
        """Retorna o caminho completo do template."""
        return f"relatorios/templates/{self.template}"
    
    def get_parametros_display(self):
        """Retorna os parâmetros em formato legível."""
        obrigatorios = ", ".join(self.parametros_obrigatorios) if self.parametros_obrigatorios else "Nenhum"
        opcionais = ", ".join(self.parametros_opcionais) if self.parametros_opcionais else "Nenhum"
        return f"Obrigatórios: {obrigatorios} | Opcionais: {opcionais}"


class ConfiguracaoRelatorio(models.Model):
    """
    Modelo para configurações de relatórios personalizados.
    """
    nome = models.CharField(
        max_length=200,
        verbose_name="Nome do Relatório"
    )
    descricao = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )
    tipo_relatorio = models.ForeignKey(
        TipoRelatorio,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Relatório"
    )
    parametros = models.JSONField(
        default=dict,
        verbose_name="Parâmetros",
        help_text="Parâmetros configurados para este relatório"
    )
    filtros = models.JSONField(
        default=dict,
        verbose_name="Filtros",
        help_text="Filtros aplicados aos dados"
    )
    sector = models.ForeignKey(
        Sector,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Sector",
        help_text="Sector específico (deixe vazio para todos)"
    )
    utilizador_criador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='relatorios_criados',
        verbose_name="Criado por"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    publico = models.BooleanField(
        default=False,
        verbose_name="Público",
        help_text="Se outros utilizadores podem usar este relatório"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    data_ultima_execucao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data da Última Execução"
    )
    execucoes_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Número de Execuções"
    )
    
    class Meta:
        ordering = ['-data_criacao']
        verbose_name = "Configuração de Relatório"
        verbose_name_plural = "Configurações de Relatórios"
    
    def __str__(self):
        return self.nome
    
    def get_tipo_display(self):
        """Retorna o nome do tipo de relatório."""
        return self.tipo_relatorio.nome
    
    def execute(self, utilizador=None):
        """Executa o relatório e retorna uma ExecucaoRelatorio."""
        if not utilizador:
            utilizador = self.utilizador_criador
        
        execucao = ExecucaoRelatorio.objects.create(
            relatorio=self,
            utilizador=utilizador,
            parametros_utilizados=self.parametros,
            filtros_utilizados=self.filtros
        )
        
        # Atualizar estatísticas
        self.data_ultima_execucao = timezone.now()
        self.execucoes_count += 1
        self.save(update_fields=['data_ultima_execucao', 'execucoes_count'])
        
        return execucao
    
    def clean(self):
        """Valida os parâmetros obrigatórios."""
        super().clean()
        
        # Verificar parâmetros obrigatórios
        parametros_obrigatorios = self.tipo_relatorio.parametros_obrigatorios
        for param in parametros_obrigatorios:
            if param not in self.parametros:
                raise ValidationError(f"Parâmetro obrigatório '{param}' não fornecido.")


class ExecucaoRelatorio(models.Model):
    """
    Modelo para registrar execuções de relatórios.
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('processando', 'Processando'),
        ('concluido', 'Concluído'),
        ('erro', 'Erro'),
        ('cancelado', 'Cancelado')
    ]
    
    relatorio = models.ForeignKey(
        ConfiguracaoRelatorio,
        on_delete=models.CASCADE,
        related_name='execucoes',
        verbose_name="Relatório"
    )
    utilizador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='execucoes_relatorios',
        verbose_name="Utilizador"
    )
    data_execucao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Execução"
    )
    data_conclusao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Conclusão"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name="Status"
    )
    ficheiro_gerado = models.FileField(
        upload_to='relatorios/',
        null=True,
        blank=True,
        verbose_name="Ficheiro Gerado"
    )
    parametros_utilizados = models.JSONField(
        default=dict,
        verbose_name="Parâmetros Utilizados"
    )
    filtros_utilizados = models.JSONField(
        default=dict,
        verbose_name="Filtros Utilizados"
    )
    erro = models.TextField(
        blank=True,
        verbose_name="Erro",
        help_text="Descrição do erro, se houver"
    )
    tamanho_ficheiro = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Tamanho do Ficheiro (bytes)"
    )
    registros_processados = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Registros Processados"
    )
    
    class Meta:
        ordering = ['-data_execucao']
        verbose_name = "Execução de Relatório"
        verbose_name_plural = "Execuções de Relatórios"
    
    def __str__(self):
        return f"{self.relatorio.nome} - {self.data_execucao.strftime('%d/%m/%Y %H:%M')}"
    
    def get_status_display(self):
        """Retorna o status com cor."""
        status_colors = {
            'pendente': 'warning',
            'processando': 'info',
            'concluido': 'success',
            'erro': 'danger',
            'cancelado': 'secondary'
        }
        return status_colors.get(self.status, 'secondary')
    
    def get_ficheiro_url(self):
        """Retorna a URL do ficheiro gerado."""
        if self.ficheiro_gerado:
            return self.ficheiro_gerado.url
        return None
    
    def get_tamanho_display(self):
        """Retorna o tamanho do ficheiro formatado."""
        if not self.tamanho_ficheiro:
            return "N/A"
        
        size = self.tamanho_ficheiro
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class Dashboard(models.Model):
    """
    Modelo para dashboards personalizados.
    """
    nome = models.CharField(
        max_length=200,
        verbose_name="Nome do Dashboard"
    )
    descricao = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )
    sector = models.ForeignKey(
        Sector,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Sector",
        help_text="Sector específico (deixe vazio para todos)"
    )
    utilizador_criador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='dashboards_criados',
        verbose_name="Criado por"
    )
    widgets = models.JSONField(
        default=list,
        verbose_name="Widgets",
        help_text="Lista de widgets configurados"
    )
    layout = models.JSONField(
        default=dict,
        verbose_name="Layout",
        help_text="Configuração do layout do dashboard"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    publico = models.BooleanField(
        default=False,
        verbose_name="Público",
        help_text="Se outros utilizadores podem ver este dashboard"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de Atualização"
    )
    
    class Meta:
        ordering = ['-data_criacao']
        verbose_name = "Dashboard"
        verbose_name_plural = "Dashboards"
    
    def __str__(self):
        return self.nome
    
    def get_widgets_count(self):
        """Retorna o número de widgets configurados."""
        return len(self.widgets) if self.widgets else 0
    
    def add_widget(self, widget_config):
        """Adiciona um widget ao dashboard."""
        if not self.widgets:
            self.widgets = []
        
        self.widgets.append(widget_config)
        self.save(update_fields=['widgets', 'data_atualizacao'])
    
    def remove_widget(self, widget_id):
        """Remove um widget do dashboard."""
        if self.widgets:
            self.widgets = [w for w in self.widgets if w.get('id') != widget_id]
            self.save(update_fields=['widgets', 'data_atualizacao'])


class WidgetDashboard(models.Model):
    """
    Modelo para widgets de dashboard.
    """
    TIPOS_WIDGET = [
        ('contador', 'Contador'),
        ('grafico_barras', 'Gráfico de Barras'),
        ('grafico_pizza', 'Gráfico de Pizza'),
        ('grafico_linha', 'Gráfico de Linha'),
        ('grafico_area', 'Gráfico de Área'),
        ('tabela', 'Tabela'),
        ('lista', 'Lista'),
        ('metricas', 'Métricas'),
        ('calendario', 'Calendário'),
        ('atividade', 'Atividade Recente')
    ]
    
    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name='widgets_dashboard',
        verbose_name="Dashboard"
    )
    tipo_widget = models.CharField(
        max_length=20,
        choices=TIPOS_WIDGET,
        verbose_name="Tipo de Widget"
    )
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título"
    )
    posicao = models.JSONField(
        default=dict,
        verbose_name="Posição",
        help_text="Posição do widget no grid (x, y, width, height)"
    )
    parametros = models.JSONField(
        default=dict,
        verbose_name="Parâmetros",
        help_text="Parâmetros específicos do widget"
    )
    tamanho = models.JSONField(
        default=dict,
        verbose_name="Tamanho",
        help_text="Tamanho do widget (width, height)"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem"
    )
    
    class Meta:
        ordering = ['dashboard', 'ordem']
        verbose_name = "Widget de Dashboard"
        verbose_name_plural = "Widgets de Dashboard"
    
    def __str__(self):
        return f"{self.dashboard.nome} - {self.titulo}"
    
    def get_tipo_display(self):
        """Retorna o nome do tipo de widget."""
        return dict(self.TIPOS_WIDGET)[self.tipo_widget]
    
    def render(self):
        """Renderiza o widget e retorna os dados."""
        # Esta função será implementada nas views
        return {
            'tipo': self.tipo_widget,
            'titulo': self.titulo,
            'dados': {},
            'parametros': self.parametros
        }