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

    if df_pesquisa is None or df_publico is None or df_pesquisa.empty or df_publico.empty:
        st.warning("Precisa de dados da pesquisa e públicos para comparar")
        return

    # Função para comparar dados exclusivos da pesquisa
    def comparar_pesquisa(col, titulo, rotulo):
        dist = df_pesquisa[col].value_counts(normalize=True).reset_index()
        dist.columns = [rotulo, 'percentual']
        fig = px.bar(dist, x=rotulo, y='percentual', title=titulo,
                     labels={'percentual': 'Percentual', rotulo: rotulo})
        st.plotly_chart(fig, use_container_width=True)

    # Novos campos exclusivos da pesquisa
    if 'status_relacional' in df_pesquisa.columns:
        st.subheader("Status Relacional (Pesquisa)")
        comparar_pesquisa('status_relacional', 'Status Relacional', 'Status Relacional')

    if 'objetivo_prep' in df_pesquisa.columns:
        st.subheader("Objetivo do uso da PrEP (Pesquisa)")
        comparar_pesquisa('objetivo_prep', 'Objetivo do uso da PrEP', 'Objetivo PrEP')

    # Filtrar dados públicos para SP
    df_publico_sp = df_publico[df_publico['UF_UDM'] == 'SP'].copy()
    df_publico_sp = df_publico_sp.rename(columns={
        'raca4_cat': 'raca',
        'fetar': 'idade',
        'Pop_genero_pratica': 'genero',
        'escol4': 'escolaridade',
        'renda': 'renda',
        'UF_UDM': 'regiao'
    })

    def comparar_coluna(col_pesquisa, col_publico, titulo, rotulo):
        dist_pesquisa = df_pesquisa[col_pesquisa].value_counts(normalize=True).reset_index()
        dist_pesquisa.columns = [rotulo, 'percentual']
        dist_pesquisa['fonte'] = 'Nossa Pesquisa'

        dist_publico = df_publico_sp[col_publico].value_counts(normalize=True).reset_index()
        dist_publico.columns = [rotulo, 'percentual']
        dist_publico['fonte'] = 'Dados Oficiais (SP)'

        df_comparativo = pd.concat([dist_pesquisa, dist_publico])
        fig = px.bar(df_comparativo, x=rotulo, y='percentual', color='fonte',
                     barmode='group', title=titulo,
                     labels={'percentual': 'Percentual', rotulo: rotulo})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Comparativo por Raça/Cor")
    comparar_coluna('raca', 'raca', 'Distribuição por Raça/Cor', 'Raça/Cor')

    st.subheader("Comparativo por Faixa Etária")
    comparar_coluna('idade', 'idade', 'Distribuição por Faixa Etária', 'Faixa Etária')

    st.subheader("Comparativo por Gênero")
    comparar_coluna('genero', 'genero', 'Distribuição por Gênero', 'Gênero')

    st.subheader("Comparativo por Escolaridade")
    comparar_coluna('escolaridade', 'escolaridade', 'Distribuição por Escolaridade', 'Escolaridade')

    # Renda e Região podem não existir nos dados oficiais, mas tentamos
    if 'renda' in df_pesquisa.columns and 'renda' in df_publico_sp.columns:
        st.subheader("Comparativo por Renda")
        comparar_coluna('renda', 'renda', 'Distribuição por Renda', 'Renda')

    if 'regiao' in df_pesquisa.columns and 'regiao' in df_publico_sp.columns:
        st.subheader("Comparativo por Região")
        comparar_coluna('regiao', 'regiao', 'Distribuição por Região', 'Região')

    # Dados exclusivos da pesquisa
    def comparar_pesquisa(col, titulo, rotulo):
        dist = df_pesquisa[col].value_counts(normalize=True).reset_index()
        dist.columns = [rotulo, 'percentual']
        fig = px.bar(dist, x=rotulo, y='percentual', title=titulo,
                     labels={'percentual': 'Percentual', rotulo: rotulo})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Conhecimento sobre PrEP (Pesquisa)")
    comparar_pesquisa('conhecimento_prep', 'Conhecimento sobre PrEP', 'Conhecimento PrEP')

    st.subheader("Uso de PrEP (Pesquisa)")
    comparar_pesquisa('uso_prep', 'Uso de PrEP', 'Uso PrEP')

    st.subheader("Barreiras para uso de PrEP (Pesquisa)")
    comparar_pesquisa('barreiras', 'Barreiras para uso de PrEP', 'Barreiras')

    st.subheader("Percepção de risco de HIV (Pesquisa)")
    comparar_pesquisa('percepcao_risco', 'Percepção de risco de HIV', 'Percepção de Risco')

    st.subheader("Efeitos colaterais (Pesquisa)")
    comparar_pesquisa('efeitos_colaterais_teve', 'Efeitos colaterais', 'Efeitos Colaterais')

    st.subheader("Efeitos colaterais - quais (Pesquisa)")
    comparar_pesquisa('efeitos_colaterais_quais', 'Quais efeitos colaterais', 'Efeitos Colaterais Quais')

    st.subheader("Comentários (Pesquisa)")
    if 'comentarios' in df_pesquisa.columns:
        st.write("Exemplo de comentários recebidos:")
        for c in df_pesquisa['comentarios'].dropna().head(5):
            st.info(c)