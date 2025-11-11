"""
reader.py — Lê um arquivo de log e envia o conteúdo linha a linha via pipe (stdout).
"""

import sys

def main():
    if len(sys.argv) != 2:
        print(f"Uso: {sys.argv[0]} <arquivo_log>")
        sys.exit(1)

    log_path = sys.argv[1]
    try:
        with open(log_path, "r") as f:
            for line in f:
                sys.stdout.write(line)
                sys.stdout.flush()  # garante envio imediato pelo pipe
    except FileNotFoundError:
        print(f"[ERRO] Arquivo '{log_path}' não encontrado.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
