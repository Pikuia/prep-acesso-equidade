# ui_pages.py
import streamlit as st
import pandas as pd
import plotly.express as px
from database import salvar_resposta, buscar_respostas

def mostrar_pesquisa():
    """Exibe o formulário da pesquisa com perguntas simplificadas."""
    st.header("📝 Pesquisa - Conhecimento sobre PrEP")
    st.markdown("""
    **Esta pesquisa faz parte de um Projeto Integrador da UNIVESP.**
    Os dados são anônimos e servirão para aprimorar o acesso, equidade e análise comparativa do perfil dos usuários de PrEP.
    """)
    
    with st.form("pesquisa_simplificada"):
        st.subheader("1. Perfil Sociodemográfico")
        
        idade = st.selectbox("Faixa etária:", [
            "Prefiro não informar", "18-24 anos", "25-29 anos", "30-34 anos", 
            "35-39 anos", "40-49 anos", "50-59 anos", "60+ anos"
        ])
        
        genero = st.selectbox("Gênero:", [
            "Prefiro não informar",
            "Homem cis (identifica-se com o gênero masculino atribuído no nascimento)",
            "Mulher cis (identifica-se com o gênero feminino atribuído no nascimento)",
            "Homem trans (pessoa que foi designada mulher ao nascer, mas se identifica como homem)",
            "Mulher trans (pessoa que foi designada homem ao nascer, mas se identifica como mulher)",
            "Não-binário (não se identifica exclusivamente como homem ou mulher)",
            "Outro"
        ])
        
        orientacao = st.selectbox("Orientação sexual:", [
            "Prefiro não informar",
            "Heterossexual (se atrai por pessoas do sexo oposto)",
            "Homossexual (se atrai por pessoas do mesmo sexo)",
            "Bissexual (se atrai por ambos os sexos)",
            "Pansexual (se atrai por pessoas independentemente do sexo ou gênero)",
            "Assexual (não sente atração sexual)",
            "Outra"
        ])
        
        raca = st.selectbox("Raça/Cor:", [
            "Prefiro não informar", "Branca", "Preta", "Parda", "Amarela", "Indígena"
        ])
        
        escolaridade = st.selectbox("Escolaridade:", [
            "Prefiro não informar", "Fundamental", "Médio", "Superior", "Pós-graduação", "Outro"
        ])
        status_relacional = st.selectbox("Status Relacional:", [
            "Solteiro", "Relacionamento não exclusivo", "Relacionamento exclusivo", "Prefiro não informar"
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
            "Uso atualmente",
            "Já usei",
            "Nunca usei mas quero",
            "Nunca usei e não quero",
            "Nunca usei",
            "Não sei se preciso"
        ])

        objetivo_prep = st.selectbox("Objetivo do uso da PrEP:", [
            "Prevenção contínua",
            "Situações específicas (viagem, parceiro novo)",
            "PEP recorrente e migração para PrEP",
            "Curiosidade/avaliação",
            "Outro"
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
            # Garantir que efeitos_colaterais_quais seja sempre string
            ec_quais = efeitos_colaterais_quais
            if isinstance(ec_quais, list):
                ec_quais = ", ".join(ec_quais)
            elif ec_quais is None:
                ec_quais = ""
            resposta = {
                'idade': idade,
                'genero': genero,
                'orientacao_sexual': orientacao,
                'raca': raca,
                'escolaridade': escolaridade,
                'renda': renda,
                'regiao': regiao,
                'status_relacional': status_relacional,
                'conhecimento_prep': conhecimento,
                'uso_prep': uso,
                'objetivo_prep': objetivo_prep,
                'acesso_servico': acesso,
                'fonte_info': ", ".join(fonte_info),
                'barreiras': ", ".join(barreiras),
                'percepcao_risco': percepcao_risco,
                'efeitos_colaterais_teve': efeitos_colaterais_teve,
                'efeitos_colaterais_quais': ec_quais,
                'comentarios': comentarios
            }
            salvar_resposta(resposta)
            st.session_state.pesquisa_enviada = True
            st.success("Obrigado por participar! Agora você pode acessar as demais informações.")
            # Tenta forçar um rerun: prefira a API estável `st.rerun()` se disponível,
            # senão tenta `experimental_rerun`. Se nenhuma estiver disponível, apenas retorna
            try:
                if hasattr(st, "rerun") and callable(getattr(st, "rerun")):
                    st.rerun()
                else:
                    rerun = getattr(st, "experimental_rerun", None)
                    if callable(rerun):
                        rerun()
                    else:
                        return
            except Exception:
                return

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
    st.header("📍 Onde Encontrar a PrEP em São Paulo")
    st.markdown("---")

    st.info("""
    A PrEP é disponibilizada gratuitamente em diversos serviços de saúde do município de São Paulo. Confira abaixo os endereços das unidades organizados por região:
    """)

    # REGIÃO CENTRAL
    st.subheader("Região Central")
    st.markdown("""
    **Estação Prevenção Jorge Beloqui**  
    Dentro da Estação República - Linha vermelha do metrô  
    De terça a sábado, das 17h às 23h

    **CTA Henfil (Henrique de Souza Filho)**  
    R. do Tesouro, 39 - Centro  
    Tel.: (11) 5128-6186  
    WhatsApp: (11) 9 7744-8964

    **SAE Campos Elíseos**  
    Al. Cleveland, 374 - Santa Cecília  
    Tel.: (11) 5237-7551 / 5237-7552  
    WhatsApp: (11) 97744-5452
    """)

    # REGIÃO NORTE
    st.subheader("Região Norte")
    st.markdown("""
    **SAE Nossa Senhora do Ó**  
    Av. Itaberaba, 1.377 - Freguesia do Ó  
    Tel.: (11) 3975-2032  
    WhatsApp: (11) 9 5898-8741

    **CTA Pirituba**  
    Av. Dr. Felipe Pinel, 12 - Pirituba  
    Tel.: (11) 3974-8569  
    WhatsApp: (11) 9 5254-3211

    **SAE Santana (Marcos Lottenberg)**  
    R. Dr. Luís Lustosa da Silva, 339 - Mandaqui  
    Tel.: (11) 2950-9217  
    WhatsApp: (11) 9 5898-9122
    """)

    # REGIÃO SUL
    st.subheader("Região Sul")
    st.markdown("""
    **SAE Santo Amaro (Dra. Denize Dornelas de Oliveira)**  
    R. Padre José de Anchieta, 640 – Santo Amaro  
    Tel.: (11) 5686-1613  
    WhatsApp: (11) 9 7744-1580

    **CTA Santo Amaro (Paula Legno)**  
    R. Mário Lopes Leão, 240 – Santo Amaro  
    Tel.: (11) 5686-9960 / 5686-1475  
    WhatsApp: (11) 9 7744-5151

    **CTA José Araújo Lima Filho**  
    R. Louis Boulanger,120, Jardim Bom Refúgio  
    Tel.: (11) 5897-4832  
    WhatsApp: (11) 9 4947-0385

    **SAE Jardim Mitsutani**  
    R. Vittório Emanuele Rossi, 97 – Jd. Bom Refúgio  
    Tel.: (11) 5841-9020  
    WhatsApp: (11) 9 7744-1630

    **SAE Cidade Dutra**  
    R. Cristina de Vasconcelos Ceccato, 109 – Cidade Dutra  
    Tel.: (11) 5666-8386  
    WhatsApp: (11) 9 7744-8288

    **SAE M’Boi Mirim**  
    R. Deocleciano de Oliveira Filho, 641 – Pq. Santo Antônio  
    Tel.: (11) 5515-6207  
    WhatsApp: (11) 9 5898-8499
    """)

    # REGIÃO SUDESTE
    st.subheader("Região Sudeste")
    st.markdown("""
    **SAE Jabaquara (antigo SAE Ceci)**  
    Rua dos Comerciários, 236 - Jabaquara  
    Tel.: (11) 2276-9719  
    WhatsApp: (11) 9 5254-2431

    **SAE Vila Prudente (Shirlei Mariotti Gomes Coelho)**  
    Pça. Centenário de Vila Prudente, 108 - Vila Prudente  
    Tel.: (11) 5237-8480 / 5237-8481  
    WhatsApp: (11) 9 7744-1359

    **SAE Penha**  
    Pça. Nossa Senhora da Penha, 55 - Penha  
    Tel.: (11) 5237-8880  
    WhatsApp: (11) 9 7744-4500

    **SAE Herbert de Souza (Betinho)**  
    Av. Arquiteto Vilanova Artigas, 515 - Teotônio Vilela  
    Tel.: (11) 2704-0833  
    WhatsApp: (11) 9 5254-1211

    **SAE Ipiranga (José Francisco de Araújo)**  
    R. Gonçalves Ledo, 606 - Ipiranga  
    Tel.: (11) 5273-8861 / 5237-8860  
    WhatsApp: (11) 9 7744-5614

    **CTA Mooca**  
    R. Taquari, 549 — salas 9 e 10 - Mooca  
    Tel.: (11) 5237-8612  
    WhatsApp: (11) 9 7744-8200
    """)

    # REGIÃO LESTE
    st.subheader("Região Leste")
    st.markdown("""
    **CTA Cidade Tiradentes**  
    R. Milagre dos Peixes, 357 - Cidade Tiradentes  
    Tel.: (11) 2282-7055  
    WhatsApp: (11) 9 4947-6346

    **CTA Dr. Sérgio Arouca (Itaim Paulista)**  
    R. Valente Novais, 131 - Itaim Paulista  
    Tel.: (11) 5237-8635 / 5237-8636  
    WhatsApp: (11) 9 7744-1756

    **SAE São Mateus**  
    Av. Mateo Bei, 838 - São Mateus  
    Tel.: (11) 2919-0697  
    WhatsApp: (11) 9 7744-1787

    **CTA São Miguel**  
    R. José Aldo Piassi, 85 - São Miguel Paulista  
    Tel.: (11) 5237-8626  
    WhatsApp: (11) 9 7744-8253

    **CTA Guaianases**  
    R. Centralina, 168 - Guaianases  
    Tel.: (11) 2554-5312  
    WhatsApp: (11) 9 5898-2728

    **SAE Cidade Líder II**  
    R. Médio Iguaçu, 86 - Cidade Líder  
    Tel.: (11) 5237-8890  
    WhatsApp: (11) 9 5254-0599

    **SAE Fidélis Ribeiro**  
    R. Peixoto, 100 - Vila Fidélis Ribeiro  
    Tel.: (11) 2621-4753  
    WhatsApp: (11) 9 5898-4962
    """)

    # REGIÃO OESTE
    st.subheader("Região Oeste")
    st.markdown("""
    **SAE Butantã**  
    Rua Dr. Bernardo Guertzenstein, 45 - Jardim Sarah  
    Tel.: (11) 3768-1523  
    WhatsApp: (11) 9 7744-4984

    **SAE Lapa (Paulo César Bonfim)**  
    Rua Tome de Souza, 30 - Lapa  
    Tel.: (11) 3832-2551  
    WhatsApp: (11) 9 5898-5432
    """)

    st.subheader("Como acessar:")
    st.write("""
    1. Procure uma unidade de saúde
    2. Solicite informações sobre PrEP
    3. Faça os exames necessários
    4. Receba a prescrição médica
    5. Retire os medicamentos na farmácia do SUS
    """)
