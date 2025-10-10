# Changelog - Atualizações do Sistema

## Data: 2025-10-10

### Mudanças Implementadas

#### 1. Nova Opção em Item 3 da Pesquisa
- **Arquivo**: `ui_pages.py`
- **Mudança**: Adicionada a opção "Nunca tomei" nas alternativas da pergunta "Você usa ou já usou PrEP?"
- **Localização**: Linha 79
- **Opções disponíveis agora**:
  - Uso atualmente
  - Já usei
  - **Nunca tomei** (NOVO)
  - Nunca usei mas quero
  - Nunca usei e não quero
  - Não sei se preciso

#### 2. Arquivo .gitignore Criado
- **Arquivo**: `.gitignore`
- **Propósito**: Excluir arquivos desnecessários do controle de versão
- **Conteúdo**:
  - Arquivos Python cache (`__pycache__`, `*.pyc`)
  - Arquivos de banco de dados (`*.db`, `*.sqlite`, `pesquisa_prep.db`)
  - Arquivos de IDE (`.vscode`, `.idea`, `*.swp`)
  - Arquivos de ambiente (`.env`)
  - Configurações do Streamlit (`secrets.toml`)

### Dependências de Banco de Dados Verificadas

#### Dependências Atuais (requirements.txt):
✅ **streamlit** - Framework web usado
✅ **pandas** - Manipulação de dados
✅ **plotly** - Visualizações interativas
✅ **mysql-connector-python** - Suporte MySQL (para uso futuro)
✅ **scikit-learn** - Machine Learning (para uso futuro)
✅ **openpyxl** - Leitura de arquivos Excel (.xlsx)
✅ **xlrd** - Leitura de arquivos Excel (.xls)
✅ **numpy** - Computação numérica

#### Dependências de Banco de Dados:
- **SQLite3**: Banco de dados atual (built-in no Python, não requer instalação)
- **mysql-connector-python**: Disponível no requirements.txt para migração futura ao MySQL

### Schema do Banco de Dados
O schema atual da tabela `respostas` inclui todos os campos necessários:
- id (PRIMARY KEY)
- data_envio
- idade, genero, orientacao_sexual, raca, escolaridade, renda, regiao
- status_relacional
- conhecimento_prep, uso_prep, objetivo_prep
- acesso_servico, fonte_info, barreiras
- percepcao_risco
- efeitos_colaterais_teve, efeitos_colaterais_quais
- comentarios

### Testes Realizados
✅ Aplicação inicia corretamente
✅ Schema do banco de dados validado
✅ Todas as dependências instaladas com sucesso
✅ Nenhum erro de importação detectado

### Próximos Passos Sugeridos
1. Testar a nova opção "Nunca tomei" com usuários reais
2. Verificar se há necessidade de atualizar análises para incluir essa nova categoria
3. Considerar migração para MySQL se necessário (infraestrutura já preparada)
