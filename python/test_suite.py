"""
Suíte de Testes Obrigatória para Algoritmos de Ordenação.
Executa os cenários exigidos pelo enunciado do TP1.
"""

import random
import sys
import unittest
from functools import lru_cache
from typing import Callable, List, Tuple

from authorial import dpes_sort
from classical import (
    bubble_sort,
    insertion_sort,
    merge_sort,
    quick_sort,
    selection_sort,
)
from student_template import my_authorial_sort

# Recursão do Quick Sort em N = 10^4 (o Mirror-Merge desce só ceil(lg n) ≈ 14 níveis)
sys.setrecursionlimit(10000)


class BaseSortMixin:
    """Classe base contendo a bateria completa de cenários de teste."""
    sort_fn: Callable[[List], Tuple[List, int, int]]
    name: str

    def assert_sorted(self, original: List, result: List):
        self.assertEqual(len(result), len(original), f"Tamanho divergente em {self.name}")
        self.assertEqual(sorted(original), result, f"Ordenação incorreta em {self.name}")

    def test_01_empty_list(self):
        """Caso limite: Vetor vazio (N = 0)"""
        data = []
        res, _, _ = self.sort_fn(data)
        self.assert_sorted(data, res)

    def test_02_single_element(self):
        """Caso limite: Vetor unitário (N = 1)"""
        data = [42]
        res, _, _ = self.sort_fn(data)
        self.assert_sorted(data, res)

    def test_03_already_sorted(self):
        """Melhor caso / Sensibilidade: Vetor já perfeitamente ordenado"""
        data = list(range(1, 101))
        res, _, _ = self.sort_fn(data)
        self.assert_sorted(data, res)

    def test_04_strictly_reverse_sorted(self):
        """Pior caso / Estresse: Vetor em ordem estritamente decrescente"""
        data = list(range(100, 0, -1))
        res, _, _ = self.sort_fn(data)
        self.assert_sorted(data, res)

    def test_05_all_identical_elements(self):
        """Colisão máxima: Vetor com todos os elementos iguais"""
        data = [7] * 50
        res, _, _ = self.sort_fn(data)
        self.assert_sorted(data, res)

    def test_06_many_duplicates(self):
        """Vetor com poucos valores únicos e muitas repetições"""
        random.seed(42)
        data = [random.choice([1, 2, 3, 4, 5]) for _ in range(200)]
        res, _, _ = self.sort_fn(data)
        self.assert_sorted(data, res)

    def test_07_negative_and_floating_point(self):
        """Vetor misto com números negativos e de ponto flutuante"""
        data = [-10.5, 3.14, 0.0, -0.01, 100.2, -50.0, 2.718, 0.0, -10.5]
        res, _, _ = self.sort_fn(data)
        self.assert_sorted(data, res)

    def test_08_random_uniform_small(self):
        """Vetores aleatórios pequenos (N = 25)"""
        random.seed(123)
        data = [random.randint(-1000, 1000) for _ in range(25)]
        res, _, _ = self.sort_fn(data)
        self.assert_sorted(data, res)

    def test_09_random_uniform_medium(self):
        """Vetores aleatórios médios (N = 1000)"""
        random.seed(456)
        data = [random.randint(-10000, 10000) for _ in range(1000)]
        res, _, _ = self.sort_fn(data)
        self.assert_sorted(data, res)

    def test_10_almost_sorted(self):
        """Vetor quase ordenado (95% ordenado com poucas permutações locais)"""
        data = list(range(200))
        # Introduz algumas trocas pontuais
        for i in (10, 50, 120, 180):
            data[i], data[i + 1] = data[i + 1], data[i]
        res, _, _ = self.sort_fn(data)
        self.assert_sorted(data, res)


class TestBubbleSort(unittest.TestCase, BaseSortMixin):
    sort_fn = staticmethod(bubble_sort)
    name = "Bubble Sort"


class TestSelectionSort(unittest.TestCase, BaseSortMixin):
    sort_fn = staticmethod(selection_sort)
    name = "Selection Sort"


class TestInsertionSort(unittest.TestCase, BaseSortMixin):
    sort_fn = staticmethod(insertion_sort)
    name = "Insertion Sort"


class TestMergeSort(unittest.TestCase, BaseSortMixin):
    sort_fn = staticmethod(merge_sort)
    name = "Merge Sort"


class TestQuickSort(unittest.TestCase, BaseSortMixin):
    sort_fn = staticmethod(quick_sort)
    name = "Quick Sort"


class TestAuthorialSort(unittest.TestCase, BaseSortMixin):
    sort_fn = staticmethod(dpes_sort)
    name = "Authorial Sort (DPES)"


class TestMirrorMergeSort(unittest.TestCase, BaseSortMixin):
    sort_fn = staticmethod(my_authorial_sort)
    name = "Mirror-Merge Sort (Autoral)"


class TestMirrorMergeSortBasic(unittest.TestCase, BaseSortMixin):
    sort_fn = staticmethod(lambda arr: my_authorial_sort(arr, adaptive=False))
    name = "Mirror-Merge Sort (sem atalho)"


def ceil_lg(n: int) -> int:
    return (n - 1).bit_length()  # ceil(log2 n), para n >= 1


def basic_comparisons(n: int) -> int:
    """Sem atalho: W(n) = n*ceil(lg n) - 2^ceil(lg n) + 1 (Seção 3.1 do relatório)."""
    if n <= 1:
        return 0
    L = ceil_lg(n)
    return n * L - (1 << L) + 1


def expected_moves(n: int) -> int:
    """M(n) = 2*(n*ceil(lg n) - 2^ceil(lg n) + n), com ou sem atalho (Seção 3.3)."""
    if n <= 1:
        return 0
    L = ceil_lg(n)
    return 2 * (n * L - (1 << L) + n)


@lru_cache(maxsize=None)
def max_comparisons(n: int) -> int:
    """Pior caso com atalho: Cmax(n) = Cmax(ceil(n/2)) + Cmax(floor(n/2)) + n + 1 (Seção 3.2)."""
    if n <= 1:
        return 0
    if n == 2:
        return 1
    return max_comparisons((n + 1) // 2) + max_comparisons(n // 2) + n + 1


def worst_case_input(n: int) -> List[int]:
    """Metades sempre intercaladas: nenhum atalho dispara (Seção 3.2)."""
    def build(vals):
        if len(vals) <= 1:
            return list(vals)
        return build(vals[0::2]) + build(vals[1::2])
    return build(list(range(n)))


def best_case_input(n: int) -> List[int]:
    """Metades sempre separadas, com a esquerda vindo primeiro: 1 comparação por fusão (Seção 3.2)."""
    def build(vals, ascending):
        m = len(vals)
        if m <= 1:
            return list(vals)
        h = (m + 1) // 2
        if ascending:  # montanha: a esquerda fica com os menores
            left, right = vals[:h], vals[h:]
        else:          # vale: a esquerda fica com os maiores
            left, right = vals[m - h:], vals[:m - h]
        return build(left, ascending) + build(right, not ascending)
    return build(list(range(n)), True)


class TestMirrorMergeScaling(unittest.TestCase):
    """
    Cenários obrigatórios do enunciado (Seção 6) em todas as ordens de grandeza
    N = 10, 10^2, 10^3, 10^4, mais verificações das fórmulas deduzidas no relatório (Seção 3).
    """
    SIZES = (10, 100, 1000, 10000)

    def check(self, data: List):
        n = len(data)
        res, comps, moves = my_authorial_sort(data)
        self.assertEqual(sorted(data), res)
        self.assertGreaterEqual(comps, max(n - 1, 0))
        self.assertLessEqual(comps, max_comparisons(n))
        self.assertEqual(moves, expected_moves(n))

        res, comps, moves = my_authorial_sort(data, adaptive=False)
        self.assertEqual(sorted(data), res)
        self.assertEqual(comps, basic_comparisons(n))
        self.assertEqual(moves, expected_moves(n))

    def test_random(self):
        rng = random.Random(2026)
        for n in self.SIZES:
            with self.subTest(n=n):
                self.check([rng.randint(-10 * n, 10 * n) for _ in range(n)])

    def test_sorted(self):
        for n in self.SIZES:
            with self.subTest(n=n):
                self.check(list(range(n)))

    def test_reverse(self):
        for n in self.SIZES:
            with self.subTest(n=n):
                self.check(list(range(n, 0, -1)))

    def test_duplicates(self):
        rng = random.Random(7)
        for n in self.SIZES:
            with self.subTest(n=n):
                self.check([rng.choice([1, 2, 3, 5, 8]) for _ in range(n)])
                self.check([0] * n)

    def test_empty_and_single(self):
        for adaptive in (True, False):
            self.assertEqual(my_authorial_sort([], adaptive), ([], 0, 0))
            self.assertEqual(my_authorial_sort([5], adaptive), ([5], 0, 0))

    def test_all_sizes_up_to_1024(self):
        """Todo N de 1 a 1024: tamanhos ímpares, potências de 2 e divisões desiguais."""
        rng = random.Random(1)
        for n in range(1, 1025):
            with self.subTest(n=n):
                self.check([rng.randint(0, n // 3) for _ in range(n)])

    def test_closed_form_solves_recurrence(self):
        """W(n) satisfaz W(n) = W(ceil(n/2)) + W(floor(n/2)) + n - 1 para todo N até 10^4."""
        W = [0, 0]
        for n in range(2, 10001):
            W.append(W[(n + 1) // 2] + W[n // 2] + n - 1)
        for n in range(1, 10001):
            with self.subTest(n=n):
                self.assertEqual(W[n], basic_comparisons(n))

    def test_max_comparisons_powers_of_two(self):
        """Para n = 2^h (h >= 1), Cmax(n) = n*lg n - 1."""
        for h in range(1, 15):
            n = 1 << h
            with self.subTest(n=n):
                self.assertEqual(max_comparisons(n), n * h - 1)

    def test_worst_case_is_tight(self):
        """A entrada intercalada atinge exatamente Cmax(n) para todo N de 1 a 1024."""
        for n in list(range(1, 1025)) + [10000]:
            with self.subTest(n=n):
                data = worst_case_input(n)
                res, comps, _ = my_authorial_sort(data)
                self.assertEqual(res, sorted(data))
                self.assertEqual(comps, max_comparisons(n))

    def test_best_case_is_tight(self):
        """A entrada com metades separadas atinge exatamente n - 1 comparações."""
        for n in list(range(1, 1025)) + [10000]:
            with self.subTest(n=n):
                data = best_case_input(n)
                res, comps, _ = my_authorial_sort(data)
                self.assertEqual(res, sorted(data))
                self.assertEqual(comps, max(n - 1, 0))

    def test_sorted_and_reverse_are_linear(self):
        """Vetores ordenados e reversos fazem no máximo 2(n - 1) comparações (Seção 3.2)."""
        for n in list(range(2, 1025)) + [10000]:
            with self.subTest(n=n):
                for data in (list(range(n)), list(range(n, 0, -1))):
                    _, comps, _ = my_authorial_sort(data)
                    self.assertLessEqual(comps, 2 * (n - 1))

    def test_input_is_not_mutated(self):
        data = [3, 1, 2]
        my_authorial_sort(data)
        self.assertEqual(data, [3, 1, 2])

    class Item:
        """Elemento comparado só pela chave; a etiqueta registra a posição original."""
        def __init__(self, key, tag):
            self.key, self.tag = key, tag
        def __le__(self, other):
            return self.key <= other.key
        def __ge__(self, other):
            return self.key >= other.key

    def test_not_stable_counterexample(self):
        """Documenta o contraexemplo de instabilidade citado no relatório (Seção 3.5)."""
        Item = self.Item
        for adaptive in (True, False):
            data = [Item(1, "a"), Item(2, "b"), Item(1, "c"), Item(1, "d")]
            res, _, _ = my_authorial_sort(data, adaptive)
            self.assertEqual([x.key for x in res], [1, 1, 1, 2])
            self.assertEqual([x.tag for x in res], ["a", "d", "c", "b"])  # "d" antes de "c"

    def test_instability_frequency(self):
        """Frequência de violações de estabilidade citada no relatório (Seção 3.5), semente fixa."""
        rng = random.Random(2026)
        violations = 0
        for _ in range(200):
            n = rng.randint(2, 40)
            data = [self.Item(rng.randint(0, 3), i) for i in range(n)]
            res, _, _ = my_authorial_sort(data)
            self.assertEqual([x.key for x in res], sorted(x.key for x in data))
            stable_order = [x.tag for x in sorted(data, key=lambda x: x.key)]
            if [x.tag for x in res] != stable_order:
                violations += 1
        self.assertEqual(violations, 165)


if __name__ == "__main__":
    unittest.main(verbosity=2)
