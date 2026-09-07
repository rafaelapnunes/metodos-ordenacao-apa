"""
TEMPLATE PARA O ALUNO — TRABALHO PRÁTICO 1 (TP1)
Disciplina: Análise e Projetos de Algoritmos (APA)

Instruções:
1. Implemente seu método de ordenação autoral na função `my_authorial_sort`.
2. O retorno deve ser obrigatoriamente a tupla: (lista_ordenada, total_comparacoes, total_movimentacoes).
3. Execute este arquivo diretamente para rodar a suíte de testes de corretude e o benchmark rápido.
"""

from typing import Any, List, Tuple
import unittest


def my_authorial_sort(arr: List[Any]) -> Tuple[List[Any], int, int]:
    """
    IMPLEMENTE AQUI SEU ALGORITMO AUTORAL.

    Parâmetros:
        arr (List[Any]): Lista de entrada a ser ordenada.

    Retorno:
        Tuple[List[Any], int, int]:
            - Lista ordenada
            - Total de comparações realizadas
            - Total de movimentações/trocas realizadas
    """
    a = list(arr)
    n = len(a)
    comps = 0
    moves = 0
    
    if n <= 1:
        return a, 0, 0

    temp = [None] * n

    def mirror_merge_sort(low: int, high: int, ascending: bool) -> None:
        nonlocal comps, moves
        if low >= high:
            return

        mid = low + (high - low) // 2

        # Estrutura espelhada: a metade esquerda segue a direção principal,
        # enquanto a metade direita é ordenada na direção oposta.
        # Isso cria uma sequência bitônica (em forma de pico ou vale).
        mirror_merge_sort(low, mid, ascending)
        mirror_merge_sort(mid + 1, high, not ascending)

        i = low
        j = high
        k = low

        # Fusão bitônica: os ponteiros começam nas extremidades e caminham para o centro.
        # Não é necessário verificar os limites (i <= mid ou j > mid), economizando comparações de índice.
        while i <= j:
            comps += 1
            if ascending:
                # Ordenação crescente: seleciona o menor das extremidades
                if a[i] <= a[j]:
                    temp[k] = a[i]
                    i += 1
                else:
                    temp[k] = a[j]
                    j -= 1
            else:
                # Ordenação decrescente: seleciona o maior das extremidades
                # Para manter a estabilidade no decrescente, usamos >= (i sempre foi posicionado antes de j originalmente)
                if a[i] >= a[j]:
                    temp[k] = a[i]
                    i += 1
                else:
                    temp[k] = a[j]
                    j -= 1
            moves += 1
            k += 1

        # Copia de volta do array temporário para o array original
        for idx in range(low, high + 1):
            a[idx] = temp[idx]
            moves += 1

    mirror_merge_sort(0, n - 1, True)

    return a, comps, moves


# =============================================================================
# SUÍTE DE TESTES AUTOMÁTICA DE VALIDAÇÃO
# =============================================================================
class TestStudentAuthorialSort(unittest.TestCase):
    def assert_sorted(self, original: List, result: List):
        self.assertEqual(len(result), len(original), "Tamanho divergente!")
        self.assertEqual(sorted(original), result, "A lista não foi ordenada corretamente!")

    def test_empty(self):
        res, _, _ = my_authorial_sort([])
        self.assert_sorted([], res)

    def test_single(self):
        res, _, _ = my_authorial_sort([99])
        self.assert_sorted([99], res)

    def test_sorted(self):
        data = list(range(100))
        res, _, _ = my_authorial_sort(data)
        self.assert_sorted(data, res)

    def test_reverse(self):
        data = list(range(100, 0, -1))
        res, _, _ = my_authorial_sort(data)
        self.assert_sorted(data, res)

    def test_identical(self):
        data = [5] * 50
        res, _, _ = my_authorial_sort(data)
        self.assert_sorted(data, res)

    def test_random(self):
        import random
        random.seed(42)
        data = [random.randint(-1000, 1000) for _ in range(200)]
        res, _, _ = my_authorial_sort(data)
        self.assert_sorted(data, res)


if __name__ == "__main__":
    print("🧪 Executando testes unitários no seu algoritmo autoral...")
    unittest.main(verbosity=2)
