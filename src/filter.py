"""
filter.py — Filtra as linhas que contêm 'ERROR' e repassa via pipe (stdout).
"""

import sys

def main():
    try:
        for line in sys.stdin:
            if "ERROR" in line:
                sys.stdout.write(line)
                sys.stdout.flush()
    except Exception as e:
        print(f"[ERRO] Falha no filtro: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
