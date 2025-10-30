# 👥 UTILIZADORES DE TESTE - FTC EXPEDIENTES

## 📋 Credenciais de Acesso ao Sistema

Este documento contém as credenciais de todos os utilizadores de teste criados no sistema.
**Guarde este documento em local seguro!**

---

## 🔐 UTILIZADORES POR TIPO

### 1️⃣ **SUPERUSER / ADMINISTRADOR DO SISTEMA**

| Campo | Valor |
|-------|-------|
| **Nome Completo** | Administrador Sistema |
| **Tipo** | Superuser / Admin |
| **Username** | `admin` |
| **Email** | admin@ftc.co.mz |
| **Password** | `Admin@123` |
| **Permissões** | Acesso total ao sistema |
| **Dashboard** | `/dashboard/admin/` |

**Descrição**: Administrador com acesso total ao sistema, incluindo Django Admin.

---

### 2️⃣ **PCA - PRESIDENTE DO CONSELHO DE ADMINISTRAÇÃO**

| Campo | Valor |
|-------|-------|
| **Nome Completo** | José Macamo |
| **Tipo** | PCA |
| **Username** | `pca.ftc` |
| **Email** | pca@ftc.co.mz |
| **Password** | `PCA@2025` |
| **Sector** | Gabinete do PCA |
| **Cargo** | Presidente |
| **Dashboard** | `/dashboard/pca/` |

**Descrição**: Presidente com visão executiva de todos os sectores e documentos importantes.

---

### 3️⃣ **SECRETARIA GERAL**

| Campo | Valor |
|-------|-------|
| **Nome Completo** | Maria Simões |
| **Tipo** | Secretaria |
| **Username** | `secretaria.geral` |
| **Email** | secretaria@ftc.co.mz |
| **Password** | `Secret@2025` |
| **Sector** | Secretaria Geral |
| **Cargo** | Secretária Geral |
| **Dashboard** | `/dashboard/secretaria/` |

**Descrição**: Responsável pela gestão de documentos de entrada e saída.

---

### 4️⃣ **CHEFE DE RECURSOS HUMANOS**

| Campo | Valor |
|-------|-------|
| **Nome Completo** | António Nguenha |
| **Tipo** | Chefe de Sector |
| **Username** | `chefe.rh` |
| **Email** | chefe.rh@ftc.co.mz |
| **Password** | `ChefeRH@2025` |
| **Sector** | Recursos Humanos |
| **Cargo** | Chefe RH |
| **Dashboard** | `/dashboard/chefe/` |

**Descrição**: Chefe do sector de Recursos Humanos, gere equipa e documentos do sector.

---

### 5️⃣ **CHEFE DE TECNOLOGIAS DE INFORMAÇÃO**

| Campo | Valor |
|-------|-------|
| **Nome Completo** | Carlos Sitoe |
| **Tipo** | Chefe de Sector |
| **Username** | `chefe.ti` |
| **Email** | chefe.ti@ftc.co.mz |
| **Password** | `ChefeTI@2025` |
| **Sector** | Tecnologias de Informação |
| **Cargo** | Chefe TI |
| **Dashboard** | `/dashboard/chefe/` |

**Descrição**: Chefe do sector de TI, gere equipa técnica e infraestrutura.

---

### 6️⃣ **COLABORADOR DE TI**

| Campo | Valor |
|-------|-------|
| **Nome Completo** | Pedro Macie |
| **Tipo** | Colaborador |
| **Username** | `colaborador.ti` |
| **Email** | pedro.ti@ftc.co.mz |
| **Password** | `Colab@2025` |
| **Sector** | Tecnologias de Informação |
| **Cargo** | Técnico |
| **Dashboard** | `/dashboard/colaborador/` |

**Descrição**: Colaborador do sector de TI, processa documentos e tarefas atribuídas.

---

### 7️⃣ **COLABORADOR DE RH**

| Campo | Valor |
|-------|-------|
| **Nome Completo** | Ana Bila |
| **Tipo** | Colaborador |
| **Username** | `colaborador.rh` |
| **Email** | ana.rh@ftc.co.mz |
| **Password** | `Colab@2025` |
| **Sector** | Recursos Humanos |
| **Cargo** | Assistente |
| **Dashboard** | `/dashboard/colaborador/` |

**Descrição**: Colaboradora do sector de RH, auxilia nas tarefas administrativas.

---

### 8️⃣ **UTILIZADOR EXTERNO**

| Campo | Valor |
|-------|-------|
| **Nome Completo** | Carlos Muianga |
| **Tipo** | Externo |
| **Username** | `utente.externo` |
| **Email** | carlos.externo@gmail.com |
| **Password** | `Externo@2025` |
| **Sector** | Nenhum |
| **Cargo** | Utente |
| **Dashboard** | `/dashboard/externo/` |

**Descrição**: Utilizador externo, pode submeter documentos através do portal público.

---

## 📊 RESUMO ESTATÍSTICO

| Estatística | Valor |
|-------------|-------|
| **Total de Utilizadores** | 8 |
| **Total de Sectores** | 4 |
| **Administradores** | 1 |
| **PCA** | 1 |
| **Secretaria** | 1 |
| **Chefes de Sector** | 2 |
| **Colaboradores** | 2 |
| **Utilizadores Externos** | 1 |

---

## 🏢 SECTORES CRIADOS

1. **Gabinete do PCA**
   - Chefe: José Macamo (PCA)
   - Descrição: Gabinete do Presidente do Conselho de Administração

2. **Secretaria Geral**
   - Chefe: Maria Simões (Secretaria)
   - Descrição: Secretaria Geral da FTC

3. **Recursos Humanos**
   - Chefe: António Nguenha
   - Colaboradores: Ana Bila
   - Descrição: Departamento de Recursos Humanos

4. **Tecnologias de Informação**
   - Chefe: Carlos Sitoe
   - Colaboradores: Pedro Macie
   - Descrição: Departamento de TI

---

## 🚀 COMO TESTAR

### 1. Aceder ao Sistema
```
URL: http://localhost:8000
```

### 2. Fazer Login
- Usar o **username** ou **email** de qualquer utilizador acima
- Inserir a **password** correspondente

### 3. Verificar Dashboard
- Cada tipo de utilizador será redirecionado para seu dashboard específico
- O dashboard mostra informações relevantes ao papel do utilizador

### 4. Testar Funcionalidades por Tipo

#### Como **Administrador** (`admin`):
- ✅ Ver todos os utilizadores
- ✅ Criar/editar/apagar utilizadores
- ✅ Gerir sectores
- ✅ Aceder ao Django Admin (`/admin/`)

#### Como **PCA** (`pca.ftc`):
- ✅ Visão executiva de todos sectores
- ✅ Aprovar documentos importantes
- ✅ Ver relatórios executivos

#### Como **Secretaria** (`secretaria.geral`):
- ✅ Registar documentos de entrada
- ✅ Registar documentos de saída
- ✅ Gerir correspondências

#### Como **Chefe** (`chefe.rh` ou `chefe.ti`):
- ✅ Ver documentos do seu sector
- ✅ Gerir equipa do sector
- ✅ Distribuir tarefas

#### Como **Colaborador** (`colaborador.ti` ou `colaborador.rh`):
- ✅ Ver documentos atribuídos
- ✅ Processar tarefas pendentes
- ✅ Consultar informações do sector

#### Como **Externo** (`utente.externo`):
- ✅ Submeter documentos
- ✅ Acompanhar status de submissões
- ✅ Ver histórico de documentos

---

## 🔒 SEGURANÇA

⚠️ **IMPORTANTE**: 
- Estas credenciais são para **AMBIENTE DE TESTE** apenas
- **NÃO** use estas passwords em ambiente de produção
- Todas as passwords devem ser alteradas antes do deployment
- Em produção, implemente política de passwords fortes

---

## 📝 NOTAS ADICIONAIS

1. **Hierarquia de Permissões**:
   ```
   Superuser (7) > Admin (6) > PCA (5) > Secretaria (4) > Chefe (3) > Colaborador (2) > Externo (1)
   ```

2. **Acesso ao Django Admin**:
   - Apenas **Superuser** tem acesso por defeito
   - URL: `http://localhost:8000/admin/`

3. **Redefinir Password**:
   ```bash
   python manage.py changepassword [username]
   ```

4. **Criar Mais Utilizadores**:
   - Via Django Admin (como superuser)
   - Via interface de gestão (como admin)
   - Via comando: `python manage.py createsuperuser`

---

## 📞 CONTACTO

**Equipa de Desenvolvimento FTC**
- Sistema: FTC Expedientes
- Versão: 1.0.0
- Data: Janeiro 2025

---

**Última Atualização**: 19/10/2025

