# Pipeline em C++ com Unix Pipes

Sistema de processamento paralelo usando pipes Unix para comunicação entre processos.

## Estrutura do Projeto

```
pipeline-project/
├── include/
│   ├── Common.h      # Tipos base e utilitários
│   ├── DataChunk.h   # Estrutura de dados
│   └── Pipeline.h    # Classes principais
├── src/
│   ├── Common.cpp    # Implementação utils
│   ├── Pipeline.cpp  # Implementação pipeline
│   └── main.cpp      # Exemplo de uso
├── data/
│   ├── input.txt     # Entrada
│   └── output.txt    # Saída (gerado)
├── Makefile
└── README.md
```

## Compilação

### Requisitos
- g++ com C++17
- make
- Sistema Unix/Linux

### Compilar
```bash
make
```

### Limpar
```bash
make clean
```

## Execução

### Teste rápido
```bash
make test
```

### Uso manual
```bash
# Criar arquivo de entrada
echo "Hello World!" > data/input.txt

# Executar
./bin/pipeline -i data/input.txt -o data/output.txt

# Com verbose
./bin/pipeline -i data/input.txt -o data/output.txt -v
```

### Opções
```
-i <file>    Arquivo de entrada (padrão: data/input.txt)
-o <file>    Arquivo de saída (padrão: data/output.txt)
-v           Modo verbose
-h           Ajuda
```

## Arquitetura

### Fluxo de Dados

```
[Input File] → [Pipe 0] → [Stage 1: ToUppercase] → [Pipe 1] 
             → [Stage 2: RemoveSpaces] → [Pipe 2]
             → [Stage 3: AddCount] → [Pipe 3] → [Output File]
```

### Componentes

1. **DataChunk**: Encapsula dados que trafegam pelo pipeline
2. **Stage**: Representa um estágio de processamento
3. **PipelineExecutor**: Orquestra o pipeline completo

### Protocolo de Comunicação

Cada chunk serializado contém:
```
[size: 8 bytes][is_last: 1 byte][data: size bytes]
```

## Implementação

### Características

**Tratamento de Erros**
- Hierarquia de exceções
- Safe read/write com retry em EINTR
- Tratamento de EPIPE e EOF
- Cleanup automático (RAII)

**Prevenção de Deadlocks**
- FDs não utilizados são fechados
- Sinalização explícita de fim (is_last)
- Ordem determinística de operações

**Gerenciamento de Recursos**
- Sem memory leaks (valgrind clean)
- Signal handling (SIGPIPE ignorado)
- Processos filhos sincronizados

## Testes

### Valgrind (Memory Leaks)
```bash
make valgrind
```

Deve mostrar: `All heap blocks were freed -- no leaks are possible`

### Exemplo de Saída

**Input:**
```
Hello World!   This is    a    test.
Multiple    spaces     here.
```

**Output:**
```
[36 chars] HELLO WORLD! THIS IS A TEST.
[26 chars] MULTIPLE SPACES HERE.
```

## Estágios de Exemplo

1. **ToUppercase**: Converte texto para maiúsculas
2. **RemoveSpaces**: Remove espaços duplicados
3. **AddCount**: Adiciona contagem de caracteres

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

## Código Importante

### Adicionar Novo Estágio

```cpp
// Defina a função de processamento
DataChunk meu_filtro(const DataChunk& input) {
    DataChunk output(input.size);
    // ... processamento ...
    return output;
}

// No main, adicione:
pipeline.add_stage("MeuFiltro", meu_filtro);
```

### Configurar Buffer Size

```cpp
PipelineExecutor pipeline(8192);  // 8KB buffer
```

## Próximos Passos

- [ ] Implementar named pipes (FIFOs)
- [ ] Adicionar métricas de throughput
- [ ] Criar benchmark comparativo
- [ ] Suporte a backpressure adaptativo

## Licença

Projeto acadêmico - Programação Paralela