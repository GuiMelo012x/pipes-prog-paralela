#include <stdio.h>
#include <string.h>

int main() {
    char line[256];

    while (fgets(line, sizeof(line), stdin)) {
        // Exemplo simples: só repassa linhas que contenham a palavra "INFO"
        if (strstr(line, "INFO")) {
            printf("%s", line);
        }
    }

    return 0;
}
// This code filters lines from standard input, only printing those that contain the word "INFO".
