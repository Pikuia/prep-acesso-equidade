#!/usr/bin/env python3
# analise_simulacao.py - Análise dos dados simulados

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def analisar_dados_simulados():
    """Análise completa dos dados simulados"""
    print("📊 ANÁLISE DOS DADOS SIMULADOS")
    print("=" * 50)
    
    # Conectar ao banco
    conn = sqlite3.connect('pesquisa_prep.db')
    df = pd.read_sql("SELECT * FROM respostas", conn)
    conn.close()
    
    print(f"📈 Total de respostas: {len(df)}")
    print(f"📅 Período: {df['data_envio'].min()} até {df['data_envio'].max()}")
    print()
    
    # Análise por categoria
    categorias = {
        'Conhecimento sobre PrEP': 'conhecimento_prep',
        'Escolaridade': 'escolaridade', 
        'Renda': 'renda',
        'Faixa Etária': 'idade',
        'Gênero': 'genero',
        'Raça/Cor': 'raca',
        'Uso da PrEP': 'uso_prep',
        'Acesso ao Serviço': 'acesso_servico'
    }
    
    for titulo, coluna in categorias.items():
        print(f"🔍 {titulo}:")
        contagem = df[coluna].value_counts()
        total = len(df)
        
        for valor, count in contagem.items():
            porcentagem = (count / total) * 100
            print(f"   {valor}: {count} ({porcentagem:.1f}%)")
        print()
    
    # Análise de percepção de risco
    print("🎯 Percepção de Risco (0-10):")
    risco_stats = df['percepcao_risco'].describe()
    print(f"   Média: {risco_stats['mean']:.1f}")
    print(f"   Mediana: {risco_stats['50%']:.1f}")
    print(f"   Mínimo: {risco_stats['min']:.0f}")
    print(f"   Máximo: {risco_stats['max']:.0f}")
    print()
    
    # Análise de barreiras mais comuns
    print("🚧 Barreiras mais mencionadas:")
    todas_barreiras = []
    for barreiras in df['barreiras'].dropna():
        if barreiras:
            todas_barreiras.extend([b.strip() for b in barreiras.split(',')])
    
    from collections import Counter
    contador_barreiras = Counter(todas_barreiras)
    
    for barreira, count in contador_barreiras.most_common(10):
        if barreira:
            porcentagem = (count / len(df)) * 100
            print(f"   {barreira}: {count} ({porcentagem:.1f}%)")
    print()
    
    # Análise cruzada: Conhecimento x Escolaridade
    print("🔄 Conhecimento sobre PrEP por Escolaridade:")
    crosstab = pd.crosstab(df['escolaridade'], df['conhecimento_prep'], normalize='index') * 100
    print(crosstab.round(1))
    print()
    
    # Análise cruzada: Conhecimento x Renda
    print("🔄 Conhecimento sobre PrEP por Renda:")
    crosstab2 = pd.crosstab(df['renda'], df['conhecimento_prep'], normalize='index') * 100
    print(crosstab2.round(1))
    print()
    
    # Comentários mais comuns
    print("💬 Comentários mais comuns:")
    comentarios = df['comentarios'].dropna()
    comentarios_nao_vazios = comentarios[comentarios != '']
    
    if len(comentarios_nao_vazios) > 0:
        contador_comentarios = Counter(comentarios_nao_vazios)
        for comentario, count in contador_comentarios.most_common(8):
            print(f"   '{comentario}': {count}x")
    else:
        print("   Nenhum comentário específico encontrado")
    print()
    
    # Insights principais
    print("💡 INSIGHTS PRINCIPAIS:")
    print("-" * 30)
    
    # Conhecimento
    nao_conhece = (df['conhecimento_prep'] == 'Não').sum()
    total = len(df)
    perc_nao_conhece = (nao_conhece / total) * 100
    print(f"• {perc_nao_conhece:.1f}% NÃO conhecem a PrEP")
    
    # Escolaridade baixa
    esc_baixa = df['escolaridade'].isin(['Fundamental', 'Médio']).sum()
    perc_esc_baixa = (esc_baixa / total) * 100
    print(f"• {perc_esc_baixa:.1f}% têm ensino fundamental ou médio")
    
    # Renda baixa
    renda_baixa = df['renda'].isin(['Até 1 salário', '1-3 salários']).sum()
    perc_renda_baixa = (renda_baixa / total) * 100
    print(f"• {perc_renda_baixa:.1f}% têm renda de até 3 salários")
    
    # Acesso
    nao_sabe_acesso = (df['acesso_servico'] == 'Não').sum()
    perc_nao_acesso = (nao_sabe_acesso / total) * 100
    print(f"• {perc_nao_acesso:.1f}% NÃO sabem onde encontrar PrEP")
    
    # Percepção de risco baixa
    risco_baixo = (df['percepcao_risco'] <= 3).sum()
    perc_risco_baixo = (risco_baixo / total) * 100
    print(f"• {perc_risco_baixo:.1f}% têm percepção de risco baixa (≤3)")
    
    print()
    print("✅ Análise concluída!")
    print("Os dados simulados refletem o perfil solicitado:")
    print("- Baixa renda e escolaridade")
    print("- Pouco conhecimento sobre PrEP")
    print("- Dificuldade de acesso a informações")

if __name__ == "__main__":
    try:
        analisar_dados_simulados()
    except Exception as e:
        print(f"Erro na análise: {e}")
        import traceback
        traceback.print_exc()