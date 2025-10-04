#!/bin/bash

echo "🚀 INICIANDO ATUALIZAÇÃO COMPLETA DA APLICAÇÃO..."

# 1. Atualizar database.py para SQLite com colunas corrigidas
echo "📁 ATUALIZANDO DATABASE.PY..."
cat > database.py << 'EOF'
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
        conhecimento_prep TEXT,
        uso_prep TEXT,
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
    (idade, genero, orientacao_sexual, raca, escolaridade, renda, regiao, 
     conhecimento_prep, uso_prep, acesso_servico, fonte_info, barreiras, 
     percepcao_risco, efeitos_colaterais_teve, efeitos_colaterais_quais, comentarios)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
EOF

# 2. Atualizar ui_pages.py com perguntas simplificadas
echo "📁 ATUALIZANDO UI_PAGES.PY..."
cat > ui_pages.py << 'EOF'
# ui_pages.py
import streamlit as st
import pandas as pd
import plotly.express as px
from database import salvar_resposta, buscar_respostas

def mostrar_pesquisa():
    """Exibe o formulário da pesquisa com perguntas simplificadas."""
    st.header("📝 Pesquisa - Conhecimento sobre PrEP")
    
    with st.form("pesquisa_simplificada"):
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
        conhecimento = st.radio("Você conhece a PrEP?", ["Sim", "Não"])

        fonte_info = []
        if conhecimento == "Sim":
            fonte_info = st.multiselect("Onde você obteve informações sobre PrEP? (Pode marcar mais de uma)", [
                "Profissional de saúde", "Amigos", "Redes sociais", 
                "Sites", "Campanhas", "ONGs", "Outro"
            ])
        
        acesso = st.radio("Você sabe onde encontrar a PrEP gratuitamente pelo SUS?", ["Sim", "Não"])
        
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

def mostrar_duvidas_frequentes():
    """Exibe uma seção com perguntas e respostas comuns sobre a PrEP."""
    st.header("❔ Dúvidas Frequentes sobre a PrEP")
    st.markdown("---")
    st.info("Clique nas perguntas abaixo para ver as respostas.")

    with st.expander("Posso parar de usar camisinha?"):
        st.write("Como a PrEP é uma profilaxia apenas para o HIV, o uso da camisinha ainda é recomendado para prevenção às outras infecções sexualmente transmissíveis, bem como evitar uma gravidez não planejada.")
    
    with st.expander("A PrEP tem efeito colateral?"):
        st.write("Nos medicamentos usados hoje, os efeitos colaterais são raros e tranquilos. A pessoa pode ter um pouco de náusea e cefaleia (dor de cabeça). É importante o acompanhamento com o profissional de saúde para garantir a correta avaliação.")

    with st.expander("E se eu esquecer de tomar a PrEP um dia? Perde o efeito logo em seguida?"):
        st.write("Na verdade você vai diminuir o efeito protetivo do medicamento. Mas, um dia só não vai comprometer a sua prevenção.")

    with st.expander("A partir de quantos dias a PrEP começa a fazer efeito?"):
        st.write("No caso de sexo vaginal e de pessoas que fazem uso do hormônio estradiol, a proteção é dada a partir do sétimo dia. No caso de pessoas com pênis que não fazem uso de hormônio estradiol, ao realizarem sexo anal, a proteção se inicia a partir de duas horas.")

    with st.expander("Preciso tomar a PrEP em jejum?"):
        st.write("Não, não precisa. Você vai escolher o melhor horário para tomar o seu medicamento. O ideal é que você repita sempre nesse mesmo horário.")
        
    with st.expander("Bebida alcóolica corta o efeito da PrEP?"):
        st.write("Não, não corta o efeito da PrEP.")

    with st.expander("Qual a diferença entre PrEP e PEP?"):
        st.write("""
        A PrEP, ou seja, a Profilaxia Pré-Exposição, é uma forma de se prevenir ao HIV antes de uma exposição de risco de infecção. Por isso ela deve ser tomada todos os dias (no caso da PrEP diária) ou no esquema 2 + 1 + 1 (no caso da PrEP sob demanda), como uma medida protetiva. Mas atenção! O uso da PrEP sob demanda é indicado for para algumas populações apenas, e deve ser utilizada conforme orientação do profissional de saúde. 
        
        Já a PEP, a Profilaxia Pós-Exposição, é indicada para pessoas que não fazem PrEP e quando a camisinha sai, rompe ou não é utilizada no sexo. É uma forma de prevenção ao HIV que deve ser acessada após uma situação de risco. A PEP deve ser iniciada em até 72 horas depois da exposição; de preferência nas duas primeiras horas.
        """)

def mostrar_onde_encontrar():
    """Exibe informações sobre onde encontrar a PrEP."""
    st.header("📍 Onde Encontrar a PrEP?")
    st.markdown("---")
    
    st.info("""
    A PrEP é disponibilizada gratuitamente pelo SUS em diversos serviços de saúde. 
    Consulte a Secretaria de Saúde do seu município para encontrar o local mais próximo.
    """)
    
    st.subheader("Principais locais em São Paulo:")
    st.write("""
    - **CRT DST/Aids-SP** - Centro de Referência e Treinamento
    - **UBSs** - Unidades Básicas de Saúde
    - **SAEs** - Serviços de Assistência Especializada
    - **CTAs** - Centros de Testagem e Aconselhamento
    """)
    
    st.subheader("Como acessar:")
    st.write("""
    1. Procure uma unidade de saúde
    2. Solicite informações sobre PrEP
    3. Faça os exames necessários
    4. Receba a prescrição médica
    5. Retire os medicamentos na farmácia do SUS
    """)
EOF

# 3. Atualizar analysis.py com análises melhoradas
echo "📁 ATUALIZANDO ANALYSIS.PY..."
cat > analysis.py << 'EOF'
# analysis.py
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Mapeamento para nomes mais compreensíveis
TRADUCOES = {
    'raca4_cat': 'Raça/Cor',
    'escol4': 'Escolaridade', 
    'fetar': 'Faixa Etária',
    'Pop_genero_pratica': 'População/Gênero',
    'UF_UDM': 'Estado',
    'Disp_12m_2024': 'Continuou no Programa em 2024'
}

@st.cache_data
def carregar_dados_publicos():
    data_path = Path('data')
    try:
        df_usuarios = pd.read_csv(data_path / 'Banco_PrEP_usuarios.csv', encoding='latin1', sep=',')
        df_dispensas = pd.read_csv(data_path / 'Banco_PrEP_dispensas.csv', encoding='latin1', sep=',')
        df_indicadores = pd.read_excel(data_path / 'indicadoresAids.xls', sheet_name=None, header=None)
        return df_usuarios, df_dispensas, df_indicadores
    except FileNotFoundError:
        st.error("Arquivos de dados não encontrados na pasta 'data'")
        return pd.DataFrame(), pd.DataFrame(), None

def traduzir_colunas(df):
    return df.rename(columns=TRADUCOES)

def mostrar_dados_oficiais():
    st.header("📊 Dados Oficiais sobre PrEP")
    
    df_usuarios, df_dispensas, df_indicadores = carregar_dados_publicos()
    
    if df_usuarios.empty:
        st.warning("Dados não carregados")
        return

    df_usuarios_traduzido = traduzir_colunas(df_usuarios)
    
    st.info("💡 Dados públicos do Ministério da Saúde sobre usuários de PrEP")
    
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Perfil dos Usuários", "💊 Dispensas", "📈 Tendências", "🔍 Análises Avançadas"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            if 'Raça/Cor' in df_usuarios_traduzido.columns:
                fig_raca = px.pie(df_usuarios_traduzido, names='Raça/Cor', 
                                title="Distribuição por Raça/Cor")
                st.plotly_chart(fig_raca, use_container_width=True)
            
            if 'Escolaridade' in df_usuarios_traduzido.columns:
                fig_esc = px.bar(df_usuarios_traduzido['Escolaridade'].value_counts(),
                               title="Nível de Escolaridade")
                st.plotly_chart(fig_esc, use_container_width=True)
                
        with col2:
            if 'Faixa Etária' in df_usuarios_traduzido.columns:
                fig_idade = px.pie(df_usuarios_traduzido, names='Faixa Etária',
                                 title="Distribuição por Idade")
                st.plotly_chart(fig_idade, use_container_width=True)
            
            if 'População/Gênero' in df_usuarios_traduzido.columns:
                fig_pop = px.bar(df_usuarios_traduzido['População/Gênero'].value_counts(),
                               title="População/Gênero")
                st.plotly_chart(fig_pop, use_container_width=True)

    with tab2:
        if not df_dispensas.empty:
            st.subheader("Dispensas de PrEP ao Longo do Tempo")
            df_dispensas['dt_disp'] = pd.to_datetime(df_dispensas['dt_disp'], errors='coerce')
            disp_por_mes = df_dispensas.set_index('dt_disp').resample('M').size().reset_index(name='count')
            fig_tempo = px.line(disp_por_mes, x='dt_disp', y='count', 
                              title='Evolução Mensal das Dispensas de PrEP')
            st.plotly_chart(fig_tempo, use_container_width=True)
            
            st.subheader("Tipos de Serviços")
            col1, col2 = st.columns(2)
            with col1:
                fig_serv = px.pie(df_dispensas, names='tp_servico_atendimento', 
                                title="Tipo de Serviço")
                st.plotly_chart(fig_serv, use_container_width=True)
            with col2:
                fig_prof = px.pie(df_dispensas, names='tp_profissional', 
                                title="Tipo de Profissional")
                st.plotly_chart(fig_prof, use_container_width=True)

    with tab3:
        st.subheader("Análises de Tendência")
        st.info("Em breve: Análises de tendência temporal e projeções")

    with tab4:
        st.subheader("Análises Avançadas com Machine Learning")
        analise_avancada_publico(df_usuarios)

def analise_avancada_publico(df_usuarios):
    st.header("🤖 Análise Avançada com Machine Learning")
    st.info("Esta análise utiliza os dados públicos para identificar padrões.")
    st.warning("Funcionalidade em desenvolvimento - Machine Learning em breve!")

def analise_indicadores_hiv(df_indicadores):
    st.header("📈 Indicadores Nacionais de AIDS")
    st.warning("Análise de indicadores de HIV em desenvolvimento!")
EOF

# 4. Criar mapa_interativo.py
echo "📁 CRIANDO MAPA_INTERATIVO.PY..."
cat > mapa_interativo.py << 'EOF'
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
EOF

# 5. Atualizar app.py para incluir o mapa
echo "📁 ATUALIZANDO APP.PY..."
cat > app.py << 'EOF'
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
EOF

# 6. Remover banco de dados antigo para forçar recriação
echo "🗃️ REMOVENDO BANCO DE DADOS ANTIGO..."
rm -f pesquisa_prep.db

# 7. Criar arquivo de melhorias futuras
echo "📋 CRIANDO ARQUIVO DE MELHORIAS FUTURAS..."
cat > melhorias_futuras.md << 'EOF'
# 🚀 Próximas Melhorias

## 📊 Análises Avançadas
- [ ] Mapa interativo com Plotly para mostrar dados por estado
- [ ] Análise de sentimentos nos comentários
- [ ] Sistema de cache para dados públicos
- [ ] Exportação de relatórios em PDF
- [ ] Dashboard administrativo para moderadores

## 🔧 Funcionalidades
- [ ] Sistema de autenticação simples
- [ ] Filtros avançados nas análises
- [ ] Comparativos entre diferentes períodos
- [ ] Integração com APIs de saúde pública

## 📱 Experiência do Usuário
- [ ] Design responsivo para mobile
- [ ] Modo escuro/claro
- [ ] Acessibilidade (leitores de tela)
- [ ] Multi-idioma
EOF

echo "✅ ATUALIZAÇÃO CONCLUÍDA!"
echo "🚀 EXECUTANDO APLICAÇÃO..."

# Executar a aplicação
python -m streamlit run app.py