# Análise Comparativa/Comparativa.py
import streamlit as st
import pandas as pd
import plotly.express as px
from database import buscar_respostas
from analysis import carregar_dados_publicos

def mostrar_pagina_comparativa():
    st.header("🔬 Comparação: Pesquisa vs Dados Oficiais")
    
    df_pesquisa = buscar_respostas()
    df_publico, _, _ = carregar_dados_publicos()
    
    if df_pesquisa.empty or df_publico.empty:
        st.warning("Precisa de dados da pesquisa e públicos para comparar")
        return

    # Filtrar dados públicos para SP
    df_publico_sp = df_publico[df_publico['UF_UDM'] == 'SP'].copy()
    
    st.subheader("Comparativo por Raça/Cor")
    
    # Preparar dados da pesquisa
    dist_pesquisa = df_pesquisa['raca'].value_counts(normalize=True).reset_index()
    dist_pesquisa.columns = ['raca', 'percentual']
    dist_pesquisa['fonte'] = 'Nossa Pesquisa'
    
    # Preparar dados públicos
    df_publico_sp.rename(columns={'raca4_cat': 'raca'}, inplace=True)
    dist_publico = df_publico_sp['raca'].value_counts(normalize=True).reset_index()
    dist_publico.columns = ['raca', 'percentual']
    dist_publico['fonte'] = 'Dados Oficiais (SP)'
    
    # Combinar
    df_comparativo = pd.concat([dist_pesquisa, dist_publico])
    
    # Gráfico
    fig = px.bar(df_comparativo, x='raca', y='percentual', color='fonte',
                 barmode='group', title='Distribuição por Raça/Cor',
                 labels={'percentual': 'Percentual', 'raca': 'Raça/Cor'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    **Interpretação:** Compare as barras para ver se o perfil dos respondentes 
    da pesquisa é similar ao perfil geral dos usuários de PrEP em São Paulo.
    """)