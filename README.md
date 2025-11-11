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
│   ├── run_bench.sh
│   └── access_sample.log
└── results.csv
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
- SIGPIPE ignorado para tratamento graceful## Benchmark/Compara��o (Item 16)
Para comparar baseline sequencial, pipeline por processos e pipeline com threads utilize o CLI em benchmark/compare.py.

`ash
# Executa 5 repeti��es por concorrente e mostra a tabela com tempos e speedup
python benchmark/compare.py benchmark/access_sample.log --runs 5

# Inclui o top-3 de cada execu��o para inspe��o r�pida
python benchmark/compare.py benchmark/access_sample.log --runs 5 --show-top
`

A sa�da segue o formato:

`
=== COMPARA��O (R=5) ===
Arquivo: benchmark/access_sample.log
+-----------------+-----------+-----------+-----------+---------+
| Implementa��o   |   M�dia s |   Desv s  |   IC95 s  | Speedup |
+-----------------+-----------+-----------+-----------+---------+
| Baseline        |    12.345 |     0.210 |     0.184 |   1.00x |
| Pipes (process) |     2.410 |     0.090 |     0.081 |   5.12x |
| Threads         |     2.770 |     0.070 |     0.063 |   4.45x |
+-----------------+-----------+-----------+-----------+---------+
`

Al�m da tabela impressa, os dados consolidados s�o adicionados em results/compare_summary.csv.
