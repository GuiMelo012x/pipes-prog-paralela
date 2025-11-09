# Pipeline com Pipes (Unix)

## Visão Geral do Projeto
Este projeto tem como foco a implementação de um sistema de processamento em pipeline utilizando pipes anônimos e processos em C.
O objetivo principal é demonstrar a comunicação eficiente entre processos (Inter-Process Communication - IPC) e comparar o seu desempenho (pipeline em C) com uma baseline equivalente implementada usando ferramentas padrão do Unix (como grep e wc).

## Arquitetura e Fluxo do Pipeline
O sistema em C utiliza três processos conectados sequencialmente por pipes, representando um pipeline de processamento de logs.

### >Reader<
Lê o arquivo de log linha a linha e envia o conteúdo para o primeiro pipe.*

### >Filter<
Recebe do primeiro pipe e filtra apenas as linhas contendo a string 'ERROR'.*

### >Aggregator<	
Lê do segundo pipe e conta o total de mensagens filtradas, exibindo o resultado final.*

## Controle de Processos
- O arquivo main.c é responsável por orquestrar todo o sistema
- ele cria os pipes, realiza o fork() dos processos filhos (Reader, Filter, Aggregator) e gerencia os descritores de arquivo abertos para garantir a comunicação correta.

## Estrutura do Repositório
```
.
├── src/
│   ├── main.c
│   ├── reader.c
│   ├── filter.c
│   ├── aggregator.c
│   └── Makefile
├── benchmark/
│   ├── run_bench.sh
│   └── access_sample.log
├── results/
│   ├── results.csv
│   └── summary.csv
└── README.md
```
 ## Execução
 1. Compilar o Projeto

Navegue até o diretório src e execute o Makefile:
```
cd src
make
```
2. Executar o Pipeline Manualmente

Após a compilação, o executável pipeline estará disponível:
*./../benchmark/access_sample.log*

3. Executar Benchmark Automatizado

O script run_bench.sh executa o pipeline e a baseline múltiplas vezes para coletar métricas de desempenho.
```
cd benchmark
./run_bench.sh
```
O script gera o arquivo de log de teste, compila, executa 10 repetições de benchmark, compara com a baseline e gera relatórios na pasta results/.

## Baseline de Comparação
A solução em C é comparada com a seguinte implementação equivalente em ferramentas Unix:
```
grep 'ERROR' data.log | grep -v 'DEBUG' | wc -l
```
Esta implementação Unix é usada como referência de desempenho para medir o ganho de velocidade (Speedup) obtido pela solução em C com pipes.

## Metricas de Desempenho
As métricas são calculadas automaticamente pelo script de benchmark e salvas em results/summary.csv:
```
Métrica|Descrição
mean   |Tempo médio de execução em segundos (s).
std    |Desvio padrão do tempo de execução.
ic95   |Intervalo de confiança de 95% do tempo médio.
speedup|Razão entre o tempo médio da baseline e o tempo médio do pipeline em C.
```
- *Exemplo de saída*
```
=== MÉTRICAS DE DESEMPENHO ===
                  mean      std       ic95
tipo
baseline        1.2034    0.0501    0.0310
pipeline        0.6257    0.0429    0.0266

Speedup: 1.92x
```

## Reprodutibilidade
O projeto foi estruturado para ser totalmente reproduzível:

1. Compilação automatizada via Makefile.

2. Execução automatizada do benchmark com run_bench.sh.

3. Geração automática de dados de teste (data.log pelo script).

4. Cálculo de métricas e exportação de resultados (results.csv, summary.csv).

5. A Baseline é um comando de terminal reproduzível.