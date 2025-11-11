"""Sequential baseline that scans a log file and aggregates ERROR messages."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Dict, Iterator


def _extract_error_message(line: str) -> str | None:
    """Return the normalized error message or None if the line is not an error."""
    if "ERROR" not in line:
        return None
    start = line.find("ERROR")
    fragment = line[start:].strip()
    return fragment or None


def _iter_errors(filepath: Path) -> Iterator[str]:
    """Yield processed error messages from the log file."""
    with filepath.open("r", encoding="utf-8", errors="ignore") as handle:
        for raw_line in handle:
            message = _extract_error_message(raw_line)
            if message:
                yield message


def run(filepath: str) -> Dict[str, int]:
    """Process the log file sequentially and return counts per error message."""
    path = Path(filepath)
    counter = Counter(_iter_errors(path))
    return dict(counter)


def _format_top(counter: Dict[str, int], limit: int = 10) -> str:
    """Return a string with the top N entries sorted by frequency."""
    if not counter:
        return "Nenhum erro encontrado."
    top_entries = Counter(counter).most_common(limit)
    lines = [f"{count} {message}" for message, count in top_entries]
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Baseline sequencial para contagem de erros.")
    parser.add_argument("logfile", help="Caminho para o arquivo de log a ser processado.")
    parser.add_argument("--top", type=int, default=10, help="Quantidade de mensagens a exibir (default=10).")
    args = parser.parse_args()

    counts = run(args.logfile)
    print(_format_top(counts, limit=args.top))


if __name__ == "__main__":
    main()
