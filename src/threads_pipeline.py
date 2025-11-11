"""Pipeline que replica reader -> filter -> aggregator usando threads."""
from __future__ import annotations

import threading
from collections import Counter
from pathlib import Path
from queue import Queue
from typing import Dict, List

QUEUE_SIZE = 8192
SENTINEL = None


def _extract_error_message(line: str) -> str | None:
    if "ERROR" not in line:
        return None
    start = line.find("ERROR")
    fragment = line[start:].strip()
    return fragment or None


def run(filepath: str) -> Dict[str, int]:
    """Executa o pipeline com threads e retorna o contador final."""
    path = Path(filepath)
    q_reader_filter: Queue = Queue(maxsize=QUEUE_SIZE)
    q_filter_agg: Queue = Queue(maxsize=QUEUE_SIZE)
    counts = Counter()

    def reader() -> None:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for raw_line in handle:
                q_reader_filter.put(raw_line)
        q_reader_filter.put(SENTINEL)

    def filter_stage() -> None:
        while True:
            line = q_reader_filter.get()
            if line is SENTINEL:
                q_filter_agg.put(SENTINEL)
                break
            message = _extract_error_message(line)
            if message:
                q_filter_agg.put(message)

    def aggregator() -> None:
        while True:
            item = q_filter_agg.get()
            if item is SENTINEL:
                break
            counts[item] += 1

    threads: List[threading.Thread] = [
        threading.Thread(target=reader, name="reader-thread"),
        threading.Thread(target=filter_stage, name="filter-thread"),
        threading.Thread(target=aggregator, name="aggregator-thread"),
    ]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    return dict(counts)


def _format_top(counter: Dict[str, int], limit: int = 10) -> List[str]:
    top = Counter(counter).most_common(limit)
    return [f"{count} {message}" for message, count in top]


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Pipeline de logs com threads.")
    parser.add_argument("logfile", help="Caminho para o arquivo de log.")
    parser.add_argument("--top", type=int, default=10, help="Número de mensagens a exibir (default=10).")
    args = parser.parse_args()

    counts = run(args.logfile)
    lines = _format_top(counts, args.top)
    print("\n".join(lines) if lines else "Nenhum erro encontrado.")


if __name__ == "__main__":
    main()
