# benchmark.py
import subprocess
import time
import csv
import os
import numpy as np

# Configurações
DATA_FILE = "data.log"
RESULTS_FILE = "results.csv"
SUMMARY_FILE = "summary.csv"
REPEAT = 5
LINES = 100000  # total de linhas do log
PIPELINE_CMD = ["python3", "main.py", DATA_FILE]  # comando do pipeline

# Gerar arquivo de teste se não existir
if not os.path.exists(DATA_FILE):
    print(f"[INFO] Gerando {DATA_FILE} com {LINES} linhas...")
    with open(DATA_FILE, "w") as f:
        for i in range(1, LINES + 1):
            f.write(f"INFO: Linha {i}\n")
            if i % 100 == 0:
                f.write(f"ERROR: Falha simulada {i}\n")

# Função para medir tempo de execução
def measure_time(cmd):
    start = time.time()
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    end = time.time()
    return end - start

# Função baseline Unix via Python
def measure_baseline(file):
    start = time.time()
    # equivalente ao grep 'ERROR' | wc -l
    count = subprocess.run(
        f"grep 'ERROR' {file} | wc -l",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    end = time.time()
    return end - start

# Executar benchmark
print(f"[INFO] Executando benchmark {REPEAT} vezes...")
results = []

for i in range(1, REPEAT + 1):
    t_pipeline = measure_time(PIPELINE_CMD)
    t_baseline = measure_baseline(DATA_FILE)
    results.append(("pipeline", i, t_pipeline))
    results.append(("baseline", i, t_baseline))

# Salvar resultados em CSV
with open(RESULTS_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["tipo", "execucao", "tempo"])
    writer.writerows(results)

# Calcular métricas
results_np = {}
for tipo in ["pipeline", "baseline"]:
    tempos = [r[2] for r in results if r[0] == tipo]
    mean = np.mean(tempos)
    std = np.std(tempos, ddof=1)
    ic95 = 1.96 * std / np.sqrt(len(tempos))
    results_np[tipo] = {"mean": mean, "std": std, "ic95": ic95}

speedup = results_np["baseline"]["mean"] / results_np["pipeline"]["mean"]

# Salvar summary em CSV
with open(SUMMARY_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["tipo", "mean", "std", "ic95"])
    for tipo, metrics in results_np.items():
        writer.writerow([tipo, metrics["mean"], metrics["std"], metrics["ic95"]])

# Mostrar métricas
print("\n=== MÉTRICAS DE DESEMPENHO ===")
for tipo, metrics in results_np.items():
    print(f"{tipo}: mean={metrics['mean']:.6f}s, std={metrics['std']:.6f}s, ic95={metrics['ic95']:.6f}s")
print(f"\nSpeedup: {speedup:.2f}x")
print(f"\nResultados salvos em {RESULTS_FILE} e {SUMMARY_FILE}")
