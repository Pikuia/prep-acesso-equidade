import streamlit as st
import mysql.connector
import pandas as pd

# Inicializa a conexão. Usa o cache do Streamlit para evitar reconectar a cada interação.
@st.cache_resource
def init_connection():
    return mysql.connector.connect(**st.secrets["mysql"])

# Função para criar a tabela (se não existir)
def criar_tabela_respostas():
    conn = init_connection()
    cursor = conn.cursor()
    # Query adaptada para MySQL com mais campos do novo questionário
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS respostas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        idade VARCHAR(255),
        genero VARCHAR(255),
        orientacao_sexual VARCHAR(255),
        raca VARCHAR(255),
        escolaridade VARCHAR(255),
        renda VARCHAR(255),
        regiao VARCHAR(255),
        conhecimento_prep VARCHAR(255),
        uso_prep VARCHAR(255),
        acesso_servico VARCHAR(255),
        fonte_info TEXT,
        barreiras TEXT,
        percepcao_risco INT,
        comentarios TEXT
    )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# Função para salvar a resposta
def salvar_resposta(resposta):
    conn = init_connection()
    cursor = conn.cursor()
    query = '''
    INSERT INTO respostas (idade, genero, orientacao_sexual, raca, escolaridade, renda, regiao, 
     conhecimento_prep, uso_prep, acesso_servico, fonte_info, barreiras, percepcao_risco, comentarios)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    cursor.execute(query, tuple(resposta.values()))
    conn.commit()
    cursor.close()
    conn.close()

# Função para buscar todas as respostas
def buscar_respostas():
    conn = init_connection()
    df = pd.read_sql("SELECT * FROM respostas", conn)
    conn.close()
    return df