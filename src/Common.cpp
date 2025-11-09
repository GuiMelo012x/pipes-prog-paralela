#include "Common.h"
#include <unistd.h>
#include <cstring>
#include <cerrno>
#include <iostream>
#include <chrono>
#include <iomanip>
#include <sstream>

namespace Pipeline {
namespace Utils {

std::string get_timestamp() {
    auto now = std::chrono::system_clock::now();
    auto time = std::chrono::system_clock::to_time_t(now);
    std::stringstream ss;
    ss << std::put_time(std::localtime(&time), "%Y-%m-%d %H:%M:%S");
    return ss.str();
}

void safe_close(int fd) {
    if (fd >= 0) {
        if (close(fd) == -1) {
            std::cerr << "[WARN] Failed to close fd " << fd 
                      << ": " << strerror(errno) << std::endl;
        }
    }
}

ssize_t safe_read(int fd, void* buf, size_t count) {
    ssize_t bytes_read;
    while (true) {
        bytes_read = read(fd, buf, count);
        if (bytes_read == -1) {
            if (errno == EINTR) {
                continue;  // Interrompido por sinal, tenta novamente
            }
            throw IOError("read() failed: " + std::string(strerror(errno)));
        }
        break;
    }
    return bytes_read;
}

ssize_t safe_write(int fd, const void* buf, size_t count) {
    ssize_t bytes_written;
    size_t total = 0;
    
    while (total < count) {
        bytes_written = write(fd, static_cast<const char*>(buf) + total, 
                              count - total);
        if (bytes_written == -1) {
            if (errno == EINTR) {
                continue;
            }
            if (errno == EPIPE) {
                throw IOError("Broken pipe: reader closed");
            }
            throw IOError("write() failed: " + std::string(strerror(errno)));
        }
        total += bytes_written;
    }
    return total;
}

} // namespace Utils
} // namespace Pipeline