"""
aggregator.py — Conta e exibe as mensagens de erro mais frequentes.
Mostra o top 10 de mensagens de erro.
"""

import sys
from collections import Counter

def main():
    counter = Counter()

    try:
        for line in sys.stdin:
            line = line.strip()
            if line:
                counter[line] += 1

        if not counter:
            print("[INFO] Nenhum erro encontrado.")
            return

        print("[INFO] Top 10 erros encontrados:")
        for msg, count in counter.most_common(10):
            print(f"{count}x - {msg}")

    except Exception as e:
        print(f"[ERRO] Falha ao agregar resultados: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
