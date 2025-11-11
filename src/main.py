"""
main.py — Coordena o pipeline de processamento de logs.
Fluxo: reader -> filter -> aggregator
Usa subprocessos conectados via pipes para simular paralelismo.
"""

import subprocess
import sys
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print(f"Uso: {sys.argv[0]} <arquivo_log>")
        sys.exit(1)

    log_file = sys.argv[1]
    log_path = Path(log_file)
    if not log_path.exists():
        print(f"[ERRO] Arquivo '{log_file}' não existe.")
        sys.exit(1)

    # Caminho dos scripts
    src_dir = Path(__file__).parent
    reader_path = src_dir / "reader.py"
    filter_path = src_dir / "filter.py"
    aggregator_path = src_dir / "aggregator.py"

    try:
        print("[INFO] Iniciando pipeline...")
        # Cria subprocessos conectados por pipes
        p1 = subprocess.Popen(
            [sys.executable, str(reader_path), log_file],
            stdout=subprocess.PIPE
        )
        p2 = subprocess.Popen(
            [sys.executable, str(filter_path)],
            stdin=p1.stdout, stdout=subprocess.PIPE
        )
        p3 = subprocess.Popen(
            [sys.executable, str(aggregator_path)],
            stdin=p2.stdout
        )

        # Fecha pipes no processo pai
        p1.stdout.close()
        p2.stdout.close()

        # Espera todos os subprocessos terminarem
        p3.wait()
        p2.wait()
        p1.wait()

        print("[INFO] Pipeline finalizado com sucesso.")

    except Exception as e:
        print(f"[ERRO] Falha na execução do pipeline: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
