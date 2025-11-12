#!/bin/bash
# run_all.sh — Executa todo o pipeline do projeto

set -e  # Para o script se ocorrer qualquer erro

echo "===> Limpando resultados antigos..."
rm -f results/*.csv benchmark/*.log

echo "===> Executando aplicação principal..."
python3 src/main.py data.log

echo "===> Executando benchmark..."
bash benchmark/run_bench.sh

echo "===> Projeto finalizado com sucesso!"
