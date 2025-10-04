# analysis.py
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Mapeamento para nomes mais compreensíveis
TRADUCOES = {
    'raca4_cat': 'Raça/Cor',
    'escol4': 'Escolaridade', 
    'fetar': 'Faixa Etária',
    'Pop_genero_pratica': 'População/Gênero',
    'UF_UDM': 'Estado',
    'Disp_12m_2024': 'Continuou no Programa em 2024'
}

@st.cache_data
def carregar_dados_publicos():
    data_path = Path('data')
    try:
        df_usuarios = pd.read_csv(data_path / 'Banco_PrEP_usuarios.csv', encoding='latin1', sep=',')
        df_dispensas = pd.read_csv(data_path / 'Banco_PrEP_dispensas.csv', encoding='latin1', sep=',')
        df_indicadores = pd.read_excel(data_path / 'indicadoresAids.xls', sheet_name=None, header=None)
        return df_usuarios, df_dispensas, df_indicadores
    except FileNotFoundError:
        st.error("Arquivos de dados não encontrados na pasta 'data'")
        return pd.DataFrame(), pd.DataFrame(), None

def traduzir_colunas(df):
    return df.rename(columns=TRADUCOES)

def mostrar_dados_oficiais():
    st.header("📊 Dados Oficiais sobre PrEP")
    
    df_usuarios, df_dispensas, df_indicadores = carregar_dados_publicos()
    
    if df_usuarios.empty:
        st.warning("Dados não carregados")
        return

    df_usuarios_traduzido = traduzir_colunas(df_usuarios)
    
    st.info("💡 Dados públicos do Ministério da Saúde sobre usuários de PrEP")
    
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Perfil dos Usuários", "💊 Dispensas", "📈 Tendências", "🔍 Análises Avançadas"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            if 'Raça/Cor' in df_usuarios_traduzido.columns:
                fig_raca = px.pie(df_usuarios_traduzido, names='Raça/Cor', 
                                title="Distribuição por Raça/Cor")
                st.plotly_chart(fig_raca, use_container_width=True)
            
            if 'Escolaridade' in df_usuarios_traduzido.columns:
                fig_esc = px.bar(df_usuarios_traduzido['Escolaridade'].value_counts(),
                               title="Nível de Escolaridade")
                st.plotly_chart(fig_esc, use_container_width=True)
                
        with col2:
            if 'Faixa Etária' in df_usuarios_traduzido.columns:
                fig_idade = px.pie(df_usuarios_traduzido, names='Faixa Etária',
                                 title="Distribuição por Idade")
                st.plotly_chart(fig_idade, use_container_width=True)
            
            if 'População/Gênero' in df_usuarios_traduzido.columns:
                fig_pop = px.bar(df_usuarios_traduzido['População/Gênero'].value_counts(),
                               title="População/Gênero")
                st.plotly_chart(fig_pop, use_container_width=True)

    with tab2:
        if not df_dispensas.empty:
            st.subheader("Dispensas de PrEP ao Longo do Tempo")
            df_dispensas['dt_disp'] = pd.to_datetime(df_dispensas['dt_disp'], errors='coerce')
            disp_por_mes = df_dispensas.set_index('dt_disp').resample('M').size().reset_index(name='count')
            fig_tempo = px.line(disp_por_mes, x='dt_disp', y='count', 
                              title='Evolução Mensal das Dispensas de PrEP')
            st.plotly_chart(fig_tempo, use_container_width=True)
            
            st.subheader("Tipos de Serviços")
            col1, col2 = st.columns(2)
            with col1:
                fig_serv = px.pie(df_dispensas, names='tp_servico_atendimento', 
                                title="Tipo de Serviço")
                st.plotly_chart(fig_serv, use_container_width=True)
            with col2:
                fig_prof = px.pie(df_dispensas, names='tp_profissional', 
                                title="Tipo de Profissional")
                st.plotly_chart(fig_prof, use_container_width=True)

    with tab3:
        st.subheader("Análises de Tendência")
        st.info("Em breve: Análises de tendência temporal e projeções")

    with tab4:
        st.subheader("Análises Avançadas com Machine Learning")
        analise_avancada_publico(df_usuarios)

def analise_avancada_publico(df_usuarios):
    st.header("🤖 Análise Avançada com Machine Learning")
    st.info("Esta análise utiliza os dados públicos para identificar padrões.")
    st.warning("Funcionalidade em desenvolvimento - Machine Learning em breve!")

def analise_indicadores_hiv(df_indicadores):
    st.header("📈 Indicadores Nacionais de AIDS")
    st.warning("Análise de indicadores de HIV em desenvolvimento!")
