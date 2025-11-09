#ifndef DATACHUNK_H
#define DATACHUNK_H

#include <vector>
#include <cstddef>

namespace Pipeline {

/**
 * Estrutura de dados que trafega pelo pipeline
 */
class DataChunk {
public:
    std::vector<char> data;
    size_t size;
    bool is_last;  // Indica fim do stream
    
    DataChunk() : size(0), is_last(false) {}
    
    explicit DataChunk(size_t capacity) 
        : data(capacity), size(0), is_last(false) {}
    
    DataChunk(const char* src, size_t len) 
        : data(src, src + len), size(len), is_last(false) {}
};

} // namespace Pipeline

#endif // DATACHUNK_H