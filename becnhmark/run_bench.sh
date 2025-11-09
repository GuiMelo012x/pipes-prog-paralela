#!/bin/bash

# Script de benchmark do projeto Pipes

# Configurações
BIN="./pipeline"                      # binário do teu programa
BASELINE_CMD="grep 'ERROR' data.log | grep -v 'DEBUG' | wc -l"  # baseline (exemplo)
DATA_FILE="data.log"
RESULTS_FILE="results.csv"
REPEAT=10                         # número de repetições
CONFIDENCE=1.96                   # intervalo de confiança 95%

# Função para medir tempo de execução (em segundos)
measure_time() {
    START=$(date +%s.%N)
    eval "$1" > /dev/null 2>&1
    END=$(date +%s.%N)
    echo "$END - $START" | bc
}

# Gera arquivo de dados de teste (se não existir)
if [ ! -f "$DATA_FILE" ]; then
    echo "[INFO] Gerando $DATA_FILE..."
    for i in $(seq 1 500000); do
        echo "INFO: Mensagem $i" >> $DATA_FILE
        [ $((i % 100)) -eq 0 ] && echo "ERROR: Falha simulada $i" >> $DATA_FILE
    done
fi

# Compila o projeto
echo "[INFO] Compilando..."
make clean && make

# Cria CSV de resultados
echo "tipo,execucao,tempo" > "$RESULTS_FILE"

# Executa benchmark
echo "[INFO] Iniciando benchmark com $REPEAT repetições..."
for i in $(seq 1 $REPEAT); do
    # Benchmark do teu programa
    T_PIPE=$(measure_time "$BIN $DATA_FILE")
    echo "pipeline,$i,$T_PIPE" >> "$RESULTS_FILE"

    # Benchmark do baseline
    T_BASE=$(measure_time "$BASELINE_CMD")
    echo "baseline,$i,$T_BASE" >> "$RESULTS_FILE"
done

# Cálculo das estatísticas
echo "[INFO] Calculando métricas..."
python3 - <<'EOF'
import pandas as pd
import numpy as np

df = pd.read_csv("results.csv")
summary = df.groupby("tipo")["tempo"].agg(['mean', 'std'])
summary['ic95'] = (1.96 * summary['std']) / np.sqrt(10)
baseline = summary.loc['baseline', 'mean']
pipeline = summary.loc['pipeline', 'mean']
speedup = baseline / pipeline

print("\n=== MÉTRICAS DE DESEMPENHO ===")
print(summary)
print(f"\nSpeedup: {speedup:.2f}x")

summary.to_csv("summary.csv")
EOF

echo "[INFO] Resultados salvos em results.csv e summary.csv"
