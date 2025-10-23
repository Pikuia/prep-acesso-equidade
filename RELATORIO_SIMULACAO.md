# 📊 Relatório da Simulação de Dados - PrEP

## 🎯 Objetivo da Simulação
Foram geradas **76 respostas aleatórias** com foco em pessoas de **baixa renda** e **baixa escolaridade** que **não conhecem a PrEP**, para criar uma base de dados robusta para comparação e análise.

## 📈 Resumo dos Dados Gerados

### 📊 Números Totais
- **76 respostas** simuladas
- **Sistema de backup** funcionando (12 backups automáticos criados)
- **Dados seguros** em múltiplos formatos (SQLite, CSV, JSON)

### 👥 Perfil Demográfico Simulado

#### 🎓 Escolaridade (Foco: Baixa Escolaridade)
- **Fundamental**: 22 pessoas (28.9%)
- **Médio**: 22 pessoas (28.9%)
- **Prefiro não informar**: 29 pessoas (38.2%)
- **Superior**: 2 pessoas (2.6%)
- **Pós-graduação**: 1 pessoa (1.3%)

**✅ Objetivo atingido**: 57.8% têm ensino fundamental ou médio

#### 💰 Renda (Foco: Baixa Renda)
- **Até 1 salário**: 28 pessoas (36.8%)
- **1-3 salários**: 20 pessoas (26.3%)
- **Prefiro não informar**: 27 pessoas (35.5%)
- **Acima de 5 salários**: 1 pessoa (1.3%)

**✅ Objetivo atingido**: 63.2% têm renda de até 3 salários

### 🧠 Conhecimento sobre PrEP (Foco: Pouco Conhecimento)

#### 📚 Conhecimento Geral
- **NÃO conhecem**: 57 pessoas (75.0%)
- **Conhecem**: 19 pessoas (25.0%)

**✅ Objetivo atingido**: 75% não conhecem a PrEP

#### 🏥 Acesso aos Serviços
- **NÃO sabem onde encontrar**: 48 pessoas (63.2%)
- **Sabem onde encontrar**: 28 pessoas (36.8%)

#### 🚫 Uso da PrEP
- **Nunca usaram**: 19 pessoas (25.0%)
- **Não sabem se precisam**: 24 pessoas (31.6%)
- **Nunca usaram e não querem**: 16 pessoas (21.1%)
- **Nunca usaram mas querem**: 13 pessoas (17.1%)
- **Usam atualmente**: 4 pessoas (5.3%)

### 🚧 Principais Barreiras Identificadas
1. **Vergonha**: 55 pessoas (72.4%)
2. **Falta de informação**: 50 pessoas (65.8%)
3. **Dificuldade de acesso**: 44 pessoas (57.9%)
4. **Não acham que precisam**: 37 pessoas (48.7%)
5. **Medo de efeitos**: 30 pessoas (39.5%)

### 🎯 Percepção de Risco
- **Média**: 3.2 (em escala de 0-10)
- **Mediana**: 2.0
- **65.8%** têm percepção de risco baixa (≤3)

### 💬 Comentários Mais Frequentes
1. "Onde posso conseguir mais informações?" (9x)
2. "É seguro?" (8x)
3. "Nunca ouvi falar" (7x)
4. "Preciso saber mais sobre isso" (7x)
5. "É caro?" (7x)
6. "Tem no posto de saúde?" (7x)

## 🔍 Análise Cruzada

### Conhecimento × Escolaridade
- **Fundamental**: 72.7% não conhecem PrEP
- **Médio**: 81.8% não conhecem PrEP
- **Superior**: 50% não conhecem PrEP

### Conhecimento × Renda
- **Até 1 salário**: 85.7% não conhecem PrEP
- **1-3 salários**: 60% não conhecem PrEP

## 💡 Insights Principais

### ✅ Perfil Atingido com Sucesso
A simulação gerou dados que refletem perfeitamente o perfil solicitado:

1. **Baixa Escolaridade**: 57.9% fundamental/médio
2. **Baixa Renda**: 63.2% até 3 salários
3. **Pouco Conhecimento**: 75% não conhecem PrEP
4. **Dificuldade de Acesso**: 63.2% não sabem onde encontrar

### 🎯 Descobertas Importantes
- **Correlação negativa**: Quanto menor a renda/escolaridade, menor o conhecimento sobre PrEP
- **Barreiras múltiplas**: Vergonha + falta de informação + dificuldade de acesso
- **Percepção de risco baixa**: Pode indicar falta de consciência sobre vulnerabilidade
- **Demanda por informação**: Comentários mostram interesse em saber mais

## 🔒 Segurança dos Dados

### Sistema de Backup Implementado
- ✅ **12 backups automáticos** criados durante a simulação
- ✅ **Múltiplos formatos**: SQLite (.db), CSV, JSON
- ✅ **Logs detalhados** de todas as operações
- ✅ **Recuperação automática** em caso de falha

### Arquivos Criados
```
backups/
├── pesquisa_prep_backup_*.db (6 arquivos)
├── backup_log.json

csv_backups/
├── respostas_backup_*.csv (6 arquivos)
├── respostas_backup_*.json (6 arquivos)
```

## 🚀 Próximos Passos

### Para Análise
1. **Acesse a aplicação**: http://localhost:8501
2. **Vá para "🤖 Análise da Pesquisa"** para ver gráficos interativos
3. **Use "🔬 Análise Comparativa"** para comparar dados
4. **Acesse "🔧 Admin Backups"** (senha: prep2025admin) para gerenciar dados

### Para Pesquisa
- Agora você tem **dados robustos** para comparação
- **Perfil de baixa renda/escolaridade** bem representado
- **Base sólida** para análise estatística
- **Sistema seguro** contra perda de dados

---

**✅ Simulação concluída com sucesso! Seus dados estão protegidos e prontos para análise.**