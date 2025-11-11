import subprocess
import time
import statistics
import pandas as pd
from pathlib import Path

RESULTS_DIR = Path("../results")
LOG_FILE = Path("access_sample.log")
PIPELINE_CMD = "python3 ../src/main.py"
BASELINE_CMD = f'grep "ERROR" {LOG_FILE} | wc -l'

RUNS = 5

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

def benchmark_pipeline(runs=RUNS):
    print(f"\nExecutando pipeline ({runs} repetições)...")
    times = [run_pipeline() for _ in range(runs)]
    mean = statistics.mean(times)
    stdev = statistics.stdev(times)
    return mean, stdev, times

def benchmark_baseline(runs=RUNS):
    print(f"\nExecutando baseline grep+wc ({runs} repetições)...")
    times = [run_baseline() for _ in range(runs)]
    mean = statistics.mean(times)
    stdev = statistics.stdev(times)
    return mean, stdev, times

def save_results(pipeline_stats, baseline_stats):
    RESULTS_DIR.mkdir(exist_ok=True)

    df = pd.DataFrame({
        "run": range(1, RUNS + 1),
        "pipeline_time": pipeline_stats[2],
        "baseline_time": baseline_stats[2],
    })
    df.to_csv(RESULTS_DIR / "results.csv", index=False)

    summary = pd.DataFrame([{
        "pipeline_mean": pipeline_stats[0],
        "pipeline_std": pipeline_stats[1],
        "baseline_mean": baseline_stats[0],
        "baseline_std": baseline_stats[1],
        "speedup": baseline_stats[0] / pipeline_stats[0],
    }])
    summary.to_csv(RESULTS_DIR / "summary.csv", index=False)

def main():
    if not LOG_FILE.exists():
        print("Arquivo de log não encontrado. Gerando arquivo de teste...")
        with open(LOG_FILE, "w") as f:
            for i in range(10000):
                level = "ERROR" if i % 5 == 0 else "INFO"
                f.write(f"{level}: Mensagem número {i}\n")

    pipeline_stats = benchmark_pipeline()
    baseline_stats = benchmark_baseline()

    save_results(pipeline_stats, baseline_stats)

    print("\nResultados:")
    print(f"Pipeline: {pipeline_stats[0]:.4f}s ± {pipeline_stats[1]:.4f}")
    print(f"Baseline (grep+wc): {baseline_stats[0]:.4f}s ± {baseline_stats[1]:.4f}")
    print(f"Speedup: {baseline_stats[0] / pipeline_stats[0]:.2f}x")

if __name__ == "__main__":
    main()
