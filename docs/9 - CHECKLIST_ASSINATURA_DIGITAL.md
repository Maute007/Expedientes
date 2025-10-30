# 📋 9. CHECKLIST - APP ASSINATURA_DIGITAL

## 🎯 Objetivo
Sistema simples de assinatura digital com mouse/pad para PDFs no processo documental.

## ✍️ Funcionalidades de Assinatura

### 1. Modelos de Assinatura
- [ ] Criar modelo AssinaturaDocumento
  - [ ] Campos: documento, utilizador, data_assinatura, tipo_assinatura
  - [ ] Campos: assinatura_imagem, posicao_x, posicao_y, pagina
  - [ ] Campos: ip_address, user_agent, observacoes, ativo
  - [ ] Métodos: __str__, get_tipo_display, save_signature

### 2. Tipos de Assinatura
- [ ] Criar modelo TipoAssinatura
  - [ ] Campos: nome, descrição, cor, largura, altura
  - [ ] Tipos: Mouse, Pad Digital, Upload de Imagem
  - [ ] Métodos: __str__, get_dimensions

### 3. Assinatura de Utilizador
- [ ] Criar modelo AssinaturaUtilizador
  - [ ] Campos: utilizador, assinatura_default, data_criacao
  - [ ] Campos: assinatura_imagem, ativo
  - [ ] Métodos: __str__, get_signature_url

## 🖊️ Interface de Assinatura

### 1. Canvas de Assinatura
- [ ] Implementar HTML5 Canvas para desenhar
- [ ] Suporte para mouse e touch
- [ ] Botões: Limpar, Salvar, Cancelar
- [ ] Preview da assinatura em tempo real

### 2. Posicionamento no PDF
- [ ] Visualizar PDF no browser
- [ ] Clicar para posicionar assinatura
- [ ] Redimensionar área de assinatura
- [ ] Preview antes de confirmar

### 3. JavaScript para Assinatura
- [ ] Biblioteca para canvas de assinatura
- [ ] Captura de eventos de mouse/touch
- [ ] Conversão para base64/PNG
- [ ] Validação de assinatura válida

## 📝 Forms de Assinatura

### 1. Forms de Canvas
- [ ] Criar AssinaturaCanvasForm
- [ ] Form para salvar assinatura padrão
- [ ] Validação de imagem de assinatura

### 2. Forms de Posicionamento
- [ ] Criar PosicionamentoAssinaturaForm
- [ ] Form para coordenadas X, Y
- [ ] Form para seleção de página

## 🎯 Views de Assinatura

### 1. Views de Canvas
- [ ] Criar AssinaturaCanvasView
- [ ] Criar AssinaturaSaveView
- [ ] Criar AssinaturaDefaultView (para utilizador)

### 2. Views de Documento
- [ ] Criar DocumentoAssinatureView
- [ ] Criar PDFViewerView
- [ ] Criar ConfirmarAssinaturaView

### 3. Views de Gestão
- [ ] Criar MinhasAssinaturasView
- [ ] Criar HistoricoAssinaturasView

## 🎨 Templates de Assinatura

### 1. Templates de Canvas
- [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para templates de assinatura
- [ ] Criar assinatura_canvas.html
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para assinatura_canvas.html
  - [ ] Canvas HTML5 para desenhar assinatura
  - [ ] Botões: Limpar, Salvar, Cancelar
  - [ ] Preview em tempo real
  - [ ] Suporte para mouse e touch
- [ ] Criar assinatura_default.html
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para assinatura_default.html
  - [ ] Gestão de assinatura padrão do utilizador
  - [ ] Upload de imagem de assinatura
  - [ ] Preview da assinatura atual
  - [ ] Botões: Salvar, Remover, Usar como Padrão
- [ ] Implementar interface responsiva

### 2. Templates de PDF
- [ ] Criar pdf_viewer.html
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para pdf_viewer.html
  - [ ] Visualizador de PDF integrado
  - [ ] Controles de navegação
  - [ ] Zoom e rotação
  - [ ] Botão "Assinar Documento"
- [ ] Criar posicionar_assinatura.html
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para posicionar_assinatura.html
  - [ ] Interface para posicionar assinatura
  - [ ] Área clicável no PDF
  - [ ] Redimensionamento da área
  - [ ] Preview da posição
- [ ] Criar confirmar_assinatura.html
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para confirmar_assinatura.html
  - [ ] Confirmação final da assinatura
  - [ ] Preview do documento assinado
  - [ ] Campos: observações, motivo
  - [ ] Botões: Confirmar, Cancelar, Revisar

### 3. Templates de Gestão
- [ ] Criar minhas_assinaturas.html
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para minhas_assinaturas.html
  - [ ] Lista de assinaturas do utilizador
  - [ ] Filtros por data, documento, tipo
  - [ ] Ações: visualizar, editar, remover
  - [ ] Estatísticas de assinaturas
- [ ] Criar historico_assinaturas.html
  - [ ] **🛑 PONTO DE PARADA - AGUARDAR LAYOUT** - Aguardar imagem de layout para historico_assinaturas.html
  - [ ] Histórico completo de assinaturas
  - [ ] Timeline de assinaturas
  - [ ] Detalhes de cada assinatura
  - [ ] Exportação do histórico

## 🔗 URLs de Assinatura

### 1. URLs de Canvas
- [ ] Configurar URLs de criação
- [ ] Configurar URLs de gestão
- [ ] Configurar APIs AJAX

### 2. URLs de Documento
- [ ] Configurar URLs de visualização
- [ ] Configurar URLs de assinatura
- [ ] Configurar URLs de confirmação

## 📚 Bibliotecas JavaScript

### 1. Canvas de Assinatura
- [ ] Signature Pad library
- [ ] PDF.js para visualização
- [ ] Canvas-to-blob para conversão

### 2. Interação
- [ ] jQuery para AJAX
- [ ] Bootstrap para UI
- [ ] SweetAlert para confirmações

## 🔧 Processamento de PDF

### 1. Inserção de Assinatura
- [ ] Biblioteca PyPDF2/PDFtk
- [ ] Inserir imagem no PDF
- [ ] Manter qualidade original
- [ ] Salvar PDF assinado

### 2. Validação
- [ ] Verificar integridade do PDF
- [ ] Verificar posição válida
- [ ] Verificar permissões do utilizador

## 🛠️ Admin de Assinatura

### 1. Admin Customizado
- [ ] Configurar AssinaturaDocumentoAdmin
- [ ] Configurar TipoAssinaturaAdmin
- [ ] Configurar AssinaturaUtilizadorAdmin
- [ ] Visualizar assinaturas

## 🔐 Segurança

### 1. Validações
- [ ] Verificar permissões de assinatura
- [ ] Validar tipos de ficheiro
- [ ] Verificar tamanho de assinatura
- [ ] Prevenir assinaturas duplicadas

### 2. Auditoria
- [ ] Log de todas as assinaturas
- [ ] Rastreamento de IP/User Agent
- [ ] Histórico de modificações

## 🧪 Testes

### 1. Testes de Funcionalidade
- [ ] Testar criação de assinatura
- [ ] Testar inserção em PDF
- [ ] Testar diferentes dispositivos

### 2. Testes de Interface
- [ ] Testar canvas em diferentes browsers
- [ ] Testar responsividade
- [ ] Testar touch em tablets/móveis

## 📋 Validação Final
- [ ] Canvas de assinatura funcionando
- [ ] Assinaturas inseridas em PDFs
- [ ] Interface responsiva
- [ ] Histórico de assinaturas
- [ ] Segurança implementada
- [ ] Testes passando

---

**Nota:** Sistema simples mas funcional para assinatura digital básica com mouse/pad de assinatura.