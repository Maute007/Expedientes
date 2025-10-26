# 🔐 CREDENCIAIS COMPLETAS - ACESSO AO SISTEMA

## Tabela de Acesso com Emails

| Tipo | Username | Email | Password | Função |
|------|----------|-------|----------|--------|
| **Admin** | `admin` | admin@ftc.co.mz | `Admin@123` | Administração total |
| **PCA** | `pca.ftc` | pca@ftc.co.mz | `PCA@2025` | Visão executiva |
| **Secretaria** | `secretaria.geral` | secretaria@ftc.co.mz | `Secret@2025` | Documentos entrada/saída |
| **Chefe RH** | `chefe.rh` | chefe.rh@ftc.co.mz | `ChefeRH@2025` | Gestão de equipa RH |
| **Chefe TI** | `chefe.ti` | chefe.ti@ftc.co.mz | `ChefeTI@2025` | Gestão de equipa TI |
| **Colab TI** | `colaborador.ti` | pedro.ti@ftc.co.mz | `Colab@2025` | Tarefas de TI |
| **Colab RH** | `colaborador.rh` | ana.rh@ftc.co.mz | `Colab@2025` | Tarefas de RH |
| **Externo** | `utente.externo` | carlos.externo@gmail.com | `Externo@2025` | Portal público |



## 🚀 Acesso Rápido

**URL do Sistema**: `http://localhost:8000`

**Django Admin**: `http://localhost:8000/admin/` (apenas superuser)

---

## 📱 Teste por Perfil

### Para testar como **ADMIN**:
```
Email: admin@ftc.co.mz
Password: Admin@123
Dashboard: Visão geral do sistema
```

### Para testar como **PCA**:
```
Email: pca@ftc.co.mz
Password: PCA@2025
Dashboard: Visão executiva
```

### Para testar como **SECRETARIA**:
```
Email: secretaria@ftc.co.mz
Password: Secret@2025
Dashboard: Gestão de documentos
```

### Para testar como **CHEFE RH**:
```
Email: chefe.rh@ftc.co.mz
Password: ChefeRH@2025
Dashboard: Gestão de sector
```

### Para testar como **CHEFE TI**:
```
Email: chefe.ti@ftc.co.mz
Password: ChefeTI@2025
Dashboard: Gestão de sector
```

### Para testar como **COLABORADOR TI**:
```
Email: pedro.ti@ftc.co.mz
Password: Colab@2025
Dashboard: Tarefas pessoais
```

### Para testar como **COLABORADOR RH**:
```
Email: ana.rh@ftc.co.mz
Password: Colab@2025
Dashboard: Tarefas pessoais
```

### Para testar como **EXTERNO**:
```
Email: carlos.externo@gmail.com
Password: Externo@2025
Dashboard: Portal de submissões
```

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
   - Chefe: José Macamo (pca@ftc.co.mz)
   - Descrição: Gabinete do Presidente do Conselho de Administração

2. **Secretaria Geral**
   - Chefe: Maria Simões (secretaria@ftc.co.mz)
   - Descrição: Secretaria Geral da FTC

3. **Recursos Humanos**
   - Chefe: António Nguenha (chefe.rh@ftc.co.mz)
   - Colaboradores: Ana Bila (ana.rh@ftc.co.mz)
   - Descrição: Departamento de Recursos Humanos

4. **Tecnologias de Informação**
   - Chefe: Carlos Sitoe (chefe.ti@ftc.co.mz)
   - Colaboradores: Pedro Macie (pedro.ti@ftc.co.mz)
   - Descrição: Departamento de TI

---

## 🔒 SEGURANÇA

⚠️ **IMPORTANTE**: 
- Estas credenciais são para **AMBIENTE DE TESTE** apenas
- **NÃO** use estas passwords em ambiente de produção
- Todas as passwords devem ser alteradas antes do deployment
- Em produção, implemente política de passwords fortes

---

## 📝 NOTAS ADICIONAIS

1. **Login**: Use sempre o **EMAIL** para fazer login
2. **Username**: Campo não utilizado para login (apenas para compatibilidade)
3. **Hierarquia de Permissões**:
   ```
   Superuser (7) > Admin (6) > PCA (5) > Secretaria (4) > Chefe (3) > Colaborador (2) > Externo (1)
   ```

4. **Acesso ao Django Admin**:
   - Apenas **Superuser** tem acesso por defeito
   - URL: `http://localhost:8000/admin/`

5. **Redefinir Password**:
   ```bash
   python manage.py changepassword [email]
   ```

---

**Última Atualização**: 19/10/2025
