"""Benchmark runner that compares sequential, process-pipe, and threaded pipelines."""
from __future__ import annotations

import argparse
import csv
import math
import statistics
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import baseline_sequential
import threads_pipeline


TopList = List[Tuple[int, str]]


@dataclass
class Executor:
    label: str
    runner: Callable[[], object]
    top_extractor: Callable[[object], TopList] | None = None


def _calc_stats(samples: Sequence[float]) -> Tuple[float, float, float]:
    mean = statistics.mean(samples)
    if len(samples) == 1:
        return mean, 0.0, 0.0
    std = statistics.stdev(samples)
    ci95 = 1.96 * std / math.sqrt(len(samples))
    return mean, std, ci95


def _format_top(entries: TopList) -> str:
    return "\n".join(f"  {count} {message}" for count, message in entries) if entries else "  (sem erros)"


def _top_from_counter_dict(result: Dict[str, int], limit: int = 3) -> TopList:
    counter = Counter(result)
    return [(count, message) for message, count in counter.most_common(limit)]


def _top_from_pipeline_stdout(stdout: str, limit: int = 3) -> TopList:
    entries: TopList = []
    for raw in stdout.splitlines():
        stripped = raw.strip()
        if not stripped or not stripped[0].isdigit():
            continue
        parts = stripped.split(" ", 1)
        try:
            count = int(parts[0])
        except ValueError:
            continue
        message = parts[1] if len(parts) > 1 else ""
        entries.append((count, message))
        if len(entries) == limit:
            break
    return entries


def _measure_executor(executor: Executor, runs: int, show_top: bool) -> List[float]:
    timings: List[float] = []
    for idx in range(1, runs + 1):
        start = time.perf_counter()
        result = executor.runner()
        elapsed = time.perf_counter() - start
        timings.append(elapsed)
        if show_top and executor.top_extractor:
            tops = executor.top_extractor(result)
            print(f"[{executor.label}] Execução {idx} top-3:")
            if tops:
                for count, message in tops:
                    print(f"  {count} {message}")
            else:
                print("  (sem erros)")
    return timings


def _write_summary_csv(rows: List[Dict[str, object]], filepath: Path) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    write_header = not filepath.exists()
    with filepath.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        if write_header:
            writer.writerow(["impl", "mean_s", "sd_s", "ci95_s", "speedup", "runs", "filepath", "timestamp"])
        timestamp = datetime.utcnow().isoformat()
        for row in rows:
            writer.writerow(
                [
                    row["name"],
                    f"{row['mean']:.6f}",
                    f"{row['std']:.6f}",
                    f"{row['ci95']:.6f}",
                    f"{row['speedup']:.2f}",
                    row["runs"],
                    row["filepath"],
                    timestamp,
                ]
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compara diferentes pipelines de processamento de logs.")
    parser.add_argument("logfile", help="Arquivo de log a ser processado.")
    parser.add_argument("--runs", type=int, default=5, help="Número de execuções por implementação (default=5).")
    parser.add_argument("--show-top", action="store_true", help="Exibe o top-3 após cada execução para inspeção rápida.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runs = args.runs
    if runs < 1:
        print("O número de execuções (--runs) deve ser >= 1.")
        sys.exit(1)

    log_path = Path(args.logfile).resolve()
    if not log_path.exists():
        print(f"Arquivo {log_path} não encontrado.")
        sys.exit(1)

    baseline_executor = Executor(
        label="Baseline",
        runner=lambda: baseline_sequential.run(str(log_path)),
        top_extractor=lambda result: _top_from_counter_dict(result, limit=3),
    )

    process_executor = Executor(
        label="Pipes (process)",
        runner=lambda: subprocess.run(
            [sys.executable, str(SRC_DIR / "main.py"), str(log_path)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout,
        top_extractor=lambda stdout: _top_from_pipeline_stdout(stdout, limit=3),
    )

    threads_executor = Executor(
        label="Threads",
        runner=lambda: threads_pipeline.run(str(log_path)),
        top_extractor=lambda result: _top_from_counter_dict(result, limit=3),
    )

    executors = [baseline_executor, process_executor, threads_executor]

    measurements: List[Dict[str, object]] = []
    baseline_mean = None

    for executor in executors:
        timings = _measure_executor(executor, runs, args.show_top)
        mean, std, ci95 = _calc_stats(timings)
        measurements.append(
            {"name": executor.label, "mean": mean, "std": std, "ci95": ci95, "runs": runs, "filepath": str(log_path)}
        )
        if baseline_mean is None:
            baseline_mean = mean

    assert baseline_mean is not None
    for row in measurements:
        row["speedup"] = baseline_mean / row["mean"] if row["mean"] else float("inf")

    border = "+-----------------+-----------+-----------+-----------+---------+"
    header = "| Implementação   |   Média s |   Desv s  |   IC95 s  | Speedup |"

    print(f"=== COMPARAÇÃO (R={runs}) ===")
    print(f"Arquivo: {log_path}")
    print(border)
    print(header)
    print(border)
    for row in measurements:
        print(
            "| {name:<15} | {mean:>9.3f} | {std:>9.3f} | {ci95:>9.3f} | {speedup:>6.2f}x |".format(
                name=row["name"],
                mean=row["mean"],
                std=row["std"],
                ci95=row["ci95"],
                speedup=row["speedup"],
            )
        )
    print(border)

    summary_rows = [
        {
            "name": row["name"],
            "mean": row["mean"],
            "std": row["std"],
            "ci95": row["ci95"],
            "speedup": row["speedup"],
            "runs": row["runs"],
            "filepath": row["filepath"],
        }
        for row in measurements
    ]
    _write_summary_csv(summary_rows, REPO_ROOT / "results" / "compare_summary.csv")


if __name__ == "__main__":
    main()
