# -*- coding: utf-8 -*-
"""
PrEP - Análise Inteligente de Dados
Versão Final com Dados Integrados, Pesquisa e Análise de Machine Learning.
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
    st.info("💡 Use o filtro abaixo para visualizar os dados de usuários e dispensas apenas do estado de São Paulo.")
    filtro_sp = st.toggle("Mostrar apenas dados de São Paulo (SP)", help="Ative para filtrar os dados da PrEP para o estado de SP.")

    df_usuarios_filtrado = df_usuarios.copy()
    df_dispensas_filtrado = df_dispensas.copy()

    if filtro_sp:
        if 'UF_UDM' in df_usuarios.columns:
            df_usuarios_filtrado = df_usuarios[df_usuarios['UF_UDM'] == 'SP']
        if 'UF_UDM' in df_dispensas.columns:
            df_dispensas_filtrado = df_dispensas[df_dispensas['UF_UDM'] == 'SP']
        st.success(f"Filtro aplicado! Mostrando dados de São Paulo.")

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
        st.subheader("Indicadores de HIV/AIDS (Ministério da Saúde)")
        if df_indicadores:
            st.info("Estes são os dados extraídos do arquivo 'indicadoresAids.xls'.")
            for sheet_name, df_sheet in df_indicadores.items():
                with st.expander(f"Visualizar Tabela: {sheet_name}"):
                    df_cleaned = df_sheet.dropna(how='all').dropna(axis=1, how='all')
                    st.dataframe(df_cleaned)
        else:
            st.warning("Não foi possível carregar os dados dos indicadores.")

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
        ("🏠 Início", "📝 Realizar Pesquisa", "🤖 Análise da Pesquisa", "📊 Dados Oficiais")
    )
    
    criar_banco()

    if menu == "🏠 Início":
        st.header("Bem-vindo(a) à Plataforma!")
        st.markdown("""
        Esta é uma ferramenta para coletar e analisar dados sobre o conhecimento e acesso à PrEP no Brasil. 
        Sua participação é fundamental para entendermos o cenário atual e ajudarmos a aprimorar as políticas de saúde.

        ### Como funciona?
        - **Realizar Pesquisa:** Participe do nosso questionário anônimo. Leva menos de 5 minutos!
        - **Análise da Pesquisa:** Veja os resultados da pesquisa em tempo real, com gráficos interativos que mostram o perfil dos participantes.
        - **Dados Oficiais:** Explore os dados públicos do Ministério da Saúde sobre o uso de PrEP e os indicadores de HIV/AIDS no país.

        Use o menu na barra lateral para navegar entre as seções.
        """)
        st.image("https://placehold.co/800x300/E8D5C4/65451F?text=Sa%C3%BAde+%C3%A9+Preven%C3%A7%C3%A3o", caption="A informação é a melhor ferramenta de prevenção.")

    elif menu == "📝 Realizar Pesquisa":
        mostrar_pesquisa()

    elif menu == "🤖 Análise da Pesquisa":
        analise_com_machine_learning()

    elif menu == "📊 Dados Oficiais":
        mostrar_dados_oficiais()

if __name__ == "__main__":
    main()

