# ui_pages.py
import streamlit as st
import pandas as pd
import plotly.express as px
from database import salvar_resposta, buscar_respostas

def mostrar_pesquisa():
    st.header("📝 Pesquisa - Conhecimento sobre PrEP")
    
    with st.form("pesquisa_aprimorada"):
        st.subheader("1. Perfil Sociodemográfico")
        
        idade = st.selectbox("Faixa etária:", [
            "Prefiro não informar", "18-24 anos", "25-29 anos", "30-34 anos", 
            "35-39 anos", "40-49 anos", "50-59 anos", "60+ anos"
        ])
        
        genero = st.selectbox("Gênero:", [
            "Prefiro não informar", "Homem cis", "Mulher cis", "Homem trans", 
            "Mulher trans", "Não-binário", "Outro"
        ])
        
        orientacao = st.selectbox("Orientação sexual:", [
            "Prefiro não informar", "Heterossexual", "Homossexual", 
            "Bissexual", "Pansexual", "Assexual", "Outra"
        ])
        
        raca = st.selectbox("Raça/Cor:", [
            "Prefiro não informar", "Branca", "Preta", "Parda", "Amarela", "Indígena"
        ])
        
        escolaridade = st.selectbox("Escolaridade:", [
            "Prefiro não informar", "Fundamental", "Médio", "Superior", "Pós-graduação"
        ])
        
        renda = st.selectbox("Renda familiar:", [
            "Prefiro não informar", "Até 1 salário", "1-3 salários", 
            "3-5 salários", "Acima de 5 salários"
        ])
        
        regiao = st.selectbox("Estado:", [
            'SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'PE', 'CE', 'PA', 'MA', 'GO',
            'AM', 'ES', 'PB', 'RN', 'MT', 'AL', 'PI', 'DF', 'MS', 'SE', 'RO', 'TO',
            'AC', 'AP', 'RR', 'Moro fora do Brasil', 'Prefiro não informar'
        ])

        st.subheader("2. Conhecimento sobre PrEP")
        conhecimento = st.radio("Você conhece a PrEP?", [
            "Nunca ouvi falar", "Ouvi falar mas não sei", 
            "Conheço o básico", "Conheço bem"
        ])
        
        fonte_info = st.multiselect("Onde ouviu sobre PrEP?", [
            "Profissional de saúde", "Amigos", "Redes sociais", 
            "Sites", "Campanhas", "ONGs", "Outro"
        ])
        
        acesso = st.radio("Sabe onde encontrar PrEP no SUS?", [
            "Sim, sei onde ir", "Tenho uma ideia", "Não faço ideia"
        ])
        
        st.subheader("3. Uso e Percepções")
        uso = st.selectbox("Você usa ou já usou PrEP?", [
            "Uso atualmente", "Já usei", "Nunca usei mas quero",
            "Nunca usei e não quero", "Não sei se preciso"
        ])
        
        # Pergunta condicional sobre efeitos colaterais
        efeitos_colaterais_teve = "Não se aplica"
        efeitos_colaterais_quais = []
        
        if uso in ["Uso atualmente", "Já usei"]:
            efeitos_colaterais_teve = st.radio("Teve efeitos colaterais?", 
                ["Não", "Sim", "Não tenho certeza"])
            if efeitos_colaterais_teve == "Sim":
                efeitos_colaterais_quais = st.multiselect("Quais efeitos?", [
                    "Náusea", "Dor de cabeça", "Diarreia", "Tontura", 
                    "Cansaço", "Outro"
                ])

        barreiras = st.multiselect("Barreiras para usar PrEP:", [
            "Não acho que preciso", "Medo de efeitos", "Dificuldade de acesso",
            "Vergonha", "Esqueço de tomar", "Falta de informação", "Não se aplica"
        ])
        
        percepcao_risco = st.select_slider(
            "Como avalia seu risco de HIV? (0=nenhum, 10=muito alto)",
            options=list(range(11))
        )

        comentarios = st.text_area("Comentários ou dúvidas:")

        if st.form_submit_button("🚀 Enviar Respostas"):
            resposta = {
                'idade': idade, 'genero': genero, 'orientacao_sexual': orientacao,
                'raca': raca, 'escolaridade': escolaridade, 'renda': renda, 
                'regiao': regiao, 'conhecimento_prep': conhecimento, 
                'uso_prep': uso, 'acesso_servico': acesso,
                'fonte_info': ", ".join(fonte_info), 
                'barreiras': ", ".join(barreiras), 
                'percepcao_risco': percepcao_risco,
                'efeitos_colaterais_teve': efeitos_colaterais_teve,
                'efeitos_colaterais_quais': ", ".join(efeitos_colaterais_quais),
                'comentarios': comentarios
            }
            salvar_resposta(resposta)

def mostrar_analise_pesquisa():
    st.header("🤖 Análise dos Dados da Pesquisa")
    
    df = buscar_respostas()
    if df.empty:
        st.warning("Ainda não há respostas para analisar.")
        return
        
    st.metric("Total de Respostas", len(df))
    
    col1, col2 = st.columns(2)
    with col1:
        fig_idade = px.pie(df, names='idade', title='Faixa Etária')
        st.plotly_chart(fig_idade, use_container_width=True)
        
        fig_raca = px.bar(df['raca'].value_counts(), title='Raça/Cor')
        st.plotly_chart(fig_raca, use_container_width=True)
        
    with col2:
        fig_genero = px.pie(df, names='genero', title='Gênero')
        st.plotly_chart(fig_genero, use_container_width=True)
        
        fig_conhecimento = px.pie(df, names='conhecimento_prep', title='Conhecimento PrEP')
        st.plotly_chart(fig_conhecimento, use_container_width=True)

# (Copiar as funções mostrar_duvidas_frequentes e mostrar_onde_encontrar do código original aqui)