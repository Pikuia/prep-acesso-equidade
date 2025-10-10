# app.py
import streamlit as st
from database import criar_tabela_respostas
from ui_pages import mostrar_pesquisa, mostrar_analise_pesquisa, mostrar_duvidas_frequentes, mostrar_onde_encontrar
from analysis import mostrar_dados_oficiais
from analise_comparativa.Comparativa import mostrar_pagina_comparativa

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

    if 'pesquisa_enviada' not in st.session_state:
        st.session_state.pesquisa_enviada = False

    if not st.session_state.pesquisa_enviada:
        mostrar_pesquisa()
        # A função mostrar_pesquisa define st.session_state.pesquisa_enviada = True após envio
        return

    st.sidebar.success("Termo aceito! ✅")
    st.sidebar.title("Navegação")
    menu = st.sidebar.radio("Seções:", [
        "🤖 Análise da Pesquisa",
        "📊 Dados Oficiais",
        "🔬 Análise Comparativa",
        "❔ Dúvidas",
        "📍 Onde Encontrar"
    ])

    criar_tabela_respostas()

    if menu == "🤖 Análise da Pesquisa":
        mostrar_analise_pesquisa()
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
