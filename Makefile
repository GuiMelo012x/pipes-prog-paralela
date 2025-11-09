# Nome dos executáveis
TARGETS = reader filter aggregator pipeline

# Compilador e flags
CC = gcc
CFLAGS = -O2 -std=gnu11 -Wall -Wextra

# Regra padrão
all: $(TARGETS)

# Compilação individual de cada módulo
reader: reader.c
	$(CC) $(CFLAGS) -o reader reader.c

filter: filter.c
	$(CC) $(CFLAGS) -o filter filter.c

aggregator: aggregator.c
	$(CC) $(CFLAGS) -o aggregator aggregator.c

pipeline: main.c
	$(CC) $(CFLAGS) -o pipeline main.c

# Limpar tudo
clean:
	rm -f $(TARGETS)
