# mapa_interativo.py
import streamlit as st
import pandas as pd
import plotly.express as px
from database import buscar_respostas

def mostrar_mapa_interativo():
    st.header("🗺️ Mapa Interativo de Respostas")
    
    df_respostas = buscar_respostas()
    
    if df_respostas.empty:
        st.warning("Ainda não há respostas para mostrar no mapa.")
        return
    
    # Contar respostas por estado
    contagem_estados = df_respostas['regiao'].value_counts().reset_index()
    contagem_estados.columns = ['estado', 'quantidade']
    
    # Mapa do Brasil
    fig = px.choropleth(contagem_estados,
                        locations='estado',
                        locationmode="ISO-3",
                        color='quantidade',
                        scope="south america",
                        title="Distribuição de Respostas por Estado",
                        color_continuous_scale="Blues")
    
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Métricas por região
    st.subheader("Métricas por Região")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Estado com Mais Respostas", 
                 contagem_estados.iloc[0]['estado'] if not contagem_estados.empty else "N/A",
                 contagem_estados.iloc[0]['quantidade'] if not contagem_estados.empty else 0)
    
    with col2:
        total_respostas = contagem_estados['quantidade'].sum()
        st.metric("Total de Respostas", total_respostas)
    
    with col3:
        estados_atingidos = len(contagem_estados)
        st.metric("Estados Atingidos", estados_atingidos)
