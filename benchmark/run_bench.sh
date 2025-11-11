import subprocess
import time
import csv
import os
import numpy as np

DATA_FILE = "data.log"
RESULTS_FILE = "../results/results.csv"
SUMMARY_FILE = "../results/summary.csv"
REPEAT = 5
LINES = 100000
PIPELINE_CMD = ["python3", "../src/main.py", DATA_FILE]

os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)

# Gerar arquivo de teste se não existir
if not os.path.exists(DATA_FILE):
    print(f"[INFO] Gerando {DATA_FILE} com {LINES} linhas...")
    with open(DATA_FILE, "w") as f:
        for i in range(1, LINES + 1):
            f.write(f"INFO: Linha {i}\n")
            if i % 100 == 0:
                f.write(f"ERROR: Falha simulada {i}\n")

def measure_time(cmd):
    start = time.perf_counter()
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    end = time.perf_counter()
    return end - start

def measure_baseline(file):
    start = time.perf_counter()
    subprocess.run(
        f"grep 'ERROR' {file} | wc -l",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )
    end = time.perf_counter()
    return end - start

print(f"[INFO] Executando benchmark {REPEAT} vezes...")
results = []

for i in range(1, REPEAT + 1):
    t_pipeline = measure_time(PIPELINE_CMD)
    t_baseline = measure_baseline(DATA_FILE)
    results.append(("pipeline", i, t_pipeline))
    results.append(("baseline", i, t_baseline))

# CSV results
with open(RESULTS_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["tipo", "execucao", "tempo"])
    writer.writerows(results)

# Métricas
results_np = {}
for tipo in ["pipeline", "baseline"]:
    tempos = [r[2] for r in results if r[0] == tipo]
    mean = np.mean(tempos)
    std = np.std(tempos, ddof=1)
    ic95 = 1.96 * std / np.sqrt(len(tempos))
    results_np[tipo] = {"mean": mean, "std": std, "ic95": ic95}

speedup = results_np["baseline"]["mean"] / results_np["pipeline"]["mean"]

# Summary CSV
with open(SUMMARY_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["tipo", "mean", "std", "ic95"])
    for tipo, m in results_np.items():
        writer.writerow([tipo, m["mean"], m["std"], m["ic95"]])

print("\n=== MÉTRICAS DE DESEMPENHO ===")
for tipo, m in results_np.items():
    print(f"{tipo}: mean={m['mean']:.6f}s, std={m['std']:.6f}s, ic95={m['ic95']:.6f}s")
print(f"\nSpeedup: {speedup:.2f}x")
print(f"\nResultados salvos em {RESULTS_FILE} e {SUMMARY_FILE}")
