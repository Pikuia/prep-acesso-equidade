# -*- coding: utf-8 -*-
"""
PrEP - Análise Inteligente de Dados
Versão Final com Dados Integrados, Pesquisa, Análise de Machine Learning e Guia de Locais.
"""
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import warnings
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


warnings.filterwarnings('ignore')

# ======================= CONFIGURAÇÃO DA PÁGINA =======================
st.set_page_config(page_title="PrEP - Pesquisa Inteligente", page_icon="❤️", layout="wide")

# ======================= BANCO DE DADOS PARA A PESQUISA =======================
def criar_banco():
    """Cria o banco de dados SQLite e a tabela de respostas se não existirem."""
    conn = sqlite3.connect('pesquisa_prep.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS respostas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        idade TEXT,
        genero TEXT,
        orientacao_sexual TEXT,
        raca TEXT,
        escolaridade TEXT,
        renda TEXT,
        regiao TEXT,
        conhecimento_prep TEXT,
        uso_prep TEXT,
        acesso_servico TEXT,
        fonte_info TEXT,
        barreiras TEXT,
        percepcao_risco TEXT,
        comentarios TEXT
    )
    ''')
    conn.commit()
    conn.close()

def salvar_resposta(resposta):
    """Salva uma nova resposta da pesquisa no banco de dados."""
    conn = sqlite3.connect('pesquisa_prep.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO respostas 
    (idade, genero, orientacao_sexual, raca, escolaridade, renda, regiao, 
     conhecimento_prep, uso_prep, acesso_servico, fonte_info, barreiras, percepcao_risco, comentarios)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', tuple(resposta.values()))
    conn.commit()
    conn.close()

# ======================= CARREGAMENTO DOS DADOS (CSV E EXCEL) =======================
@st.cache_data
def carregar_dados_iniciais():
    """Carrega todos os arquivos de dados (CSV e Excel) da pasta 'data'."""
    data_path = Path('data')
    try:
        # Carrega dados de usuários PrEP
        df_usuarios = pd.read_csv(data_path / 'Banco_PrEP_usuarios.csv', encoding='latin1', sep=',')
        
        # Carrega o arquivo de dispensas único e grande
        df_dispensas = pd.read_csv(data_path / 'Banco_PrEP_dispensas.csv', encoding='latin1', sep=',')
        
        # Carrega dados de indicadores de AIDS do Excel
        df_indicadores = pd.read_excel(data_path / 'indicadoresAids.xls', sheet_name=None, header=None)
        
        return df_usuarios, df_dispensas, df_indicadores
    except FileNotFoundError:
        st.error(
            "Erro: Arquivos de dados não encontrados. "
            "Certifique-se de que a pasta 'data' existe e contém os arquivos: "
            "'Banco_PrEP_usuarios.csv', 'Banco_PrEP_dispensas.csv', e 'indicadoresAids.xls'."
        )
        return pd.DataFrame(), pd.DataFrame(), None
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado ao carregar os dados: {e}")
        return pd.DataFrame(), pd.DataFrame(), None

# ======================= FUNÇÕES DE MACHINE LEARNING =======================
@st.cache_data
def analise_avancada_publico(df_usuarios):
    """Executa análises de Machine Learning (Clusterização e Feature Importance) nos dados públicos."""
    st.header("🤖 Análise Avançada com Machine Learning")
    
    # 1. ANÁLISE DE PERFIS (CLUSTERIZAÇÃO)
    st.subheader("1. Identificação de Perfis de Usuários (Clusterização)")
    st.markdown("""
    Utilizamos um algoritmo de Machine Learning (*K-Means*) para agrupar os usuários em perfis (clusters) com características semelhantes. 
    Isso nos ajuda a entender melhor os diferentes grupos que utilizam a PrEP.
    """)

    # Selecionar e preparar os dados para clusterização
    features_cluster = ['raca4_cat', 'escol4', 'fetar', 'Pop_genero_pratica', 'UF_UDM']
    df_cluster = df_usuarios[features_cluster].dropna()

    if df_cluster.empty:
        st.warning("Não há dados suficientes para a análise de perfis.")
        return

    # Pipeline de pré-processamento
    preprocessor = ColumnTransformer(
        transformers=[('cat', OneHotEncoder(handle_unknown='ignore'), features_cluster)],
        remainder='passthrough'
    )
    
    pipeline = Pipeline(steps=[('preprocessor', preprocessor)])
    X_processed = pipeline.fit_transform(df_cluster)
    
    # Executar K-Means
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    df_cluster['perfil'] = kmeans.fit_predict(X_processed)
    
    st.success("Encontramos 4 perfis principais de usuários. Veja a descrição de cada um:")
    
    for i in range(4):
        st.markdown(f"---")
        st.markdown(f"#### Perfil {i+1}")
        perfil_df = df_cluster[df_cluster['perfil'] == i]
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**População/Gênero:**")
            st.dataframe(perfil_df['Pop_genero_pratica'].value_counts().head(3))
            st.write("**Faixa Etária:**")
            st.dataframe(perfil_df['fetar'].value_counts().head(3))

        with col2:
            st.write("**Estado (UF):**")
            st.dataframe(perfil_df['UF_UDM'].value_counts().head(3))
            st.write("**Escolaridade:**")
            st.dataframe(perfil_df['escol4'].value_counts().head(3))

    # 2. FATORES DE RETENÇÃO (FEATURE IMPORTANCE)
    st.subheader("2. Fatores Chave para a Retenção de Usuários")
    st.markdown("""
    Aqui, usamos outro modelo (*Random Forest*) para prever se um usuário continuou no programa em 2024. 
    O gráfico abaixo mostra quais características (idade, raça, etc.) são mais importantes para essa previsão.
    """)

    # Preparar dados
    features_retencao = ['raca4_cat', 'escol4', 'fetar', 'Pop_genero_pratica', 'UF_UDM']
    target_retencao = 'Disp_12m_2024'
    df_retencao = df_usuarios[features_retencao + [target_retencao]].dropna()
    df_retencao = df_retencao[df_retencao[target_retencao] != 'nan']


    if df_retencao.empty or df_retencao[target_retencao].nunique() < 2:
        st.warning("Não há dados suficientes para a análise de retenção.")
        return
        
    X = df_retencao[features_retencao]
    y = (df_retencao[target_retencao] == 'Teve dispensaÃ§Ã£o em 2024').astype(int)

    # Pipeline de pré-processamento para o modelo
    cat_features = X.select_dtypes(include=['object']).columns
    preprocessor_rf = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features)
        ],
        remainder='passthrough'
    )
    
    # Modelo
    rf_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor_rf),
        ('classifier', RandomForestClassifier(random_state=42))
    ])
    
    rf_pipeline.fit(X, y)
    
    # Extrair e exibir a importância das features
    feature_names = rf_pipeline.named_steps['preprocessor'].get_feature_names_out()
    importances = rf_pipeline.named_steps['classifier'].feature_importances_
    
    feature_importance_df = pd.DataFrame({'feature': feature_names, 'importance': importances})
    feature_importance_df = feature_importance_df.sort_values('importance', ascending=False).head(15)

    fig = px.bar(feature_importance_df, x='importance', y='feature', orientation='h', title='Top 15 Fatores que Influenciam a Retenção')
    st.plotly_chart(fig, use_container_width=True)

def analise_indicadores_hiv(df_indicadores):
    """Processa o arquivo Excel de indicadores e exibe gráficos sobre HIV/AIDS."""
    st.subheader("Gráficos sobre HIV/AIDS no Brasil (Dados Nacionais)")
    st.info("Estes gráficos são baseados nos dados nacionais do arquivo `indicadoresAids.xls` e **não são afetados pelo filtro de estado (SP)**.")

    if not df_indicadores:
        st.warning("Não foi possível carregar os dados dos indicadores para gerar os gráficos.")
        return

    # Tenta usar a aba 'Boletim', se não encontrar, usa a primeira disponível
    sheet_name_to_use = 'Boletim'
    if sheet_name_to_use not in df_indicadores:
        first_sheet_name = list(df_indicadores.keys())[0]
        st.warning(f"A aba 'Boletim' não foi encontrada. Analisando a primeira aba: '{first_sheet_name}'.")
        sheet_name_to_use = first_sheet_name

    df_sheet = df_indicadores[sheet_name_to_use]

    # Helper function to find the start row of a table by its title
    def find_table_start(df, title_keyword):
        for idx, row in df.iterrows():
            if row.astype(str).str.contains(title_keyword, case=False, na=False).any():
                return idx
        return None

    # --- Gráfico 1: Casos de Aids por ano ---
    st.markdown("---")
    try:
        start_row = find_table_start(df_sheet, "Tabela 1 - Casos de aids")
        if start_row is not None:
            header_row = df_sheet.iloc[start_row + 1]
            tabela1 = df_sheet.iloc[start_row + 2 : start_row + 5].copy()
            tabela1.columns = header_row
            
            tabela1 = tabela1.set_index(tabela1.columns[0])
            tabela1.index.name = "Categoria"
            
            tabela1 = tabela1.drop(columns=['Total', '1980-2012'], errors='ignore')
            
            anos_colunas = [col for col in tabela1.columns if isinstance(col, (int, float)) and 2013 <= col <= 2023]
            tabela1 = tabela1[anos_colunas].T
            tabela1.index = tabela1.index.astype(int).astype(str)
            tabela1.index.name = "Ano"
            tabela1 = tabela1.astype(float)
            
            tabela1 = tabela1.rename(columns={'Total': 'Total de Casos', 'Masculino': 'Masculino', 'Feminino': 'Feminino'})
            
            st.markdown("#### Evolução dos Casos de AIDS no Brasil (2013-2023)")
            fig = px.line(tabela1, x=tabela1.index, y=tabela1.columns, title="Novos Casos de AIDS por Ano", labels={'value': 'Número de Casos', 'variable': 'Legenda'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            raise ValueError("Tabela 1 não encontrada.")
    except Exception:
        st.warning("Não foi possível gerar o gráfico de 'Evolução dos Casos de AIDS'. Verifique o formato do arquivo Excel.")


    # --- Gráfico 2: Óbitos por Aids por ano ---
    st.markdown("---")
    try:
        start_row_obitos = find_table_start(df_sheet, "Tabela 7 - Óbitos por causa básica aids")
        if start_row_obitos is not None:
            header = df_sheet.iloc[start_row_obitos + 1]
            dados_obitos = df_sheet.iloc[start_row_obitos + 2]
            
            df_obitos = pd.DataFrame(data=[dados_obitos.values], columns=header.values).T.reset_index()
            df_obitos.columns = ['Variavel', 'Valor']
            df_obitos = df_obitos[df_obitos['Variavel'].astype(str).str.match(r'^\d{4}(\.0)?$')]
            df_obitos = df_obitos[(df_obitos['Variavel'] >= 2013) & (df_obitos['Variavel'] <= 2023)]
            df_obitos.columns = ['Ano', 'Óbitos']
            df_obitos['Ano'] = df_obitos['Ano'].astype(int).astype(str)
            df_obitos['Óbitos'] = pd.to_numeric(df_obitos['Óbitos'])

            st.markdown("#### Evolução dos Óbitos por AIDS no Brasil (2013-2023)")
            fig_obitos = px.bar(df_obitos, x='Ano', y='Óbitos', title='Número de Óbitos Anuais por AIDS')
            st.plotly_chart(fig_obitos, use_container_width=True)
        else:
            raise ValueError("Tabela 7 não encontrada.")
    except Exception:
        st.warning("Não foi possível gerar o gráfico de 'Óbitos por AIDS'. Verifique o formato do arquivo Excel.")

    # --- Gráfico 3: Casos por Raça/Cor em 2023 ---
    st.markdown("---")
    try:
        start_row_raca = find_table_start(df_sheet, "Tabela 8 - Casos de aids notificados no Sinan, segundo raça/cor")
        if start_row_raca is not None:
            header_raca = df_sheet.iloc[start_row_raca + 1]
            dados_raca = df_sheet.iloc[start_row_raca + 2 : start_row_raca + 7].copy()
            dados_raca.columns = header_raca
            
            dados_raca = dados_raca.set_index(dados_raca.columns[0])
            dados_2023 = dados_raca[[2023.0]].copy() # O cabeçalho pode ser float
            dados_2023.columns = ['Casos em 2023']
            dados_2023 = dados_2023.reset_index()
            dados_2023.columns = ['Raça/Cor', 'Casos em 2023']
            dados_2023['Casos em 2023'] = pd.to_numeric(dados_2023['Casos em 2023'])

            st.markdown("#### Distribuição de Casos de AIDS por Raça/Cor (2023)")
            fig_raca = px.pie(dados_2023, names='Raça/Cor', values='Casos em 2023', title='Distribuição de Casos por Raça/Cor em 2023', hole=0.3)
            st.plotly_chart(fig_raca, use_container_width=True)
        else:
            raise ValueError("Tabela 8 não encontrada.")
    except Exception:
        st.warning("Não foi possível gerar o gráfico de 'Casos por Raça/Cor'. Verifique o formato do arquivo Excel.")


    with st.expander("Visualizar todas as tabelas originais do arquivo 'indicadoresAids.xls'"):
        for sheet_name, df_sheet_raw in df_indicadores.items():
            st.write(f"Dados da aba: {sheet_name}")
            df_cleaned = df_sheet_raw.dropna(how='all').dropna(axis=1, how='all')
            st.dataframe(df_cleaned)

# ======================= PÁGINA "DÚVIDAS FREQUENTES" =======================
def mostrar_duvidas_frequentes():
    """Exibe uma seção com perguntas e respostas comuns sobre a PrEP."""
    st.header("❔ Dúvidas Frequentes sobre a PrEP")
    st.markdown("---")
    st.info("Clique nas perguntas abaixo para ver as respostas.")

    with st.expander("Posso parar de usar camisinha?"):
        st.write("Como a PrEP é uma profilaxia apenas para o HIV, o uso da camisinha ainda é recomendado para prevenção às outras infecções sexualmente transmissíveis, bem como evitar uma gravidez não planejada.")
    
    with st.expander("A PrEP tem efeito colateral?"):
        st.write("Nos medicamentos usados hoje, os efeitos colaterais são raros e tranquilos. A pessoa pode ter um pouco de náusea e cefaleia (dor de cabeça). É importante o acompanhamento com o profissional de saúde para garantir a correta avaliação.")

    with st.expander("E se eu esquecer de tomar a PrEP um dia? Perde o efeito logo em seguida?"):
        st.write("Na verdade você vai diminuir o efeito protetivo do medicamento. Mas, um dia só não vai comprometer a sua prevenção.")

    with st.expander("A partir de quantos dias a PrEP começa a fazer efeito?"):
        st.write("No caso de sexo vaginal e de pessoas que fazem uso do hormônio estradiol, a proteção é dada a partir do sétimo dia. No caso de pessoas com pênis que não fazem uso de hormônio estradiol, ao realizarem sexo anal, a proteção se inicia a partir de duas horas.")

    with st.expander("Preciso tomar a PrEP em jejum?"):
        st.write("Não, não precisa. Você vai escolher o melhor horário para tomar o seu medicamento. O ideal é que você repita sempre nesse mesmo horário.")
        
    with st.expander("Bebida alcóolica corta o efeito da PrEP?"):
        st.write("Não, não corta o efeito da PrEP.")

    with st.expander("Qual a diferença entre PrEP e PEP?"):
        st.write("""
        A PrEP, ou seja, a Profilaxia Pré-Exposição, é uma forma de se prevenir ao HIV antes de uma exposição de risco de infecção. Por isso ela deve ser tomada todos os dias (no caso da PrEP diária) ou no esquema 2 + 1 + 1 (no caso da PrEP sob demanda), como uma medida protetiva. Mas atenção! O uso da PrEP sob demanda é indicado for para algumas populações apenas, e deve ser utilizada conforme orientação do profissional de saúde. 
        
        Já a PEP, a Profilaxia Pós-Exposição, é indicada para pessoas que não fazem PrEP e quando a camisinha sai, rompe ou não é utilizada no sexo. É uma forma de prevenção ao HIV que deve ser acessada após uma situação de risco. A PEP deve ser iniciada em até 72 horas depois da exposição; de preferência nas duas primeiras horas.
        """)


# ======================= PÁGINA "ONDE ENCONTRAR" =======================
def mostrar_onde_encontrar():
    """Exibe informações sobre a PrEP e onde encontrá-la, com foco em São Paulo."""
    st.header("📍 Onde Encontrar a PrEP?")
    st.markdown("---")

    # --- INFORMAÇÕES GERAIS ---
    st.subheader("O que é a PrEP?")
    st.info("""
    A Profilaxia Pré-Exposição (PrEP) ao HIV é um método de prevenção que consiste no uso de medicamentos antirretrovirais por pessoas não infectadas pelo HIV, mas que estão em situações de maior vulnerabilidade à infecção.
    
    O objetivo é preparar o organismo para se proteger do vírus caso haja contato. Existem duas modalidades principais:
    - **PrEP Diária:** Consiste em tomar um comprimido por dia, de forma contínua.
    - **PrEP Sob Demanda:** Consiste em tomar dois comprimidos de 2 a 24 horas antes da relação sexual, um comprimido 24 horas após a primeira dose, e um último comprimido 24 horas após a segunda dose.
    
    A PrEP é segura, eficaz e oferecida gratuitamente pelo Sistema Único de Saúde (SUS).
    """)

    # --- DADOS DOS LOCAIS EM SÃO PAULO ---
    st.subheader("Encontre um serviço de saúde em São Paulo (Capital)")
    
    # Criando o DataFrame com os dados dos locais
    dados_locais = {
        'Unidade': [
            # Centro
            'Estação Prevenção Jorge Beloqui', 'CTA Henfil', 'SAE Campos Elíseos',
            'Centro de Saúde Escola Barra Funda', 'UBS Dr. Humberto Pascale - Santa Cecília', 'UBS República',
            'Centro de Referência Janaina Lima',
            # Norte
            'SAE Nossa Senhora do Ó', 'CTA Pirituba', 'SAE Santana (Marcos Lottenberg)',
            'AMA Especialidades Perus', 'Ambulatório de Especialidades Freguesia do Ó',
            'Hospital Dia Brasilândia', 'Hospital Dia Vila Guilherme',
            # Sul
            'SAE Santo Amaro', 'CTA Santo Amaro (Paula Legno)', 'CTA José Araújo Lima Filho',
            'SAE Jardim Mitsutani', 'SAE Cidade Dutra', 'SAE M’Boi Mirim',
            'AMA Jd. Icaraí – Quintana', 'Ambulatório de Especialidades Alto da Boa Vista',
            'Hospital Dia Campo Limpo - AMA Pirajussara', 'Hospital Dia M Boi Mirim I', 'Hospital Municipal Capela do Socorro',
            # Sudeste
            'SAE Jabaquara (antigo SAE Ceci)', 'SAE Vila Prudente (Shirlei Mariotti Gomes Coelho)', 'SAE Penha',
            'SAE Herbert de Souza (Betinho)', 'SAE Ipiranga (José Francisco de Araújo)', 'CTA Mooca',
            # Leste
            'CTA Cidade Tiradentes', 'CTA Dr. Sérgio Arouca (Itaim Paulista)', 'SAE São Mateus',
            'CTA São Miguel', 'CTA Guaianases', 'SAE Cidade Líder II', 'SAE Fidélis Ribeiro',
            'AMA/UBS Humberto Cerruti', 'Casa Ser – Cidade Tiradentes',
            # Oeste
            'SAE Butantã', 'SAE Lapa (Paulo César Bonfim)', 'AMA/UBS Vila Nova Jaguaré',
            'Centro de Saúde Escola Butantã', 'UBS Butantã', 'UBS Jardim Boa Vista',
            'UBS Jardim D’Abril', 'UBS Jardim São Jorge', 'UBS Magaldi', 'UBS Paulo VI',
            'UBS Real Parque', 'UBS São Remo', 'UBS Vila Dalva', 'AMA/UBS Vila Sônia',
            'UBS Vila Jaguará', 'UBS Vila Ipojuca - Dra. Wanda Coelho de Moraes'
        ],
        'Endereço': [
            # Centro
            'Dentro da Estação República - Linha vermelha do metrô', 'R. do Tesouro, 39 - Centro', 'Al. Cleveland, 374 - Santa Cecília',
            'Avenida Dr. Abraão Ribeiro, 283, Barra Funda', 'R. Vitorino Carmilo, 599 - Barra Funda', 'Praça do Patriarca, 100, Centro Histórico',
            'R. Jaraguá, 866 - Bom Retiro',
            # Norte
            'Av. Itaberaba, 1.377 - Freguesia do Ó', 'Av. Dr. Felipe Pinel, 12 - Pirituba', 'R. Dr. Luís Lustosa da Silva, 339 - Mandaqui',
            'R. José Antonio Anacleto, 80 – Vl. Caiuba', 'R. Bonifácio Cubas, 304 - Freguesia do Ó',
            'Rui Moraes do Apocalipse, 02 - Jd. do Tiro', 'João Ventura Batista, 615 - Vila Guilherme',
            # Sul
            'R. Padre José de Anchieta, 640 – Santo Amaro', 'R. Mário Lopes Leão, 240 – Santo Amaro', 'R. Louis Boulanger,120, Jardim Bom Refúgio',
            'R. Vittório Emanuele Rossi, 97 – Jd. Bom Refúgio', 'R. Cristina de Vasconcelos Ceccato, 109 – Cidade Dutra', 'R. Deocleciano de Oliveira Filho, 641 – Pq. Santo Antônio',
            'Rua São Roque do Paraguaçu, 190 - Vila Quintana', 'R. Min. Roberto Cardoso Alves, 386 - Santo Amaro',
            'Av. Amadeu da Silva Samelo, 423 - Jd. Martinica', 'R. Philippe de Vitry, 280 - Jd. Santa Josefina', 'R. Cássio de Campos Nogueira, 2031 - Jardim das Imbuias',
            # Sudeste
            'Rua dos Comerciários, 236 - Jabaquara', 'Pça. Centenário de Vila Prudente, 108 - Vila Prudente', 'Pça. Nossa Senhora da Penha, 55 - Penha',
            'Av. Arquiteto Vilanova Artigas, 515 - Teotônio Vilela', 'R. Gonçalves Ledo, 606 - Ipiranga', 'R. Taquari, 549 — salas 9 e 10 - Mooca',
            # Leste
            'R. Milagre dos Peixes, 357 - Cidade Tiradentes', 'R. Valente Novais, 131 - Itaim Paulista', 'Av. Mateo Bei, 838 - São Mateus',
            'R. José Aldo Piassi, 85 - São Miguel Paulista', 'R. Centralina, 168 - Guaianases', 'R. Médio Iguaçu, 86 - Cidade Líder',
            'R. Peixoto, 100 - Vila Fidélis Ribeiro', 'Av. Olavo Egídio de Souza Aranha, 704 - Parque Cisper', 'Av. Dr. Guilherme de Abreu Sodré, 485 - Conj. Res. Prestes Maia',
            # Oeste
            'Rua Dr. Bernardo Guertzenstein, 45 - Jardim Sarah', 'Rua Tome de Souza, 30 - Lapa', 'R. Salatiel de Campos, 222 – Jaguaré',
            'Av. Vital Brasil, 1490 - Butantã', 'R. Cabral de Menezes, 51 - Vila Gomes', 'R. Cândido Fontoura, 620 - Raposo Tavares',
            'R. Paulo Maranhão, 444 - Jd. D’Abril', 'R. Ângelo Aparecido dos Santos Dias, 331 - Jd. São Jorge', 'Rua Salvador Cardoso, 177 - Itaim Bibi',
            'R. Vaticano, 69 - Jd. João XXIII', 'Av. Barão do Melgaço, 339 - Real Parque', 'R.Baltazar Rabelo, 167 - Vila Butantã',
            'Av. Gustavo Berthier, 155 - Vila Dalva', 'R. Abrão Calil Rezek, 91 - Vila Sonia', 'Rua Paúva, 721 - Vila Jaguará',
            'R. Catão, 1266 - Lapa'
        ],
        'Região': [
            'Centro', 'Centro', 'Centro', 'Centro', 'Centro', 'Centro', 'Centro',
            'Norte', 'Norte', 'Norte', 'Norte', 'Norte', 'Norte', 'Norte',
            'Sul', 'Sul', 'Sul', 'Sul', 'Sul', 'Sul', 'Sul', 'Sul', 'Sul', 'Sul', 'Sul',
            'Sudeste', 'Sudeste', 'Sudeste', 'Sudeste', 'Sudeste', 'Sudeste',
            'Leste', 'Leste', 'Leste', 'Leste', 'Leste', 'Leste', 'Leste', 'Leste', 'Leste',
            'Oeste', 'Oeste', 'Oeste', 'Oeste', 'Oeste', 'Oeste', 'Oeste', 'Oeste', 'Oeste', 'Oeste', 'Oeste', 'Oeste', 'Oeste', 'Oeste', 'Oeste', 'Oeste'
        ],
        'Observações': [
            # Centro
            'Atendimento no metrô', '', '', 'Referência para hormonização', 'Referência para hormonização', 'Referência para hormonização', 'Referência para hormonização',
            # Norte
            '', '', '', 'Referência para hormonização', 'Referência para hormonização', 'Referência para hormonização', 'Referência para hormonização',
            # Sul
            '', '', '', '', '', '', 'Referência para hormonização', 'Referência para hormonização', 'Referência para hormonização', 'Referência para hormonização', 'Referência para hormonização',
            # Sudeste
            '', '', '', '', '', '',
            # Leste
            '', '', '', '', '', '', '', 'Referência para hormonização', 'Referência para hormonização',
            # Oeste
            '', '', 'Referência para hormonização', 'Referência para hormonização', 'Referência para hormonização', 'Referência para hormonização', 'Referência para hormonização',
            'Referência para hormonização', 'Referência para hormonização', 'Referência para hormonização', 'Referência para hormonização', 'Referência para hormonização',
            'Referência para hormonização', 'Referência para hormonização', 'Referência para hormonização', 'Referência para hormonização'
        ],
        'lat': [
            -23.5446, -23.5480, -23.5353, -23.5298, -23.5348, -23.5471, -23.5293,
            -23.4939, -23.4862, -23.4815, -23.4093, -23.4957, -23.4565, -23.5097,
            -23.6508, -23.6514, -23.6334, -23.6338, -23.7081, -23.6781, -23.6881, -23.6429, -23.6366, -23.6823, -23.7226,
            -23.6433, -23.5852, -23.5268, -23.6190, -23.5898, -23.5552,
            -23.5880, -23.4983, -23.6017, -23.4939, -23.5516, -23.5658, -23.5413, -23.5049, -23.5901,
            -23.5721, -23.5226, -23.5583, -23.5714, -23.5746, -23.5881, -23.5905, -23.6053, -23.5910, -23.5804, -23.5956, -23.5713, -23.5746, -23.6047, -23.5085, -23.5204
        ],
        'lon': [
            -46.6419, -46.6343, -46.6439, -46.6565, -46.6508, -46.6353, -46.6387,
            -46.6905, -46.7214, -46.6310, -46.7601, -46.6872, -46.6895, -46.6025,
            -46.7037, -46.7088, -46.7629, -46.7629, -46.6953, -46.7626, -46.7725, -46.6983, -46.7663, -46.7779, -46.7071,
            -46.6456, -46.5794, -46.5484, -46.4811, -46.6053, -46.6026,
            -46.4022, -46.3980, -46.4800, -46.4293, -46.4025, -46.4719, -46.5419, -46.4950, -46.4039,
            -46.7303, -46.7025, -46.7554, -46.7174, -46.7214, -46.7825, -46.7909, -46.7523, -46.6811, -46.7885, -46.7099, -46.7410, -46.7766, -46.7328, -46.7454, -46.7077
        ]
    }
    df_locais = pd.DataFrame(dados_locais)

    # --- FILTRO E MAPA ---
    st.markdown("Use o filtro abaixo para encontrar os locais por região da cidade.")
    
    regioes = ['Todas'] + sorted(df_locais['Região'].unique())
    regiao_selecionada = st.selectbox("Selecione a Região:", regioes)

    if regiao_selecionada == 'Todas':
        df_filtrado = df_locais
    else:
        df_filtrado = df_locais[df_locais['Região'] == regiao_selecionada]

    if df_filtrado.empty:
        st.warning("Nenhum local encontrado para a região selecionada.")
    else:
        st.dataframe(df_filtrado[['Unidade', 'Endereço', 'Região', 'Observações']])
        
        st.subheader(f"Mapa de Locais ({regiao_selecionada})")
        st.map(df_filtrado, zoom=10)
        
    # --- FONTES ---
    st.markdown("---")
    st.markdown("""
    **Fontes e Links Úteis:**
    - [Governo Federal - Informações sobre PrEP](https://www.gov.br/aids/pt-br/assuntos/prevencao-combinada/prep-profilaxia-pre-exposicao)
    - [Prefeitura de São Paulo - Locais de Atendimento](https://prefeitura.sp.gov.br/web/saude/w/istaids/248175)
    """)


# ======================= INTERFACE DO APP =======================

def mostrar_termo_consentimento():
    """Exibe o termo de consentimento e gerencia a aceitação."""
    st.header("Termo de Consentimento Livre e Esclarecido")
    
    try:
        with open("termo_consentimento.md", "r", encoding="utf-8") as f:
            termo_texto = f.read()
        st.markdown(termo_texto, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("Arquivo 'termo_consentimento.md' não encontrado.")
        return

    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Aceito e quero participar da pesquisa"):
            st.session_state.termo_aceito = True
            st.rerun()
    with col2:
        if st.button("❌ Não aceito"):
            st.info("Obrigado pelo seu interesse. Você pode fechar esta página.")
            st.stop()

def mostrar_pesquisa():
    """Exibe o formulário da pesquisa."""
    st.header("📝 Pesquisa - Conhecimento sobre PrEP/PEP")
    st.markdown("Por favor, responda às perguntas abaixo. Suas respostas são anônimas e muito importantes.")

    with st.form("formulario_pesquisa"):
        st.subheader("1. Perfil Demográfico")
        idade = st.selectbox("Qual sua faixa etária?", ["18-24 anos", "25-34 anos", "35-44 anos", "45-54 anos", "55 anos ou mais"])
        genero = st.selectbox("Com qual gênero você se identifica?", ["Homem Cis", "Mulher Cis", "Homem Trans", "Mulher Trans", "Não-binário", "Prefiro não informar"])
        raca = st.selectbox("Como você se autodeclara em relação à raça/cor?", ["Branca", "Preta", "Parda", "Amarela", "Indígena", "Prefiro não informar"])
        escolaridade = st.selectbox("Qual seu nível de escolaridade?", ["Ensino Fundamental", "Ensino Médio", "Ensino Superior", "Pós-graduação"])
        renda = st.selectbox("Qual sua renda familiar mensal?", ["Até 1 salário mínimo", "De 1 a 3 salários", "De 3 a 5 salários", "Acima de 5 salários"])

        st.subheader("2. Conhecimento e Acesso à PrEP")
        conhecimento = st.radio("Você já ouviu falar sobre a PrEP (Profilaxia Pré-Exposição ao HIV)?", ["Sim, conheço bem", "Já ouvi falar, mas sei pouco", "Nunca ouvi falar"])
        fonte_info = st.selectbox("Onde você ouviu falar sobre PrEP pela primeira vez?", ["Profissional de saúde (médico, enfermeiro)", "Amigos ou parceiro(a)", "Redes sociais (Instagram, TikTok, etc.)", "Sites de notícias ou blogs", "Campanhas do governo", "Outro"])
        acesso = st.radio("Você sabe onde encontrar a PrEP gratuitamente pelo SUS?", ["Sim", "Não", "Tenho uma ideia, mas não tenho certeza"])
        
        st.subheader("3. Uso e Percepções")
        uso = st.radio("Você já fez uso da PrEP?", ["Sim, uso atualmente", "Já usei no passado", "Nunca usei, mas tenho interesse", "Nunca usei e não tenho interesse"])
        barreiras = st.multiselect("Se você nunca usou ou parou de usar, qual foi o principal motivo? (Pode marcar mais de um)", ["Não acho que preciso", "Preocupação com efeitos colaterais", "Dificuldade de conseguir consulta ou receita", "Vergonha ou estigma", "Esqueço de tomar o remédio todo dia", "Não se aplica a mim"])
        percepcao_risco = st.radio("Em sua opinião, qual o seu risco de se expor ao HIV hoje?", ["Alto", "Médio", "Baixo", "Nenhum", "Não sei avaliar"])

        comentarios = st.text_area("Se quiser, deixe um comentário, dúvida ou sugestão:")

        if st.form_submit_button("🚀 Enviar Minhas Respostas"):
            resposta = {
                'idade': idade, 'genero': genero, 'orientacao_sexual': 'N/A', 'raca': raca,
                'escolaridade': escolaridade, 'renda': renda, 'regiao': "Brasil",
                'conhecimento_prep': conhecimento, 'uso_prep': uso, 'acesso_servico': acesso,
                'fonte_info': fonte_info, 'barreiras': ", ".join(barreiras), 'percepcao_risco': percepcao_risco,
                'comentarios': comentarios
            }
            salvar_resposta(resposta)
            st.success("✅ Resposta enviada com sucesso! Muito obrigado por sua contribuição.")
            st.balloons()

def analise_com_machine_learning():
    """Exibe as análises dos dados coletados na pesquisa."""
    st.header("🤖 Análise dos Dados da Pesquisa (Resultados em Tempo Real)")
    st.markdown("Aqui vemos os perfis dos participantes e suas respostas de forma visual.")

    conn = sqlite3.connect('pesquisa_prep.db')
    try:
        df_respostas = pd.read_sql_query("SELECT * FROM respostas", conn)
    finally:
        conn.close()

    if df_respostas.empty:
        st.warning("Ainda não há respostas para analisar. Participe da pesquisa!")
        return

    st.metric("Total de Respostas Coletadas", len(df_respostas))

    st.subheader("Recorte por Perfil Demográfico")
    col1, col2 = st.columns(2)
    with col1:
        fig_idade = px.pie(df_respostas, names='idade', title='Distribuição por Idade', hole=.3)
        st.plotly_chart(fig_idade, use_container_width=True)
        
        fig_raca = px.bar(df_respostas['raca'].value_counts().reset_index(), x='raca', y='count', title='Distribuição por Raça/Cor', labels={'raca': 'Raça/Cor', 'count': 'Quantidade'})
        st.plotly_chart(fig_raca, use_container_width=True)
    with col2:
        fig_genero = px.pie(df_respostas, names='genero', title='Distribuição por Gênero', hole=.3)
        st.plotly_chart(fig_genero, use_container_width=True)

        fig_escolaridade = px.bar(df_respostas['escolaridade'].value_counts().reset_index(), x='escolaridade', y='count', title='Distribuição por Escolaridade', labels={'escolaridade': 'Escolaridade', 'count': 'Quantidade'})
        st.plotly_chart(fig_escolaridade, use_container_width=True)

    st.subheader("Análise sobre Conhecimento e Acesso à PrEP")
    col1, col2 = st.columns(2)
    with col1:
        fig_conhecimento = px.pie(df_respostas, names='conhecimento_prep', title='Conhecimento sobre a PrEP', hole=.3)
        st.plotly_chart(fig_conhecimento, use_container_width=True)
    with col2:
        fig_acesso = px.pie(df_respostas, names='acesso_servico', title='Sabe onde obter PrEP?', hole=.3)
        st.plotly_chart(fig_acesso, use_container_width=True)

    st.subheader("Fontes de Informação e Percepção de Risco")
    col3, col4 = st.columns(2)
    with col3:
        fig_fonte = px.bar(df_respostas['fonte_info'].value_counts().reset_index(), x='fonte_info', y='count', title='Principal Fonte de Informação sobre PrEP')
        st.plotly_chart(fig_fonte, use_container_width=True)
    with col4:
        fig_risco = px.pie(df_respostas, names='percepcao_risco', title='Autopercepção de Risco de Exposição ao HIV', hole=.3)
        st.plotly_chart(fig_risco, use_container_width=True)
    
    with st.expander("Ver dados brutos da pesquisa"):
        st.dataframe(df_respostas)


def mostrar_dados_oficiais():
    """Exibe os dados pré-carregados dos arquivos CSV e Excel com análises detalhadas."""
    st.header("📊 Dados Oficiais sobre PrEP e HIV/AIDS no Brasil")
    
    df_usuarios, df_dispensas, df_indicadores = carregar_dados_iniciais()

    if df_usuarios.empty and df_dispensas.empty and df_indicadores is None:
        return 

    st.markdown("---")
    st.info("💡 Use o filtro abaixo para visualizar os dados de usuários e dispensas de PrEP apenas do estado de São Paulo.")
    filtro_sp = st.toggle("Mostrar apenas dados de PrEP de São Paulo (SP)", help="Ative para filtrar os dados da PrEP para o estado de SP.")

    df_usuarios_filtrado = df_usuarios.copy()
    df_dispensas_filtrado = df_dispensas.copy()

    if filtro_sp:
        if 'UF_UDM' in df_usuarios.columns:
            df_usuarios_filtrado = df_usuarios[df_usuarios['UF_UDM'] == 'SP']
        if 'UF_UDM' in df_dispensas.columns:
            df_dispensas_filtrado = df_dispensas[df_dispensas['UF_UDM'] == 'SP']
        st.success(f"Filtro aplicado! Mostrando dados de PrEP de São Paulo.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "👤 Perfil dos Usuários de PrEP", 
        "💊 Dispensas de PrEP", 
        "🤖 Análise Avançada (ML)", 
        "📈 Indicadores Nacionais de AIDS"
    ])

    with tab1:
        st.subheader("Análise Detalhada do Perfil dos Usuários de PrEP")
        if not df_usuarios_filtrado.empty:
            st.dataframe(df_usuarios_filtrado.head(100))
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Perfil por Raça/Cor**")
                fig_raca = px.pie(df_usuarios_filtrado, names='raca4_cat', title="Raça/Cor", hole=.3)
                st.plotly_chart(fig_raca, use_container_width=True)

                st.write("**Perfil por Escolaridade**")
                fig_esc = px.bar(df_usuarios_filtrado['escol4'].value_counts().reset_index(), x='escol4', y='count', title="Escolaridade")
                st.plotly_chart(fig_esc, use_container_width=True)
            with col2:
                st.write("**Perfil por Faixa Etária**")
                fig_idade = px.pie(df_usuarios_filtrado, names='fetar', title="Faixa Etária", hole=.3)
                st.plotly_chart(fig_idade, use_container_width=True)

                st.write("**Perfil por População/Gênero**")
                fig_pop = px.bar(df_usuarios_filtrado['Pop_genero_pratica'].value_counts().reset_index(), x='Pop_genero_pratica', y='count', title="População/Gênero")
                st.plotly_chart(fig_pop, use_container_width=True)
        else:
            st.warning("Não foram encontrados dados de usuários para a seleção atual.")

    with tab2:
        st.subheader("Análise Detalhada das Dispensas de PrEP")
        if not df_dispensas_filtrado.empty:
            st.info("A tabela abaixo exibe uma amostra. Os gráficos são calculados sobre o total de dados.")
            st.dataframe(df_dispensas_filtrado.head(100))
            
            df_dispensas_filtrado['dt_disp'] = pd.to_datetime(df_dispensas_filtrado['dt_disp'], errors='coerce')
            disp_por_mes = df_dispensas_filtrado.set_index('dt_disp').resample('M').size().reset_index(name='count')

            st.write("**Dispensas de PrEP ao longo do tempo**")
            fig_tempo = px.line(disp_por_mes, x='dt_disp', y='count', title='Evolução Mensal das Dispensas de PrEP')
            st.plotly_chart(fig_tempo, use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                st.write("**Tipo de Serviço de Atendimento**")
                fig_serv = px.pie(df_dispensas_filtrado, names='tp_servico_atendimento', title="Serviço", hole=.3)
                st.plotly_chart(fig_serv, use_container_width=True)
            with col2:
                st.write("**Tipo de Profissional**")
                fig_prof = px.pie(df_dispensas_filtrado, names='tp_profissional', title="Profissional", hole=.3)
                st.plotly_chart(fig_prof, use_container_width=True)
        else:
            st.warning("Não foram encontrados dados de dispensas para a seleção atual.")
            
    with tab3:
        if not df_usuarios_filtrado.empty:
            analise_avancada_publico(df_usuarios_filtrado)
        else:
            st.warning("Não há dados de usuários para realizar a análise avançada. Desative o filtro de SP se necessário.")

    with tab4:
        analise_indicadores_hiv(df_indicadores)


# ======================= FUNÇÃO PRINCIPAL =======================
def main():
    """Função principal que executa o aplicativo Streamlit."""
    st.title("❤️ Plataforma de Pesquisa e Análise sobre PrEP")

    if 'termo_aceito' not in st.session_state:
        st.session_state.termo_aceito = False

    if not st.session_state.termo_aceito:
        mostrar_termo_consentimento()
        return

    st.sidebar.success("Termo de consentimento aceito! ✅")
    st.sidebar.title("Menu de Navegação")
    menu = st.sidebar.radio(
        "Escolha uma seção:",
        ("🏠 Início", "📝 Realizar Pesquisa", "🤖 Análise da Pesquisa", "📊 Dados Oficiais", "❔ Dúvidas Frequentes", "📍 Onde Encontrar a PrEP")
    )
    
    criar_banco()

    if menu == "🏠 Início":
        st.header("Bem-vindo(a) à Plataforma!")
        st.markdown("""
        Esta é uma ferramenta para coletar e analisar dados sobre o conhecimento e acesso à PrEP no Brasil. 
        Sua participação é fundamental para entendermos o cenário atual e ajudarmos a aprimorar as políticas de saúde.

        ### Como funciona?
        - **Realizar Pesquisa:** Participe do nosso questionário anônimo. Leva menos de 5 minutos!
        - **Análise da Pesquisa:** Veja os resultados da pesquisa em tempo real, com gráficos interativos.
        - **Dados Oficiais:** Explore os dados públicos sobre o uso de PrEP e os indicadores de HIV/AIDS no país.
        - **Dúvidas Frequentes:** Tire suas principais dúvidas sobre a PrEP.
        - **Onde Encontrar a PrEP:** Encontre locais de atendimento em São Paulo.

        Use o menu na barra lateral para navegar entre as seções.
        """)

    elif menu == "📝 Realizar Pesquisa":
        mostrar_pesquisa()

    elif menu == "🤖 Análise da Pesquisa":
        analise_com_machine_learning()

    elif menu == "📊 Dados Oficiais":
        mostrar_dados_oficiais()

    elif menu == "❔ Dúvidas Frequentes":
        mostrar_duvidas_frequentes()

    elif menu == "📍 Onde Encontrar a PrEP":
        mostrar_onde_encontrar()

if __name__ == "__main__":
    main()

