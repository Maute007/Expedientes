from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.conf import settings
from .managers import UserManager
import os


class User(AbstractUser):
    """
    Modelo de utilizador customizado com campos adicionais para o sistema FTC.
    """
    
    # Configurações de related_name para evitar conflitos
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    
    # Constantes
    GENEROS = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]
    
    # Campos de autenticação
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name="Email",
        help_text="Email único para login no sistema"
    )
    
    # Campos básicos
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Nome"
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Sobrenome"
    )
    
    # Campo username não é usado para login (apenas para compatibilidade)
    username = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Username",
        help_text="Campo não utilizado para login. Use email."
    )
    
    # Campos de contacto
    telefone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Formato de telefone inválido. Use: +258 82 123 4567"
        )],
        verbose_name="Telefone"
    )
    
    # Campos organizacionais
    sector_atual = models.ForeignKey(
        'core.Sector',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='utilizadores',
        verbose_name="Sector Atual"
    )
    cargo = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Cargo"
    )
    
    # Campos de status
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Se o utilizador está ativo no sistema"
    )
    
    # Constantes para tipos de utilizador
    TIPOS_UTILIZADOR = [
        ('admin', 'Administrador do Sistema'),
        ('pca', 'PCA'),
        ('secretaria', 'Secretaria'),
        ('chefe', 'Chefe de Sector'),
        ('colaborador', 'Colaborador'),
        ('externo', 'Utilizador Externo'),
    ]
    
    tipo_utilizador = models.CharField(
        max_length=20,
        choices=TIPOS_UTILIZADOR,
        default='colaborador',
        verbose_name="Tipo de Utilizador",
        help_text="Papel do utilizador no sistema"
    )
    
    # Campos de acesso
    ultimo_acesso = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último Acesso"
    )
    
    # Campos de perfil
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Avatar"
    )
    biografia = models.TextField(
        blank=True,
        null=True,
        verbose_name="Biografia"
    )
    data_nascimento = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Nascimento"
    )
    genero = models.CharField(
        max_length=10,
        choices=GENEROS,
        blank=True,
        null=True,
        verbose_name="Género"
    )
    
    # Campos de endereço
    endereco = models.TextField(
        blank=True,
        null=True,
        verbose_name="Endereço"
    )
    codigo_postal = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Código Postal"
    )
    cidade = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Cidade"
    )
    pais = models.CharField(
        max_length=100,
        default='Moçambique',
        verbose_name="País"
    )
    
    # Manager customizado
    objects = UserManager()
    
    # Configurações do modelo
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        ordering = ['first_name', 'last_name']
        verbose_name = "Utilizador"
        verbose_name_plural = "Utilizadores"
    
    def save(self, *args, **kwargs):
        """
        Salva o utilizador preenchendo automaticamente o username com o email.
        """
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)
    
    def __str__(self):
        """Representação string do utilizador."""
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """Retorna nome completo do utilizador."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """Retorna nome curto do utilizador."""
        return self.first_name
    
    def obter_papel_exibicao(self):
        """Retorna papel do utilizador para exibição."""
        if self.is_superuser:
            return "Superuser"
        
        tipo_display = dict(self.TIPOS_UTILIZADOR)
        papel_base = tipo_display.get(self.tipo_utilizador, 'Utilizador')
        
        # Para chefes, mostrar o sector específico
        if self.tipo_utilizador == 'chefe' and self.sector_atual:
            return f"Chefe de {self.sector_atual.nome}"
        elif self.tipo_utilizador == 'colaborador' and self.sector_atual:
            return f"Colaborador de {self.sector_atual.nome}"
        
        return papel_base
    
    def obter_nivel_hierarquico(self):
        """Retorna nível hierárquico numérico do utilizador."""
        if self.is_superuser:
            return 7  # Superuser (máximo)
        
        niveis = {
            'admin': 6,      # Administrador do Sistema
            'pca': 5,        # PCA
            'secretaria': 4, # Secretaria
            'chefe': 3,      # Chefe de Sector
            'colaborador': 2, # Colaborador
            'externo': 1,    # Externo
        }
        
        return niveis.get(self.tipo_utilizador, 1)
    
    def pode_gerir_utilizador(self, outro_user):
        """Verifica se pode gerir outro utilizador."""
        if not outro_user:
            return False
        
        # Superuser pode gerir todos
        if self.is_superuser:
            return True
        
        # Administrador pode gerir todos
        if self.tipo_utilizador == 'admin':
            return True
        
        # PCA pode gerir todos
        if self.tipo_utilizador == 'pca':
            return True
        
        # Secretaria pode gerir colaboradores
        if self.tipo_utilizador == 'secretaria' and outro_user.sector_atual:
            return True
        
        # Chefe pode gerir colaboradores do seu sector
        if (self.tipo_utilizador == 'chefe' and 
            self.sector_atual and 
            outro_user.sector_atual == self.sector_atual):
            return True
        
        return False
    
    def obter_subordinados(self):
        """Retorna utilizadores subordinados."""
        if self.is_superuser:
            # Superuser pode ver todos os utilizadores
            return User.objects.filter(ativo=True).exclude(pk=self.pk)
        elif self.tipo_utilizador == 'admin':
            # Administrador pode ver todos os utilizadores
            return User.objects.filter(ativo=True).exclude(pk=self.pk)
        elif self.tipo_utilizador == 'pca':
            # PCA pode ver todos os utilizadores ativos
            return User.objects.filter(ativo=True).exclude(pk=self.pk)
        elif self.tipo_utilizador == 'secretaria':
            # Secretaria pode ver todos os colaboradores
            return User.objects.filter(ativo=True, sector_atual__isnull=False).exclude(pk=self.pk)
        elif self.tipo_utilizador == 'chefe' and self.sector_atual:
            # Chefe pode ver colaboradores do seu sector
            return User.objects.filter(
                ativo=True,
                sector_atual=self.sector_atual
            ).exclude(pk=self.pk)
        else:
            return User.objects.none()
    
    def atualizar_ultimo_acesso(self):
        """Atualiza timestamp do último acesso."""
        self.ultimo_acesso = timezone.now()
        self.save(update_fields=['ultimo_acesso'])
    
    def eh_admin_ou_superuser(self):
        """Verifica se é Administrador ou superuser."""
        return self.tipo_utilizador == 'admin' or self.is_superuser
    
    def eh_pca_ou_superuser(self):
        """Verifica se é PCA ou superuser."""
        return self.tipo_utilizador == 'pca' or self.is_superuser
    
    def eh_chefe_ou_acima(self):
        """Verifica se é chefe ou acima na hierarquia."""
        return self.tipo_utilizador in ['admin', 'pca', 'secretaria', 'chefe']
    
    def eh_chefe_de_sector(self):
        """Verifica se é chefe de algum sector."""
        return (self.tipo_utilizador == 'chefe' and 
                self.sector_atual and 
                self.sector_atual.chefe == self)
    
    def obter_avatar_url(self):
        """Retorna URL do avatar ou avatar padrão."""
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return '/static/images/default-avatar.png'
    
    def obter_idade(self):
        """Retorna idade do utilizador."""
        if self.data_nascimento:
            today = timezone.now().date()
            return today.year - self.data_nascimento.year - (
                (today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day)
            )
        return None
    
    def obter_endereco_completo(self):
        """Retorna endereço completo formatado."""
        endereco_parts = []
        if self.endereco:
            endereco_parts.append(self.endereco)
        if self.codigo_postal:
            endereco_parts.append(self.codigo_postal)
        if self.cidade:
            endereco_parts.append(self.cidade)
        if self.pais:
            endereco_parts.append(self.pais)
        return ', '.join(endereco_parts) if endereco_parts else None


class PerfilUtilizador(models.Model):
    """
    Perfil estendido do utilizador com configurações e preferências.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name="Utilizador"
    )
    
    # Configurações de notificação
    receber_notificacoes_email = models.BooleanField(
        default=True,
        verbose_name="Receber Notificações por Email"
    )
    receber_notificacoes_push = models.BooleanField(
        default=True,
        verbose_name="Receber Notificações Push"
    )
    receber_newsletter = models.BooleanField(
        default=False,
        verbose_name="Receber Newsletter"
    )
    
    # Configurações de interface
    tema_preferido = models.CharField(
        max_length=20,
        choices=[
            ('light', 'Claro'),
            ('dark', 'Escuro'),
            ('auto', 'Automático'),
        ],
        default='light',
        verbose_name="Tema Preferido"
    )
    idioma_preferido = models.CharField(
        max_length=10,
        choices=[
            ('pt-pt', 'Português'),
            ('en', 'English'),
        ],
        default='pt-pt',
        verbose_name="Idioma Preferido"
    )
    timezone = models.CharField(
        max_length=50,
        default='Africa/Maputo',
        verbose_name="Fuso Horário"
    )
    
    # Configurações de privacidade
    perfil_publico = models.BooleanField(
        default=False,
        verbose_name="Perfil Público"
    )
    mostrar_email = models.BooleanField(
        default=False,
        verbose_name="Mostrar Email"
    )
    mostrar_telefone = models.BooleanField(
        default=False,
        verbose_name="Mostrar Telefone"
    )
    
    # Configurações de trabalho
    horario_trabalho_inicio = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Horário de Trabalho - Início"
    )
    horario_trabalho_fim = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Horário de Trabalho - Fim"
    )
    dias_trabalho = models.CharField(
        max_length=20,
        default='1,2,3,4,5',  # Segunda a Sexta
        verbose_name="Dias de Trabalho",
        help_text="Dias da semana separados por vírgula (1=Segunda, 7=Domingo)"
    )
    
    # Metadados
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de Atualização"
    )
    
    class Meta:
        verbose_name = "Perfil de Utilizador"
        verbose_name_plural = "Perfis de Utilizadores"
    
    def __str__(self):
        return f"Perfil de {self.user.get_full_name()}"
    
    def obter_dias_trabalho_lista(self):
        """Retorna lista de dias de trabalho."""
        try:
            return [int(dia) for dia in self.dias_trabalho.split(',')]
        except (ValueError, AttributeError):
            return [1, 2, 3, 4, 5]  # Padrão: Segunda a Sexta
    
    def obter_dias_trabalho_nomes(self):
        """Retorna nomes dos dias de trabalho."""
        dias_nomes = {
            1: 'Segunda',
            2: 'Terça',
            3: 'Quarta',
            4: 'Quinta',
            5: 'Sexta',
            6: 'Sábado',
            7: 'Domingo'
        }
        dias = self.obter_dias_trabalho_lista()
        return [dias_nomes.get(dia, f'Dia {dia}') for dia in dias]


class HierarquiaUtilizador(models.Model):
    """
    Modelo para definir hierarquia entre utilizadores.
    """
    
    superior = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subordinados_diretos',
        verbose_name="Superior"
    )
    subordinado = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='superiores_diretos',
        verbose_name="Subordinado"
    )
    tipo_relacao = models.CharField(
        max_length=20,
        choices=[
            ('chefe_direto', 'Chefe Direto'),
            ('supervisor', 'Supervisor'),
            ('mentor', 'Mentor'),
            ('substituto', 'Substituto'),
        ],
        default='chefe_direto',
        verbose_name="Tipo de Relação"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    data_inicio = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Início"
    )
    data_fim = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Fim"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )
    
    class Meta:
        unique_together = ['superior', 'subordinado', 'tipo_relacao']
        verbose_name = "Hierarquia de Utilizador"
        verbose_name_plural = "Hierarquias de Utilizadores"
        ordering = ['-data_inicio']
    
    def __str__(self):
        return f"{self.superior.get_full_name()} → {self.subordinado.get_full_name()}"
    
    def ativar(self):
        """Ativa a relação hierárquica."""
        self.ativo = True
        self.data_fim = None
        self.save()
    
    def desativar(self):
        """Desativa a relação hierárquica."""
        self.ativo = False
        self.data_fim = timezone.now()
        self.save()
    
    def eh_ativa(self):
        """Verifica se a relação está ativa."""
        return self.ativo and (not self.data_fim or self.data_fim > timezone.now())