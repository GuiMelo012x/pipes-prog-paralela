#ifndef PIPELINE_H
#define PIPELINE_H

#include "Common.h"
#include "DataChunk.h"
#include <functional>
#include <vector>
#include <string>
#include <sys/types.h>

namespace Pipeline {

// Função de processamento de cada estágio
using StageFunction = std::function<DataChunk(const DataChunk&)>;

/**
 * Representa um estágio do pipeline
 */
class Stage {
private:
    std::string name_;
    StageFunction process_fn_;
    int input_fd_;
    int output_fd_;
    pid_t pid_;
    
public:
    Stage(const std::string& name, StageFunction fn);
    
    const std::string& name() const { return name_; }
    void set_input_fd(int fd) { input_fd_ = fd; }
    void set_output_fd(int fd) { output_fd_ = fd; }
    void set_pid(pid_t pid) { pid_ = pid; }
    pid_t pid() const { return pid_; }
    
    // Executa o estágio (no processo filho)
    void execute();
    
private:
    DataChunk read_from_pipe();
    void write_to_pipe(const DataChunk& chunk);
};

/**
 * Orquestrador do pipeline
 */
class PipelineExecutor {
private:
    std::vector<Stage*> stages_;
    std::vector<int*> pipes_;  // Array de file descriptors
    size_t buffer_size_;
    bool verbose_;
    
public:
    explicit PipelineExecutor(size_t buffer_size = DEFAULT_BUFFER_SIZE);
    ~PipelineExecutor();
    
    // Adiciona um estágio
    void add_stage(const std::string& name, StageFunction fn);
    
    // Executa o pipeline
    void run(const std::string& input_file, const std::string& output_file);
    
    void set_verbose(bool v) { verbose_ = v; }
    
private:
    void create_pipes();
    void cleanup_pipes();
    void fork_stages();
    void wait_for_completion();
    void log(const std::string& message);
};

} // namespace Pipeline

#endif // PIPELINE_H