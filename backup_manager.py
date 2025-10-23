# backup_manager.py
import sqlite3
import pandas as pd
import os
import shutil
from datetime import datetime
import json

class BackupManager:
    def __init__(self, db_path='pesquisa_prep.db'):
        self.db_path = db_path
        self.backup_dir = 'backups'
        self.csv_backup_dir = 'csv_backups'
        
        # Criar diretórios de backup se não existirem
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(self.csv_backup_dir, exist_ok=True)
    
    def criar_backup_db(self):
        """Cria backup do banco SQLite com timestamp"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"pesquisa_prep_backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, backup_path)
                return backup_path
            return None
        except Exception as e:
            print(f"Erro ao criar backup do banco: {e}")
            return None
    
    def exportar_csv(self):
        """Exporta dados para CSV como backup adicional"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql("SELECT * FROM respostas", conn)
            conn.close()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"respostas_backup_{timestamp}.csv"
            csv_path = os.path.join(self.csv_backup_dir, csv_filename)
            
            df.to_csv(csv_path, index=False, encoding='utf-8')
            return csv_path
        except Exception as e:
            print(f"Erro ao exportar CSV: {e}")
            return None
    
    def exportar_json(self):
        """Exporta dados para JSON como backup adicional"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql("SELECT * FROM respostas", conn)
            conn.close()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = f"respostas_backup_{timestamp}.json"
            json_path = os.path.join(self.csv_backup_dir, json_filename)
            
            # Converter DataFrame para JSON
            df.to_json(json_path, orient='records', date_format='iso', indent=2)
            return json_path
        except Exception as e:
            print(f"Erro ao exportar JSON: {e}")
            return None
    
    def backup_completo(self):
        """Realiza backup completo em múltiplos formatos"""
        resultados = {
            'db_backup': self.criar_backup_db(),
            'csv_backup': self.exportar_csv(),
            'json_backup': self.exportar_json(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Salvar log do backup
        log_path = os.path.join(self.backup_dir, 'backup_log.json')
        logs = []
        
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                logs = json.load(f)
        
        logs.append(resultados)
        
        with open(log_path, 'w') as f:
            json.dump(logs, f, indent=2)
        
        return resultados
    
    def contar_respostas(self):
        """Conta o número atual de respostas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM respostas")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            print(f"Erro ao contar respostas: {e}")
            return 0
    
    def listar_backups(self):
        """Lista todos os backups disponíveis"""
        backups = {
            'db_backups': [],
            'csv_backups': []
        }
        
        if os.path.exists(self.backup_dir):
            for file in os.listdir(self.backup_dir):
                if file.endswith('.db'):
                    backups['db_backups'].append(file)
        
        if os.path.exists(self.csv_backup_dir):
            for file in os.listdir(self.csv_backup_dir):
                if file.endswith('.csv') or file.endswith('.json'):
                    backups['csv_backups'].append(file)
        
        return backups
    
    def restaurar_backup(self, backup_path):
        """Restaura backup do banco de dados"""
        try:
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, self.db_path)
                return True
            return False
        except Exception as e:
            print(f"Erro ao restaurar backup: {e}")
            return False

def backup_automatico():
    """Função para ser chamada automaticamente"""
    backup_manager = BackupManager()
    resultado = backup_manager.backup_completo()
    print(f"Backup realizado: {resultado}")
    return resultado

if __name__ == "__main__":
    # Teste do sistema de backup
    backup_manager = BackupManager()
    print(f"Respostas atuais: {backup_manager.contar_respostas()}")
    resultado = backup_manager.backup_completo()
    print(f"Backup realizado: {resultado}")