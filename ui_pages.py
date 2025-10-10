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
            efeitos_colaterais_teve = st.radio("Teve efeitos colaterais?", ["Não", "Sim", "Não tenho certeza"])
            if efeitos_colaterais_teve == "Sim":
                efeitos_colaterais_quais = st.text_area("Qual/quais efeitos colaterais?")

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
    Veja abaixo a lista completa de locais cadastrados no Brasil.
    """)

    # Exibir todos os locais do arquivo CSV
    import pandas as pd
    locais_path = "data/locais_prep.csv"
    try:
        df_locais = pd.read_csv(locais_path)
        st.subheader("Todos os Locais de PrEP no Brasil:")
        st.dataframe(df_locais, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao carregar locais: {e}")

    st.subheader("Como acessar:")
    st.write("""
    1. Procure uma unidade de saúde
    2. Solicite informações sobre PrEP
    3. Faça os exames necessários
    4. Receba a prescrição médica
    5. Retire os medicamentos na farmácia do SUS
    """)
