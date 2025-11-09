#include <stdio.h>
#include <stdlib.h>

int main() {
    char line[256];

    while (fgets(line, sizeof(line), stdin)) {
        // Aqui poderíamos simular uma leitura de log real
        printf("%s", line);
    }

    return 0;
}
// This code reads lines from standard input and prints them to standard output.
// It simulates a log reader that could be part of a pipeline processing system.
