// core_cpp/text_streamer.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <string>
#include <vector>
#include <deque>
#include <chrono>
#include <mutex>
#include <thread>
#include <functional>

class AdaptiveTextStreamer {
private:
    std::deque<std::string> token_buffer_;
    std::string accumulated_text_;
    std::mutex buffer_mutex_;
    size_t buffer_size_;
    int flush_interval_ms_;
    bool is_streaming_;
    std::thread flush_thread_;
    std::function<void(const std::string&)> update_callback_;

public:
    AdaptiveTextStreamer(size_t buffer_size = 20, int flush_interval_ms = 100) 
        : buffer_size_(buffer_size), flush_interval_ms_(flush_interval_ms), is_streaming_(false) {}

    ~AdaptiveTextStreamer() {
        stop_streaming();
    }

    void set_update_callback(std::function<void(const std::string&)> callback) {
        update_callback_ = callback;
    }

    void add_token(const std::string& token) {
        std::lock_guard<std::mutex> lock(buffer_mutex_);
        token_buffer_.push_back(token);
        accumulated_text_ += token;
        
        if (token_buffer_.size() >= buffer_size_) {
            flush_buffer_internal();
        }
    }

    void start_streaming() {
        if (is_streaming_) return;
        
        is_streaming_ = true;
        flush_thread_ = std::thread([this]() {
            while (is_streaming_) {
                std::this_thread::sleep_for(std::chrono::milliseconds(flush_interval_ms_));
                flush_buffer();
            }
        });
    }

    void stop_streaming() {
        if (!is_streaming_) return;
        
        is_streaming_ = false;
        if (flush_thread_.joinable()) {
            flush_thread_.join();
        }
        flush_buffer(); // Final flush
    }

    void flush_buffer() {
        std::lock_guard<std::mutex> lock(buffer_mutex_);
        flush_buffer_internal();
    }

    std::string get_full_text() const {
        std::lock_guard<std::mutex> lock(buffer_mutex_);
        return accumulated_text_;
    }

    void clear() {
        std::lock_guard<std::mutex> lock(buffer_mutex_);
        token_buffer_.clear();
        accumulated_text_.clear();
    }

    size_t get_buffer_size() const {
        std::lock_guard<std::mutex> lock(buffer_mutex_);
        return token_buffer_.size();
    }

    void set_buffer_size(size_t size) {
        buffer_size_ = size;
    }

    void set_flush_interval(int interval_ms) {
        flush_interval_ms_ = interval_ms;
    }

private:
    void flush_buffer_internal() {
        if (!token_buffer_.empty() && update_callback_) {
            std::string batch_text;
            for (const auto& token : token_buffer_) {
                batch_text += token;
            }
            token_buffer_.clear();
            
            // Call Python callback without holding the lock
            update_callback_(batch_text);
        }
    }
};

class FileProcessor {
public:
    static std::string read_file_fast(const std::string& file_path) {
        std::ifstream file(file_path, std::ios::binary);
        if (!file) {
            throw std::runtime_error("Failed to open file: " + file_path);
        }
        
        file.seekg(0, std::ios::end);
        size_t size = file.tellg();
        file.seekg(0, std::ios::beg);
        
        std::string content(size, '\0');
        file.read(&content[0], size);
        
        return content;
    }

    static bool is_valid_python_file(const std::string& file_path) {
        return file_path.length() > 3 && 
               file_path.substr(file_path.length() - 3) == ".py";
    }
};

PYBIND11_MODULE(core_performance, m) {
    m.doc() = "High-performance C++ core for code review application";

    pybind11::class_<AdaptiveTextStreamer>(m, "AdaptiveTextStreamer")
        .def(pybind11::init<size_t, int>(), 
             pybind11::arg("buffer_size") = 20, 
             pybind11::arg("flush_interval_ms") = 100)
        .def("set_update_callback", &AdaptiveTextStreamer::set_update_callback)
        .def("add_token", &AdaptiveTextStreamer::add_token)
        .def("start_streaming", &AdaptiveTextStreamer::start_streaming)
        .def("stop_streaming", &AdaptiveTextStreamer::stop_streaming)
        .def("flush_buffer", &AdaptiveTextStreamer::flush_buffer)
        .def("get_full_text", &AdaptiveTextStreamer::get_full_text)
        .def("clear", &AdaptiveTextStreamer::clear)
        .def("get_buffer_size", &AdaptiveTextStreamer::get_buffer_size)
        .def("set_buffer_size", &AdaptiveTextStreamer::set_buffer_size)
        .def("set_flush_interval", &AdaptiveTextStreamer::set_flush_interval);

    pybind11::class_<FileProcessor>(m, "FileProcessor")
        .def_static("read_file_fast", &FileProcessor::read_file_fast)
        .def_static("is_valid_python_file", &FileProcessor::is_valid_python_file);
}