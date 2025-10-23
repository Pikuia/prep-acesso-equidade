# 🛡️ Guia de Proteção dos Dados - Questionário PrEP

## ⚠️ Problema Identificado
As respostas do questionário estavam sendo perdidas, reduzindo de 35+ para apenas 6 respostas.

## ✅ Soluções Implementadas

### 1. Sistema de Backup Automático
- **Backup automático**: Toda vez que uma resposta é enviada, um backup é criado automaticamente
- **Múltiplos formatos**: Os dados são salvos em SQLite, CSV e JSON
- **Backup de emergência**: Se o banco principal falhar, as respostas são salvas em CSV de emergência

### 2. Estrutura de Backups
```
backups/                          # Backups do banco SQLite
├── pesquisa_prep_backup_YYYYMMDD_HHMMSS.db
├── backup_log.json               # Log de todos os backups
csv_backups/                      # Backups em CSV e JSON
├── respostas_backup_YYYYMMDD_HHMMSS.csv
├── respostas_backup_YYYYMMDD_HHMMSS.json
respostas_emergencia.csv          # Backup de emergência (se existir)
```

### 3. Página de Administração
- Acesse "🔧 Admin Backups" no menu lateral
- Senha: `prep2025admin`
- Funcionalidades:
  - Ver status atual das respostas
  - Criar backups manuais
  - Listar todos os backups
  - Exportar dados em CSV/JSON
  - Recuperar dados de emergência

### 4. Monitoramento Automático
Execute o script de monitoramento periodicamente:
```bash
./monitor_respostas.sh
```

## 🔧 Como Usar

### Para Usuários Regulares
- As respostas agora são salvas automaticamente com backup
- Não é necessário fazer nada diferente

### Para Administradores

#### Verificar Status
```python
from backup_manager import BackupManager
bm = BackupManager()
print(f"Total de respostas: {bm.contar_respostas()}")
```

#### Fazer Backup Manual
```python
from backup_manager import BackupManager
bm = BackupManager()
resultado = bm.backup_completo()
print(f"Backup criado: {resultado}")
```

#### Listar Backups
```python
from backup_manager import BackupManager
bm = BackupManager()
backups = bm.listar_backups()
print(backups)
```

## 🚨 Recuperação de Emergência

### Se o banco principal for perdido:

1. **Via página Admin**:
   - Acesse "🔧 Admin Backups"
   - Use "🔄 Importar Respostas de Emergência" se houver arquivo de emergência

2. **Via linha de comando**:
   ```bash
   # Restaurar backup mais recente
   cp backups/pesquisa_prep_backup_YYYYMMDD_HHMMSS.db pesquisa_prep.db
   ```

3. **Via CSV de emergência**:
   ```python
   import pandas as pd
   import sqlite3
   
   # Ler CSV de emergência
   df = pd.read_csv('respostas_emergencia.csv')
   
   # Recriar banco
   conn = sqlite3.connect('pesquisa_prep.db')
   df.to_sql('respostas', conn, if_exists='replace', index=False)
   conn.close()
   ```

## 📊 Monitoramento Contínuo

### Script de Monitoramento
Execute regularmente para detectar perdas:
```bash
./monitor_respostas.sh
```

### Configurar Cron (Linux/Mac)
Para executar automaticamente a cada hora:
```bash
crontab -e
# Adicionar linha:
0 * * * * cd /caminho/para/projeto && ./monitor_respostas.sh
```

### Verificação Manual
```bash
# Contar respostas atuais
sqlite3 pesquisa_prep.db "SELECT COUNT(*) FROM respostas;"

# Ver últimas respostas
sqlite3 pesquisa_prep.db "SELECT id, data_envio FROM respostas ORDER BY data_envio DESC LIMIT 5;"
```

## 🔒 Segurança dos Dados

### Localização dos Backups
- **Banco principal**: `pesquisa_prep.db`
- **Backups SQLite**: `backups/`
- **Backups CSV/JSON**: `csv_backups/`
- **Emergência**: `respostas_emergencia.csv`

### Recomendações
1. **Fazer backup externo**: Copie os arquivos da pasta `backups/` para um local seguro
2. **Verificar regularmente**: Execute o monitoramento
3. **Testar recuperação**: Pratique a restauração de backups
4. **Manter múltiplas cópias**: Não dependa apenas de um backup

## 🆘 Contatos de Emergência

Se houver problemas com os dados:
1. Verifique a página "🔧 Admin Backups"
2. Execute `./monitor_respostas.sh`
3. Consulte os logs em `backups/backup_log.json`
4. Use os arquivos CSV como backup final

## 📝 Log de Mudanças

- **2025-10-23**: Implementado sistema completo de backup automático
- **2025-10-23**: Adicionada página de administração
- **2025-10-23**: Criado script de monitoramento
- **2025-10-23**: Implementado backup de emergência em CSV

---

**⚠️ IMPORTANTE**: Sempre mantenha backups dos seus dados em local seguro e teste regularmente os procedimentos de recuperação!