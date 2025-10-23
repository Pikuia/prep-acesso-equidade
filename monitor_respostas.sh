#!/bin/bash
# monitor_respostas.sh - Script para monitorar e fazer backup das respostas

echo "=== Monitor de Respostas PrEP ==="
echo "Data/Hora: $(date)"

# Contar respostas atuais
TOTAL_RESPOSTAS=$(sqlite3 pesquisa_prep.db "SELECT COUNT(*) FROM respostas;")
echo "Total de respostas atual: $TOTAL_RESPOSTAS"

# Verificar se existe log anterior
LOG_FILE="monitor_log.txt"
if [ -f "$LOG_FILE" ]; then
    ULTIMO_TOTAL=$(tail -n 1 "$LOG_FILE" | cut -d',' -f2)
    echo "Último total registrado: $ULTIMO_TOTAL"
    
    if [ "$TOTAL_RESPOSTAS" -lt "$ULTIMO_TOTAL" ]; then
        echo "⚠️  ALERTA: Perda de respostas detectada!"
        echo "Antes: $ULTIMO_TOTAL, Agora: $TOTAL_RESPOSTAS"
        
        # Fazer backup de emergência
        echo "Fazendo backup de emergência..."
        python3 -c "from backup_manager import BackupManager; BackupManager().backup_completo()"
        
        # Notificar por email (se configurado)
        # mail -s "ALERTA: Perda de respostas PrEP" admin@exemplo.com < /dev/null
    fi
fi

# Registrar no log
echo "$(date),$TOTAL_RESPOSTAS" >> "$LOG_FILE"

# Fazer backup automático a cada 10 respostas
if [ $((TOTAL_RESPOSTAS % 10)) -eq 0 ] && [ "$TOTAL_RESPOSTAS" -gt 0 ]; then
    echo "Fazendo backup automático (múltiplo de 10)..."
    python3 -c "from backup_manager import BackupManager; BackupManager().backup_completo()"
fi

echo "Monitor executado com sucesso!"
echo "================================"