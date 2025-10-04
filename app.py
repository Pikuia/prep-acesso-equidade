# app.py
import streamlit as st
from database import criar_tabela_respostas
from ui_pages import mostrar_pesquisa, mostrar_analise_pesquisa, mostrar_duvidas_frequentes, mostrar_onde_encontrar
from analysis import mostrar_dados_oficiais
from analise_comparativa.Comparativa import mostrar_pagina_comparativa
from mapa_interativo import mostrar_mapa_interativo

st.set_page_config(page_title="PrEP - Análise Inteligente", page_icon="❤️", layout="wide")

def mostrar_termo_consentimento():
    st.header("Termo de Consentimento")
    try:
        with open("termo_consentimento.md", "r", encoding="utf-8") as f:
            st.markdown(f.read(), unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("Arquivo do termo não encontrado.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Aceito participar"):
            st.session_state.termo_aceito = True
            st.rerun()
    with col2:
        if st.button("❌ Não aceito"):
            st.stop()

def main():
    if 'termo_aceito' not in st.session_state:
        st.session_state.termo_aceito = False

    if not st.session_state.termo_aceito:
        mostrar_termo_consentimento()
        return

    st.sidebar.success("Termo aceito! ✅")
    st.sidebar.title("Navegação")
    
    menu = st.sidebar.radio("Seções:", [
        "🏠 Início", "📝 Pesquisa", "🤖 Análise da Pesquisa", "🗺️ Mapa Interativo",
        "📊 Dados Oficiais", "🔬 Análise Comparativa", "❔ Dúvidas", "📍 Onde Encontrar"
    ])

    criar_tabela_respostas()

    if menu == "🏠 Início":
        st.title("❤️ Plataforma de Pesquisa sobre PrEP")
        st.markdown("""
        Bem-vindo(a) à plataforma do nosso Projeto Integrador! 
        Esta ferramenta coleta e analisa dados sobre conhecimento e acesso à PrEP no Brasil.
        
        ### Funcionalidades:
        - **📝 Pesquisa**: Questionário anônimo sobre PrEP (5 minutos)
        - **🤖 Análise**: Resultados em tempo real da pesquisa
        - **🗺️ Mapa Interativo**: Visualização das respostas por estado
        - **📊 Dados Oficiais**: Dados públicos do Ministério da Saúde
        - **🔬 Comparativa**: Compare dados da pesquisa com oficiais
        - **❔ Dúvidas**: Tire suas dúvidas sobre PrEP
        - **📍 Onde Encontrar**: Locais de atendimento em SP
        """)

    elif menu == "📝 Pesquisa":
        mostrar_pesquisa()
    elif menu == "🤖 Análise da Pesquisa":
        mostrar_analise_pesquisa()
    elif menu == "🗺️ Mapa Interativo":
        mostrar_mapa_interativo()
    elif menu == "📊 Dados Oficiais":
        mostrar_dados_oficiais()
    elif menu == "🔬 Análise Comparativa":
        mostrar_pagina_comparativa()
    elif menu == "❔ Dúvidas":
        mostrar_duvidas_frequentes()
    elif menu == "📍 Onde Encontrar":
        mostrar_onde_encontrar()

if __name__ == "__main__":
    main()
