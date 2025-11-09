#include <stdio.h>
#include <string.h>

int main() {
    int count = 0;
    char line[256];

    while (fgets(line, sizeof(line), stdin)) {
        count++;
    }

    printf("Total de linhas INFO: %d\n", count);
    return 0;
}
// This code counts the number of lines received from standard input and prints the total count.
