from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from core.models import EstadoDocumento, Sector, ConfiguracaoSistema


class Command(BaseCommand):
    help = 'Cria dados iniciais do sistema (estados, sectores e configurações)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a criação mesmo se os dados já existirem',
        )
        parser.add_argument(
            '--pca-username',
            type=str,
            default='pca',
            help='Nome de utilizador para o PCA (padrão: pca)',
        )
        parser.add_argument(
            '--pca-email',
            type=str,
            default='pca@sistema.pt',
            help='Email para o PCA (padrão: pca@sistema.pt)',
        )

    def handle(self, *args, **options):
        force = options['force']
        pca_username = options['pca_username']
        pca_email = options['pca_email']

        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando criação de dados iniciais...')
        )

        with transaction.atomic():
            # 1. Criar estados de documento
            self.criar_estados_documento(force)
            
            # 2. Criar configurações do sistema
            self.criar_configuracoes_sistema(force)
            
            # 3. Verificar/criar PCA
            pca_user = self.verificar_ou_criar_pca(pca_username, pca_email, force)
            
            # 4. Criar sectores especiais
            self.criar_sectores_especiais(pca_user, force)

        self.stdout.write(
            self.style.SUCCESS('✅ Dados iniciais criados com sucesso!')
        )

    def criar_estados_documento(self, force=False):
        """Cria os estados de documento se não existirem."""
        self.stdout.write('📄 Criando estados de documento...')
        
        estados_data = [
            {
                'nome': 'Recebido',
                'descricao': 'Documento recebido no sistema e aguardando processamento inicial',
                'cor': '#007bff',
                'ordem': 1,
                'requer_acao': False
            },
            {
                'nome': 'Encaminhado',
                'descricao': 'Documento encaminhado para sector ou utilizador específico',
                'cor': '#fd7e14',
                'ordem': 2,
                'requer_acao': True
            },
            {
                'nome': 'Em Tratamento',
                'descricao': 'Documento está a ser processado pelo sector/utilizador responsável',
                'cor': '#ffc107',
                'ordem': 3,
                'requer_acao': True
            },
            {
                'nome': 'Concluído',
                'descricao': 'Processamento do documento foi finalizado com sucesso',
                'cor': '#198754',
                'ordem': 4,
                'requer_acao': False
            },
            {
                'nome': 'Arquivado',
                'descricao': 'Documento arquivado definitivamente no sistema',
                'cor': '#6c757d',
                'ordem': 5,
                'requer_acao': False
            },
            {
                'nome': 'Devolvido',
                'descricao': 'Documento devolvido ao PCA ou sector anterior para reanálise',
                'cor': '#dc3545',
                'ordem': 6,
                'requer_acao': True
            }
        ]

        for estado_data in estados_data:
            estado, created = EstadoDocumento.objects.get_or_create(
                nome=estado_data['nome'],
                defaults=estado_data
            )
            
            if created:
                self.stdout.write(f'  ✅ Estado "{estado.nome}" criado')
            elif force:
                for key, value in estado_data.items():
                    setattr(estado, key, value)
                estado.save()
                self.stdout.write(f'  🔄 Estado "{estado.nome}" atualizado')
            else:
                self.stdout.write(f'  ⏭️  Estado "{estado.nome}" já existe')

    def criar_configuracoes_sistema(self, force=False):
        """Cria as configurações do sistema se não existirem."""
        self.stdout.write('⚙️  Criando configurações do sistema...')
        
        configuracoes_data = [
            {
                'chave': 'nome_sistema',
                'valor': 'Sistema de Gestão de Expedientes',
                'descricao': 'Nome oficial do sistema',
                'tipo': 'string'
            },
            {
                'chave': 'versao_sistema',
                'valor': '1.0.0',
                'descricao': 'Versão atual do sistema',
                'tipo': 'string'
            },
            {
                'chave': 'manutencao_ativa',
                'valor': 'false',
                'descricao': 'Indica se o sistema está em modo de manutenção',
                'tipo': 'bool'
            },
            {
                'chave': 'limite_notificacoes',
                'valor': '100',
                'descricao': 'Número máximo de notificações por utilizador',
                'tipo': 'int'
            },
            {
                'chave': 'tempo_sessao',
                'valor': '3600',
                'descricao': 'Tempo de sessão em segundos (1 hora)',
                'tipo': 'int'
            },
            {
                'chave': 'tamanho_max_anexo',
                'valor': '10485760',
                'descricao': 'Tamanho máximo de anexos em bytes (10MB)',
                'tipo': 'int'
            },
            {
                'chave': 'tipos_ficheiro_permitidos',
                'valor': '["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "jpg", "jpeg", "png", "gif"]',
                'descricao': 'Tipos de ficheiro permitidos para upload',
                'tipo': 'json'
            }
        ]

        for config_data in configuracoes_data:
            config, created = ConfiguracaoSistema.objects.get_or_create(
                chave=config_data['chave'],
                defaults=config_data
            )
            
            if created:
                self.stdout.write(f'  ✅ Configuração "{config.chave}" criada')
            elif force:
                for key, value in config_data.items():
                    setattr(config, key, value)
                config.save()
                self.stdout.write(f'  🔄 Configuração "{config.chave}" atualizada')
            else:
                self.stdout.write(f'  ⏭️  Configuração "{config.chave}" já existe')

    def verificar_ou_criar_pca(self, username, email, force=False):
        """Verifica se o PCA existe ou cria um novo."""
        self.stdout.write('👤 Verificando/criando PCA...')
        
        try:
            pca = User.objects.get(username=username)
            if hasattr(pca, 'is_pca') and pca.is_pca:
                self.stdout.write(f'  ✅ PCA "{username}" já existe')
                return pca
            else:
                # Se o campo is_pca não existe ainda, vamos assumir que é PCA
                self.stdout.write(f'  ⚠️  Utilizador "{username}" existe mas campo is_pca não está disponível')
                return pca
        except User.DoesNotExist:
            # Criar PCA
            pca = User.objects.create_user(
                username=username,
                email=email,
                password='pca123',  # Senha temporária
                first_name='PCA',
                last_name='Sistema',
                is_staff=True,
                is_superuser=True
            )
            
            # Tentar definir is_pca se o campo existir
            if hasattr(pca, 'is_pca'):
                pca.is_pca = True
                pca.save()
            
            self.stdout.write(f'  ✅ PCA "{username}" criado com sucesso')
            self.stdout.write(f'  🔑 Senha temporária: pca123 (ALTERE IMEDIATAMENTE!)')
            return pca

    def criar_sectores_especiais(self, pca_user, force=False):
        """Cria sectores especiais do sistema."""
        self.stdout.write('🏢 Criando sectores especiais...')
        
        sectores_data = [
            {
                'nome': 'Gabinete do PCA',
                'descricao': 'Sector responsável pela presidência e direção geral da organização',
                'chefe': pca_user,
                'observacoes': 'Sector especial para o PCA'
            },
            {
                'nome': 'Secretaria',
                'descricao': 'Sector responsável pela receção, distribuição e gestão administrativa de documentos',
                'chefe': pca_user,  # Temporariamente o PCA até criar utilizador secretaria
                'observacoes': 'Sector especial para secretaria - ajustar chefe quando necessário'
            }
        ]

        for sector_data in sectores_data:
            sector, created = Sector.objects.get_or_create(
                nome=sector_data['nome'],
                defaults=sector_data
            )
            
            if created:
                self.stdout.write(f'  ✅ Sector "{sector.nome}" criado')
            elif force:
                for key, value in sector_data.items():
                    setattr(sector, key, value)
                sector.save()
                self.stdout.write(f'  🔄 Sector "{sector.nome}" atualizado')
            else:
                self.stdout.write(f'  ⏭️  Sector "{sector.nome}" já existe')

    def verificar_dependencias(self):
        """Verifica se todas as dependências estão satisfeitas."""
        self.stdout.write('🔍 Verificando dependências...')
        
        # Verificar se existem estados
        estados_count = EstadoDocumento.objects.count()
        if estados_count == 0:
            self.stdout.write(self.style.WARNING('⚠️  Nenhum estado de documento encontrado'))
        else:
            self.stdout.write(f'  ✅ {estados_count} estados de documento encontrados')
        
        # Verificar se existe PCA
        try:
            pca = User.objects.filter(is_superuser=True).first()
            if pca:
                self.stdout.write(f'  ✅ PCA encontrado: {pca.username}')
            else:
                self.stdout.write(self.style.WARNING('⚠️  Nenhum PCA encontrado'))
        except:
            self.stdout.write(self.style.WARNING('⚠️  Erro ao verificar PCA'))
        
        # Verificar sectores
        sectores_count = Sector.objects.count()
        if sectores_count == 0:
            self.stdout.write(self.style.WARNING('⚠️  Nenhum sector encontrado'))
        else:
            self.stdout.write(f'  ✅ {sectores_count} sectores encontrados')
