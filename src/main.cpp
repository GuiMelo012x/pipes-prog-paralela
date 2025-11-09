#include "Pipeline.h"
#include <iostream>
#include <cctype>

using namespace Pipeline;

// ==================== Funções de Processamento ====================

// Stage 1: Converte para maiúsculas
DataChunk to_uppercase(const DataChunk& input) {
    DataChunk output(input.size);
    output.size = input.size;
    
    for (size_t i = 0; i < input.size; ++i) {
        output.data[i] = std::toupper(static_cast<unsigned char>(input.data[i]));
    }
    
    return output;
}

// Stage 2: Remove espaços extras
DataChunk remove_spaces(const DataChunk& input) {
    DataChunk output(input.size);
    
    bool last_was_space = false;
    size_t write_pos = 0;
    
    for (size_t i = 0; i < input.size; ++i) {
        char c = input.data[i];
        
        if (std::isspace(static_cast<unsigned char>(c))) {
            if (!last_was_space && write_pos > 0) {
                output.data[write_pos++] = ' ';
                last_was_space = true;
            }
        } else {
            output.data[write_pos++] = c;
            last_was_space = false;
        }
    }
    
    output.size = write_pos;
    return output;
}

// Stage 3: Adiciona contador
DataChunk add_count(const DataChunk& input) {
    std::string prefix = "[" + std::to_string(input.size) + " chars] ";
    
    DataChunk output(prefix.size() + input.size);
    
    std::memcpy(output.data.data(), prefix.c_str(), prefix.size());
    std::memcpy(output.data.data() + prefix.size(), 
                input.data.data(), input.size);
    
    output.size = prefix.size() + input.size;
    return output;
}

// ==================== Main ====================

int main(int argc, char* argv[]) {
    try {
        std::cout << "=== Pipeline Processor ===" << std::endl;
        std::cout << std::endl;
        
        // Parâmetros padrão
        std::string input_file = "data/input.txt";
        std::string output_file = "data/output.txt";
        bool verbose = false;
        
        // Parse argumentos
        for (int i = 1; i < argc; ++i) {
            std::string arg = argv[i];
            
            if (arg == "-i" && i + 1 < argc) {
                input_file = argv[++i];
            } else if (arg == "-o" && i + 1 < argc) {
                output_file = argv[++i];
            } else if (arg == "-v" || arg == "--verbose") {
                verbose = true;
            } else if (arg == "-h" || arg == "--help") {
                std::cout << "Usage: " << argv[0] << " [options]" << std::endl;
                std::cout << "Options:" << std::endl;
                std::cout << "  -i <file>    Input file (default: data/input.txt)" << std::endl;
                std::cout << "  -o <file>    Output file (default: data/output.txt)" << std::endl;
                std::cout << "  -v           Verbose mode" << std::endl;
                std::cout << "  -h           Show help" << std::endl;
                return 0;
            }
        }
        
        std::cout << "Configuration:" << std::endl;
        std::cout << "  Input:  " << input_file << std::endl;
        std::cout << "  Output: " << output_file << std::endl;
        std::cout << "  Verbose: " << (verbose ? "Yes" : "No") << std::endl;
        std::cout << std::endl;
        
        // Cria o pipeline
        PipelineExecutor pipeline;
        pipeline.set_verbose(verbose);
        
        // Adiciona os estágios
        pipeline.add_stage("ToUppercase", to_uppercase);
        pipeline.add_stage("RemoveSpaces", remove_spaces);
        pipeline.add_stage("AddCount", add_count);
        
        std::cout << "Pipeline stages:" << std::endl;
        std::cout << "  1. ToUppercase  - Convert to uppercase" << std::endl;
        std::cout << "  2. RemoveSpaces - Remove extra spaces" << std::endl;
        std::cout << "  3. AddCount     - Add character count" << std::endl;
        std::cout << std::endl;
        
        // Executa
        auto start = std::chrono::high_resolution_clock::now();
        
        pipeline.run(input_file, output_file);
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
        
        std::cout << std::endl;
        std::cout << "=== SUCCESS ===" << std::endl;
        std::cout << "Duration: " << duration.count() << " ms" << std::endl;
        std::cout << "Output: " << output_file << std::endl;
        
        return 0;
        
    } catch (const PipelineException& e) {
        std::cerr << std::endl;
        std::cerr << "=== Pipeline Error ===" << std::endl;
        std::cerr << e.what() << std::endl;
        return 1;
        
    } catch (const std::exception& e) {
        std::cerr << std::endl;
        std::cerr << "=== Fatal Error ===" << std::endl;
        std::cerr << e.what() << std::endl;
        return 2;
    }
}