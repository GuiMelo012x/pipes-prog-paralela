CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -Werror -O2 -g
LDFLAGS = -pthread

SRC_DIR = src
INCLUDE_DIR = include
BUILD_DIR = build
BIN_DIR = bin

SOURCES = $(SRC_DIR)/Common.cpp \
          $(SRC_DIR)/Pipeline.cpp \
          $(SRC_DIR)/main.cpp

OBJECTS = $(SOURCES:$(SRC_DIR)/%.cpp=$(BUILD_DIR)/%.o)
TARGET = $(BIN_DIR)/pipeline

# Cores
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m

.PHONY: all
all: directories $(TARGET)
	@echo "$(GREEN)✓ Build completo!$(NC)"

.PHONY: directories
directories:
	@mkdir -p $(BUILD_DIR) $(BIN_DIR) data

$(TARGET): $(OBJECTS)
	@echo "$(YELLOW)Linkando...$(NC)"
	$(CXX) $(CXXFLAGS) $(OBJECTS) -o $(TARGET) $(LDFLAGS)
	@echo "$(GREEN)✓ Executável criado: $(TARGET)$(NC)"

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp
	@echo "$(YELLOW)Compilando $<...$(NC)"
	@$(CXX) $(CXXFLAGS) -I$(INCLUDE_DIR) -c $< -o $@

.PHONY: clean
clean:
	@echo "$(YELLOW)Limpando...$(NC)"
	rm -rf $(BUILD_DIR) $(BIN_DIR)
	@echo "$(GREEN)✓ Limpo$(NC)"

.PHONY: test
test: all
	@echo "$(YELLOW)Criando arquivo de teste...$(NC)"
	@echo "Hello World!   This is    a    test." > data/input.txt
	@echo "Multiple    spaces     here." >> data/input.txt
	@echo "$(GREEN)Executando pipeline...$(NC)"
	@./$(TARGET) -i data/input.txt -o data/output.txt -v
	@echo ""
	@echo "$(GREEN)Resultado:$(NC)"
	@cat data/output.txt
	@echo ""

.PHONY: valgrind
valgrind: all
	@echo "$(YELLOW)Executando valgrind...$(NC)"
	@echo "Test data" > data/input.txt
	valgrind --leak-check=full \
	         --show-leak-kinds=all \
	         --track-origins=yes \
	         ./$(TARGET) -i data/input.txt -o data/output.txt

.PHONY: help
help:
	@echo "$(GREEN)Pipeline Project$(NC)"
	@echo ""
	@echo "Targets:"
	@echo "  all      - Compila o projeto (padrão)"
	@echo "  clean    - Remove arquivos compilados"
	@echo "  test     - Executa teste básico"
	@echo "  valgrind - Verifica memory leaks"
	@echo "  help     - Mostra esta ajuda"