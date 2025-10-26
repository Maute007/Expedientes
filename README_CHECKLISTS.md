# 📚 GUIA DOS CHECKLISTS - SISTEMA DE GESTÃO DOCUMENTAL

## 🎯 Visão Geral
Este sistema de gestão documental foi desenvolvido com uma abordagem modular usando Django e PostgreSQL. Os checklists foram criados para garantir um desenvolvimento organizado e sem confusões entre as diferentes funcionalidades.

## 📋 Lista de Checklists

### 1. [CHECKLIST DE INSTALAÇÃO E CONFIGURAÇÃO INICIAL](1 - CHECKLIST_INSTALACAO.md) ✅ **COMPLETO**
**Objetivo:** Configurar o ambiente de desenvolvimento, instalar dependências e preparar a estrutura base do projeto.

**Conteúdo:**
- Configuração do ambiente virtual
- Instalação do Django 5+ e PostgreSQL
- Configuração das apps principais
- Configuração de templates e ficheiros estáticos
- Configurações de segurança
- Criação de dados iniciais (PCA, sectores especiais)

### 2. [CHECKLIST - APP CORE](2. CHECKLIST_CORE.md) ✅ **EXPANDIDO ULTRA-DETALHADO**
**Objetivo:** App central com configurações, utilitários, workflow de estados e notificações internas.

**Conteúdo Expandido:**
- **Modelos ultra-detalhados:** EstadoDocumento, Notificacao, Sector, ConfiguracaoSistema, DespachoDocumento, AnexoDespacho
- **Sistema de notificações completo:** tipos, prioridades, navegação, marcação automática/manual
- **Sistema de despachos/pareceres/comentários:** com visibilidade controlada e permissões
- **Views específicas:** 6 views de notificações com métodos detalhados
- **Templates:** 4 templates com pontos de parada para layouts Bootstrap 5
- **URLs:** padrões específicos para todas as funcionalidades
- **Admin:** configuração completa com filtros e ações
- **Testes:** casos de teste para modelos e views
- **Nomenclatura:** 100% em português

### 3. [CHECKLIST - APP USERS](3- CHECKLIST_USERS.md) ✅ **EXPANDIDO ULTRA-DETALHADO**
**Objetivo:** Gestão de utilizadores e perfis com Custom User Model e hierarquia organizacional.

**Conteúdo Expandido:**
- **Custom User Model:** campos adicionais (is_pca, is_secretaria, avatar, biografia, etc.)
- **PerfilUtilizador:** modelo completo com preferências e configurações
- **HierarquiaUtilizador:** histórico de posições e níveis hierárquicos
- **Forms:** 8 forms específicos com validações detalhadas
- **Views:** 12 views com decorators, context data e métodos específicos
- **Templates:** 7 templates com pontos de parada para layouts Bootstrap 5
- **URLs:** padrões específicos para autenticação e gestão
- **Admin:** configuração completa com camposets e ações
- **Signals:** 4 signals para auditoria e atualizações automáticas
- **Testes:** 12 classes de teste com métodos específicos
- **Nomenclatura:** 100% em português

### 4. [CHECKLIST - APP ENTRADA](4 - CHECKLIST_ENTRADA.md) ✅ **EXPANDIDO ULTRA-DETALHADO**
**Objetivo:** Gestão de documentos que entram via secretaria ou portal online.

**Conteúdo Expandido:**
- **Modelos ultra-detalhados:** DocumentoEntrada, TipoDocumento, AnexoDocumento, MovimentacaoDocumento
- **Tratamento completo de anexos:** upload, download, visualização, validação, scan de vírus, integridade
- **Tipos de documento:** 15+ tipos com categorias e prioridades
- **Fluxo de encaminhamento:** PCA → Sectores → Colaboradores com regras específicas
- **Views:** 12 views principais + 8 views específicas para anexos
- **Forms:** 5 forms com validações e widgets específicos
- **Templates:** 8 templates com pontos de parada para layouts Bootstrap 5
- **URLs:** padrões específicos para documentos e anexos
- **Signals:** 3 signals para workflow automático
- **Fixtures:** dados iniciais para tipos de documento
- **Management Commands:** comandos para criação de dados iniciais
- **Testes:** casos de teste para workflow completo
- **Nomenclatura:** 100% em português

### 5. [CHECKLIST - APP SAIDA](5 - CHECKLIST_SAIDA.md) ✅ **EXPANDIDO ULTRA-DETALHADO**
**Objetivo:** Gestão de documentos emitidos para fora da instituição.

**Conteúdo Expandido:**
- **Modelos ultra-detalhados:** DocumentoSaida, TipoDocumentoSaida, Destinatario, AnexoDocumentoSaida, AprovacaoDocumento
- **Sistema de aprovação:** níveis múltiplos com workflow específico
- **Gestão de destinatários:** tipos, preferências, bloqueios
- **Numeração automática:** por tipo de documento com prefixos
- **Views:** 15 views com métodos específicos para documentos, aprovações e anexos
- **Forms:** 8 forms com validações específicas
- **Templates:** 12 templates com pontos de parada para layouts Bootstrap 5
- **URLs:** padrões específicos para todas as funcionalidades
- **Admin:** configuração completa com filtros e ações
- **Signals:** 4 signals para workflow automático
- **Fixtures:** dados iniciais para tipos e destinatários
- **Management Commands:** comandos para criação de dados iniciais
- **Testes:** casos de teste para workflow de aprovação
- **Nomenclatura:** 100% em português

### 6. [CHECKLIST - APP INTERNA](6 - CHECKLIST_INTERNA.md) ✅ **EXPANDIDO ULTRA-DETALHADO**
**Objetivo:** Gestão de comunicação entre sectores e utilizadores.

**Conteúdo Expandido:**
- **Modelos ultra-detalhados:** MensagemInterna, TipoMensagem, AnexoMensagem, RespostaMensagem, GrupoComunicacao
- **Sistema de comunicação:** individual, sector, grupo, geral
- **Gestão de grupos:** criação, membros, tipos, configurações
- **Anexos de mensagens:** upload, visualização, validação
- **Views:** 15 views com métodos específicos para mensagens, grupos e anexos
- **Forms:** 9 forms com validações específicas
- **Templates:** 15 templates com pontos de parada para layouts Bootstrap 5
- **URLs:** padrões específicos para comunicação e grupos
- **Admin:** configuração completa com filtros e ações
- **Signals:** 5 signals para notificações e workflow
- **Fixtures:** dados iniciais para tipos e grupos
- **Management Commands:** comandos para criação de dados iniciais
- **Testes:** casos de teste para fluxo de comunicação
- **Nomenclatura:** 100% em português

### 7. [CHECKLIST - APP EXTERNA](7 - CHECKLIST_EXTERNA.md) ✅ **EXPANDIDO ULTRA-DETALHADO**
**Objetivo:** Portal público para submissão de documentos externos e comunicação com entidades externas.

**Conteúdo Expandido:**
- **Modelos ultra-detalhados:** SubmissaoExterna, TipoSubmissao, AnexoExterno, StatusSubmissao
- **Portal público:** formulários, validações, captcha
- **Integração com sistema interno:** conversão automática para DocumentoEntrada
- **Tracking completo:** histórico de status, notificações por email
- **Segurança:** proteção contra spam, validação de ficheiros, rate limiting
- **Views:** 8 views para portal público e gestão interna
- **Forms:** 4 forms com validações e captcha
- **Templates:** 6 templates públicos com pontos de parada para layouts Bootstrap 5
- **URLs:** padrões públicos e internos
- **Admin:** configuração para gestão de submissões
- **Signals:** conversão automática e notificações
- **Relatórios:** estatísticas do portal
- **Nomenclatura:** 100% em português

### 8. [CHECKLIST - APP RELATORIOS](8 - CHECKLIST_RELATORIOS.md) ✅ **EXPANDIDO ULTRA-DETALHADO**
**Objetivo:** Relatórios e estatísticas com dashboards personalizados.

**Conteúdo Expandido:**
- **Modelos ultra-detalhados:** ConfiguracaoRelatorio, TipoRelatorio, ExecucaoRelatorio, Dashboard, WidgetDashboard
- **Tipos de relatórios:** 8+ tipos específicos com queries detalhadas
- **Dashboards personalizados:** widgets configuráveis, layouts flexíveis
- **Exportação:** PDF, Excel, CSV com formatação específica
- **Views:** 12 views para relatórios, dashboards e exportação
- **Forms:** 6 forms para configuração de relatórios e dashboards
- **Templates:** 9 templates com pontos de parada para layouts Bootstrap 5
- **URLs:** padrões específicos para relatórios e dashboards
- **Admin:** configuração completa com filtros
- **Bibliotecas:** Chart.js, ReportLab, openpyxl
- **Testes:** casos de teste para geração de relatórios
- **Nomenclatura:** 100% em português

### 9. [CHECKLIST - APP ASSINATURA_DIGITAL](9 - CHECKLIST_ASSINATURA_DIGITAL.md) ✅ **EXPANDIDO ULTRA-DETALHADO**
**Objetivo:** Sistema simples de assinatura digital com mouse/pad para PDFs.

**Conteúdo Expandido:**
- **Modelos ultra-detalhados:** AssinaturaDocumento, TipoAssinatura, AssinaturaUtilizador
- **Canvas HTML5:** desenho com mouse/touch, conversão para imagem
- **Posicionamento em PDF:** visualização, clique para posicionar, redimensionamento
- **Processamento de PDF:** inserção de assinatura, manutenção de qualidade
- **Views:** 8 views para canvas, PDF e gestão de assinaturas
- **Forms:** 4 forms para assinatura e configuração
- **Templates:** 6 templates com pontos de parada para layouts Bootstrap 5
- **URLs:** padrões específicos para assinatura
- **Bibliotecas JavaScript:** Signature Pad, PDF.js, Canvas-to-blob
- **Bibliotecas Python:** PyPDF2, Pillow
- **Testes:** casos de teste para processo de assinatura
- **Nomenclatura:** 100% em português

### 10. [CHECKLIST - INTEGRAÇÃO FINAL E TESTES](10 - CHECKLIST_INTEGRACAO_FINAL.md) ✅ **COMPLETO**
**Objetivo:** Integração de todas as apps, testes finais e validação do sistema.

**Conteúdo:**
- Integração entre apps
- Testes completos
- Configuração de produção
- Documentação final
- Deploy e lançamento

## 🚀 Como Usar os Checklists

### 1. Ordem de Execução
Execute os checklists na ordem numérica:
1. **Instalação** - Configure o ambiente primeiro
2. **Core** - Implemente a base do sistema
3. **Users** - Configure utilizadores e permissões
4. **Entrada** - Implemente o fluxo de documentos de entrada
5. **Saída** - Implemente o fluxo de documentos de saída
6. **Interna** - Implemente comunicação interna
7. **Externa** - Implemente portal público
8. **Relatórios** - Implemente dashboards e relatórios
9. **Assinatura Digital** - Prepare para futuro
10. **Integração Final** - Teste e integre tudo

### 2. Marcação de Progresso
- [ ] Marque cada item como concluído quando terminado
- [ ] Use ✅ para itens concluídos
- [ ] Use ❌ para itens com problemas
- [ ] Use ⏳ para itens em progresso

### 3. Validação
- Complete cada checklist antes de passar ao seguinte
- Execute os testes de validação de cada app
- Verifique se não há conflitos entre apps
- Mantenha a documentação atualizada

## 🏢 Estrutura Hierárquica e Organizacional

### Hierarquia de Utilizadores
O sistema implementa uma hierarquia clara de autoridade:

1. **PCA (Presidente do Conselho de Administração)**
   - Máxima autoridade organizacional
   - Identificado por `is_pca=True` no modelo User
   - Tem sector "Gabinete do PCA" ou "Presidência"
   - Permissões: ver todos documentos, aprovar documentos de saída

2. **Secretaria**
   - Recebe e distribui documentos de entrada
   - Primeiro ponto de contacto para documentos externos
   - Encaminha para PCA ou sectores conforme necessário

3. **Chefe de Sector**
   - Gere um sector específico e sua equipa
   - Definido no campo `chefe` do modelo Sector
   - Aprova documentos de saída do seu sector
   - Gere colaboradores do sector

4. **Colaborador**
   - Trabalha num sector específico
   - Processa documentos atribuídos ao sector
   - Reporta ao chefe de sector

5. **Utilizador Externo**
   - Submete documentos via portal público
   - Acesso limitado apenas para submissão

### Estrutura de Sectores
- Cada Sector tem um `chefe` (obrigatório) e `chefe_substituto` (opcional)
- Sectores especiais recomendados:
  - **Gabinete do PCA/Presidência**: Sector do PCA
  - **Secretaria**: Sector de receção e distribuição
  - Outros sectores organizacionais conforme necessário

### Fluxo de Documentos de Entrada
O sistema implementa um fluxo rigoroso de documentos:

1. **Entrada** → Documento entra (Secretaria/Portal/Quiosque)
2. **Encaminhamento Automático** → Vai sempre para o PCA
3. **PCA Decide** → Tratar, Encaminhar para Sector, ou Arquivar
4. **Sector Processa** → Chefe pode tratar ou distribuir a colaboradores
5. **Conclusão** → PCA é sempre notificado quando sector conclui
6. **Arquivamento** → PCA arquiva definitivamente

**Regras de Visibilidade:**
- PCA e Secretaria vêem tudo
- Chefes vêem apenas documentos do seu sector
- Colaboradores vêem apenas documentos atribuídos a eles
- Documentos com PCA são privados (exceto Secretaria)

## 🔧 Dicas de Desenvolvimento

### 1. Modularidade
- Mantenha cada app independente
- Use signals para comunicação entre apps
- Evite dependências circulares
- Documente as interfaces entre apps

### 2. Segurança
- Implemente permissões em cada app
- Valide todos os inputs
- Use HTTPS em produção
- Mantenha dependências atualizadas

### 3. Performance
- Otimize queries da base de dados
- Use cache quando apropriado
- Implemente paginação
- Teste com dados reais

### 4. Manutenibilidade
- Escreva código limpo e documentado
- Use nomes descritivos
- Implemente testes abrangentes
- Mantenha logs detalhados

## 📞 Suporte

Se encontrar problemas durante o desenvolvimento:
1. Verifique se seguiu o checklist corretamente
2. Consulte a documentação do Django
3. Verifique os logs de erro
4. Teste em ambiente isolado
5. Documente o problema para referência futura

## 📊 Resumo das Expansões Realizadas

### ✅ Status Geral dos Checklists
**TODOS os 9 checklists principais foram expandidos com detalhes ultra-específicos:**

| Checklist | Status | Modelos | Views | Forms | Templates | URLs | Testes |
|-----------|--------|---------|-------|-------|-----------|------|--------|
| CORE | ✅ | 6 | 6 | 2 | 4 | 6 | ✅ |
| USERS | ✅ | 3 | 12 | 8 | 7 | 12 | ✅ |
| ENTRADA | ✅ | 4 | 20 | 5 | 8 | 20 | ✅ |
| SAIDA | ✅ | 5 | 15 | 8 | 12 | 15 | ✅ |
| INTERNA | ✅ | 5 | 15 | 9 | 15 | 15 | ✅ |
| EXTERNA | ✅ | 4 | 8 | 4 | 6 | 8 | ✅ |
| RELATORIOS | ✅ | 5 | 12 | 6 | 9 | 12 | ✅ |
| ASSINATURA | ✅ | 3 | 8 | 4 | 6 | 8 | ✅ |

### 🎯 Características das Expansões

#### 1. **Nomenclatura 100% Portuguesa**
- Todos os modelos, views, forms, templates e URLs em português
- Métodos e campos com nomes descritivos em português
- Facilita compreensão e manutenção por desenvolvedores portugueses

#### 2. **Modelos Ultra-Detalhados**
- **Campos específicos:** cada modelo tem campos detalhados para funcionalidade completa
- **Métodos personalizados:** métodos específicos para cada funcionalidade
- **Relacionamentos:** ForeignKeys, ManyToMany, GenericForeignKeys bem definidos
- **Validações:** campos obrigatórios, choices, constraints específicos

#### 3. **Views Completas**
- **Métodos específicos:** get(), post(), get_context_data(), etc.
- **Decorators:** @login_required, @permission_required, @method_decorator
- **Context data:** dados específicos para cada template
- **Permissões:** verificação de acesso baseada em roles

#### 4. **Forms Detalhados**
- **Campos específicos:** widgets, validações, help_text
- **Métodos de validação:** clean(), clean_field() específicos
- **Widgets personalizados:** DateInput, Select, CheckboxSelectMultiple
- **Validações:** campos obrigatórios, formatos, dependências

#### 5. **Templates com Pontos de Parada**
- **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** em cada template
- **Bootstrap 5:** estrutura responsiva especificada
- **JavaScript:** funcionalidades específicas detalhadas
- **Componentes:** cards, tabelas, formulários, paginação

#### 6. **URLs Específicas**
- **Padrões em português:** nomes descritivos e claros
- **Parâmetros:** pk, slug, filtros específicos
- **Namespaces:** organização por app
- **Inclui:** URLs para APIs AJAX quando necessário

#### 7. **Admin Configurado**
- **List display:** campos relevantes para cada modelo
- **Filters:** filtros úteis para gestão
- **Search fields:** campos pesquisáveis
- **Fieldsets:** organização lógica dos campos
- **Actions:** ações personalizadas quando necessário

#### 8. **Signals Detalhados**
- **post_save:** atualizações automáticas
- **pre_save:** validações e preparação
- **post_delete:** limpeza e auditoria
- **user_logged_in/out:** auditoria de acesso

#### 9. **Testes Completos**
- **TestCase classes:** para cada modelo e view
- **Métodos específicos:** test_* para cada funcionalidade
- **Fixtures:** dados de teste quando necessário
- **Cobertura:** modelos, views, forms, signals

#### 10. **Fixtures e Management Commands**
- **Dados iniciais:** tipos de documento, sectores, configurações
- **Commands:** criar_tipos_*, criar_dados_iniciais
- **JSON fixtures:** estrutura de dados inicial
- **Comandos personalizados:** para setup e manutenção

### 🚀 Próximos Passos

1. **Implementação por Checklist:** Seguir ordem numérica (1→10)
2. **Layouts por Template:** Fornecer imagem de layout para cada template
3. **Desenvolvimento Incremental:** Implementar um checklist completo antes do próximo
4. **Testes Contínuos:** Validar cada funcionalidade implementada
5. **Integração:** Conectar apps conforme especificado no CHECKLIST_INTEGRACAO_FINAL

### 📈 Estatísticas Finais

- **Total de Modelos:** 35+ modelos ultra-detalhados
- **Total de Views:** 96+ views com métodos específicos
- **Total de Forms:** 46+ forms com validações
- **Total de Templates:** 77+ templates com pontos de parada
- **Total de URLs:** 96+ padrões específicos
- **Total de Testes:** 50+ classes de teste
- **Nomenclatura:** 100% em português
- **Bootstrap:** 100% responsivo
- **Cobertura:** Completa para todas as funcionalidades

---

**Nota:** Estes checklists foram expandidos com detalhes ultra-específicos para garantir desenvolvimento sem ambiguidades. Cada template aguarda layout específico antes da implementação. Siga rigorosamente para evitar desvios e garantir qualidade.
