#!/bin/bash
# Script de benchmark para pipeline Python

BIN="python3 ./src/main.py"
DATA_FILE="access_sample.log"
RESULTS_FILE="results.csv"
REPEAT=5  # número de execuções para benchmark

# Gera arquivo de teste se não existir
if [ ! -f "$DATA_FILE" ]; then
    echo "[INFO] Gerando $DATA_FILE..."
    for i in $(seq 1 50000); do
        echo "INFO: Mensagem $i" >> "$DATA_FILE"
        if [ $((i % 100)) -eq 0 ]; then
            echo "ERROR: Falha simulada $i" >> "$DATA_FILE"
        fi
    done
fi

# Cria CSV de resultados
echo "execucao,tempo" > "$RESULTS_FILE"

for i in $(seq 1 $REPEAT); do
    START=$(date +%s.%N)
    $BIN $DATA_FILE > /dev/null
    END=$(date +%s.%N)
    DIFF=$(echo "$END - $START" | bc)
    echo "$i,$DIFF" >> "$RESULTS_FILE"
done

# Estatísticas simples usando Python
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
