#ifndef MIRROR_MERGE_SORT_HPP
#define MIRROR_MERGE_SORT_HPP

#include "classical.hpp"
#include <cstdint>
#include <vector>

// Mirror-Merge Sort (Ordenação por Fusão Espelhada), porta em C++ de
// python/student_template.py::my_authorial_sort.
//
// A metade esquerda é ordenada no sentido pedido e a direita no sentido oposto,
// formando uma sequência bitônica que é fundida por dois ponteiros vindos das
// extremidades (ver relatorio.md, Seções 1 e 2). Antes de fundir, um atalho
// testa se as metades já estão separadas (Seção 1.4).
//
// Comparações: entre n - 1 e Cmax(n); sem atalho, exatamente n*ceil(lg n) - 2^ceil(lg n) + 1.
// Movimentações: sempre 2*(n*ceil(lg n) - 2^ceil(lg n) + n).
// Espaço auxiliar O(n). Não estável. Não in-place.

namespace mirror_merge_detail {

// Copia a[from..to] para temp a partir de k, na ordem dada pelo passo (+1 ou -1).
template <typename T>
inline void copy_run(const std::vector<T>& a, std::vector<T>& temp, int64_t from, int64_t to,
                     int64_t step, int64_t& k) {
    for (int64_t idx = from; idx != to + step; idx += step) temp[k++] = a[idx];
}

// Implementação genérica: T precisa apenas de operator<= e operator>=.
// É template para que os testes possam usar elementos com etiqueta (estabilidade).
template <typename T>
void sort_rec(std::vector<T>& a, std::vector<T>& temp, int64_t low, int64_t high,
              bool ascending, bool adaptive, uint64_t& comps, uint64_t& moves) {
    if (low >= high) return;

    int64_t mid = low + (high - low) / 2;

    // Chamadas espelhadas: a metade direita é ordenada no sentido oposto.
    sort_rec(a, temp, low, mid, ascending, adaptive, comps, moves);
    sort_rec(a, temp, mid + 1, high, !ascending, adaptive, comps, moves);

    int64_t k = low;
    bool done = false;

    // Atalho adaptativo (só para m >= 3; com m = 2 a fusão já usa 1 comparação).
    if (adaptive && high - low >= 2) {
        comps++;
        if (ascending ? a[mid] <= a[high] : a[mid] >= a[high]) {
            // A esquerda vem primeiro: esquerda, depois a direita invertida.
            copy_run(a, temp, low, mid, 1, k);
            copy_run(a, temp, high, mid + 1, -1, k);
            done = true;
        } else {
            comps++;
            // Empate fica com a esquerda (teste estrito), para não inverter iguais à toa.
            if (ascending ? !(a[low] <= a[mid + 1]) : !(a[low] >= a[mid + 1])) {
                // A direita vem primeiro: direita invertida, depois a esquerda.
                copy_run(a, temp, high, mid + 1, -1, k);
                copy_run(a, temp, low, mid, 1, k);
                done = true;
            }
        }
    }

    if (!done) {
        // Fusão bitônica: o sentido é testado uma vez, fora do laço, e cada laço
        // só testa i < j (sem testes de fronteira por metade nem laços de esgotamento).
        int64_t i = low;
        int64_t j = high;
        if (ascending) {
            // Montanha: o menor elemento restante está em a[i] ou a[j].
            while (i < j) {
                comps++;
                if (a[i] <= a[j]) temp[k++] = a[i++];
                else              temp[k++] = a[j--];
            }
        } else {
            // Vale: o maior elemento restante está em a[i] ou a[j].
            while (i < j) {
                comps++;
                if (a[i] >= a[j]) temp[k++] = a[i++];
                else              temp[k++] = a[j--];
            }
        }
        // Resta um único elemento (i == j): vai para a última posição sem comparação.
        temp[k] = a[i];
    }
    moves += static_cast<uint64_t>(high - low + 1);

    // Copia de volta do vetor temporário para o original.
    for (int64_t idx = low; idx <= high; ++idx) a[idx] = temp[idx];
    moves += static_cast<uint64_t>(high - low + 1);
}

template <typename T>
void sort(std::vector<T>& a, uint64_t& comps, uint64_t& moves, bool adaptive = true) {
    comps = 0;
    moves = 0;
    if (a.size() <= 1) return;
    std::vector<T> temp(a.size());
    sort_rec(a, temp, 0, static_cast<int64_t>(a.size()) - 1, true, adaptive, comps, moves);
}

}  // namespace mirror_merge_detail

// Interfaces compatíveis com os demais algoritmos do pacote.
SortResult mirror_merge_sort(std::vector<int> arr);        // com atalho adaptativo
SortResult mirror_merge_sort_basic(std::vector<int> arr);  // sem atalho

#endif  // MIRROR_MERGE_SORT_HPP
