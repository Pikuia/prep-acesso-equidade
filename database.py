# database.py (Versão SQLite - Funciona Imediatamente)
import streamlit as st
import sqlite3
import pandas as pd

def criar_tabela_respostas():
    """Cria a tabela de respostas usando SQLite"""
    conn = sqlite3.connect('pesquisa_prep.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS respostas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        idade TEXT,
        genero TEXT,
        orientacao_sexual TEXT,
        raca TEXT,
        escolaridade TEXT,
        renda TEXT,
        regiao TEXT,
        status_relacional TEXT,
        conhecimento_prep TEXT,
        uso_prep TEXT,
        objetivo_prep TEXT,
        acesso_servico TEXT,
        fonte_info TEXT,
        barreiras TEXT,
        percepcao_risco INTEGER,
        efeitos_colaterais_teve TEXT,
        efeitos_colaterais_quais TEXT,
        comentarios TEXT
    )
    ''')
    conn.commit()
    conn.close()

def salvar_resposta(resposta):
    """Salva uma resposta no SQLite"""
    conn = sqlite3.connect('pesquisa_prep.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO respostas 
    (idade, genero, orientacao_sexual, raca, escolaridade, renda, regiao, status_relacional,
     conhecimento_prep, uso_prep, objetivo_prep, acesso_servico, fonte_info, barreiras, 
     percepcao_risco, efeitos_colaterais_teve, efeitos_colaterais_quais, comentarios)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', tuple(resposta.values()))
    conn.commit()
    conn.close()
    st.success("✅ Resposta enviada com sucesso!")
    st.balloons()

def buscar_respostas():
    """Busca todas as respostas do SQLite"""
    try:
        conn = sqlite3.connect('pesquisa_prep.db')
        df = pd.read_sql("SELECT * FROM respostas", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao buscar respostas: {e}")
        return pd.DataFrame()
