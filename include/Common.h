#ifndef COMMON_H
#define COMMON_H

#include <string>
#include <stdexcept>
#include <cstddef>

namespace Pipeline {

// Constantes
constexpr size_t DEFAULT_BUFFER_SIZE = 4096;

// Exceções
class PipelineException : public std::runtime_error {
public:
    explicit PipelineException(const std::string& msg) 
        : std::runtime_error(msg) {}
};

class PipeError : public PipelineException {
public:
    explicit PipeError(const std::string& msg) 
        : PipelineException("Pipe error: " + msg) {}
};

class IOError : public PipelineException {
public:
    explicit IOError(const std::string& msg) 
        : PipelineException("IO error: " + msg) {}
};

// Funções utilitárias
namespace Utils {
    std::string get_timestamp();
    void safe_close(int fd);
    ssize_t safe_read(int fd, void* buf, size_t count);
    ssize_t safe_write(int fd, const void* buf, size_t count);
}

} // namespace Pipeline

#endif // COMMON_H