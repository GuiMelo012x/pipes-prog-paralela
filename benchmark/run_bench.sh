#!/bin/bash

# Script de benchmark simples
BIN="../src/main.py"
LOG_FILE="access_sample.log"
RESULTS_FILE="results.csv"
REPEAT=5

echo "[INFO] Executando benchmark $REPEAT vezes..."
echo "execucao,tempo" > "$RESULTS_FILE"

for i in $(seq 1 $REPEAT); do
    START=$(date +%s.%N)
    python3 "$BIN" "$LOG_FILE" > /dev/null
    END=$(date +%s.%N)
    TIME=$(echo "$END - $START" | bc)
    echo "$i,$TIME" >> "$RESULTS_FILE"
done

# Calcula métricas simples
MEAN=$(awk -F, '{sum+=$2} END {print sum/NR}' "$RESULTS_FILE")
echo -e "\n=== MÉTRICAS DE DESEMPENHO ==="
echo "Mean: ${MEAN}s"
