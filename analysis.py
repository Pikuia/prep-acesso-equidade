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

    # Aplicar traduções
    df_usuarios_traduzido = traduzir_colunas(df_usuarios)
    
    st.info("💡 Dados públicos do Ministério da Saúde sobre usuários de PrEP")
    
    tab1, tab2, tab3 = st.tabs(["👤 Perfil dos Usuários", "💊 Dispensas", "📈 Indicadores HIV"])
    
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
            st.write("Dados de dispensas de medicamentos PrEP")
            # Adicionar gráficos de dispensas aqui

    with tab3:
        if df_indicadores:
            st.write("Indicadores nacionais de HIV/AIDS")
            # Adicionar análise dos indicadores aqui

# (Copiar funções de machine learning do código original aqui)