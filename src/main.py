# main.py
# Orquestra o pipeline usando subprocess e pipes
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
        print(f"Arquivo {log_file} não existe")
        sys.exit(1)

    # Cria subprocesses
    p1 = subprocess.Popen([sys.executable, "reader.py", log_file], stdout=subprocess.PIPE)
    p2 = subprocess.Popen([sys.executable, "filter.py"], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen([sys.executable, "aggregator.py"], stdin=p2.stdout)

    # Fecha pipes no processo pai
    p1.stdout.close()
    p2.stdout.close()

    # Espera todos os subprocesses terminarem
    p3.wait()
    p2.wait()
    p1.wait()

    print("Pipeline finalizado com sucesso.")

if __name__ == "__main__":
    main()
