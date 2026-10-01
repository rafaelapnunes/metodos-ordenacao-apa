"""
Suíte de Testes Obrigatória para Algoritmos de Ordenação.
Executa os cenários exigidos pelo enunciado do TP1.
"""

import random
import sys
import unittest
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

# Recursão do Quick Sort / Mirror-Merge em N = 10^4
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


class TestMirrorMergeScaling(unittest.TestCase):
    """
    Cenários obrigatórios do enunciado (Seção 6) em todas as ordens de grandeza
    N = 10, 10^2, 10^3, 10^4, mais verificações das propriedades deduzidas no relatório.
    """
    SIZES = (10, 100, 1000, 10000)

    @staticmethod
    def expected_comparisons(n: int) -> int:
        """C(n) = n*ceil(lg n) - 2^ceil(lg n) + n (Seção 3 do relatório)."""
        if n <= 1:
            return 0
        L = (n - 1).bit_length()  # ceil(log2 n)
        return n * L - (1 << L) + n

    def check(self, data: List):
        res, comps, moves = my_authorial_sort(data)
        self.assertEqual(sorted(data), res)
        self.assertEqual(comps, self.expected_comparisons(len(data)))
        self.assertEqual(moves, 2 * comps)

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
        self.assertEqual(my_authorial_sort([]), ([], 0, 0))
        self.assertEqual(my_authorial_sort([5]), ([5], 0, 0))

    def test_all_sizes_up_to_1024(self):
        """Todo N de 1 a 1024: tamanhos ímpares, potências de 2 e divisões desiguais."""
        rng = random.Random(1)
        for n in range(1, 1025):
            with self.subTest(n=n):
                self.check([rng.randint(0, n // 3) for _ in range(n)])

    def test_closed_form_solves_recurrence(self):
        """A fórmula fechada satisfaz C(n) = C(ceil(n/2)) + C(floor(n/2)) + n para todo N até 10^4."""
        C = [0, 0]
        for n in range(2, 10001):
            C.append(C[(n + 1) // 2] + C[n // 2] + n)
        for n in range(1, 10001):
            with self.subTest(n=n):
                self.assertEqual(C[n], self.expected_comparisons(n))

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
        """Documenta o contraexemplo de instabilidade citado no relatório (Seção 3.4)."""
        Item = self.Item
        data = [Item(1, "a"), Item(2, "b"), Item(1, "c"), Item(1, "d")]
        res, _, _ = my_authorial_sort(data)
        self.assertEqual([x.key for x in res], [1, 1, 1, 2])
        self.assertEqual([x.tag for x in res], ["a", "d", "c", "b"])  # "d" antes de "c"

    def test_instability_frequency(self):
        """Frequência de violações de estabilidade citada no relatório (Seção 3.4), semente fixa."""
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
        self.assertEqual(violations, 163)


if __name__ == "__main__":
    unittest.main(verbosity=2)
