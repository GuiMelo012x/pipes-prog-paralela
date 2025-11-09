#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    int pipe1[2], pipe2[2];

    // Cria os dois pipes: reader->filter e filter->aggregator
    if (pipe(pipe1) == -1 || pipe(pipe2) == -1) {
        perror("pipe");
        exit(1);
    }

    pid_t pid1, pid2, pid3;

    // --- Processo 1: READER ---
    pid1 = fork();
    if (pid1 == 0) {
        dup2(pipe1[1], STDOUT_FILENO); // envia saída para o pipe1
        close(pipe1[0]);
        close(pipe2[0]); close(pipe2[1]);
        execlp("./reader", "reader", NULL);
        perror("execlp reader");
        exit(1);
    }

    // --- Processo 2: FILTER ---
    pid2 = fork();
    if (pid2 == 0) {
        dup2(pipe1[0], STDIN_FILENO);  // lê do pipe1
        dup2(pipe2[1], STDOUT_FILENO); // envia para o pipe2
        close(pipe1[1]);
        close(pipe2[0]);
        execlp("./filter", "filter", NULL);
        perror("execlp filter");
        exit(1);
    }

    // --- Processo 3: AGGREGATOR ---
    pid3 = fork();
    if (pid3 == 0) {
        dup2(pipe2[0], STDIN_FILENO); // lê do pipe2
        close(pipe1[0]); close(pipe1[1]);
        close(pipe2[1]);
        execlp("./aggregator", "aggregator", NULL);
        perror("execlp aggregator");
        exit(1);
    }

    // --- Processo Pai ---
    close(pipe1[0]); close(pipe1[1]);
    close(pipe2[0]); close(pipe2[1]);

    // Espera os filhos terminarem
    waitpid(pid1, NULL, 0);
    waitpid(pid2, NULL, 0);
    waitpid(pid3, NULL, 0);

    printf("Pipeline finalizado com sucesso.\n");
    return 0;
}
// This code sets up a pipeline with three processes: reader, filter, and aggregator. Each process communicates via pipes.
