# -*- coding: utf-8 -*-
import io, zipfile, requests
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import statsmodels.api as sm
from sklearn.preprocessing import OneHotEncoder
from sklearn.mixture import GaussianMixture
from pandas.api import types as pdt
from supabase_client import get_supabase

st.set_page_config(page_title="PrEP — Oferta x Conhecimento (SP)", layout="wide")
st.title("PrEP — Entre a Oferta e o Conhecimento (Município de São Paulo)")

TABLE = "respostas_prep"
URL_PREP_ZIP = "https://mediacenter.aids.gov.br/prep/Dados_PrEP_transparencia.zip"  # pode falhar por SSL
COD_IBGE_SAO_PAULO = 3550308  # Filtro de município por código IBGE (SP)

# ========================= BANCO (SUPABASE) =========================

def insert_resposta(payload: dict) -> dict:
    sb = get_supabase(backend=False)  # ANON para inserts (RLS libera)
    valid = {"ts_utc","versao_form","conhecimento_prep","conhecimento_pep","acesso_servicos",
             "fonte_informacao","uso_preppep","conhece_usuarios","teste_hiv_freq","metodos_prevencao",
             "genero","orientacao_sexual","raca","faixa_etaria","escolaridade","renda",
             "regiao","subprefeitura","comentarios"}
    row = {k: v for k,v in payload.items() if k in valid and v is not None}
    return sb.table(TABLE).insert(row).execute().model_dump()

def fetch_respostas(limit: int = 10000) -> pd.DataFrame:
    sb = get_supabase(backend=True)   # SERVICE ROLE (somente no servidor)
    rows, start, page = [], 0, 1000
    while True:
        data = (sb.table(TABLE).select("*").order("ts_utc", desc=False).range(start, start+page-1)).execute().data
        if not data: break
        rows.extend(data)
        start += page
        if len(rows) >= limit or len(data) < page: break
    return pd.DataFrame(rows)

# ========================= DADOS PrEP (MS) =========================
# Rotas: A) Upload CSVs; B) URL; C) ZIP oficial (pode falhar por SSL)

def _uppercase_cols(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().upper() for c in df.columns]
    return df

def _harmonize_users_cols(df_users: pd.DataFrame) -> pd.DataFrame:
    """Mapeia colunas segundo dicionário do MS para nomes canônicos."""
    mapping = {
        "RACA4_CAT": "RACA_COR",
        "ESCOL4": "ESCOLARIDADE",
        "FETAR": "FAIXA_ETARIA",
        "POP_GENERO_PRATICA": "POPULACAO_CHAVE",
        "COD_IBGE_UDM": "COD_IBGE_UDM",
        "CODIGO_IBGE_RESID": "COD_IBGE_RESID",
        "DT_DISP": "DT_DISP_MAX_SNAP"
    }
    for k,v in mapping.items():
        if k in df_users.columns:
            df_users[v] = df_users[k]
    return df_users

def _harmonize_disp_cols(df_disp: pd.DataFrame) -> pd.DataFrame:
    """Padroniza dispensações: adiciona ANO."""
    if "DT_DISP" in df_disp.columns:
        df_disp["DT_DISP"] = pd.to_datetime(df_disp["DT_DISP"], errors="coerce")
        df_disp["ANO"] = df_disp["DT_DISP"].dt.year
    return df_disp

def ms_from_upload(users_file, disp_file) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_users = _uppercase_cols(pd.read_csv(users_file, sep=None, engine="python"))
    df_disp  = _uppercase_cols(pd.read_csv(disp_file,  sep=None, engine="python"))
    df_users = _harmonize_users_cols(df_users)
    df_disp  = _harmonize_disp_cols(df_disp)
    # Filtro município SP — pelo serviço dispensador (UDM)
    if "COD_IBGE_UDM" in df_disp.columns:
        mask_sp = df_disp["COD_IBGE_UDM"].astype(str).str.startswith(str(COD_IBGE_SAO_PAULO)) | (df_disp["COD_IBGE_UDM"]==str(COD_IBGE_SAO_PAULO))
        df_disp_sp = df_disp[mask_sp].copy()
    else:
        df_disp_sp = df_disp.copy()
    return df_users, df_disp_sp

def ms_from_urls(url_users: str, url_disp: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    r1 = requests.get(url_users, timeout=120); r1.raise_for_status()
    r2 = requests.get(url_disp,  timeout=120); r2.raise_for_status()
    return ms_from_upload(io.BytesIO(r1.content), io.BytesIO(r2.content))

def ms_from_zip_official() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Tenta baixar o ZIP oficial do MS em memória (pode falhar por SSL)."""
    r = requests.get(URL_PREP_ZIP, timeout=120)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    names = [n for n in z.namelist() if n.lower().endswith(".csv")]
    fn_users = next((n for n in names if "usuario" in n.lower()), None)
    fn_disp  = next((n for n in names if "disp" in n.lower()), None)
    if not fn_users or not fn_disp:
        raise RuntimeError(f"Arquivos esperados não encontrados no ZIP: {names[:6]} ...")
    df_users = _uppercase_cols(pd.read_csv(z.open(fn_users), sep=";", encoding="utf-8"))
    df_disp  = _uppercase_cols(pd.read_csv(z.open(fn_disp),  sep=";", encoding="utf-8"))
    df_users = _harmonize_users_cols(df_users)
    df_disp  = _harmonize_disp_cols(df_disp)
    if "COD_IBGE_UDM" in df_disp.columns:
        mask_sp = df_disp["COD_IBGE_UDM"].astype(str).str.startswith(str(COD_IBGE_SAO_PAULO)) | (df_disp["COD_IBGE_UDM"]==str(COD_IBGE_SAO_PAULO))
        df_disp = df_disp[mask_sp].copy()
    return df_users, df_disp

# ========================= PROXY (distribuição/positividade) =================

def load_proxy_from_upload(file) -> pd.DataFrame:
    # comment='#' ignora linhas que começarem com '#'
    return pd.read_csv(file, sep=None, engine="python", comment='#')

def load_proxy_from_url(url: str) -> pd.DataFrame:
    r = requests.get(url, timeout=120); r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content), sep=None, engine="python", comment='#')

# ========================= ANÁLISE: OFERTA × DEMANDA × CONHECIMENTO =========

def offer_counts_by_year_dim(df_users: pd.DataFrame, df_disp: pd.DataFrame, dim_col: str, year: int) -> pd.DataFrame:
    """
    Oferta = nº de usuários distintos com ao menos uma dispensação no ANO (por grupo).
    Faz join para obter a dimensão do usuário (df_users).
    Limitação: df_users é um 'snapshot' (última dispensa).
    """
    if "ANO" not in df_disp.columns or "COD_UNIFICADO" not in df_disp.columns:
        raise ValueError("Dispensações precisam ter colunas ANO e COD_UNIFICADO.")
    if dim_col not in df_users.columns:
        raise ValueError(f"Dimensão {dim_col} não encontrada no banco de usuários.")
    disp_y = df_disp[df_disp["ANO"]==year][["COD_UNIFICADO"]].dropna().drop_duplicates()
    col_keep = ["COD_UNIFICADO", dim_col]
    if "COD_UNIFICADO" not in df_users.columns:
        df_users = df_users.rename(columns={c: "COD_UNIFICADO" for c in df_users.columns if c.strip()=="COD_UNIFICADO"})
    users_y = disp_y.merge(df_users[col_keep], on="COD_UNIFICADO", how="left")
    out = users_y.groupby(dim_col).size().rename("prep").reset_index()
    out["ANO"] = year
    return out

def gap_with_ci(offer_df: pd.DataFrame, demand_df: pd.DataFrame, dim: str, ano: int) -> pd.DataFrame:
    a = offer_df[offer_df["ANO"]==ano][[dim,"prep"]].copy()
    b = demand_df[demand_df["ANO"]==ano][[dim,"COUNT"]].copy().rename(columns={"COUNT":"hiv"})
    m = a.merge(b, on=dim, how="outer").fillna(0)
    n1, n2 = m["prep"].sum(), m["hiv"].sum()
    m["p1"] = m["prep"]/n1 if n1>0 else 0.0
    m["p2"] = m["hiv"]/n2 if n2>0 else 0.0
    m["gap_repr"] = m["p1"] - m["p2"]
    se = np.sqrt((m["p1"]*(1-m["p1"])/max(n1,1)) + (m["p2"]*(1-m["p2"])/max(n2,1)))
    z = 1.96
    m["ci_low"] = m["gap_repr"] - z*se
    m["ci_high"] = m["gap_repr"] + z*se
    m["signif"] = np.where((m["ci_low"]>0)|(m["ci_high"]<0),"Significativo (95%)","Não significativo")
    return m.sort_values("gap_repr")

def harmonize_survey(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['Conhecimento_PrEP_bin'] = df['conhecimento_prep'].map({
        "Sim, conheço bem": 1, "Conheço parcialmente": 1,
        "Já ouvi falar mas não sei detalhes": 0, "Não conheço": 0
    }).astype('Int64')
    df['Uso_PrEP_bin'] = df['uso_preppep'].map({"Sim, uso atualmente": 1}).fillna(0).astype(int)
    if 'metodos_prevencao' in df.columns:
        df.loc[df['metodos_prevencao'].fillna('').str.contains('PrEP', case=False), 'Uso_PrEP_bin'] = 1
    for c in ['raca','faixa_etaria','escolaridade','genero','orientacao_sexual','regiao','subprefeitura']:
        if c in df.columns: df[c] = df[c].astype(str).str.strip()
    return df

def logistic_or(df: pd.DataFrame, target: str, features: list[str]) -> pd.DataFrame:
    data = df[[target]+features].dropna()
    if data.empty: raise ValueError("Dados insuficientes.")
    X = pd.get_dummies(data[features], drop_first=True)
    X = sm.add_constant(X)
    y = data[target].astype(int)
    model = sm.Logit(y, X).fit(disp=0)
    conf = model.conf_int()
    out = pd.DataFrame({
        "feature": model.params.index,
        "OR": np.exp(model.params.values),
        "CI_low": np.exp(conf[0].values),
        "CI_high": np.exp(conf[1].values),
        "pvalue": model.pvalues.values
    })
    return out.sort_values("OR", ascending=False)

def latent_profiles(df: pd.DataFrame, cat_cols: list[str], k_range=range(2,6)):
    enc = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    Z = enc.fit_transform(df[cat_cols].astype(str))
    best = {"bic": float('inf'), "k": None, "model": None}
    for k in k_range:
        gm = GaussianMixture(n_components=k, covariance_type='spherical', random_state=42).fit(Z)
        bic = gm.bic(Z)
        if bic < best["bic"]: best = {"bic": bic, "k": k, "model": gm}
    labels = best["model"].predict(Z)
    out = df.copy(); out["Perfil_Latente"] = labels
    return out, best

# ========================= INTERFACE =========================

menu = st.sidebar.radio(
    "Navegação",
    ["Coleta (Pesquisa)", "Dados PrEP (MS)", "Proxy (distribuição)", "Oferta × Demanda × Conhecimento", "Modelos (ML)", "Sobre"]
)

# --- 1) Coleta ---
if menu == "Coleta (Pesquisa)":
    st.header("Formulário — conhecimento/uso de PrEP/PEP (grava no Supabase)")
    with st.form("frm"):
        col1, col2 = st.columns(2)
        with col1:
            q1 = st.radio("Você conhece a PrEP?", ["Sim, conheço bem","Conheço parcialmente","Já ouvi falar mas não sei detalhes","Não conheço"])
            q2 = st.radio("E a PEP?", ["Sim, conheço bem","Conheço parcialmente","Já ouvi falar mas não sei detalhes","Não conheço"])
            q3 = st.radio("Sabe onde conseguir PrEP/PEP em São Paulo?", ["Sim, conheço vários serviços","Conheço apenas um local","Não sei mas gostaria de saber","Não sei e não tenho interesse"])
            q4 = st.selectbox("Como soube da PrEP/PEP?", ["Profissional de saúde","Amigos/conhecidos","Internet/redes sociais","Material informativo","Nunca ouvi falar","Outra"])
            q5 = st.radio("Já usou/usa PrEP/PEP?", ["Sim, uso atualmente","Sim, já usei no passado","Não, mas pretendo usar","Não uso e não tenho interesse"])
            q6 = st.radio("Conhece alguém que usa PrEP/PEP?", ["Sim, vários","Sim, alguns","Não conheço ninguém","Prefiro não responder"])
        with col2:
            q7 = st.radio("Frequência de teste de HIV", ["A cada 3 meses","A cada 6 meses","Uma vez por ano","Raramente faço","Nunca fiz","Prefiro não responder"])
            genero = st.selectbox("Identidade de gênero", ["Mulher cisgênero","Homem cisgênero","Mulher trans","Homem trans","Pessoa não-binária","Travesti","Outro","Prefiro não responder"])
            orient = st.selectbox("Orientação sexual", ["Assexual","Bissexual","Gay","Lésbica","Pansexual","Heterossexual","Queer","Outra","Prefiro não responder"])
            raca = st.radio("Raça/cor", ["Amarela","Branca","Indígena","Parda","Preta","Prefiro não responder"])
            faixa = st.radio("Faixa etária", ["13-17","18-24","25-29","30-39","40-49","50-59","60+","Prefiro não responder"])
            escolar = st.selectbox("Escolaridade", ["Fundamental incompleto","Fundamental completo","Médio incompleto","Médio completo","Superior incompleto","Superior completo","Pós-graduação","Prefiro não responder"])
            renda = st.radio("Renda mensal individual", ["Até 1 SM","1-2 SM","2-3 SM","3-5 SM","Mais de 5 SM","Prefiro não responder"])
            regiao = st.selectbox("Região de residência em SP", ["Centro expandido","Zona Norte","Zona Sul","Zona Leste","Zona Oeste","Região Metropolitana","Não moro em S. Paulo","Prefiro não responder"])
            subpref = st.text_input("Subprefeitura (opcional)")
            metodos = st.multiselect("Métodos de prevenção", ["PrEP","PEP","Camisinha masculina","Camisinha feminina","Testagem regular","Não utilizo","Outro"])
            comentarios = st.text_area("Comentários (opcional)", height=70)
        enviado = st.form_submit_button("Enviar")
    if enviado:
        payload = {
            "versao_form": "v1",
            "conhecimento_prep": q1, "conhecimento_pep": q2,
            "acesso_servicos": q3, "fonte_informacao": q4,
            "uso_preppep": q5, "conhece_usuarios": q6,
            "teste_hiv_freq": q7, "genero": genero, "orientacao_sexual": orient,
            "raca": raca, "faixa_etaria": faixa, "escolaridade": escolar, "renda": renda,
            "regiao": regiao, "subprefeitura": (subpref or None),
            "metodos_prevencao": ", ".join(metodos) if metodos else None,
            "comentarios": (comentarios or None),
        }
        _ = insert_resposta(payload)
        st.success("✅ Resposta registrada!")
    st.divider()
    df = fetch_respostas()
    st.caption(f"Total de respostas armazenadas: {len(df)}")
    st.dataframe(df.tail(30), use_container_width=True)

# --- 2) Dados PrEP (MS) ---
elif menu == "Dados PrEP (MS)":
    st.header("Carregar dados PrEP do MS (sem CSV local, ou via CSV de apoio)")
    tabs = st.tabs(["A) Upload CSVs", "B) URLs remotas", "C) ZIP oficial (tentativa)"])

    # A) Upload
    with tabs[0]:
        uf  = st.file_uploader("Banco_PrEP_usuarios.csv",  type=["csv"], key="u1")
        dfp = st.file_uploader("Banco_PrEP_dispensas.csv", type=["csv"], key="u2")
        if st.button("Carregar (upload)"):
            if uf and dfp:
                try:
                    users, disp = ms_from_upload(uf, dfp)
                    st.session_state["MS_USERS"] = users
                    st.session_state["MS_DISP"]  = disp
                    st.success(f"OK! Usuários: {len(users):,} | Dispensas (SP): {len(disp):,}")
                    st.dataframe(users.head(20), use_container_width=True)
                    st.dataframe(disp.head(20),  use_container_width=True)
                except Exception as e:
                    st.error(f"Erro ao processar CSVs: {e}")
            else:
                st.warning("Envie os dois arquivos.")

    # B) URLs
    with tabs[1]:
        url_users = st.text_input("URL - Banco_PrEP_usuarios.csv")
        url_disp  = st.text_input("URL - Banco_PrEP_dispensas.csv")
        if st.button("Carregar (URLs)"):
            try:
                users, disp = ms_from_urls(url_users, url_disp)
                st.session_state["MS_USERS"] = users
                st.session_state["MS_DISP"]  = disp
                st.success(f"OK! Usuários: {len(users):,} | Dispensas (SP): {len(disp):,}")
            except Exception as e:
                st.error(f"Falha ao baixar pelas URLs: {e}")

    # C) ZIP oficial
    with tabs[2]:
        st.info("Tentativa de baixar o ZIP oficial (pode falhar se o certificado SSL do servidor estiver vencido).")
        if st.button("Baixar ZIP oficial (em memória)"):
            try:
                users, disp = ms_from_zip_official()
                st.session_state["MS_USERS"] = users
                st.session_state["MS_DISP"]  = disp
                st.success(f"OK! Usuários: {len(users):,} | Dispensas (SP): {len(disp):,}")
                st.caption("Fonte: Painel PrEP — Ministério da Saúde (link público para o ZIP).")
            except requests.exceptions.SSLError:
                st.error("Falha SSL no servidor oficial (certificado expirado). Use Upload ou URLs dos seus CSVs.")
            except Exception as e:
                st.error(f"Erro ao baixar/processar ZIP: {e}")

# --- 3) Proxy ---
elif menu == "Proxy (distribuição)":
    st.header("Proxy de necessidade (incidência/positividade) — use upload ou URL remota")
    colA, colB = st.columns(2)
    with colA:
        fp = st.file_uploader("CSV de proxy (ANO, DIM, COUNT) ou tidy (ANO,DIM_TIPO,DIM_VALOR,COUNT)", type=["csv"], key="p1")
        if st.button("Carregar (upload)"):
            if fp:
                try:
                    dfp = load_proxy_from_upload(fp)
                    st.session_state["PROXY"] = dfp
                    st.success(f"Proxy carregado ({len(dfp):,} linhas).")
                    st.dataframe(dfp.head(20), use_container_width=True)
                except Exception as e:
                    st.error(f"Erro no proxy (upload): {e}")
            else:
                st.warning("Envie o CSV do proxy.")
    with colB:
        urlp = st.text_input("URL remota do CSV de proxy")
        if st.button("Carregar (URL)"):
            try:
                dfp = load_proxy_from_url(urlp)
                st.session_state["PROXY"] = dfp
                st.success(f"Proxy carregado ({len(dfp):,} linhas).")
                st.dataframe(dfp.head(20), use_container_width=True)
            except Exception as e:
                st.error(f"Erro no proxy (URL): {e}")

# --- 4) Oferta × Demanda × Conhecimento ---
elif menu == "Oferta × Demanda × Conhecimento":
    st.header("Oferta (PrEP) × Demanda (proxy) × Conhecimento (pesquisa)")
    users = st.session_state.get("MS_USERS")
    disp  = st.session_state.get("MS_DISP")
    prox  = st.session_state.get("PROXY")
    if users is None or disp is None:
        st.warning("Carregue os dados PrEP (aba 'Dados PrEP (MS)') via Upload/URL.")
    if prox is None:
        st.warning("Carregue o proxy (aba 'Proxy (distribuição)').")

    if (users is not None) and (disp is not None) and (prox is not None):
        dims_ok = [c for c in ["RACA_COR","FAIXA_ETARIA","ESCOLARIDADE","POPULACAO_CHAVE"] if c in users.columns]
        if not dims_ok:
            st.error("Não encontrei colunas de dimensão esperadas nos dados de usuários (ver dicionário do MS).")
        else:
            dim = st.selectbox("Dimensão", dims_ok)
            anos = disp["ANO"].dropna().astype(int).unique()
            ano  = st.selectbox("Ano", sorted(anos), index=len(anos)-1)

            # Suporte ao arquivo único 'tidy': ANO, DIM_TIPO, DIM_VALOR, COUNT
            if {'DIM_TIPO','DIM_VALOR','ANO','COUNT'}.issubset(set(prox.columns)):
                prox_work = prox[prox['DIM_TIPO'] == dim].rename(columns={'DIM_VALOR': dim}).copy()
            else:
                prox_work = prox.copy()

            # Escolha de colunas (funciona tanto para tidy quanto para CSV simples)
            prox_cols = prox_work.columns.tolist()
            col_dim = st.selectbox("Coluna DIM no proxy", prox_cols, index=prox_cols.index(dim) if dim in prox_cols else min(1,len(prox_cols)-1))
            col_ano = st.selectbox("Coluna ANO no proxy", prox_cols, index=prox_cols.index("ANO") if "ANO" in prox_cols else 0)
            col_cnt = st.selectbox("Coluna COUNT no proxy", prox_cols, index=prox_cols.index("COUNT") if "COUNT" in prox_cols else min(2,len(prox_cols)-1))

            # Padroniza nomes
            prox_std = prox_work.rename(columns={col_dim: dim, col_ano: "ANO", col_cnt: "COUNT"}).copy()

            # --- Patch robusto para garantir Series e strings na coluna de dimensão ---
            obj = prox_std[dim]
            if isinstance(obj, pd.DataFrame):
                prox_std[dim] = obj.iloc[:, 0]
            else:
                prox_std[dim] = obj
            if pdt.is_object_dtype(prox_std[dim]) or pdt.is_string_dtype(prox_std[dim]):
                prox_std[dim] = prox_std[dim].astype(str).str.strip()

            try:
                offer = offer_counts_by_year_dim(users, disp, dim_col=dim, year=int(ano))