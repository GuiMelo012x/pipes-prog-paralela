#!/bin/bash

# Configurações
BIN="../src/main.py"
DATA_FILE="access_sample.log"
RESULTS_DIR="../results"
RESULTS_FILE="$RESULTS_DIR/results.csv"
SUMMARY_FILE="$RESULTS_DIR/summary.csv"
REPEAT=5

# Cria pasta de resultados se não existir
mkdir -p "$RESULTS_DIR"

# Limpa arquivos antigos
rm -f "$RESULTS_FILE" "$SUMMARY_FILE"

echo "[INFO] Executando benchmark $REPEAT vezes..."

# Cria CSV de resultados
echo "execucao,tempo" > "$RESULTS_FILE"

for i in $(seq 1 $REPEAT); do
    START=$(date +%s.%N)
    python3 "$BIN" "$DATA_FILE" > /dev/null
    END=$(date +%s.%N)
    DURATION=$(echo "$END - $START" | bc)
    echo "$i,$DURATION" >> "$RESULTS_FILE"
done

# Calcula métricas com Python
python3 - << EOF
import pandas as pd
import numpy as np

df = pd.read_csv("$RESULTS_FILE")
mean = df['tempo'].mean()
std = df['tempo'].std()
ic95 = 1.96 * std / np.sqrt(len(df))

summary = pd.DataFrame({
    'Mean':[mean],
    'Std':[std],
    'IC95':[ic95]
})

summary.to_csv("$SUMMARY_FILE", index=False)
print("=== MÉTRICAS DE DESEMPENHO ===")
print(summary)
EOF

echo "[INFO] Benchmark finalizado. Resultados em $RESULTS_FILE e $SUMMARY_FILE"
