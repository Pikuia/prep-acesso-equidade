#!/bin/bash
echo "🚀 Sistema PrEP - Verificação e Backup"
echo "====================================="

echo "📦 Fazendo backup..."
python3 -c "from backup_manager import BackupManager; print('Backup:', BackupManager().backup_completo())"

echo ""
echo "📊 Status:"
TOTAL=$(sqlite3 pesquisa_prep.db "SELECT COUNT(*) FROM respostas;" 2>/dev/null || echo "0")
echo "Total de respostas: $TOTAL"

echo ""
echo "🎯 Para executar a aplicação:"
echo "python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0"
echo ""
echo "✅ Verificação concluída!"
