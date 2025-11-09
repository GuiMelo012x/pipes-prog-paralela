# pipes-prog-paralela

## Processamento de Logs de servidores web
Cenário:
Você tem arquivos de log Apache/Nginx enormes (100MB - 10GB) e precisa:

Ler o arquivo de log
Filtrar apenas requisições HTTP 4xx e 5xx (erros)
Extrair IP, timestamp, código de status, URL
Agregar contagem de erros por IP
Escrever relatório CSV
Por que isso é bom para Pipes?

-Processamento sequencial (lê linha por linha)
-Cada stage tem função clara
-I/O intensivo (ler arquivo grande + escrever saída)
-Permite paralelismo (um stage lê, outro processa, outro escreve)