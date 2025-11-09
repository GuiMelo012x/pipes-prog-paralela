# filter.py
# Filtra linhas que contenham 'ERROR' e envia para stdout
import sys

def main():
    for line in sys.stdin:
        if "ERROR" in line:
            sys.stdout.write(line)
            sys.stdout.flush()

if __name__ == "__main__":
    main()
