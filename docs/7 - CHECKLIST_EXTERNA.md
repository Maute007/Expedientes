# 📋 7. CHECKLIST - APP EXTERNA

## 🎯 Objetivo
Gestão de portal público para submissão de documentos externos e comunicação com entidades externas.

## 🌐 Portal Público

### 1. Portal de Submissão
- [ ] Criar modelo SubmissaoExterna
  - [ ] Campos: nome_remetente, email, telefone, assunto, mensagem
  - [ ] Campos: tipo_documento, anexos, data_submissao, status
  - [ ] Campos: numero_protocolo, ip_address, user_agent
  - [ ] Métodos: __str__, generate_protocol_number, get_status_display

### 2. Tipos de Submissão
- [ ] Criar modelo TipoSubmissao
  - [ ] Campos: nome, descrição, template_form, campos_obrigatorios
  - [ ] Campos: prazo_resposta, sector_destino, ativo
  - [ ] Métodos: __str__, get_form_fields

### 3. Anexos Externos
- [ ] Criar modelo AnexoExterno
  - [ ] Campos: submissao, ficheiro, nome_original, tamanho, tipo
  - [ ] Campos: data_upload, verificado, virus_scan
  - [ ] Métodos: __str__, get_tamanho_display, is_safe

## 🔗 Integração com Sistema Interno

### 1. Conversão para Documento Interno
- [ ] Criar processo de conversão
- [ ] Integrar com app entrada
- [ ] Notificar secretaria
- [ ] Gerar número de expediente

### 2. Tracking de Status
- [ ] Criar modelo StatusSubmissao
  - [ ] Campos: submissao, status, data_mudanca, observacoes
  - [ ] Métodos: __str__, get_tempo_processamento

## 📝 Forms Públicos

### 1. Forms de Submissão
- [ ] Criar SubmissaoExternaForm
- [ ] Criar AnexoExternoForm
- [ ] Implementar captcha
- [ ] Validação de ficheiros

### 2. Forms de Consulta
- [ ] Criar ConsultaStatusForm
- [ ] Form para consulta por protocolo
- [ ] Form para consulta por email

## 🎯 Views Públicas

### 1. Views de Submissão
- [ ] Criar PortalSubmissaoView
- [ ] Criar SubmissaoCreateView
- [ ] Criar SubmissaoSuccessView
- [ ] Implementar rate limiting

### 2. Views de Consulta
- [ ] Criar ConsultaStatusView
- [ ] Criar StatusDetailView
- [ ] Implementar cache de consultas

## 🎨 Templates Públicos

### 1. Templates do Portal
- [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para templates do portal público
- [ ] Criar portal_base.html
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para portal_base.html
  - [ ] Template base para portal público
  - [ ] Bootstrap 5 responsivo
  - [ ] Header com logo e navegação
  - [ ] Footer com informações de contacto
  - [ ] CSS específico para portal público
- [ ] Criar submissao_form.html
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para submissao_form.html
  - [ ] Formulário de submissão de documentos
  - [ ] Campos: nome, email, telefone, assunto, mensagem
  - [ ] Upload de anexos com drag & drop
  - [ ] Captcha de verificação
  - [ ] Validação JavaScript
- [ ] Criar submissao_success.html
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para submissao_success.html
  - [ ] Página de confirmação de submissão
  - [ ] Número de protocolo gerado
  - [ ] Instruções para acompanhamento
  - [ ] Botão para nova submissão
- [ ] Criar consulta_status.html
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para consulta_status.html
  - [ ] Formulário de consulta por protocolo
  - [ ] Exibição do status atual
  - [ ] Histórico de movimentações
  - [ ] Informações de contacto

### 2. Templates de Email
- [ ] Criar email_confirmacao.html
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para email_confirmacao.html
  - [ ] Template de email de confirmação
  - [ ] Design responsivo para email
  - [ ] Informações da submissão
  - [ ] Link para consulta de status
- [ ] Criar email_status_update.html
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para email_status_update.html
  - [ ] Template de email de atualização de status
  - [ ] Design responsivo para email
  - [ ] Novo status do documento
  - [ ] Observações adicionais
- [ ] Implementar templates responsivos

## 🔗 URLs Públicas

### 1. URLs do Portal
- [ ] Configurar URLs públicas
- [ ] Configurar URLs de consulta
- [ ] Implementar URLs amigáveis

## 🛠️ Admin

### 1. Admin para Gestão
- [ ] Configurar SubmissaoExternaAdmin
- [ ] Configurar TipoSubmissaoAdmin
- [ ] Configurar AnexoExternoAdmin
- [ ] Implementar filtros e pesquisa

## 🔐 Segurança

### 1. Proteção contra Spam
- [ ] Implementar captcha
- [ ] Implementar rate limiting
- [ ] Validar ficheiros perigosos
- [ ] Implementar blacklist de IPs

### 2. Validação de Dados
- [ ] Sanitizar inputs
- [ ] Validar emails
- [ ] Verificar tamanho de ficheiros
- [ ] Implementar honeypot

## 📊 Relatórios

### 1. Estatísticas do Portal
- [ ] Submissões por dia/mês
- [ ] Tipos de submissão mais comuns
- [ ] Tempo médio de resposta
- [ ] Taxa de spam/válidas

## 🧪 Testes

### 1. Testes de Funcionalidade
- [ ] Testar submissão de formulários
- [ ] Testar upload de ficheiros
- [ ] Testar consulta de status
- [ ] Testar segurança

## 📋 Validação Final
- [ ] Portal público funcionando
- [ ] Submissões sendo processadas
- [ ] Integração com sistema interno
- [ ] Notificações enviadas
- [ ] Segurança implementada
- [ ] Testes passando

---

**Nota:** Esta app gere toda a interação com o público externo através do portal web.
