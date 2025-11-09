# reader.py
# Lê linhas de um arquivo de log e envia para stdout (pipe)
import sys

def main():
    if len(sys.argv) != 2:
        print(f"Uso: {sys.argv[0]} <arquivo_log>")
        sys.exit(1)

    log_path = sys.argv[1]
    with open(log_path, "r") as f:
        for line in f:
            sys.stdout.write(line)
            sys.stdout.flush()  # garante envio imediato pelo pipe

if __name__ == "__main__":
    main()
