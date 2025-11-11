#!/bin/bash

# =============================
# Benchmark automatizado do pipeline
# =============================

BIN="../src/main.py"
DATA_FILE="access_sample.log"
RESULTS_DIR="../results"
RESULTS_FILE="$RESULTS_DIR/results.csv"
SUMMARY_FILE="$RESULTS_DIR/summary.csv"
REPEAT=5

# Garante que pasta de resultados exista
mkdir -p "$RESULTS_DIR"

# Limpa resultados antigos
rm -f "$RESULTS_FILE" "$SUMMARY_FILE"

echo "[INFO] Executando benchmark com $REPEAT repetições..."

# Cria CSV base
echo "tipo,execucao,tempo" > "$RESULTS_FILE"

# === Função auxiliar para medir tempo médio ===
measure_time() {
    local tipo=$1
    local cmd=$2

    for i in $(seq 1 $REPEAT); do
        START=$(date +%s.%N)
        eval "$cmd" > /dev/null 2>&1
        END=$(date +%s.%N)
        DURATION=$(echo "$END - $START" | bc)
        echo "$tipo,$i,$DURATION" >> "$RESULTS_FILE"
    done
}

# Executa pipeline
measure_time "pipeline" "python3 $BIN $DATA_FILE"

# Executa baseline (grep + wc -l simulando pipeline em Unix)
measure_time "baseline" "grep 'ERROR' $DATA_FILE | wc -l"

# Calcula métricas e speedup em Python
python3 - << EOF
import pandas as pd
import numpy as np

df = pd.read_csv("$RESULTS_FILE")

summary = []
for tipo in df['tipo'].unique():
    subset = df[df['tipo'] == tipo]['tempo']
    mean = subset.mean()
    std = subset.std(ddof=1)
    ic95 = 1.96 * std / np.sqrt(len(subset))
    summary.append([tipo, mean, std, ic95])

summary_df = pd.DataFrame(summary, columns=["tipo", "mean", "std", "ic95"])
summary_df.to_csv("$SUMMARY_FILE", index=False)

# Calcula speedup
pipeline_mean = summary_df.loc[summary_df['tipo']=="pipeline", 'mean'].values[0]
baseline_mean = summary_df.loc[summary_df['tipo']=="baseline", 'mean'].values[0]
speedup = baseline_mean / pipeline_mean

print("\n=== RESULTADOS DO BENCHMARK ===")
print(summary_df.to_string(index=False))
print(f"\n Speedup médio (baseline / pipeline): {speedup:.2f}x")
EOF

echo -e "\n[INFO] Benchmark finalizado. Resultados em $RESULTS_FILE e $SUMMARY_FILE"
