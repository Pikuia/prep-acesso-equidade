# database.py (Versão SQLite - Funciona Imediatamente)
import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
from backup_manager import BackupManager

def carregar_dados_iniciais():
    """Carrega dados iniciais do CSV se o banco estiver vazio"""
    try:
        conn = sqlite3.connect('pesquisa_prep.db')
        cursor = conn.cursor()
        
        # Verificar se já existem respostas
        cursor.execute("SELECT COUNT(*) FROM respostas")
        count = cursor.fetchone()[0]
        
        # Se não existem respostas e existe arquivo CSV, carregar dados
        if count == 0 and os.path.exists('dados_iniciais.csv'):
            df = pd.read_csv('dados_iniciais.csv')
            
            # Remover colunas id e data_envio do CSV (serão geradas automaticamente)
            if 'id' in df.columns:
                df = df.drop('id', axis=1)
            if 'data_envio' in df.columns:
                df = df.drop('data_envio', axis=1)
            
            # Inserir dados no banco
            df.to_sql('respostas', conn, if_exists='append', index=False)
            st.success(f"✅ {len(df)} respostas iniciais carregadas do arquivo de dados!")
            
        conn.close()
        
    except Exception as e:
        st.error(f"Erro ao carregar dados iniciais: {e}")

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
    
    # Carregar dados iniciais se necessário
    carregar_dados_iniciais()

def salvar_resposta(resposta):
    """Salva uma resposta no SQLite com backup automático"""
    try:
        # Salvar no banco principal
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
        
        # Criar backup automático após salvar
        backup_manager = BackupManager()
        backup_resultado = backup_manager.backup_completo()
        
        # Salvar também em arquivo CSV de emergência
        salvar_backup_csv_emergencia(resposta)
        
        st.success("✅ Resposta enviada e backup realizado com sucesso!")
        st.balloons()
        
        # Mostrar informações do backup (opcional, para transparência)
        with st.expander("ℹ️ Informações do Backup"):
            st.write(f"**Total de respostas salvas:** {backup_manager.contar_respostas()}")
            if backup_resultado['csv_backup']:
                st.write(f"**Backup CSV:** {os.path.basename(backup_resultado['csv_backup'])}")
            if backup_resultado['json_backup']:
                st.write(f"**Backup JSON:** {os.path.basename(backup_resultado['json_backup'])}")
    
    except Exception as e:
        st.error(f"Erro ao salvar resposta: {e}")
        # Tentar salvar pelo menos no arquivo de emergência
        salvar_backup_csv_emergencia(resposta)

def salvar_backup_csv_emergencia(resposta):
    """Salva resposta em CSV de emergência caso o banco falhe"""
    try:
        timestamp = datetime.now().isoformat()
        resposta_com_timestamp = {'timestamp': timestamp, **resposta}
        
        # Criar DataFrame
        df = pd.DataFrame([resposta_com_timestamp])
        
        arquivo_emergencia = 'respostas_emergencia.csv'
        
        # Verificar se arquivo existe para append
        if os.path.exists(arquivo_emergencia):
            df.to_csv(arquivo_emergencia, mode='a', header=False, index=False)
        else:
            df.to_csv(arquivo_emergencia, index=False)
            
    except Exception as e:
        print(f"Erro no backup de emergência: {e}")

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
