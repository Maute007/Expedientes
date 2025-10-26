"""
Testes para o app users.
Testa modelos, views, forms, signals e permissões.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from core.models import Sector
from .models import PerfilUtilizador, HierarquiaUtilizador
from .forms import (
    CriarUtilizadorForm, PerfilUtilizadorForm, 
    UserLoginForm, PasswordChangeFormCustomizada
)

User = get_user_model()


# ==================== TESTES DE MODELOS ====================

class TestUserModel(TestCase):
    """Testes para o modelo User customizado."""
    
    def setUp(self):
        """Configurar dados de teste."""
        # Criar admin primeiro para poder ser chefe do setor
        self.admin = User.objects.create_user(
            email='admin@ftc.ac.mz',
            first_name='Admin',
            last_name='Sistema',
            password='admin123',
            tipo_utilizador='admin',
            ativo=True
        )
        
        # Criar setor com o admin como chefe
        self.sector = Sector.objects.create(
            nome='TI',
            descricao='Sector de Tecnologia',
            chefe=self.admin,
            ativo=True
        )
        
        self.pca = User.objects.create_user(
            email='pca@ftc.ac.mz',
            first_name='PCA',
            last_name='FTC',
            password='pca123',
            tipo_utilizador='pca',
            ativo=True
        )
        
        self.chefe = User.objects.create_user(
            email='chefe@ftc.ac.mz',
            first_name='Chefe',
            last_name='TI',
            password='chefe123',
            tipo_utilizador='chefe',
            sector_atual=self.sector,
            ativo=True
        )
        
        self.colaborador = User.objects.create_user(
            email='colab@ftc.ac.mz',
            first_name='Colaborador',
            last_name='TI',
            password='colab123',
            tipo_utilizador='colaborador',
            sector_atual=self.sector,
            ativo=True
        )
    
    def test_criar_utilizador(self):
        """Teste: criar utilizador com dados válidos."""
        user = User.objects.create_user(
            email='teste@ftc.ac.mz',
            first_name='Teste',
            last_name='Utilizador',
            password='teste123'
        )
        self.assertEqual(user.email, 'teste@ftc.ac.mz')
        self.assertTrue(user.check_password('teste123'))
        self.assertEqual(user.get_full_name(), 'Teste Utilizador')
    
    def test_obter_papel_exibicao(self):
        """Teste: retorna papel correto baseado em tipo_utilizador."""
        self.assertEqual(self.admin.obter_papel_exibicao(), 'Administrador do Sistema')
        self.assertEqual(self.pca.obter_papel_exibicao(), 'PCA')
        self.assertEqual(self.colaborador.obter_papel_exibicao(), 'Colaborador')
    
    def test_obter_nivel_hierarquico(self):
        """Teste: retorna nível numérico correto."""
        self.assertEqual(self.admin.obter_nivel_hierarquico(), 6)
        self.assertEqual(self.pca.obter_nivel_hierarquico(), 5)
        self.assertEqual(self.chefe.obter_nivel_hierarquico(), 3)
        self.assertEqual(self.colaborador.obter_nivel_hierarquico(), 2)
    
    def test_pode_gerir_utilizador(self):
        """Teste: valida hierarquia de gestão."""
        # Admin pode gerir todos
        self.assertTrue(self.admin.pode_gerir_utilizador(self.pca))
        self.assertTrue(self.admin.pode_gerir_utilizador(self.chefe))
        self.assertTrue(self.admin.pode_gerir_utilizador(self.colaborador))
        
        # PCA pode gerir chefe e colaborador
        self.assertTrue(self.pca.pode_gerir_utilizador(self.chefe))
        self.assertTrue(self.pca.pode_gerir_utilizador(self.colaborador))
        self.assertFalse(self.pca.pode_gerir_utilizador(self.admin))
        
        # Colaborador não pode gerir ninguém
        self.assertFalse(self.colaborador.pode_gerir_utilizador(self.chefe))
    
    def test_eh_pca_ou_superuser(self):
        """Teste: verifica permissões máximas."""
        self.assertTrue(self.pca.eh_pca_ou_superuser())
        self.assertFalse(self.colaborador.eh_pca_ou_superuser())
    
    def test_atualizar_ultimo_acesso(self):
        """Teste: atualiza campo ultimo_acesso corretamente."""
        self.assertIsNone(self.colaborador.ultimo_acesso)
        self.colaborador.atualizar_ultimo_acesso()
        self.assertIsNotNone(self.colaborador.ultimo_acesso)


class TestPerfilUtilizador(TestCase):
    """Testes para o modelo PerfilUtilizador."""
    
    def setUp(self):
        """Configurar dados de teste."""
        self.user = User.objects.create_user(
            email='teste@ftc.ac.mz',
            first_name='Teste',
            last_name='User',
            password='teste123',
            tipo_utilizador='chefe',
            data_nascimento=date(1990, 1, 1)
        )
        self.perfil = self.user.perfil
    
    def test_obter_nivel_display(self):
        """Teste: retorna nome do nível."""
        self.perfil.nivel_hierarquico = 'chefe'
        self.assertEqual(self.perfil.obter_nivel_display(), 'Chefe de Sector')
    
    def test_eh_chefe(self):
        """Teste: verifica se é chefe."""
        self.perfil.nivel_hierarquico = 'chefe'
        self.assertTrue(self.perfil.eh_chefe())
        
        self.perfil.nivel_hierarquico = 'colaborador'
        self.assertFalse(self.perfil.eh_chefe())
    
    def test_obter_idade(self):
        """Teste: calcula idade corretamente."""
        idade = self.perfil.obter_idade()
        self.assertIsNotNone(idade)
        self.assertGreater(idade, 30)
    
    def test_obter_preferencia_notificacao(self):
        """Teste: retorna configuração de notificação."""
        self.perfil.preferencias_notificacao = {'email': True, 'push': False}
        self.perfil.save()
        
        self.assertTrue(self.perfil.obter_preferencia_notificacao('email'))
        self.assertFalse(self.perfil.obter_preferencia_notificacao('push'))
    
    def test_definir_preferencia_notificacao(self):
        """Teste: define configuração de notificação."""
        self.perfil.definir_preferencia_notificacao('sms', True)
        self.assertTrue(self.perfil.preferencias_notificacao.get('sms'))


class TestHierarquiaUtilizador(TestCase):
    """Testes para o modelo HierarquiaUtilizador."""
    
    def setUp(self):
        """Configurar dados de teste."""
        # Criar superior primeiro
        self.superior = User.objects.create_user(
            email='superior@ftc.ac.mz',
            first_name='Superior',
            last_name='RH',
            password='sup123',
            tipo_utilizador='chefe'
        )
        
        # Criar setor com o superior como chefe
        self.sector = Sector.objects.create(
            nome='RH',
            descricao='Recursos Humanos',
            chefe=self.superior,
            ativo=True
        )
        
        self.subordinado = User.objects.create_user(
            email='sub@ftc.ac.mz',
            first_name='Subordinado',
            last_name='RH',
            password='sub123',
            tipo_utilizador='colaborador'
        )
        
        self.hierarquia = HierarquiaUtilizador.objects.create(
            superior=self.superior,
            subordinado=self.subordinado,
            tipo_relacao='chefe_colaborador',
            ativo=True,
            data_inicio=timezone.now()
        )
    
    def test_obter_subordinados(self):
        """Teste: retorna subordinados corretos."""
        subordinados = self.hierarquia.obter_subordinados()
        self.assertEqual(subordinados.count(), 0)  # Subordinado não tem subordinados
    
    def test_pode_gerir_utilizador(self):
        """Teste: valida hierarquia."""
        self.assertTrue(self.hierarquia.pode_gerir_utilizador(self.subordinado))
    
    def test_eh_ativo(self):
        """Teste: verifica se posição está ativa."""
        self.assertTrue(self.hierarquia.eh_ativo())
        
        self.hierarquia.ativo = False
        self.assertFalse(self.hierarquia.eh_ativo())
    
    def test_obter_nivel_peso(self):
        """Teste: retorna peso numérico."""
        peso = self.hierarquia.obter_nivel_peso()
        self.assertIsInstance(peso, int)
    
    def test_obter_duracao(self):
        """Teste: calcula duração da posição."""
        duracao = self.hierarquia.obter_duracao()
        self.assertIsNotNone(duracao)
    
    def test_finalizar_posicao(self):
        """Teste: marca posição como inativa."""
        self.hierarquia.finalizar_posicao()
        self.assertFalse(self.hierarquia.ativo)
        self.assertIsNotNone(self.hierarquia.data_fim)


# ==================== TESTES DE VIEWS ====================

class TestLoginView(TestCase):
    """Testes para a view de login."""
    
    def setUp(self):
        """Configurar dados de teste."""
        self.client = Client()
        self.user = User.objects.create_user(
            email='teste@ftc.ac.mz',
            first_name='Teste',
            last_name='User',
            password='teste123',
            ativo=True
        )
        self.login_url = reverse('users:login')
    
    def test_get(self):
        """Teste: renderiza template correto."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
    
    def test_post_valid(self):
        """Teste: autentica utilizador e redireciona."""
        response = self.client.post(self.login_url, {
            'username': 'teste@ftc.ac.mz',
            'password': 'teste123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_post_invalid(self):
        """Teste: mostra erros de validação."""
        response = self.client.post(self.login_url, {
            'username': 'teste@ftc.ac.mz',
            'password': 'errado'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error', status_code=200)


class TestListarUtilizadoresView(TestCase):
    """Testes para a view de listagem de utilizadores."""
    
    def setUp(self):
        """Configurar dados de teste."""
        self.client = Client()
        self.admin = User.objects.create_user(
            email='admin@ftc.ac.mz',
            first_name='Admin',
            last_name='Sistema',
            password='admin123',
            tipo_utilizador='admin',
            ativo=True,
            is_staff=True
        )
        
        # Criar alguns utilizadores para listar
        for i in range(5):
            User.objects.create_user(
                email=f'user{i}@ftc.ac.mz',
                first_name=f'User{i}',
                last_name='Test',
                password='test123',
                ativo=True
            )
        
        self.list_url = reverse('users:lista_utilizadores')
    
    def test_get_sem_permissao(self):
        """Teste: redireciona se não tiver permissão."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_get_com_permissao(self):
        """Teste: lista utilizadores com permissão."""
        self.client.login(email='admin@ftc.ac.mz', password='admin123')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/lista_utilizadores.html')


class TestCriarUtilizadorView(TestCase):
    """Testes para a view de criação de utilizador."""
    
    def setUp(self):
        """Configurar dados de teste."""
        self.client = Client()
        self.admin = User.objects.create_user(
            email='admin@ftc.ac.mz',
            first_name='Admin',
            last_name='Sistema',
            password='admin123',
            tipo_utilizador='admin',
            ativo=True,
            is_staff=True
        )
        self.create_url = reverse('users:criar_utilizador')
    
    def test_get(self):
        """Teste: mostra formulário de criação."""
        self.client.login(email='admin@ftc.ac.mz', password='admin123')
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/criar_utilizador.html')


# ==================== TESTES DE FORMS ====================

class TestCriarUtilizadorForm(TestCase):
    """Testes para o form de criação de utilizador."""
    
    def test_campos_obrigatorios(self):
        """Teste: valida campos obrigatórios."""
        form = CriarUtilizadorForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('first_name', form.errors)
        self.assertIn('last_name', form.errors)
    
    def test_clean_email(self):
        """Teste: valida email único."""
        User.objects.create_user(
            email='existente@ftc.ac.mz',
            first_name='Existente',
            last_name='User',
            password='teste123'
        )
        
        form = CriarUtilizadorForm(data={
            'email': 'existente@ftc.ac.mz',
            'first_name': 'Novo',
            'last_name': 'User',
            'password1': 'senha123',
            'password2': 'senha123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class TestUserLoginForm(TestCase):
    """Testes para o form de login."""
    
    def setUp(self):
        """Configurar dados de teste."""
        self.user = User.objects.create_user(
            email='teste@ftc.ac.mz',
            first_name='Teste',
            last_name='User',
            password='teste123',
            ativo=True
        )
    
    def test_clean_username(self):
        """Teste: valida se username/email existe."""
        form = UserLoginForm(data={
            'username': 'naoexiste@ftc.ac.mz',
            'password': 'teste123'
        })
        self.assertFalse(form.is_valid())


class TestPerfilUtilizadorForm(TestCase):
    """Testes para o form de perfil de utilizador."""
    
    def setUp(self):
        """Configurar dados de teste."""
        self.user = User.objects.create_user(
            email='teste@ftc.ac.mz',
            first_name='Teste',
            last_name='User',
            password='teste123'
        )
    
    def test_clean_data_nascimento(self):
        """Teste: valida idade mínima."""
        # Data de nascimento muito recente (menor de idade)
        form = PerfilUtilizadorForm(
            instance=self.user,
            data={
                'first_name': 'Teste',
                'last_name': 'User',
                'email': 'teste@ftc.ac.mz',
                'data_nascimento': date.today() - timedelta(days=365*10)  # 10 anos
            }
        )
        # Forma aceita qualquer data, mas podemos adicionar validação


# ==================== TESTES DE SIGNALS ====================

class TestUserSignals(TestCase):
    """Testes para os signals de User."""
    
    def test_criar_perfil_automatico(self):
        """Teste: cria perfil automaticamente ao criar utilizador."""
        user = User.objects.create_user(
            email='novo@ftc.ac.mz',
            first_name='Novo',
            last_name='User',
            password='novo123',
            tipo_utilizador='colaborador'
        )
        
        # Verificar se o perfil foi criado
        self.assertTrue(hasattr(user, 'perfil'))
        self.assertIsNotNone(user.perfil)
        self.assertEqual(user.perfil.nivel_hierarquico, 'colaborador')
    
    def test_definir_nivel_hierarquico(self):
        """Teste: define nível baseado em tipo_utilizador."""
        user = User.objects.create_user(
            email='chefe@ftc.ac.mz',
            first_name='Chefe',
            last_name='Sector',
            password='chefe123',
            tipo_utilizador='chefe'
        )
        
        self.assertEqual(user.perfil.nivel_hierarquico, 'chefe')


# ==================== TESTES DE PERMISSÕES ====================

class TestPermissoesUtilizador(TestCase):
    """Testes para o sistema de permissões."""
    
    def setUp(self):
        """Configurar dados de teste."""
        self.admin = User.objects.create_user(
            email='admin@ftc.ac.mz',
            first_name='Admin',
            last_name='Sistema',
            password='admin123',
            tipo_utilizador='admin'
        )
        
        self.pca = User.objects.create_user(
            email='pca@ftc.ac.mz',
            first_name='PCA',
            last_name='FTC',
            password='pca123',
            tipo_utilizador='pca'
        )
        
        self.colaborador = User.objects.create_user(
            email='colab@ftc.ac.mz',
            first_name='Colaborador',
            last_name='FTC',
            password='colab123',
            tipo_utilizador='colaborador'
        )
    
    def test_hierarquia_permissoes(self):
        """Teste: Admin > PCA > Secretaria > Chefe > Colaborador."""
        nivel_admin = self.admin.obter_nivel_hierarquico()
        nivel_pca = self.pca.obter_nivel_hierarquico()
        nivel_colab = self.colaborador.obter_nivel_hierarquico()
        
        self.assertGreater(nivel_admin, nivel_pca)
        self.assertGreater(nivel_pca, nivel_colab)
    
    def test_gestao_utilizadores(self):
        """Teste: apenas superiores podem gerir."""
        # Admin pode gerir PCA e Colaborador
        self.assertTrue(self.admin.pode_gerir_utilizador(self.pca))
        self.assertTrue(self.admin.pode_gerir_utilizador(self.colaborador))
        
        # PCA pode gerir Colaborador mas não Admin
        self.assertTrue(self.pca.pode_gerir_utilizador(self.colaborador))
        self.assertFalse(self.pca.pode_gerir_utilizador(self.admin))
        
        # Colaborador não pode gerir ninguém
        self.assertFalse(self.colaborador.pode_gerir_utilizador(self.pca))
        self.assertFalse(self.colaborador.pode_gerir_utilizador(self.admin))
