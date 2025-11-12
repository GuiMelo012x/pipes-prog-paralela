# Pipeline com Pipes (Unix)

## Visão Geral do Projeto
Este projeto implementa um sistema de processamento de logs em pipeline, utilizando subprocessos e pipes em Python.
O objetivo é demonstrar comunicação entre processos (IPC), paralelismo simples e coleta de métricas de desempenho comparando o pipeline com uma baseline equivalente (ferramentas Unix ou implementação trivial).

## Arquitetura e Fluxo do Pipeline
O sistema consiste em três módulos conectados em sequência

### >Reader<
Lê o arquivo de log linha a linha e envia o conteúdo para o primeiro processo.

### >Filter<
Recebe do primeiro pipe e filtra apenas as linhas contendo a string 'ERROR'.*

### >Aggregator<	
	Conta a ocorrência das mensagens filtradas e exibe as top 10 mais frequentes.

## Fluxo de execução
- access_sample.log --> reader.py --> filter.py --> aggregator.py --> saída

## Estrutura do Repositório
```
.
├── src/
│   ├── main.py
│   ├── reader.py
│   ├── filter.py
│   └── aggregator.py
├── benchmark/
│   ├── benchmark.py
│   ├── run_bench.sh
│   └── access_sample.log
├── results/
│   ├── results.csv
│   └── summary.csv
└── README.md
```
 ## Execução
 1. Preparar o ambiente

Certifique-se de ter Python 3 e bc instalado (para cálculo de tempo):
```
sudo apt install bc python3-pip -y
pip install pandas numpy
```
2. Tornar o benchmark executável
```
chmod +x benchmark/run_bench.sh
```

3. Executar Benchmark Automatizado

- O script irá:
```
Gerar access_sample.log (se não existir)

Executar o pipeline 5 vezes

Salvar os tempos em results/results.csv

Exibir métricas (mean, std, IC95) 
```
```
cd benchmark
./run_bench.sh

```
O script gera o arquivo de log de teste, compila, executa 10 repetições de benchmark, compara com a baseline e gera relatórios na pasta results/.

## Benchmark e Métricas
O script de benchmark mede:

- mean: tempo médio de execução (s)
- std: desvio padrão dos tempos
- IC95: intervalo de confiança 95%

Esses valores permitem avaliar a consistência e performance do pipeline.

## Justificativa da Tecnologia e Funcionamento

### Por que Python e não C?
Facilidade de desenvolvimento: Python permite implementar pipelines e subprocessos com menos linhas de código e menos complexidade de gerenciamento de memória.

- Portabilidade: O mesmo código funciona em diferentes sistemas sem precisar recompilar.
- Bibliotecas robustas: subprocess, os e pathlib facilitam a manipulação de arquivos, pipes e processos.
- Benchmark confiável: Apesar de ser interpretado, Python consegue medir tempo e comparar com baselines de forma precisa para fins acadêmicos.

Observação: O uso de Python não prejudica a avaliação, já que o objetivo principal é demonstrar IPC e paralelismo via pipeline, independentemente da linguagem.

### Como funciona o pipeline em Python?
- Subprocessos: Cada etapa (reader, filter, aggregator) é um script Python separado, executado via subprocess.Popen.
- Pipes anônimos: A saída de um processo (stdout) é conectada à entrada do próximo (stdin) usando pipes.
- Encadeamento: Isso cria um fluxo contínuo de dados, similar ao reader | grep | wc do Unix, mas controlado pelo main.py.
- Sincronização: O processo pai (main.py) espera cada subprocesso terminar (wait()), garantindo que a execução esteja completa antes de exibir resultados.

```
access_sample.log
       │
       ▼
   reader.py ──┐
               │ stdout -> stdin
            filter.py ──┐
                          │ stdout -> stdin
                     aggregator.py
                          │
                          ▼
                      Saída final
```

## Perguntas da Banca

### P1: Pipeline bound por CPU, I/O ou sincronização?
**Resposta**: No caso atual, é **I/O bound** pois os estágios fazem processamento leve (conversão de case, remoção de espaços). Com processamento mais pesado, seria CPU bound.

### P2: Diferença pipes anônimos vs nomeados?
**Resposta**: Este projeto usa **pipes anônimos** (criados com `pipe()`), que são mais eficientes para processos relacionados (fork). Named pipes (FIFOs) seriam necessários para processos independentes.

### P3: Prevenção de deadlocks?
**Resposta**: 
- Cada processo filho fecha FDs que não usa
- Sinalização explícita com flag `is_last`
- Leitura → Processamento → Escrita em ordem determinística
- SIGPIPE ignorado para tratamento graceful

### P1 geral: Qual o baseline e quais ganhos absolutos e relativos obtidos? Descreva a metodologia do teste, tamanho de amostra e variância.
- Baseline: grep "ERROR" access_sample.log | wc -l, utilizando pipes nativos do sistema operacional (implementação em C).
Metodologia: foram realizadas 5 repetições independentes de cada execução, medindo o tempo total com time.perf_counter().
Métricas analisadas: média, desvio-padrão, intervalo de confiança de 95% e speedup.
- Resultados:

Pipeline (Python): 0.0415s ± 0.0036

Baseline (Shell): 0.0034s ± 0.0005

Speedup: 0.08x (o pipeline é ~12x mais lento).

- Interpretação: o baseline é significativamente mais rápido, pois usa processos nativos otimizados em C. O pipeline em Python reproduz o mesmo comportamento de fluxo, mas com maior overhead interpretado.

### P4 geral: Onde está o gargalo dominante hoje? Qual mudança única traria o maior ganho marginal e por quê?
- Gargalo dominante: a principal limitação de desempenho está na comunicação entre processos Python via pipes (os.pipe() / multiprocessing), que exige serialização e cópia de dados em memória. Esse overhead é alto em comparação com os pipes nativos do SO (implementados em C).

- Maior ganho marginal: reescrever o pipeline usando módulos nativos de C (ex: Cython) ou integração direta com comandos shell via subprocess reduziria drasticamente o overhead. Outra alternativa seria usar threads em vez de processos, quando não houver limitação de GIL, para eliminar custos de IPC.
