from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import EstadoDocumento, Notificacao, Sector, ConfiguracaoSistema, DespachoDocumento, AnexoDespacho
from .utils import enviar_notificacao, notificar_pca, notificar_chefe_sector

User = get_user_model()


class EstadoDocumentoModelTest(TestCase):
    """
    Testes para o modelo EstadoDocumento.
    """
    
    def setUp(self):
        self.estado = EstadoDocumento.objects.create(
            nome="Recebido",
            descricao="Documento recebido no sistema",
            cor="#007bff",
            ordem=1,
            ativo=True,
            requer_acao=False
        )
    
    def test_estado_creation(self):
        """Testa criação de estado de documento."""
        self.assertEqual(self.estado.nome, "Recebido")
        self.assertTrue(self.estado.ativo)
        self.assertFalse(self.estado.requer_acao)
    
    def test_estado_str(self):
        """Testa método __str__."""
        self.assertEqual(str(self.estado), "Recebido")
    
    def test_estado_ordering(self):
        """Testa ordenação por campo ordem."""
        estado2 = EstadoDocumento.objects.create(
            nome="Processado",
            descricao="Documento processado",
            cor="#28a745",
            ordem=2
        )
        
        estados = EstadoDocumento.objects.all()
        self.assertEqual(estados[0], self.estado)
        self.assertEqual(estados[1], estado2)


class NotificacaoModelTest(TestCase):
    """
    Testes para o modelo Notificacao.
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.remetente = User.objects.create_user(
            username='remetente',
            email='remetente@example.com',
            password='testpass123'
        )
        
        self.notificacao = Notificacao.objects.create(
            destinatario=self.user,
            remetente=self.remetente,
            titulo="Teste",
            mensagem="Mensagem de teste",
            tipo="documento_novo",
            prioridade="normal"
        )
    
    def test_notificacao_creation(self):
        """Testa criação de notificação."""
        self.assertEqual(self.notificacao.destinatario, self.user)
        self.assertEqual(self.notificacao.titulo, "Teste")
        self.assertFalse(self.notificacao.lida)
    
    def test_marcar_como_lida(self):
        """Testa marcar notificação como lida."""
        self.assertFalse(self.notificacao.lida)
        self.assertIsNone(self.notificacao.data_lida)
        
        self.notificacao.marcar_como_lida()
        
        self.assertTrue(self.notificacao.lida)
        self.assertIsNotNone(self.notificacao.data_lida)
    
    def test_obter_icone(self):
        """Testa obter ícone da notificação."""
        icone = self.notificacao.obter_icone()
        self.assertIn("bi-", icone)
    
    def test_eh_urgente(self):
        """Testa verificação de urgência."""
        self.assertFalse(self.notificacao.eh_urgente())
        
        self.notificacao.prioridade = "urgente"
        self.notificacao.save()
        
        self.assertTrue(self.notificacao.eh_urgente())


class SectorModelTest(TestCase):
    """
    Testes para o modelo Sector.
    """
    
    def setUp(self):
        self.chefe = User.objects.create_user(
            username='chefe',
            email='chefe@example.com',
            password='testpass123'
        )
        self.substituto = User.objects.create_user(
            username='substituto',
            email='substituto@example.com',
            password='testpass123'
        )
        
        self.sector = Sector.objects.create(
            nome="Teste Sector",
            descricao="Sector de teste",
            chefe=self.chefe,
            chefe_substituto=self.substituto,
            ativo=True
        )
    
    def test_sector_creation(self):
        """Testa criação de sector."""
        self.assertEqual(self.sector.nome, "Teste Sector")
        self.assertEqual(self.sector.chefe, self.chefe)
        self.assertTrue(self.sector.ativo)
    
    def test_sector_str(self):
        """Testa método __str__."""
        self.assertEqual(str(self.sector), "Teste Sector")
    
    def test_obter_chefe(self):
        """Testa obter chefe atual."""
        chefe_atual = self.sector.obter_chefe()
        self.assertEqual(chefe_atual, self.chefe)
    
    def test_eh_chefe(self):
        """Testa verificação se utilizador é chefe."""
        self.assertTrue(self.sector.eh_chefe(self.chefe))
        self.assertTrue(self.sector.eh_chefe(self.substituto))
        
        outro_user = User.objects.create_user(
            username='outro',
            email='outro@example.com',
            password='testpass123'
        )
        self.assertFalse(self.sector.eh_chefe(outro_user))


class ConfiguracaoSistemaModelTest(TestCase):
    """
    Testes para o modelo ConfiguracaoSistema.
    """
    
    def setUp(self):
        self.config = ConfiguracaoSistema.objects.create(
            chave="test_key",
            valor="test_value",
            descricao="Configuração de teste",
            tipo="string"
        )
    
    def test_config_creation(self):
        """Testa criação de configuração."""
        self.assertEqual(self.config.chave, "test_key")
        self.assertEqual(self.config.valor, "test_value")
        self.assertEqual(self.config.tipo, "string")
    
    def test_config_str(self):
        """Testa método __str__."""
        self.assertEqual(str(self.config), "test_key")


class NotificacaoUtilsTest(TestCase):
    """
    Testes para utilitários de notificação.
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.remetente = User.objects.create_user(
            username='remetente',
            email='remetente@example.com',
            password='testpass123'
        )
    
    def test_enviar_notificacao(self):
        """Testa envio de notificação."""
        notificacao = enviar_notificacao(
            destinatario=self.user,
            titulo="Teste",
            mensagem="Mensagem de teste",
            tipo="documento_novo",
            remetente=self.remetente
        )
        
        self.assertIsNotNone(notificacao)
        self.assertEqual(notificacao.destinatario, self.user)
        self.assertEqual(notificacao.titulo, "Teste")
        self.assertEqual(notificacao.tipo, "documento_novo")
    
    def test_enviar_notificacao_sem_remetente(self):
        """Testa envio de notificação sem remetente."""
        notificacao = enviar_notificacao(
            destinatario=self.user,
            titulo="Teste",
            mensagem="Mensagem de teste",
            tipo="documento_novo"
        )
        
        self.assertIsNotNone(notificacao)
        self.assertIsNone(notificacao.remetente)


class NotificacaoViewsTest(TestCase):
    """
    Testes para views de notificação.
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.force_login(self.user)
        
        self.notificacao = Notificacao.objects.create(
            destinatario=self.user,
            titulo="Teste",
            mensagem="Mensagem de teste",
            tipo="documento_novo"
        )
    
    def test_lista_notificacoes_view(self):
        """Testa view de lista de notificações."""
        response = self.client.get(reverse('core:lista_notificacoes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Teste")
    
    def test_marcar_notificacao_lida(self):
        """Testa marcar notificação como lida via AJAX."""
        response = self.client.post(
            reverse('core:marcar_notificacao_lida', args=[self.notificacao.pk]),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.notificacao.refresh_from_db()
        self.assertTrue(self.notificacao.lida)
    
    def test_marcar_todas_lidas(self):
        """Testa marcar todas as notificações como lidas."""
        # Criar mais uma notificação
        Notificacao.objects.create(
            destinatario=self.user,
            titulo="Teste 2",
            mensagem="Mensagem de teste 2",
            tipo="documento_novo"
        )
        
        response = self.client.post(
            reverse('core:marcar_todas_lidas'),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        nao_lidas = Notificacao.objects.filter(destinatario=self.user, lida=False).count()
        self.assertEqual(nao_lidas, 0)


class SectorViewsTest(TestCase):
    """
    Testes para views de sector.
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.force_login(self.user)
        
        self.chefe = User.objects.create_user(
            username='chefe',
            email='chefe@example.com',
            password='testpass123'
        )
        
        self.sector = Sector.objects.create(
            nome="Teste Sector",
            descricao="Sector de teste",
            chefe=self.chefe,
            ativo=True
        )
    
    def test_lista_sectores_view(self):
        """Testa view de lista de sectores."""
        response = self.client.get(reverse('core:lista_sectores'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Teste Sector")
    
    def test_criar_sector_view(self):
        """Testa view de criação de sector."""
        response = self.client.get(reverse('core:criar_sector'))
        self.assertEqual(response.status_code, 200)
    
    def test_detalhes_sector_view(self):
        """Testa view de detalhes de sector."""
        response = self.client.get(reverse('core:detalhes_sector', args=[self.sector.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Teste Sector")


class DashboardViewTest(TestCase):
    """
    Testes para view do dashboard.
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.force_login(self.user)
    
    def test_dashboard_view(self):
        """Testa view do dashboard."""
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Visão Geral do Sistema")


class TemplateTagsTest(TestCase):
    """
    Testes para template tags customizadas.
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_notificacao_icone(self):
        """Testa template tag para ícone de notificação."""
        notificacao = Notificacao.objects.create(
            destinatario=self.user,
            titulo="Teste",
            mensagem="Mensagem de teste",
            tipo="documento_novo"
        )
        
        icone = notificacao.obter_icone()
        self.assertIn("bi-", icone)


class AdminTest(TestCase):
    """
    Testes para configuração do admin.
    """
    
    def setUp(self):
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client = Client()
        self.client.force_login(self.user)
    
    def test_admin_estado_documento(self):
        """Testa admin de EstadoDocumento."""
        response = self.client.get('/admin/core/estadodocumento/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_notificacao(self):
        """Testa admin de Notificacao."""
        response = self.client.get('/admin/core/notificacao/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_sector(self):
        """Testa admin de Sector."""
        response = self.client.get('/admin/core/sector/')
        self.assertEqual(response.status_code, 200)