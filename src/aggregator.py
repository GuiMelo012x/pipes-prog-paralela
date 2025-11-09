# aggregator.py
# Conta quantas vezes cada erro apareceu e imprime top 10
import sys
from collections import Counter

def main():
    counter = Counter()
    for line in sys.stdin:
        line = line.strip()
        if line:
            counter[line] += 1

    top10 = counter.most_common(10)
    for msg, count in top10:
        print(f"{count} {msg}")

if __name__ == "__main__":
    main()
