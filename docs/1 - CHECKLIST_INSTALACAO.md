# 📋 1. CHECKLIST DE INSTALAÇÃO E CONFIGURAÇÃO INICIAL

## 🚀 Configuração do Ambiente

### 1. Ambiente Virtual e Dependências
- [x] Criar ambiente virtual Python
- [x] Ativar ambiente virtual
- [x] Instalar Django 5+
- [x] Instalar psycopg2-binary (PostgreSQL adapter)
- [x] Instalar python-decouple (para .env)
- [x] Instalar django-crispy-forms
- [x] Instalar crispy-bootstrap5
- [x] Instalar Pillow (para upload de imagens)
- [x] Criar requirements.txt com todas as dependências

### 2. Configuração do Projeto Django
- [x] Criar projeto Django principal
- [x] Configurar settings.py com PostgreSQL
- [x] Configurar .env com variáveis sensíveis
- [x] Configurar STATIC_ROOT e MEDIA_ROOT
- [x] Configurar TIME_ZONE para Portugal
- [x] Configurar LANGUAGE_CODE para pt-pt
- [x] Configurar crispy forms

### 3. Base de Dados PostgreSQL
- [x] Instalar PostgreSQL
- [x] Criar base de dados
- [x] Configurar conexão no settings.py
- [x] Testar conexão com a base de dados

### 4. Estrutura de Apps
- [x] Criar app core
- [x] Criar app users
- [x] Criar app entrada
- [x] Criar app saida
- [x] Criar app interna
- [x] Criar app externa
- [x] Criar app relatorios
- [x] Criar app assinatura_digital
- [x] Registrar todas as apps no settings.py

### 5. Configuração Inicial
- [x] Executar migrations iniciais
- [x] Criar superuser
- [ ] Criar PCA inicial (utilizador com is_pca=True)
- [ ] Criar sectores especiais: "Gabinete do PCA", "Secretaria"
- [x] Configurar URLs principais
- [x] Testar servidor de desenvolvimento
- [x] Verificar se todas as apps estão funcionando

### 6. Templates e Estáticos
- [x] Configurar diretório de templates
- [x] Configurar diretório de ficheiros estáticos
- [x] Instalar Bootstrap 5
- [x] Criar template base
- [x] Configurar crispy forms com Bootstrap 5

### 7. Configurações de Segurança
- [x] Configurar SECRET_KEY no .env
- [x] Configurar DEBUG=False para produção
- [x] Configurar ALLOWED_HOSTS
- [x] Configurar CSRF_TRUSTED_ORIGINS
- [x] Configurar segurança de ficheiros upload



## ✅ Validação Final
- [x] Projeto Django inicia sem erros
- [x] Base de dados conecta corretamente
- [x] Todas as apps estão registradas
- [x] Templates carregam corretamente
- [x] Ficheiros estáticos servem corretamente
- [x] Ambiente está pronto para desenvolvimento



**Nota:** Este checklist deve ser completado antes de começar o desenvolvimento das funcionalidades específicas de cada app.

