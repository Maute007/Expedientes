from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Sector, EstadoDocumento
from entrada.models import Expediente, TipoDocumento, AnexoExpediente
from django.core.files.uploadedfile import SimpleUploadedFile
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Testa as funcionalidades avançadas de anexos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧪 Testando funcionalidades avançadas de anexos...'))
        
        try:
            # 1. Criar dados de teste se necessário
            self.criar_dados_teste()
            
            # 2. Testar criação de anexo
            self.testar_criacao_anexo()
            
            # 3. Testar URLs de anexos
            self.testar_urls_anexos()
            
            self.stdout.write(self.style.SUCCESS('✅ Todos os testes de anexos avançados passaram!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro nos testes: {str(e)}'))

    def criar_dados_teste(self):
        """Cria dados de teste se não existirem"""
        
        # Criar sector se não existir
        sector, created = Sector.objects.get_or_create(
            nome='Sector de Teste',
            defaults={
                'descricao': 'Sector para testes',
                'ativo': True
            }
        )
        
        # Criar tipo de documento se não existir
        tipo_doc, created = TipoDocumento.objects.get_or_create(
            nome='Documento de Teste',
            defaults={
                'descricao': 'Tipo de documento para testes',
                'ativo': True
            }
        )
        
        # Criar estado se não existir
        estado, created = EstadoDocumento.objects.get_or_create(
            nome='Recebido',
            defaults={
                'descricao': 'Documento recebido',
                'ativo': True
            }
        )
        
        self.stdout.write('📋 Dados de teste criados/verificados')

    def testar_criacao_anexo(self):
        """Testa a criação de um anexo"""
        
        # Buscar expediente existente ou criar um
        expediente = Expediente.objects.first()
        if not expediente:
            sector = Sector.objects.first()
            tipo_doc = TipoDocumento.objects.first()
            estado = EstadoDocumento.objects.first()
            
            expediente = Expediente.objects.create(
                numero_protocolo='20250100001',
                referencia='TESTE-001',
                tipo_documento=tipo_doc,
                sector_responsavel=sector,
                estado_atual=estado,
                assunto='Documento de teste para anexos',
                conteudo='Conteúdo de teste'
            )
        
        # Criar arquivo de teste
        conteudo_teste = b'Conteudo do arquivo de teste'
        arquivo_teste = SimpleUploadedFile(
            'teste.txt',
            conteudo_teste,
            content_type='text/plain'
        )
        
        # Criar anexo
        anexo = AnexoExpediente.objects.create(
            expediente=expediente,
            nome_original='teste.txt',
            arquivo=arquivo_teste,
            tamanho=len(conteudo_teste),
            tipo_mime='text/plain',
            upload_por=User.objects.first()
        )
        
        self.stdout.write(f'📎 Anexo criado: {anexo.nome_original} ({anexo.tamanho_humanizado})')
        
        # Verificar se anexo foi criado corretamente
        assert anexo.pk is not None, "Anexo não foi salvo"
        assert anexo.ativo == True, "Anexo não está ativo"
        assert anexo.expediente == expediente, "Anexo não está associado ao expediente correto"
        
        self.stdout.write('✅ Criação de anexo testada com sucesso')

    def testar_urls_anexos(self):
        """Testa se as URLs de anexos estão configuradas"""
        
        from django.urls import reverse, NoReverseMatch
        
        # Testar URLs de anexos
        urls_teste = [
            'entrada:anexos:baixar_anexo',
            'entrada:anexos:visualizar_anexo', 
            'entrada:anexos:apagar_anexo',
            'entrada:anexos:lista_anexos',
            'entrada:anexos:verificar_integridade_anexo',
            'entrada:anexos:scan_virus_anexo',
        ]
        
        for url_name in urls_teste:
            try:
                # Testar se URL existe (com pk fictício)
                reverse(url_name, kwargs={'pk': 1})
                self.stdout.write(f'✅ URL {url_name} configurada')
            except NoReverseMatch:
                self.stdout.write(self.style.ERROR(f'❌ URL {url_name} não encontrada'))
                raise
        
        self.stdout.write('✅ Todas as URLs de anexos estão configuradas')
