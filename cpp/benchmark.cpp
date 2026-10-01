#include "classical.hpp"
#include "authorial.hpp"
#include "mirror_merge.hpp"
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <iostream>
#include <vector>
#include <chrono>
#include <random>
#include <iomanip>
#include <string>
#include <functional>

struct BenchmarkResult {
    std::string alg_name;
    int size;
    std::string dist;
    double time_ms;      // mediana
    double time_std_ms;  // desvio-padrão
    double comparisons;  // média entre as repetições
    double moves;        // média entre as repetições
};

std::vector<int> make_dataset(int n, const std::string& dist, std::mt19937& rng) {
    std::vector<int> v(n);
    if (dist == "random") {
        for (int i = 0; i < n; ++i) v[i] = rng() % (10 * n);
    } else if (dist == "sorted") {
        for (int i = 0; i < n; ++i) v[i] = i;
    } else if (dist == "reverse") {
        for (int i = 0; i < n; ++i) v[i] = n - i;
    } else if (dist == "duplicates") {
        for (int i = 0; i < n; ++i) v[i] = rng() % 5;
    } else if (dist == "almost_sorted") {
        for (int i = 0; i < n; ++i) v[i] = i;
        int swaps = std::max(1, n / 20);
        for (int s = 0; s < swaps; ++s) {
            int i = rng() % n;
            int j = rng() % n;
            std::swap(v[i], v[j]);
        }
    }
    return v;
}

using SortFn = std::function<SortResult(std::vector<int>)>;

// Versão original do Mirror-Merge (antes das melhorias da Seção 1.4 do relatório):
// testa o sentido dentro do laço e compara o último elemento consigo mesmo.
// Mantida só como referência no benchmark, para medir o efeito das melhorias na mesma execução.
static void mirror_merge_v1_rec(std::vector<int>& a, std::vector<int>& temp, int64_t low, int64_t high,
                                bool ascending, uint64_t& comps, uint64_t& moves) {
    if (low >= high) return;
    int64_t mid = low + (high - low) / 2;
    mirror_merge_v1_rec(a, temp, low, mid, ascending, comps, moves);
    mirror_merge_v1_rec(a, temp, mid + 1, high, !ascending, comps, moves);
    int64_t i = low, j = high, k = low;
    while (i <= j) {
        comps++;
        if (ascending) {
            if (a[i] <= a[j]) temp[k] = a[i++];
            else              temp[k] = a[j--];
        } else {
            if (a[i] >= a[j]) temp[k] = a[i++];
            else              temp[k] = a[j--];
        }
        moves++;
        k++;
    }
    for (int64_t idx = low; idx <= high; ++idx) {
        a[idx] = temp[idx];
        moves++;
    }
}

static SortResult mirror_merge_v1(std::vector<int> arr) {
    SortResult res{std::move(arr), 0, 0};
    if (res.data.size() <= 1) return res;
    std::vector<int> temp(res.data.size());
    mirror_merge_v1_rec(res.data, temp, 0, static_cast<int64_t>(res.data.size()) - 1, true,
                        res.comparisons, res.moves);
    return res;
}

static const std::vector<std::pair<std::string, SortFn>> ALGORITHMS = {
    {"Bubble Sort", bubble_sort},
    {"Selection Sort", selection_sort},
    {"Insertion Sort", insertion_sort},
    {"Merge Sort", merge_sort},
    {"Quick Sort", quick_sort},
    {"Authorial (DPES)", dpes_sort},
    {"Mirror-Merge Sort (Autoral)", mirror_merge_sort},
    {"Mirror-Merge (sem atalho)", mirror_merge_sort_basic},
    {"Mirror-Merge v1 (original)", mirror_merge_v1},
};

static bool is_quadratic(const std::string& name) {
    return name == "Bubble Sort" || name == "Selection Sort" || name == "Insertion Sort";
}

constexpr int QUADRATIC_MAX_N = 2500;

// Evita que o compilador descarte a ordenação como código sem efeito.
static volatile long long g_sink = 0;

static double median(std::vector<double> v) {
    std::sort(v.begin(), v.end());
    size_t m = v.size() / 2;
    return v.size() % 2 ? v[m] : (v[m - 1] + v[m]) / 2.0;
}

static double stdev(const std::vector<double>& v) {
    if (v.size() < 2) return 0.0;
    double mean = 0.0;
    for (double x : v) mean += x;
    mean /= v.size();
    double acc = 0.0;
    for (double x : v) acc += (x - mean) * (x - mean);
    return std::sqrt(acc / (v.size() - 1));
}

std::vector<BenchmarkResult> benchmark_dist(const std::string& dist, const std::vector<int>& sizes,
                                            int trials, std::mt19937& rng) {
    std::vector<BenchmarkResult> out;
    for (int n : sizes) {
        std::vector<size_t> active;
        for (size_t a = 0; a < ALGORITHMS.size(); ++a)
            if (!(n > QUADRATIC_MAX_N && is_quadratic(ALGORITHMS[a].first))) active.push_back(a);

        std::vector<std::vector<double>> times(ALGORITHMS.size());
        std::vector<double> comps(ALGORITHMS.size(), 0.0), moves(ALGORITHMS.size(), 0.0);

        // Repetições intercaladas: em cada repetição todos os algoritmos ordenam o mesmo
        // vetor, em ordem sorteada, para que oscilações da máquina afetem todos igualmente.
        std::vector<size_t> order = active;
        for (int t = 0; t < trials; ++t) {
            auto data = make_dataset(n, dist, rng);
            auto expected = data;
            std::sort(expected.begin(), expected.end());
            std::shuffle(order.begin(), order.end(), rng);
            for (size_t a : order) {
                auto start = std::chrono::steady_clock::now();
                auto res = ALGORITHMS[a].second(data);
                auto end = std::chrono::steady_clock::now();
                if (res.data != expected) {
                    std::cerr << "Erro de ordenação em " << ALGORITHMS[a].first << std::endl;
                    std::exit(1);
                }
                g_sink = g_sink + (res.data.empty() ? 0 : res.data[0]);
                times[a].push_back(std::chrono::duration<double, std::milli>(end - start).count());
                comps[a] += static_cast<double>(res.comparisons) / trials;
                moves[a] += static_cast<double>(res.moves) / trials;
            }
        }

        for (size_t a : active) {
            out.push_back({ALGORITHMS[a].first, n, dist, median(times[a]), stdev(times[a]),
                           comps[a], moves[a]});
        }
    }
    return out;
}

static void print_table(const std::vector<BenchmarkResult>& rows, const std::string& dist,
                        const std::vector<int>& sizes, const std::string& title,
                        const std::function<std::string(const BenchmarkResult&)>& cell) {
    std::cout << "\n### `" << dist << "`: " << title << "\n\n| Algoritmo | ";
    for (int s : sizes) std::cout << "N=" << s << " | ";
    std::cout << "\n| :--- | ";
    for (size_t i = 0; i < sizes.size(); ++i) std::cout << ":---: | ";
    std::cout << "\n";
    for (const auto& alg : ALGORITHMS) {
        std::cout << "| " << alg.first << " | ";
        for (int s : sizes) {
            auto it = std::find_if(rows.begin(), rows.end(), [&](const BenchmarkResult& r) {
                return r.alg_name == alg.first && r.size == s && r.dist == dist;
            });
            std::cout << (it == rows.end() ? std::string("não medido") : cell(*it)) << " | ";
        }
        std::cout << "\n";
    }
}

static std::string fmt(double v, int prec) {
    std::ostringstream os;
    os << std::fixed << std::setprecision(prec) << v;
    return os.str();
}

int main(int argc, char** argv) {
    // Uso: benchmark [repeticoes] [arquivo.csv]
    int trials = argc > 1 ? std::atoi(argv[1]) : 100;
    std::string csv_path = argc > 2 ? argv[2] : "benchmark_results_cpp.csv";

    std::vector<int> sizes = {10, 100, 500, 1000, 2500, 5000, 10000};
    std::vector<std::string> dists = {"random", "sorted", "reverse", "duplicates", "almost_sorted"};
    std::mt19937 rng(42);

    std::vector<BenchmarkResult> all;
    for (const auto& d : dists) {
        auto rows = benchmark_dist(d, sizes, trials, rng);
        all.insert(all.end(), rows.begin(), rows.end());
    }

    std::cout << "# Resultados dos Benchmarks em C++ (TP1, APA)\n\n"
              << "Tempo em ms: mediana ± desvio-padrão de " << trials << " repetições intercaladas.\n";
    for (const auto& d : dists) {
        print_table(all, d, sizes, "tempo (ms)", [](const BenchmarkResult& r) {
            return fmt(r.time_ms, 4) + " ± " + fmt(r.time_std_ms, 4);
        });
        print_table(all, d, sizes, "comparações", [](const BenchmarkResult& r) {
            return fmt(r.comparisons, 0);
        });
        print_table(all, d, sizes, "movimentações", [](const BenchmarkResult& r) {
            return fmt(r.moves, 0);
        });
    }

    std::ofstream csv(csv_path);
    csv << "distribuicao,algoritmo,n,tempo_mediana_ms,tempo_desvio_ms,comparacoes,movimentacoes\n";
    for (const auto& r : all) {
        csv << r.dist << "," << r.alg_name << "," << r.size << "," << fmt(r.time_ms, 6) << ","
            << fmt(r.time_std_ms, 6) << "," << fmt(r.comparisons, 1) << "," << fmt(r.moves, 1) << "\n";
    }
    std::cout << "\nCSV salvo em: " << csv_path << std::endl;
    return 0;
}
