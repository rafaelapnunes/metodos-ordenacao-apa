#include "classical.hpp"
#include "authorial.hpp"
#include "mirror_merge.hpp"
#include <iostream>
#include <vector>
#include <algorithm>
#include <random>
#include <cassert>
#include <functional>
#include <string>
#include <cstdint>

void run_test_suite(const std::string& alg_name, const std::function<SortResult(std::vector<int>)>& sort_fn) {
    std::cout << "  🧪 Testando [" << alg_name << "]...";

    // 1. Vetor vazio
    {
        std::vector<int> v = {};
        auto res = sort_fn(v);
        assert(res.data.empty());
    }

    // 2. Elemento único
    {
        std::vector<int> v = {42};
        auto res = sort_fn(v);
        assert(res.data.size() == 1 && res.data[0] == 42);
    }

    // 3. Já ordenado
    {
        std::vector<int> v(100);
        for (int i = 0; i < 100; ++i) v[i] = i;
        auto expected = v;
        auto res = sort_fn(v);
        assert(res.data == expected);
    }

    // 4. Inversamente ordenado
    {
        std::vector<int> v(100);
        for (int i = 0; i < 100; ++i) v[i] = 100 - i;
        auto expected = v;
        std::sort(expected.begin(), expected.end());
        auto res = sort_fn(v);
        assert(res.data == expected);
    }

    // 5. Elementos idênticos
    {
        std::vector<int> v(50, 7);
        auto res = sort_fn(v);
        assert(res.data == v);
    }

    // 6. Muitos repetidos
    {
        std::mt19937 rng(42);
        std::vector<int> v(200);
        for (auto& x : v) x = rng() % 5;
        auto expected = v;
        std::sort(expected.begin(), expected.end());
        auto res = sort_fn(v);
        assert(res.data == expected);
    }

    // 7. Números negativos
    {
        std::vector<int> v = {-50, 10, -200, 0, 5, -1, 100, -50};
        auto expected = v;
        std::sort(expected.begin(), expected.end());
        auto res = sort_fn(v);
        assert(res.data == expected);
    }

    // 8. Aleatório grande
    {
        std::mt19937 rng(123);
        std::vector<int> v(1000);
        for (auto& x : v) x = static_cast<int>(rng() % 20000) - 10000;
        auto expected = v;
        std::sort(expected.begin(), expected.end());
        auto res = sort_fn(v);
        assert(res.data == expected);
    }

    std::cout << " [PASSOU EM TODOS OS CENÁRIOS ✅]" << std::endl;
}

static uint64_t ceil_lg(uint64_t n) {
    uint64_t L = 0;
    while ((uint64_t{1} << L) < n) ++L;
    return L;
}

// Sem atalho: W(n) = n*ceil(lg n) - 2^ceil(lg n) + 1 (relatorio.md, Seção 3.1)
static uint64_t basic_comparisons(uint64_t n) {
    if (n <= 1) return 0;
    uint64_t L = ceil_lg(n);
    return n * L - (uint64_t{1} << L) + 1;
}

// M(n) = 2*(n*ceil(lg n) - 2^ceil(lg n) + n), com ou sem atalho (Seção 3.3)
static uint64_t expected_moves(uint64_t n) {
    if (n <= 1) return 0;
    uint64_t L = ceil_lg(n);
    return 2 * (n * L - (uint64_t{1} << L) + n);
}

// Pior caso com atalho: Cmax(n) = Cmax(ceil(n/2)) + Cmax(floor(n/2)) + n + 1, Cmax(2) = 1 (Seção 3.2)
static std::vector<uint64_t> max_comparisons_table(uint64_t limit) {
    std::vector<uint64_t> C(limit + 1, 0);
    if (limit >= 2) C[2] = 1;
    for (uint64_t n = 3; n <= limit; ++n) C[n] = C[(n + 1) / 2] + C[n / 2] + n + 1;
    return C;
}
static const std::vector<uint64_t> CMAX = max_comparisons_table(10000);

// Metades sempre intercaladas: nenhum atalho dispara.
static std::vector<int> worst_case_input(const std::vector<int>& vals) {
    if (vals.size() <= 1) return vals;
    std::vector<int> even, odd;
    for (size_t i = 0; i < vals.size(); ++i) (i % 2 ? odd : even).push_back(vals[i]);
    auto out = worst_case_input(even);
    auto right = worst_case_input(odd);
    out.insert(out.end(), right.begin(), right.end());
    return out;
}

// Metades sempre separadas, com a esquerda vindo primeiro: 1 comparação por fusão.
static std::vector<int> best_case_input(const std::vector<int>& vals, bool ascending) {
    size_t m = vals.size();
    if (m <= 1) return vals;
    size_t h = (m + 1) / 2;
    std::vector<int> left, right;
    if (ascending) {  // montanha: a esquerda fica com os menores
        left.assign(vals.begin(), vals.begin() + h);
        right.assign(vals.begin() + h, vals.end());
    } else {          // vale: a esquerda fica com os maiores
        left.assign(vals.begin() + (m - h), vals.end());
        right.assign(vals.begin(), vals.begin() + (m - h));
    }
    auto out = best_case_input(left, ascending);
    auto r = best_case_input(right, !ascending);
    out.insert(out.end(), r.begin(), r.end());
    return out;
}

static std::vector<int> iota_vec(int n) {
    std::vector<int> v(n);
    for (int i = 0; i < n; ++i) v[i] = i;
    return v;
}

static void check_mirror(const std::vector<int>& v) {
    uint64_t n = v.size();
    auto expected = v;
    std::sort(expected.begin(), expected.end());

    auto res = mirror_merge_sort(v);
    assert(res.data == expected);
    assert(res.comparisons >= (n > 0 ? n - 1 : 0));
    assert(res.comparisons <= CMAX[n]);
    assert(res.moves == expected_moves(n));

    auto basic = mirror_merge_sort_basic(v);
    assert(basic.data == expected);
    assert(basic.comparisons == basic_comparisons(n));
    assert(basic.moves == expected_moves(n));
}

// Elemento comparado só pela chave; a etiqueta registra a posição original.
struct Item {
    int key;
    char tag;
    bool operator<=(const Item& o) const { return key <= o.key; }
    bool operator>=(const Item& o) const { return key >= o.key; }
};

void run_mirror_merge_tests() {
    std::cout << "  🧪 Testando [Mirror-Merge Sort (Autoral)] em escala...";

    // Cenários obrigatórios do enunciado em N = 10, 10^2, 10^3, 10^4
    std::mt19937 rng(2026);
    for (int n : {10, 100, 1000, 10000}) {
        std::vector<int> v(n);
        for (auto& x : v) x = static_cast<int>(rng() % (20 * n)) - 10 * n;  // aleatório
        check_mirror(v);
        for (int i = 0; i < n; ++i) v[i] = i;                                // ordenado
        check_mirror(v);
        for (int i = 0; i < n; ++i) v[i] = n - i;                            // reverso
        check_mirror(v);
        for (auto& x : v) x = static_cast<int>(rng() % 5);                   // repetidos
        check_mirror(v);
        check_mirror(std::vector<int>(n, 0));                                // todos iguais
    }

    // Casos limite
    check_mirror({});
    check_mirror({5});

    // Todo N de 1 a 1024 (divisões desiguais das metades)
    for (int n = 1; n <= 1024; ++n) {
        std::vector<int> v(n);
        for (auto& x : v) x = static_cast<int>(rng() % (n / 3 + 1));
        check_mirror(v);
    }

    // W(n) satisfaz W(n) = W(ceil(n/2)) + W(floor(n/2)) + n - 1 até 10^4
    std::vector<uint64_t> W(10001, 0);
    for (uint64_t n = 2; n <= 10000; ++n) W[n] = W[(n + 1) / 2] + W[n / 2] + n - 1;
    for (uint64_t n = 1; n <= 10000; ++n) assert(W[n] == basic_comparisons(n));

    // Cmax(2^h) = 2^h * h - 1
    for (uint64_t h = 1; (uint64_t{1} << h) <= 10000; ++h)
        assert(CMAX[uint64_t{1} << h] == (uint64_t{1} << h) * h - 1);

    // Pior e melhor caso são atingidos exatamente; ordenado e reverso fazem no máximo 2(n - 1)
    std::vector<int> sizes;
    for (int n = 1; n <= 1024; ++n) sizes.push_back(n);
    sizes.push_back(10000);
    for (int n : sizes) {
        auto worst = mirror_merge_sort(worst_case_input(iota_vec(n)));
        assert(worst.comparisons == CMAX[n]);
        auto best = mirror_merge_sort(best_case_input(iota_vec(n), true));
        assert(best.comparisons == static_cast<uint64_t>(n - 1));
        if (n >= 2) {
            std::vector<int> rev(n);
            for (int i = 0; i < n; ++i) rev[i] = n - i;
            assert(mirror_merge_sort(iota_vec(n)).comparisons <= 2 * static_cast<uint64_t>(n - 1));
            assert(mirror_merge_sort(rev).comparisons <= 2 * static_cast<uint64_t>(n - 1));
        }
    }

    // Contraexemplo de instabilidade (relatorio.md, Seção 3.5), com e sem atalho
    for (bool adaptive : {true, false}) {
        std::vector<Item> v = {{1, 'a'}, {2, 'b'}, {1, 'c'}, {1, 'd'}};
        uint64_t comps = 0, moves = 0;
        mirror_merge_detail::sort(v, comps, moves, adaptive);
        std::string tags;
        for (const auto& it : v) tags += it.tag;
        assert(tags == "adcb");  // "d" antes de "c": ordem relativa invertida
    }

    std::cout << " [PASSOU EM TODOS OS CENÁRIOS ✅]" << std::endl;
}

int main() {
    std::cout << "==================================================" << std::endl;
    std::cout << "  SUÍTE DE TESTES UNITÁRIOS EM C++ (APA, TP1)     " << std::endl;
    std::cout << "==================================================" << std::endl;

    run_test_suite("Bubble Sort", bubble_sort);
    run_test_suite("Selection Sort", selection_sort);
    run_test_suite("Insertion Sort", insertion_sort);
    run_test_suite("Merge Sort", merge_sort);
    run_test_suite("Quick Sort", quick_sort);
    run_test_suite("Authorial (DPES)", dpes_sort);
    run_test_suite("Mirror-Merge Sort (Autoral)", mirror_merge_sort);
    run_test_suite("Mirror-Merge Sort (sem atalho)", mirror_merge_sort_basic);
    run_mirror_merge_tests();

    std::cout << "\n🎉 Todos os 8 algoritmos foram validados com 100% de sucesso no C++!" << std::endl;
    return 0;
}
