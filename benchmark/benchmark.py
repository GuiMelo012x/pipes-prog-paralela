import subprocess
import time
import statistics
import pandas as pd
from pathlib import Path
import random
import numpy as np
from math import sqrt

# === Controle de reprodutibilidade ===
def set_seed(seed=42):
    """Define semente fixa para reprodutibilidade dos testes."""
    random.seed(seed)
    np.random.seed(seed)
    print(f"[INFO] Seed definida para {seed}")

set_seed()
# =====================================

RESULTS_DIR = Path("../results")
LOG_FILE = Path("access_sample.log")
PIPELINE_CMD = "python3 ../src/main.py"
BASELINE_CMD = f'grep \"ERROR\" {LOG_FILE} | wc -l'

RUNS = 5
Z95 = 1.96  # z-score 95%

# === Funções auxiliares ===
def ic95(times):
    """Calcula intervalo de confiança 95%."""
    mean = statistics.mean(times)
    stdev = statistics.stdev(times)
    ic = Z95 * (stdev / sqrt(len(times)))
    return mean, stdev, ic

# === Execução dos comandos ===
def run_pipeline():
    start = time.perf_counter()
    subprocess.run(PIPELINE_CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    end = time.perf_counter()
    return end - start

def run_baseline():
    start = time.perf_counter()
    subprocess.run(BASELINE_CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    end = time.perf_counter()
    return end - start

# === Benchmarks ===
def benchmark_pipeline(runs=RUNS):
    print(f"\nExecutando pipeline ({runs} repetições)...")
    times = [run_pipeline() for _ in range(runs)]
    mean, stdev, ic = ic95(times)
    return mean, stdev, ic, times

def benchmark_baseline(runs=RUNS):
    print(f"\nExecutando baseline grep+wc ({runs} repetições)...")
    times = [run_baseline() for _ in range(runs)]
    mean, stdev, ic = ic95(times)
    return mean, stdev, ic, times

# === Salvamento ===
def save_results(pipeline_stats, baseline_stats):
    RESULTS_DIR.mkdir(exist_ok=True)

    df = pd.DataFrame({
        "run": range(1, RUNS + 1),
        "pipeline_time": pipeline_stats[3],
        "baseline_time": baseline_stats[3],
    })
    df.to_csv(RESULTS_DIR / "results.csv", index=False)

    summary = pd.DataFrame([{
        "pipeline_mean": pipeline_stats[0],
        "pipeline_std": pipeline_stats[1],
        "pipeline_ic95": pipeline_stats[2],
        "baseline_mean": baseline_stats[0],
        "baseline_std": baseline_stats[1],
        "baseline_ic95": baseline_stats[2],
        "speedup": baseline_stats[0] / pipeline_stats[0],
    }])
    summary.to_csv(RESULTS_DIR / "summary.csv", index=False)

# === Main ===
def main():
    if not LOG_FILE.exists():
        print("Arquivo de log não encontrado. Gerando arquivo de teste...")
        with open(LOG_FILE, "w") as f:
            for i in range(10000):
                # Mesmo padrão garantido pela seed
                level = "ERROR" if i % 5 == 0 else "INFO"
                f.write(f"{level}: Mensagem número {i}\n")

    pipeline_stats = benchmark_pipeline()
    baseline_stats = benchmark_baseline()

    save_results(pipeline_stats, baseline_stats)

    print("\n=== Resultados ===")
    print(f"Pipeline: {pipeline_stats[0]:.4f}s ± {pipeline_stats[1]:.4f} (IC95 ±{pipeline_stats[2]:.4f})")
    print(f"Baseline: {baseline_stats[0]:.4f}s ± {baseline_stats[1]:.4f} (IC95 ±{baseline_stats[2]:.4f})")
    print(f"Speedup: {baseline_stats[0] / pipeline_stats[0]:.2f}x")
    print(f"\nArquivos gerados em: {RESULTS_DIR.absolute()}")

if __name__ == "__main__":
    main()
