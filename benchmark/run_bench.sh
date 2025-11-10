#!/bin/bash
# Script de benchmark do pipeline Python

BIN="../src/main.py"
DATA_FILE="access_sample.log"
RESULTS_FILE="../results/results.csv"
REPEAT=5

mkdir -p ../results

# Gera arquivo de log de teste se não existir
if [ ! -f "$DATA_FILE" ]; then
    echo "[INFO] Gerando $DATA_FILE..."
    for i in $(seq 1 5000); do
        echo "INFO: Mensagem $i" >> $DATA_FILE
        [ $((i % 100)) -eq 0 ] && echo "ERROR: Falha simulada $i" >> $DATA_FILE
    done
fi

echo "execucao,tempo" > "$RESULTS_FILE"

echo "[INFO] Executando benchmark $REPEAT vezes..."
for i in $(seq 1 $REPEAT); do
    START=$(date +%s.%N)
    python3 "$BIN" "$DATA_FILE" > /dev/null
    END=$(date +%s.%N)
    ELAPSED=$(echo "$END - $START" | bc)
    echo "$i,$ELAPSED" >> "$RESULTS_FILE"
done

# Calcula métricas
python3 - <<EOF
import pandas as pd
import numpy as np

df = pd.read_csv("$RESULTS_FILE")
mean = df['tempo'].mean()
std = df['tempo'].std()
ic95 = 1.96 * std / np.sqrt(len(df))

print("\n=== MÉTRICAS DE DESEMPENHO ===")
print(f"Mean: {mean:.6f}s")
print(f"Std: {std:.6f}s")
print(f"IC95: {ic95:.6f}s")
EOF
echo "[INFO] Benchmark concluído. Resultados salvos em $RESULTS_FILE"