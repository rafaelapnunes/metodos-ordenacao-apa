CXX = g++
# No Windows, use: make PYTHON=python <alvo>
PYTHON ?= python3
CXXFLAGS = -std=c++17 -O3 -Wall -Wextra

CPP_DIR = cpp
BUILD_DIR = build

OBJS = $(BUILD_DIR)/classical.o $(BUILD_DIR)/authorial.o $(BUILD_DIR)/mirror_merge.o

all: $(BUILD_DIR) test_cpp benchmark_cpp

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(BUILD_DIR)/classical.o: $(CPP_DIR)/classical.cpp $(CPP_DIR)/classical.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(BUILD_DIR)/authorial.o: $(CPP_DIR)/authorial.cpp $(CPP_DIR)/authorial.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(BUILD_DIR)/mirror_merge.o: $(CPP_DIR)/mirror_merge.cpp $(CPP_DIR)/mirror_merge.hpp $(CPP_DIR)/classical.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -c $< -o $@

test_cpp: $(OBJS) $(CPP_DIR)/mirror_merge.hpp $(CPP_DIR)/test_runner.cpp
	$(CXX) $(CXXFLAGS) $(OBJS) $(CPP_DIR)/test_runner.cpp -o $(BUILD_DIR)/test_runner
	./$(BUILD_DIR)/test_runner

benchmark_cpp: $(OBJS) $(CPP_DIR)/benchmark.cpp
	$(CXX) $(CXXFLAGS) $(OBJS) $(CPP_DIR)/benchmark.cpp -o $(BUILD_DIR)/benchmark

run_benchmark_cpp: benchmark_cpp
	./$(BUILD_DIR)/benchmark 100 cpp/benchmark_results_cpp.csv > cpp/benchmark_output_cpp.md

install_python:
	$(PYTHON) -m pip install -r requirements.txt

test_python:
	$(PYTHON) python/test_suite.py

benchmark_python:
	$(PYTHON) python/benchmark.py --trials 10 --plot python/benchmark_results.png --csv python/benchmark_results.csv --md python/benchmark_output.md

clean:
	rm -rf $(BUILD_DIR) *.png

.PHONY: all install_python test_cpp benchmark_cpp run_benchmark_cpp test_python benchmark_python clean
