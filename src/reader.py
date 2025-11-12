import os

def read_log(log_path, max_size_mb=50):
    """
    Lê o arquivo de log e retorna suas linhas.
    Inclui verificações de segurança e tratamento de erro.
    """

    try:
        # Verifica se o arquivo existe
        if not os.path.exists(log_path):
            raise FileNotFoundError(f"Arquivo '{log_path}' não encontrado.")

        # Verifica tamanho máximo permitido (ex: 50MB)
        size_mb = os.path.getsize(log_path) / (1024 * 1024)
        if size_mb > max_size_mb:
            raise MemoryError(
                f"O arquivo '{log_path}' tem {size_mb:.1f}MB, excedendo o limite de {max_size_mb}MB."
            )

        # Abre com tratamento de encoding e ignora erros de caracteres
        with open(log_path, "r", encoding="utf-8", errors="ignore") as file:
            lines = file.readlines()

        # Caso o arquivo esteja vazio
        if not lines:
            raise ValueError(f"O arquivo '{log_path}' está vazio.")

        return lines

    except (FileNotFoundError, MemoryError, ValueError) as e:
        print(f"[ERRO] {e}")
        return []

    except Exception as e:
        print(f"[ERRO INESPERADO] Falha ao ler o arquivo: {e}")
        return []
