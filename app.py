"""
PrEP - Análise Inteligente de Dados
Versão Aprimorada com Análises Geográficas, Temporais e de Texto.
"""
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
import warnings
import folium
from streamlit_folium import st_folium
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import requests

warnings.filterwarnings('ignore')

# ======================= CONFIGURAÇÃO DA PÁGINA =======================
st.set_page_config(page_title="PrEP - Pesquisa Inteligente", page_icon="❤️", layout="wide")

# ======================= BANCO DE DADOS DA PESQUISA =======================
def criar_banco():
    conn = sqlite3.connect('pesquisa_prep.db', timeout=20)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS respostas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_resposta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        idade TEXT, genero TEXT, raca TEXT, escolaridade TEXT, renda TEXT,
        conhece_prep TEXT, usou_prep TEXT, acesso_facil TEXT,
        fonte_info TEXT, barreiras TEXT, percepcao_risco TEXT, comentarios TEXT
    )
    ''')
    conn.commit()
    conn.close()

def salvar_resposta(resposta):
    conn = sqlite3.connect('pesquisa_prep.db', timeout=20)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO respostas (idade, genero, raca, escolaridade, renda, conhece_prep, 
                           usou_prep, acesso_facil, fonte_info, barreiras, 
                           percepcao_risco, comentarios)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', tuple(resposta.values()))
    conn.commit()
    conn.close()

# ======================= CARREGAMENTO DOS DADOS PÚBLICOS =======================
@st.cache_data(ttl=3600)
def carregar_dados_prep():
    try:
        df_usuarios = pd.read_csv('data/Banco_PrEP_usuarios.csv', encoding='utf-8')
        df_dispensas = pd.read_csv('data/Banco_PrEP_dispensas.csv', encoding='utf-8')
        return df_usuarios, df_dispensas
    except FileNotFoundError:
        st.error("Erro: Arquivos de dados não encontrados. Certifique-se de que a pasta 'data' existe e contém os arquivos necessários.")
        return pd.DataFrame(), pd.DataFrame()

@st.cache_data(ttl=3600)
def carregar_dados_hiv():
    try:
        # Leitura inteligente do arquivo Excel, pulando as linhas iniciais de cabeçalho
        df_aids = pd.read_excel('data/indicadoresAids.xls', sheet_name='Boletim', header=6)
        return df_aids
    except FileNotFoundError:
        st.error("Erro: Arquivo 'indicadoresAids.xls' não encontrado na pasta 'data'.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Ocorreu um erro ao ler o arquivo de indicadores de AIDS: {e}")
        return pd.DataFrame()

# ======================= MÓDULOS DE ANÁLISE =======================

def gerar_nuvem_palavras(df_pesquisa):
    st.subheader("💭 Nuvem de Palavras dos Comentários")
    texto_comentarios = ' '.join(df_pesquisa['comentarios'].dropna().astype(str))

    if not texto_comentarios.strip():
        st.warning("Ainda não há comentários suficientes para gerar a nuvem de palavras.")
        return

    # Lista de stopwords em português
    stopwords = set(['de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'à', 'seu', 'sua'])

    try:
        wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='viridis', stopwords=stopwords).generate(texto_comentarios)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Não foi possível gerar a nuvem de palavras: {e}")

def grafico_tendencia_temporal(df_dispensas):
    st.subheader("📈 Tendência Temporal de Dispensas de PrEP")
    df_temporal = df_dispensas.copy()
    df_temporal['dt_disp'] = pd.to_datetime(df_temporal['dt_disp'], errors='coerce')
    df_temporal.dropna(subset=['dt_disp'], inplace=True)
    df_temporal['ano_mes'] = df_temporal['dt_disp'].dt.to_period('M').astype(str)
    
    contagem_mensal = df_temporal.groupby('ano_mes').size().reset_index(name='contagem')
    contagem_mensal = contagem_mensal.sort_values('ano_mes')
    
    fig = px.line(contagem_mensal, x='ano_mes', y='contagem', title='Evolução Mensal de Dispensas de PrEP', labels={'ano_mes': 'Mês', 'contagem': 'Número de Dispensas'}, markers=True)
    st.plotly_chart(fig, use_container_width=True)

@st.cache_resource
def get_geojson():
    url_geojson = 'https://raw.githubusercontent.com/luizbd/mapa-brasil-estado/master/estados.json'
    response = requests.get(url_geojson)
    return response.json()

def mapa_geografico(df_usuarios):
    st.subheader("🗺️ Mapa de Calor de Usuários de PrEP no Brasil")
    st.info("O mapa abaixo exibe a concentração de usuários de PrEP por estado. As cores mais intensas indicam um maior número de usuários.")
    
    contagem_estados = df_usuarios['UF_UDM'].value_counts().reset_index()
    contagem_estados.columns = ['estado', 'usuarios']
    
    try:
        geojson_brasil = get_geojson()
        
        m = folium.Map(location=[-14.2350, -51.9253], zoom_start=4, tiles='CartoDB positron')
        
        folium.Choropleth(
            geo_data=geojson_brasil,
            name='choropleth',
            data=contagem_estados,
            columns=['estado', 'usuarios'],
            key_on='feature.properties.sigla',
            fill_color='YlOrRd',
            fill_opacity=0.8,
            line_opacity=0.2,
            legend_name='Número de Usuários de PrEP por Estado'
        ).add_to(m)
        
        st_folium(m, width=725, height=500)
    except Exception as e:
        st.error(f"Não foi possível gerar o mapa geográfico: {e}")


# ======================= PÁGINAS DA APLICAÇÃO =======================

def pagina_inicio():
    st.title("Plataforma de Pesquisa e Análise sobre PrEP ❤️")
    st.markdown("""
    Esta é uma ferramenta para coletar e analisar dados sobre o conhecimento e acesso à PrEP no Brasil. 
    Sua participação é fundamental para entendermos o cenário atual e ajudarmos a aprimorar as políticas de saúde.
    
    **Como funciona?**
    - **Realizar Pesquisa:** Participe do nosso questionário anônimo. Leva menos de 5 minutos!
    - **Análise da Pesquisa:** Veja os resultados da pesquisa em tempo real, com gráficos interativos.
    - **Dados Oficiais:** Explore os dados públicos do Ministério da Saúde sobre o uso de PrEP e os indicadores de HIV/AIDS.
    
    Use o menu na barra lateral para navegar entre as seções.
    """)

def pagina_pesquisa():
    st.title("📝 Pesquisa - Conhecimento sobre PrEP/PEP")
    st.info("Por favor, responda às perguntas abaixo. Suas respostas são anônimas e muito importantes.")
    with st.form("formulario_pesquisa"):
        # Seção 1: Perfil Demográfico
        st.subheader("1. Perfil Demográfico")
        idade = st.selectbox("Qual sua faixa etária?", ["18-24 anos", "25-34 anos", "35-44 anos", "45-54 anos", "55+ anos", "Prefiro não informar"])
        genero = st.selectbox("Com qual gênero você se identifica?", ["Homem Cis", "Mulher Cis", "Homem Trans", "Mulher Trans", "Não-binário", "Prefiro não informar"])
        raca = st.selectbox("Como você se autodeclara em relação à raça/cor?", ["Branca", "Preta", "Parda", "Amarela", "Indígena", "Prefiro não informar"])
        escolaridade = st.selectbox("Qual seu nível de escolaridade?", ["Ensino Fundamental", "Ensino Médio", "Ensino Superior", "Pós-graduação", "Prefiro não informar"])
        renda = st.selectbox("Qual sua renda familiar mensal?", ["Até 1 salário mínimo", "Entre 1 e 3 salários", "Entre 3 e 5 salários", "Acima de 5 salários", "Prefiro não informar"])
        
        # Seção 2: Conhecimento e Acesso
        st.subheader("2. Conhecimento e Acesso à PrEP")
        conhece_prep = st.radio("Você já ouviu falar sobre a PrEP?", ["Sim, conheço bem", "Já ouvi falar superficialmente", "Nunca ouvi falar"])
        usou_prep = st.radio("Você já utilizou ou utiliza a PrEP?", ["Sim, uso atualmente", "Já usei no passado", "Nunca usei, mas tenho interesse", "Nunca usei e não tenho interesse"])
        acesso_facil = st.radio("Você sabe onde encontrar a PrEP gratuitamente?", ["Sim", "Não", "Tenho dúvidas"])
        
        # Seção 3: Percepções e Barreiras
        st.subheader("3. Percepções e Barreiras")
        fonte_info = st.selectbox("Onde você mais ouviu falar sobre PrEP?", ["Profissionais de saúde", "Amigos ou parceiros(as)", "Redes sociais (Instagram, TikTok, etc.)", "Mídia tradicional (TV, rádio)", "Sites de busca (Google)", "Não ouvi falar"])
        barreiras = st.selectbox("Na sua opinião, qual a maior dificuldade para as pessoas usarem a PrEP?", ["Falta de informação", "Medo de efeitos colaterais", "Vergonha ou estigma", "Dificuldade de acesso ao serviço de saúde", "Acho que não preciso", "Outro"])
        percepcao_risco = st.radio("Como você avalia seu risco pessoal de contrair HIV atualmente?", ["Alto", "Médio", "Baixo", "Nenhum", "Não sei avaliar"])
        
        comentarios = st.text_area("Se quiser, deixe um comentário, sugestão ou relate sua experiência:")
        
        submitted = st.form_submit_button("✅ Enviar Resposta")
        if submitted:
            resposta = {
                'idade': idade, 'genero': genero, 'raca': raca, 'escolaridade': escolaridade, 'renda': renda,
                'conhece_prep': conhece_prep, 'usou_prep': usou_prep, 'acesso_facil': acesso_facil,
                'fonte_info': fonte_info, 'barreiras': barreiras, 'percepcao_risco': percepcao_risco,
                'comentarios': comentarios
            }
            salvar_resposta(resposta)
            st.success("Obrigado! Sua resposta foi registrada com sucesso.")

def pagina_analise_pesquisa():
    st.title("📊 Análise da Pesquisa (Resultados em Tempo Real)")
    conn = sqlite3.connect('pesquisa_prep.db')
    try:
        df_respostas = pd.read_sql_query("SELECT * FROM respostas", conn)
    except pd.io.sql.DatabaseError:
        st.warning("O banco de dados da pesquisa está sendo criado. Responda à pesquisa para começar a ver os dados.")
        return
    finally:
        conn.close()

    if df_respostas.empty:
        st.info("Ainda não há respostas. Seja o primeiro a participar da pesquisa!")
        return

    st.metric("Total de Respostas Coletadas", len(df_respostas))
    
    st.subheader("Recorte por Perfil Demográfico")
    col1, col2 = st.columns(2)
    with col1:
        fig_idade = px.pie(df_respostas, names='idade', title='Distribuição por Idade')
        st.plotly_chart(fig_idade, use_container_width=True)
        fig_raca = px.pie(df_respostas, names='raca', title='Distribuição por Raça/Cor')
        st.plotly_chart(fig_raca, use_container_width=True)
    with col2:
        fig_genero = px.pie(df_respostas, names='genero', title='Distribuição por Gênero')
        st.plotly_chart(fig_genero, use_container_width=True)
        fig_escolaridade = px.pie(df_respostas, names='escolaridade', title='Distribuição por Escolaridade')
        st.plotly_chart(fig_escolaridade, use_container_width=True)
        
    gerar_nuvem_palavras(df_respostas)


def pagina_dados_oficiais():
    st.title("📈 Dados Oficiais sobre PrEP e HIV/AIDS no Brasil")
    
    df_usuarios, df_dispensas = carregar_dados_prep()
    
    if df_usuarios.empty or df_dispensas.empty:
        return

    # Filtro para São Paulo
    apenas_sp = st.checkbox("Mostrar apenas dados de PrEP de São Paulo (SP)")
    if apenas_sp:
        df_usuarios = df_usuarios[df_usuarios['UF_UDM'] == 'SP']
        df_dispensas = df_dispensas[df_dispensas['UF_UDM'] == 'SP']

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Perfil dos Usuários", "Dispensas de PrEP", "Análise Geográfica e Temporal", "Análise Avançada (ML)", "Indicadores Nacionais de AIDS"])

    with tab1:
        st.header("Análise Detalhada do Perfil dos Usuários de PrEP")
        st.dataframe(df_usuarios.head())
        # Gráficos de Perfil
        col1, col2 = st.columns(2)
        with col1:
            fig_raca_prep = px.pie(df_usuarios, names='raca4_cat', title='Perfil Racial dos Usuários de PrEP')
            st.plotly_chart(fig_raca_prep, use_container_width=True)
        with col2:
            fig_idade_prep = px.pie(df_usuarios, names='fetar', title='Perfil Etário dos Usuários de PrEP')
            st.plotly_chart(fig_idade_prep, use_container_width=True)

    with tab2:
        st.header("Análise Detalhada das Dispensas de PrEP")
        st.dataframe(df_dispensas.head())
        fig_servico = px.pie(df_dispensas, names='tp_servico_atendimento', title='Tipo de Serviço de Atendimento na Dispensação')
        st.plotly_chart(fig_servico, use_container_width=True)
    
    with tab3:
        st.header("Análise Geográfica e Temporal")
        grafico_tendencia_temporal(df_dispensas)
        mapa_geografico(df_usuarios)

    with tab4:
        st.header("Análise Avançada com Machine Learning")
        st.write("### 1. Identificação de Perfis de Usuários (Clusterização)")
        try:
            # Preparação dos dados para ML
            df_ml = df_usuarios[['raca4_cat', 'escol4', 'fetar', 'Pop_genero_pratica']].dropna()
            encoder = OneHotEncoder(handle_unknown='ignore')
            X_encoded = encoder.fit_transform(df_ml)
            
            # Clusterização
            kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
            df_ml['cluster'] = kmeans.fit_predict(X_encoded)
            
            st.write("Encontramos 4 perfis principais de usuários. Veja a descrição de cada um:")
            for i in range(4):
                st.write(f"**Perfil {i+1}:**")
                perfil_info = df_ml[df_ml['cluster'] == i].describe(include='object').loc['top']
                st.write(f"- **Gênero/Prática:** {perfil_info['Pop_genero_pratica']}")
                st.write(f"- **Faixa Etária:** {perfil_info['fetar']}")
                st.write(f"- **Raça/Cor:** {perfil_info['raca4_cat']}")
        except Exception as e:
            st.warning(f"Não foi possível executar a análise de clusterização. Erro: {e}")

    with tab5:
        st.header("Gráficos sobre HIV/AIDS no Brasil (Dados Nacionais)")
        st.info("Estes gráficos são baseados nos dados nacionais e não são afetados pelo filtro de estado.")
        df_aids = carregar_dados_hiv()
        if not df_aids.empty:
            try:
                # Gráfico 1: Evolução dos Casos
                tabela1 = df_aids.iloc[1:2, 3:15].T.reset_index()
                tabela1.columns = ['Ano', 'Novos Casos']
                tabela1['Ano'] = tabela1['Ano'].astype(str).str.replace('.0', '', regex=False)
                fig_casos = px.bar(tabela1, x='Ano', y='Novos Casos', title='Evolução dos Casos de AIDS no Brasil (2013-2023)')
                st.plotly_chart(fig_casos)
            except Exception:
                st.warning("Não foi possível gerar o gráfico de 'Evolução dos Casos de AIDS'.")


# ======================= APLICAÇÃO PRINCIPAL =======================
def main():
    criar_banco()
    st.sidebar.title("Menu de Navegação")
    menu = st.sidebar.radio("Escolha uma seção:", ["Início", "Realizar Pesquisa", "Análise da Pesquisa", "Dados Oficiais"])

    if menu == "Início":
        pagina_inicio()
    elif menu == "Realizar Pesquisa":
        pagina_pesquisa()
    elif menu == "Análise da Pesquisa":
        pagina_analise_pesquisa()
    elif menu == "Dados Oficiais":
        pagina_dados_oficiais()

if __name__ == "__main__":
    main()

