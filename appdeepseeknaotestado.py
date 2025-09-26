# -*- coding: utf-8 -*-
"""
PrEP - Análise Inteligente de Dados (São Paulo)
Versão Simplificada com Machine Learning Integrado
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

# ======================= CONFIGURAÇÃO =======================
st.set_page_config(page_title="PrEP - Pesquisa Inteligente", page_icon="❤️", layout="wide")

# ======================= TERMO DE CONSENTIMENTO =======================
def mostrar_termo_consentimento():
    st.markdown("""
    ## TERMO DE CONSENTIMENTO LIVRE E ESCLARECIDO
    
    **Objetivo da Pesquisa:** 
    Esta pesquisa visa entender o conhecimento e uso da PrEP/PEP na população de São Paulo, 
    identificando gaps de acesso e representação para melhorar as políticas públicas.
    
    **Responsável pela pesquisa:** 
    Weslei - Projeto PrEP São Paulo
    
    **Descrição:** 
    Você está sendo convidado(a) para participar da pesquisa sobre prevenção ao HIV. 
    Buscamos entender como as pessoas conhecem e acessam métodos como PrEP e PEP.
    
    **Riscos e benefícios:** 
    Não existem riscos associados a este estudo. Os benefícios incluem contribuir para 
    melhorias nas políticas de prevenção ao HIV em nossa cidade.
    
    **Direitos do participante:** 
    - Sua participação é voluntária
    - Você pode desistir a qualquer momento
    - Seus dados serão mantidos em sigilo
    - Não haverá gastos ou ganhos financeiros
    
    **Ao clicar em "Aceito participar", você concorda com estes termos.**
    """)
    
    if st.button("✅ Aceito participar"):
        st.session_state.termo_aceito = True
        st.rerun()
    
    if st.button("❌ Recusar"):
        st.stop()
    
    return False

# ======================= BANCO DE DADOS =======================
def criar_banco():
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
        comentarios TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

def salvar_resposta(resposta):
    conn = sqlite3.connect('pesquisa_prep.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO respostas 
    (idade, genero, orientacao_sexual, raca, escolaridade, renda, regiao, 
     conhecimento_prep, uso_prep, acesso_servico, comentarios)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', tuple(resposta.values()))
    
    conn.commit()
    conn.close()

# ======================= CARREGAR DADOS PRÉP =======================
@st.cache_data
def carregar_dados_prep():
    try:
        # Carrega dados de usuários da PrEP
        df_usuarios = pd.read_csv('data/Banco_PrEP_usuarios.csv', encoding='utf-8')
        
        # Carrega dados de dispensas
        df_dispensas1 = pd.read_csv('data/Banco_PrEP_dispensas_1.csv', encoding='utf-8')
        df_dispensas2 = pd.read_csv('data/Banco_PrEP_dispensas_2.csv', encoding='utf-8')
        df_dispensas = pd.concat([df_dispensas1, df_dispensas2], ignore_index=True)
        
        return df_usuarios, df_dispensas
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame(), pd.DataFrame()

# ======================= MACHINE LEARNING =======================
def analise_machine_learning(df):
    st.subheader("🤖 Análise com Machine Learning")
    
    # Análise por Idade
    st.write("**Distribuição por Idade**")
    if 'idade' in df.columns:
        fig = px.histogram(df, x='idade', title="Distribuição por Faixa Etária")
        st.plotly_chart(fig)
    
    # Análise por Gênero
    st.write("**Distribuição por Gênero**")
    if 'genero' in df.columns:
        contagem_genero = df['genero'].value_counts()
        fig = px.pie(values=contagem_genero.values, names=contagem_genero.index, title="Distribuição por Gênero")
        st.plotly_chart(fig)
    
    # Análise por Raça/Cor
    st.write("**Distribuição por Raça/Cor**")
    if 'raca' in df.columns:
        contagem_raca = df['raca'].value_counts()
        fig = px.bar(x=contagem_raca.index, y=contagem_raca.values, title="Distribuição por Raça/Cor")
        st.plotly_chart(fig)

def criar_relatorio(df):
    st.subheader("📊 Relatório Automático")
    
    # Estatísticas básicas
    st.write(f"**Total de participantes:** {len(df)}")
    
    if len(df) > 0:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Conhecem PrEP", 
                     df[df['conhecimento_prep'].str.contains('Sim', na=False)].shape[0])
        
        with col2:
            st.metric("Já usaram PrEP", 
                     df[df['uso_prep'].str.contains('Sim', na=False)].shape[0])
        
        with col3:
            st.metric("Têm acesso fácil", 
                     df[df['acesso_servico'].str.contains('Sim', na=False)].shape[0])

# ======================= PESQUISA =======================
def mostrar_pesquisa():
    st.header("📝 Pesquisa - Conhecimento sobre PrEP/PEP")
    
    with st.form("formulario_pesquisa"):
        st.subheader("Dados Pessoais")
        
        col1, col2 = st.columns(2)
        
        with col1:
            idade = st.selectbox("Idade", 
                               ["18-24", "25-34", "35-44", "45-54", "55+"])
            
            genero = st.selectbox("Gênero",
                                ["Masculino", "Feminino", "Não-binário", "Transgênero", "Prefiro não informar"])
            
            orientacao = st.selectbox("Orientação Sexual",
                                    ["Heterossexual", "Homossexual", "Bissexual", "Pansexual", "Assexual", "Prefiro não informar"])
        
        with col2:
            raca = st.selectbox("Raça/Cor",
                              ["Branca", "Preta", "Parda", "Amarela", "Indígena", "Prefiro não informar"])
            
            escolaridade = st.selectbox("Escolaridade",
                                      ["Fundamental", "Médio", "Superior", "Pós-graduação"])
            
            renda = st.selectbox("Renda Mensal",
                               ["Até 1 salário", "1-2 salários", "2-5 salários", "Mais de 5 salários"])
        
        st.subheader("Sobre PrEP/PEP")
        
        conhecimento = st.radio("Você conhece a PrEP?",
                              ["Sim, conheço bem", "Já ouvi falar", "Não conheço"])
        
        uso = st.radio("Você já usou PrEP?",
                     ["Sim, uso atualmente", "Já usei no passado", "Nunca usei"])
        
        acesso = st.radio("Sabe onde conseguir PrEP gratuitamente?",
                        ["Sim", "Não", "Talvez"])
        
        comentarios = st.text_area("Comentários ou sugestões")
        
        if st.form_submit_button("Enviar Resposta"):
            resposta = {
                'idade': idade,
                'genero': genero,
                'orientacao_sexual': orientacao,
                'raca': raca,
                'escolaridade': escolaridade,
                'renda': renda,
                'regiao': "São Paulo",
                'conhecimento_prep': conhecimento,
                'uso_prep': uso,
                'acesso_servico': acesso,
                'comentarios': comentarios
            }
            
            salvar_resposta(resposta)
            st.success("✅ Resposta salva com sucesso!")

# ======================= DADOS PRÉP =======================
def mostrar_dados_prep():
    st.header("📈 Dados Oficiais da PrEP")
    
    df_usuarios, df_dispensas = carregar_dados_prep()
    
    if not df_usuarios.empty:
        st.subheader("Dados de Usuários da PrEP")
        st.dataframe(df_usuarios.head(10))
        
        # Análise rápida
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Total de usuários:**", len(df_usuarios))
            if 'raca4_cat' in df_usuarios.columns:
                st.write("**Distribuição racial:**")
                st.write(df_usuarios['raca4_cat'].value_counts())
        
        with col2:
            if 'fetar' in df_usuarios.columns:
                st.write("**Distribuição por idade:**")
                st.write(df_usuarios['fetar'].value_counts())
    
    if not df_dispensas.empty:
        st.subheader("Dados de Dispensação")
        st.dataframe(df_dispensas.head(10))

# ======================= PAINEL PRINCIPAL =======================
def main():
    st.title("❤️ PrEP - Pesquisa Inteligente São Paulo")
    
    # Verificar termo de consentimento
    if 'termo_aceito' not in st.session_state:
        st.session_state.termo_aceito = False
    
    if not st.session_state.termo_aceito:
        mostrar_termo_consentimento()
        return
    
    # Menu lateral
    menu = st.sidebar.selectbox("Navegação", 
                               ["🏠 Início", "📝 Fazer Pesquisa", "🤖 Análise dos Dados", "📊 Dados PrEP"])
    
    # Criar banco se não existir
    criar_banco()
    
    if menu == "🏠 Início":
        st.header("Bem-vindo à Pesquisa PrEP!")
        st.markdown("""
        Esta pesquisa ajuda a entender como a PrEP está sendo conhecida e usada em São Paulo.
        
        **Como participar:**
        1. Clique em "Fazer Pesquisa" no menu
        2. Responda as perguntas (leva 5 minutos)
        3. Veja os resultados em tempo real
        
        **Objetivos:**
        - Identificar gaps de conhecimento
        - Melhorar o acesso à PrEP
        - Direcionar políticas públicas
        """)
        
    elif menu == "📝 Fazer Pesquisa":
        mostrar_pesquisa()
        
    elif menu == "🤖 Análise dos Dados":
        # Carregar respostas do banco
        conn = sqlite3.connect('pesquisa_prep.db')
        df_respostas = pd.read_sql_query("SELECT * FROM respostas", conn)
        conn.close()
        
        if len(df_respostas) > 0:
            analise_machine_learning(df_respostas)
            criar_relatorio(df_respostas)
            
            # Mostrar dados brutos
            with st.expander("Ver todas as respostas"):
                st.dataframe(df_respostas)
        else:
            st.info("Ainda não há respostas. Faça a pesquisa primeiro!")
            
    elif menu == "📊 Dados PrEP":
        mostrar_dados_prep()

if __name__ == "__main__":
    main()