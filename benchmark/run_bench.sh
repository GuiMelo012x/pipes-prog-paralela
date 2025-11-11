#!/bin/bash
# ============================================================
# Script de benchmark automatizado - Pipeline vs Baseline (grep+wc)
# ============================================================

# Configurações
SRC_DIR="../src"
DATA_FILE="access_sample.log"
RESULTS_DIR="../results"
RESULTS_FILE="$RESULTS_DIR/results.csv"
SUMMARY_FILE="$RESULTS_DIR/summary.csv"
PYTHON_BIN="python3"
REPEAT=5

# ============================================================
# Pré-execução
# ============================================================

echo "[INFO] Preparando ambiente..."
mkdir -p "$RESULTS_DIR"

# Gera log de exemplo se não existir
if [ ! -f "$DATA_FILE" ]; then
  echo "[INFO] Gerando $DATA_FILE..."
  cat << EOF > "$DATA_FILE"
127.0.0.1 - - [09/Nov/2025:14:00:00] "GET /api/produto/1 HTTP/1.1" 200
127.0.0.1 - - [09/Nov/2025:14:01:00] "GET /api/produto/2 HTTP/1.1" 500
127.0.0.1 - - [09/Nov/2025:14:01:01] "GET /api/produto/3 HTTP/1.1" 500
127.0.0.1 - - [09/Nov/2025:14:02:00] "POST /api/login HTTP/1.1" 500
127.0.0.1 - - [09/Nov/2025:14:03:00] "GET /api/produto/2 HTTP/1.1" 500
INFO: Inicializando sistema
ERROR: Falha ao abrir arquivo
INFO: Usuário logado
ERROR: Conexão perdida
INFO: Operação concluída
ERROR: Timeout na requisição
INFO: Usuário entrou no sistema
ERROR: Falha na autenticação
INFO: Usuário saiu
ERROR: Falha na conexão
ERROR: Timeout na requisição
INFO: Sistema finalizado com sucesso
EOF
fi

# ============================================================
# Execução principal (Benchmark Python)
# ============================================================

echo "[INFO] Executando benchmark com $REPEAT repetições..."
$PYTHON_BIN "$SRC_DIR/../benchmark/benchmark.py" > "$RESULTS_DIR/benchmark_output.log" 2>&1

# ============================================================
# Exibição dos resultados
# ============================================================

if [ -f "$SUMMARY_FILE" ]; then
  echo ""
  echo "=== RESULTADOS DO BENCHMARK ==="
  column -s, -t "$SUMMARY_FILE"
  echo ""
  echo "Speedup calculado: "
  grep "Speedup" "$RESULTS_DIR/benchmark_output.log" || echo "Ver arquivo de log em $RESULTS_DIR/benchmark_output.log"
else
  echo "[ERRO] Arquivo $SUMMARY_FILE não encontrado."
  echo "Verifique o log em $RESULTS_DIR/benchmark_output.log"
fi
echo "[INFO] Benchmark concluído."