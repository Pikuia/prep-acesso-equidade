#!/usr/bin/env python3
# simular_respostas.py - Gera respostas aleatórias para o questionário PrEP

import random
import sqlite3
from datetime import datetime, timedelta
from database import salvar_resposta
import sys

def gerar_resposta_aleatoria():
    """Gera uma resposta aleatória focada em baixa renda e baixa escolaridade"""
    
    # Perfil focado em baixa renda e baixa escolaridade
    idades = ["18-24 anos", "25-29 anos", "30-34 anos", "35-39 anos", "40-49 anos"]
    
    generos = [
        "Homem cis (identifica-se com o gênero masculino atribuído no nascimento)",
        "Mulher cis (identifica-se com o gênero feminino atribuído no nascimento)",
        "Prefiro não informar"
    ]
    
    orientacoes = [
        "Heterossexual (se atrai por pessoas do sexo oposto)",
        "Homossexual (se atrai por pessoas do mesmo sexo)", 
        "Bissexual (se atrai por ambos os sexos)",
        "Prefiro não informar"
    ]
    
    racas = ["Parda", "Preta", "Branca", "Prefiro não informar"]
    
    # Foco em baixa escolaridade
    escolaridades = ["Fundamental", "Médio", "Prefiro não informar"]
    
    # Foco em baixa renda
    rendas = ["Até 1 salário", "1-3 salários", "Prefiro não informar"]
    
    status_relacionais = ["Solteiro", "Relacionamento exclusivo", "Relacionamento não exclusivo", "Prefiro não informar"]
    
    estados = ['SP', 'RJ', 'MG', 'BA', 'PE', 'CE', 'PA', 'MA', 'RS', 'PR', 'SC', 'GO', 'AM']
    
    # Maioria NÃO conhece PrEP (foco do perfil)
    conhecimento_prep = random.choices(["Não", "Sim"], weights=[75, 25])[0]
    
    # Se conhece, fonte limitada (sem muito acesso à informação)
    fontes_info = []
    if conhecimento_prep == "Sim":
        opcoes_fonte = ["Amigos", "Redes sociais", "Profissional de saúde"]
        fontes_info = random.sample(opcoes_fonte, random.randint(1, 2))
    
    # Maioria não sabe onde encontrar
    acesso = random.choices(["Não", "Sim"], weights=[70, 30])[0]
    
    # Uso da PrEP - maioria nunca usou
    usos = ["Nunca usei", "Nunca usei e não quero", "Não sei se preciso", "Nunca usei mas quero"]
    uso = random.choices(usos, weights=[40, 20, 25, 15])[0]
    
    objetivos = [
        "Prevenção contínua",
        "Curiosidade/avaliação", 
        "Situações específicas (viagem, parceiro novo)",
        "Outro"
    ]
    objetivo_prep = random.choice(objetivos)
    
    # Efeitos colaterais - NA para quem nunca usou
    efeitos_colaterais_teve = "Não se aplica"
    efeitos_colaterais_quais = ""
    
    if uso in ["Uso atualmente", "Já usei"]:
        efeitos_colaterais_teve = random.choice(["Não", "Sim", "Não tenho certeza"])
        if efeitos_colaterais_teve == "Sim":
            efeitos_lista = ["Náusea", "Dor de cabeça", "Tontura", "Cansaço"]
            efeitos_colaterais_quais = ", ".join(random.sample(efeitos_lista, random.randint(1, 2)))
    
    # Barreiras - pessoas com baixa escolaridade/renda
    barreiras_opcoes = [
        "Não acho que preciso",
        "Falta de informação", 
        "Dificuldade de acesso",
        "Vergonha",
        "Medo de efeitos"
    ]
    barreiras = random.sample(barreiras_opcoes, random.randint(2, 4))
    
    # Percepção de risco - geralmente baixa por falta de informação
    percepcao_risco = random.choices(range(11), weights=[15, 20, 20, 15, 10, 8, 5, 3, 2, 1, 1])[0]
    
    # Comentários típicos do perfil
    comentarios_opcoes = [
        "",
        "Não sabia que existia essa medicação",
        "Preciso saber mais sobre isso",
        "Onde posso conseguir mais informações?",
        "É caro?",
        "Tem no posto de saúde?",
        "Nunca ouvi falar",
        "Meu médico nunca comentou",
        "É seguro?",
        "Como funciona?"
    ]
    comentarios = random.choice(comentarios_opcoes)
    
    resposta = {
        'idade': random.choice(idades),
        'genero': random.choice(generos),
        'orientacao_sexual': random.choice(orientacoes),
        'raca': random.choice(racas),
        'escolaridade': random.choice(escolaridades),
        'renda': random.choice(rendas),
        'regiao': random.choice(estados),
        'status_relacional': random.choice(status_relacionais),
        'conhecimento_prep': conhecimento_prep,
        'uso_prep': uso,
        'objetivo_prep': objetivo_prep,
        'acesso_servico': acesso,
        'fonte_info': ", ".join(fontes_info),
        'barreiras': ", ".join(barreiras),
        'percepcao_risco': percepcao_risco,
        'efeitos_colaterais_teve': efeitos_colaterais_teve,
        'efeitos_colaterais_quais': efeitos_colaterais_quais,
        'comentarios': comentarios
    }
    
    return resposta

def simular_respostas(quantidade=50):
    """Simula múltiplas respostas"""
    print(f"🎲 Gerando {quantidade} respostas aleatórias...")
    print("Perfil: Baixa renda, baixa escolaridade, pouco conhecimento sobre PrEP")
    print("-" * 60)
    
    sucessos = 0
    erros = 0
    
    for i in range(quantidade):
        try:
            resposta = gerar_resposta_aleatoria()
            
            # Salvar diretamente no banco (sem usar Streamlit)
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
            
            sucessos += 1
            
            # Mostrar progresso
            if (i + 1) % 10 == 0:
                print(f"✅ {i + 1}/{quantidade} respostas geradas")
                
        except Exception as e:
            erros += 1
            print(f"❌ Erro na resposta {i + 1}: {e}")
    
    print("-" * 60)
    print(f"✅ Simulação concluída!")
    print(f"   Sucessos: {sucessos}")
    print(f"   Erros: {erros}")
    
    # Mostrar total atual
    try:
        conn = sqlite3.connect('pesquisa_prep.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM respostas")
        total = cursor.fetchone()[0]
        conn.close()
        print(f"   Total no banco: {total}")
    except Exception as e:
        print(f"   Erro ao contar total: {e}")
    
    # Fazer backup após simulação
    try:
        from backup_manager import BackupManager
        backup_manager = BackupManager()
        resultado = backup_manager.backup_completo()
        print(f"📦 Backup realizado: {resultado['timestamp']}")
    except Exception as e:
        print(f"⚠️  Erro no backup: {e}")

def mostrar_estatisticas():
    """Mostra estatísticas das respostas simuladas"""
    try:
        conn = sqlite3.connect('pesquisa_prep.db')
        cursor = conn.cursor()
        
        print("\n📊 Estatísticas das Respostas:")
        print("-" * 40)
        
        # Total
        cursor.execute("SELECT COUNT(*) FROM respostas")
        total = cursor.fetchone()[0]
        print(f"Total de respostas: {total}")
        
        # Conhecimento PrEP
        cursor.execute("SELECT conhecimento_prep, COUNT(*) FROM respostas GROUP BY conhecimento_prep")
        print("\nConhecimento sobre PrEP:")
        for conhecimento, count in cursor.fetchall():
            print(f"  {conhecimento}: {count}")
        
        # Escolaridade
        cursor.execute("SELECT escolaridade, COUNT(*) FROM respostas GROUP BY escolaridade")
        print("\nEscolaridade:")
        for escolaridade, count in cursor.fetchall():
            print(f"  {escolaridade}: {count}")
        
        # Renda
        cursor.execute("SELECT renda, COUNT(*) FROM respostas GROUP BY renda")
        print("\nRenda:")
        for renda, count in cursor.fetchall():
            print(f"  {renda}: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro ao mostrar estatísticas: {e}")

if __name__ == "__main__":
    # Verificar argumentos
    quantidade = 50
    if len(sys.argv) > 1:
        try:
            quantidade = int(sys.argv[1])
        except ValueError:
            print("Uso: python simular_respostas.py [quantidade]")
            sys.exit(1)
    
    # Criar tabela se não existir
    from database import criar_tabela_respostas
    criar_tabela_respostas()
    
    # Simular respostas
    simular_respostas(quantidade)
    
    # Mostrar estatísticas
    mostrar_estatisticas()