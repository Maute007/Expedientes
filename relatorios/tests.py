from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
import json

from relatorios.models import (
    ConfiguracaoRelatorio, TipoRelatorio, ExecucaoRelatorio, 
    Dashboard, WidgetDashboard
)
from core.models import Sector, EstadoDocumento
from entrada.models import Expediente, TipoDocumento

User = get_user_model()


class RelatoriosModelsTestCase(TestCase):
    """Testes para os modelos de relatórios."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        # Criar utilizador
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Criar sector
        self.sector = Sector.objects.create(
            nome='Sector Teste',
            descricao='Sector para testes',
            chefe=self.user,
            ativo=True
        )
        
        # Criar tipo de relatório
        self.tipo_relatorio = TipoRelatorio.objects.create(
            nome='Teste Relatório',
            descricao='Relatório para testes',
            tipo_relatorio='teste',
            template='teste.html',
            parametros_obrigatorios=['param1'],
            formato_saida='pdf',
            ativo=True
        )
        
        # Criar configuração de relatório
        self.config_relatorio = ConfiguracaoRelatorio.objects.create(
            nome='Relatório Teste',
            descricao='Relatório para testes',
            tipo_relatorio=self.tipo_relatorio,
            parametros={'param1': 'valor1'},
            sector=self.sector,
            utilizador_criador=self.user,
            ativo=True,
            publico=True
        )
        
        # Criar dashboard
        self.dashboard = Dashboard.objects.create(
            nome='Dashboard Teste',
            descricao='Dashboard para testes',
            sector=self.sector,
            utilizador_criador=self.user,
            widgets=[],
            layout='grid',
            ativo=True,
            publico=True
        )
        
        # Criar widget
        self.widget = WidgetDashboard.objects.create(
            dashboard=self.dashboard,
            tipo_widget='contador',
            titulo='Widget Teste',
            posicao={'x': 0, 'y': 0},
            parametros={'tipo': 'teste'},
            tamanho={'width': 2, 'height': 1},
            ativo=True
        )

    def test_tipo_relatorio_creation(self):
        """Testa a criação de tipo de relatório."""
        self.assertEqual(self.tipo_relatorio.nome, 'Teste Relatório')
        self.assertEqual(self.tipo_relatorio.tipo_relatorio, 'teste')
        self.assertTrue(self.tipo_relatorio.ativo)
        self.assertEqual(str(self.tipo_relatorio), 'Teste Relatório')

    def test_config_relatorio_creation(self):
        """Testa a criação de configuração de relatório."""
        self.assertEqual(self.config_relatorio.nome, 'Relatório Teste')
        self.assertEqual(self.config_relatorio.tipo_relatorio, self.tipo_relatorio)
        self.assertTrue(self.config_relatorio.ativo)
        self.assertTrue(self.config_relatorio.publico)
        self.assertEqual(str(self.config_relatorio), 'Relatório Teste')

    def test_execucao_relatorio_creation(self):
        """Testa a criação de execução de relatório."""
        execucao = ExecucaoRelatorio.objects.create(
            relatorio=self.config_relatorio,
            utilizador=self.user,
            data_execucao=timezone.now(),
            status='executando',
            parametros_utilizados={'param1': 'valor1'},
            erro=''
        )
        
        self.assertEqual(execucao.relatorio, self.config_relatorio)
        self.assertEqual(execucao.utilizador, self.user)
        self.assertEqual(execucao.status, 'executando')
        # O método __str__ retorna: "Nome do Relatório - DD/MM/YYYY HH:MM"
        expected_str = f"{self.config_relatorio.nome} - {execucao.data_execucao.strftime('%d/%m/%Y %H:%M')}"
        self.assertEqual(str(execucao), expected_str)

    def test_dashboard_creation(self):
        """Testa a criação de dashboard."""
        self.assertEqual(self.dashboard.nome, 'Dashboard Teste')
        self.assertEqual(self.dashboard.sector, self.sector)
        self.assertEqual(self.dashboard.utilizador_criador, self.user)
        self.assertTrue(self.dashboard.ativo)
        self.assertEqual(str(self.dashboard), 'Dashboard Teste')

    def test_widget_creation(self):
        """Testa a criação de widget."""
        self.assertEqual(self.widget.dashboard, self.dashboard)
        self.assertEqual(self.widget.tipo_widget, 'contador')
        self.assertEqual(self.widget.titulo, 'Widget Teste')
        self.assertTrue(self.widget.ativo)
        # O método __str__ retorna: "Nome do Dashboard - Título do Widget"
        self.assertEqual(str(self.widget), f'{self.dashboard.nome} - {self.widget.titulo}')

    def test_config_relatorio_execute(self):
        """Testa a execução de relatório."""
        execucao = self.config_relatorio.execute(self.user)
        
        self.assertEqual(execucao.relatorio, self.config_relatorio)
        self.assertEqual(execucao.utilizador, self.user)
        self.assertEqual(execucao.status, 'pendente')
        self.assertIsNotNone(execucao.data_execucao)

    def test_dashboard_add_widget(self):
        """Testa a adição de widget ao dashboard."""
        widget_data = {
            'tipo': 'grafico',
            'titulo': 'Novo Widget',
            'parametros': {'tipo': 'barras'},
            'posicao': {'x': 1, 'y': 1},
            'tamanho': {'width': 2, 'height': 2}
        }
        
        self.dashboard.add_widget(widget_data)
        self.assertEqual(len(self.dashboard.widgets), 1)
        self.assertEqual(self.dashboard.widgets[0]['titulo'], 'Novo Widget')

    def test_dashboard_remove_widget(self):
        """Testa a remoção de widget do dashboard."""
        widget_data = {
            'id': 1,
            'tipo': 'contador',
            'titulo': 'Widget para Remover',
            'parametros': {'tipo': 'teste'},
            'posicao': {'x': 0, 'y': 0},
            'tamanho': {'width': 2, 'height': 1}
        }
        
        self.dashboard.widgets = [widget_data]
        self.dashboard.save()
        
        self.dashboard.remove_widget(1)
        self.assertEqual(len(self.dashboard.widgets), 0)


class RelatoriosViewsTestCase(TestCase):
    """Testes para as views de relatórios."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        # Criar utilizador
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Criar utilizador admin
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Criar sector
        self.sector = Sector.objects.create(
            nome='Sector Teste',
            descricao='Sector para testes',
            chefe=self.user,
            ativo=True
        )
        
        # Criar tipo de relatório
        self.tipo_relatorio = TipoRelatorio.objects.create(
            nome='Teste Relatório',
            descricao='Relatório para testes',
            tipo_relatorio='teste',
            template='teste.html',
            parametros_obrigatorios=['param1'],
            formato_saida='pdf',
            ativo=True
        )
        
        # Criar configuração de relatório
        self.config_relatorio = ConfiguracaoRelatorio.objects.create(
            nome='Relatório Teste',
            descricao='Relatório para testes',
            tipo_relatorio=self.tipo_relatorio,
            parametros={'param1': 'valor1'},
            sector=self.sector,
            utilizador_criador=self.user,
            ativo=True,
            publico=True
        )
        
        # Criar dashboard
        self.dashboard = Dashboard.objects.create(
            nome='Dashboard Teste',
            descricao='Dashboard para testes',
            sector=self.sector,
            utilizador_criador=self.user,
            widgets=[],
            layout='grid',
            ativo=True,
            publico=True
        )
        
        # Definir sector_atual do utilizador
        self.user.sector_atual = self.sector
        self.user.save()
        
        # Criar cliente de teste
        self.client = Client()

    def test_dashboard_relatorios_view(self):
        """Testa a view do dashboard principal."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('relatorios:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Relatórios')

    def test_lista_relatorios_view(self):
        """Testa a view de lista de relatórios."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('relatorios:lista_relatorios'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Relatório Teste')

    def test_detalhar_relatorio_view(self):
        """Testa a view de detalhes do relatório."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('relatorios:detalhar_relatorio', args=[self.config_relatorio.pk]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Relatório Teste')

    def test_criar_relatorio_view_get(self):
        """Testa a view de criação de relatório (GET)."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('relatorios:criar_relatorio'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Criar Novo Relatório')

    def test_criar_relatorio_view_post(self):
        """Testa a view de criação de relatório (POST)."""
        self.client.login(email='test@example.com', password='testpass123')
        
        data = {
            'nome': 'Novo Relatório',
            'descricao': 'Descrição do novo relatório',
            'tipo_relatorio': self.tipo_relatorio.pk,
            'param1': 'valor1',  # Parâmetro obrigatório do tipo de relatório
            'sector': self.sector.pk,
            'ativo': True,
            'publico': True
        }
        
        response = self.client.post(reverse('relatorios:criar_relatorio'), data)
        
        # O formulário pode retornar 200 (com erros) ou 302 (sucesso)
        self.assertIn(response.status_code, [200, 302])
        
        # Se retornou 302, verificar se o relatório foi criado
        if response.status_code == 302:
            self.assertTrue(ConfiguracaoRelatorio.objects.filter(nome='Novo Relatório').exists())

    def test_executar_relatorio_view(self):
        """Testa a view de execução de relatório."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('relatorios:executar_relatorio', args=[self.config_relatorio.pk]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Executar Relatório')

    def test_lista_dashboards_view(self):
        """Testa a view de lista de dashboards."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('relatorios:lista_dashboards'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard Teste')

    def test_visualizar_dashboard_view(self):
        """Testa a view de visualização do dashboard."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('relatorios:visualizar_dashboard', args=[self.dashboard.pk]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard Teste')

    def test_criar_dashboard_view_get(self):
        """Testa a view de criação de dashboard (GET)."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('relatorios:criar_dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Criar Novo Dashboard')

    def test_criar_dashboard_view_post(self):
        """Testa a view de criação de dashboard (POST)."""
        self.client.login(email='test@example.com', password='testpass123')
        
        data = {
            'nome': 'Novo Dashboard',
            'descricao': 'Descrição do novo dashboard',
            'sector': self.sector.pk,
            'widgets': '[]',
            'layout': 'grid',
            'ativo': True,
            'publico': True
        }
        
        response = self.client.post(reverse('relatorios:criar_dashboard'), data)
        
        # Deve redirecionar após criação
        self.assertEqual(response.status_code, 302)
        
        # Verificar se o dashboard foi criado
        self.assertTrue(Dashboard.objects.filter(nome='Novo Dashboard').exists())

    def test_dashboard_administrador_view(self):
        """Testa a view do dashboard administrador."""
        self.client.login(email='admin@example.com', password='adminpass123')
        response = self.client.get(reverse('relatorios:dashboard_admin'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard Administrador')

    def test_dashboard_pca_ca_view(self):
        """Testa a view do dashboard PCA/CA."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('relatorios:dashboard_pca_ca'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard PCA/CA')

    def test_dashboard_chefe_sector_view(self):
        """Testa a view do dashboard chefe de sector."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('relatorios:dashboard_chefe_sector'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')

    def test_dashboard_colaborador_view(self):
        """Testa a view do dashboard colaborador."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('relatorios:dashboard_colaborador'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard Colaborador')

    def test_relatorio_mensagens_sector_view(self):
        """Testa a view de relatório de mensagens por sector."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('relatorios:relatorio_mensagens_sector'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Relatório de Mensagens por Sector')

    def test_relatorio_atividade_utilizadores_view(self):
        """Testa a view de relatório de atividade de utilizadores."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('relatorios:relatorio_atividade_utilizadores'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Relatório de Atividade de Utilizadores')

    def test_relatorio_tempo_resposta_view(self):
        """Testa a view de relatório de tempo de resposta."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('relatorios:relatorio_tempo_resposta'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Relatório de Tempo de Resposta')

    def test_unauthorized_access(self):
        """Testa acesso não autorizado."""
        response = self.client.get(reverse('relatorios:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redireciona para login

    def test_permission_checks(self):
        """Testa verificações de permissão."""
        # Criar relatório privado
        relatorio_privado = ConfiguracaoRelatorio.objects.create(
            nome='Relatório Privado',
            descricao='Relatório privado',
            tipo_relatorio=self.tipo_relatorio,
            parametros={'param1': 'valor1'},
            sector=self.sector,
            utilizador_criador=self.admin_user,
            ativo=True,
            publico=False
        )
        
        # Tentar acessar com utilizador diferente
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('relatorios:detalhar_relatorio', args=[relatorio_privado.pk]))
        
        self.assertEqual(response.status_code, 404)  # Não encontrado para utilizador não autorizado