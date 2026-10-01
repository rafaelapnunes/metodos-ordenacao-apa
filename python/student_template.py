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


def my_authorial_sort(arr: List[Any], adaptive: bool = True) -> Tuple[List[Any], int, int]:
    """
    Mirror-Merge Sort (Ordenação por Fusão Espelhada).

    Ordena a metade esquerda em um sentido e a direita no sentido oposto,
    formando uma sequência bitônica que é fundida por dois ponteiros vindos
    das extremidades (ver relatorio.md, Seções 1 e 2).

    Antes de fundir, testa se as metades já estão separadas (todos os elementos
    de uma metade não passam dos da outra). Nesse caso a saída é uma metade
    seguida da outra invertida, sem fundir (atalho adaptativo, Seção 1.4).

    Comparações: entre n - 1 (melhor caso) e Cmax(n) (pior caso), ver Seção 3.
    Sem o atalho (adaptive=False): exatamente n*ceil(lg n) - 2^ceil(lg n) + 1.
    Movimentações: sempre 2*(n*ceil(lg n) - 2^ceil(lg n) + n).
    Tempo: Θ(n log n) em todos os casos. Espaço auxiliar: O(n).
    Não estável. Não in-place.

    Parâmetros:
        arr (List[Any]): Lista de entrada a ser ordenada.
        adaptive (bool): Usa o atalho das metades separadas (padrão: True).

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

        # Atalho adaptativo (só para m >= 3; com m = 2 a fusão já usa 1 comparação).
        # Na montanha, a[mid] é o máximo da esquerda e a[high] o mínimo da direita;
        # no vale, a[mid] é o mínimo da esquerda e a[high] o máximo da direita.
        if adaptive and high - low >= 2:
            comps += 1
            if (a[mid] <= a[high]) if ascending else (a[mid] >= a[high]):
                # A esquerda vem primeiro: esquerda, depois a direita invertida.
                k = low
                for idx in range(low, mid + 1):
                    temp[k] = a[idx]
                    k += 1
                for idx in range(high, mid, -1):
                    temp[k] = a[idx]
                    k += 1
                moves += high - low + 1
                copy_back(low, high)
                return
            comps += 1
            # Empate fica com a esquerda (teste estrito), para não inverter iguais à toa.
            if not (a[low] <= a[mid + 1]) if ascending else not (a[low] >= a[mid + 1]):
                # A direita vem primeiro: direita invertida, depois a esquerda.
                k = low
                for idx in range(high, mid, -1):
                    temp[k] = a[idx]
                    k += 1
                for idx in range(low, mid + 1):
                    temp[k] = a[idx]
                    k += 1
                moves += high - low + 1
                copy_back(low, high)
                return

        i = low
        j = high
        k = low

        # Fusão bitônica: os ponteiros começam nas extremidades e caminham para o centro.
        # Não é necessário verificar os limites (i <= mid ou j > mid), economizando comparações de índice.
        # O sentido é testado uma vez, fora do laço, e cada laço só testa i < j.
        # Obs.: nenhuma regra de desempate torna o método estável, pois o ponteiro que
        # atravessa o pico lê a outra metade pelo lado oposto (ver relatorio.md, Seção 3.4).
        if ascending:
            # Montanha: seleciona o menor das extremidades
            while i < j:
                comps += 1
                if a[i] <= a[j]:
                    temp[k] = a[i]
                    i += 1
                else:
                    temp[k] = a[j]
                    j -= 1
                k += 1
        else:
            # Vale: seleciona o maior das extremidades
            while i < j:
                comps += 1
                if a[i] >= a[j]:
                    temp[k] = a[i]
                    i += 1
                else:
                    temp[k] = a[j]
                    j -= 1
                k += 1

        # Resta um único elemento (i == j): é o maior (montanha) ou o menor (vale)
        # do segmento e vai para a última posição sem precisar de comparação.
        temp[k] = a[i]
        moves += high - low + 1
        copy_back(low, high)

    def copy_back(low: int, high: int) -> None:
        """Copia de volta do array temporário para o array original."""
        nonlocal moves
        for idx in range(low, high + 1):
            a[idx] = temp[idx]
        moves += high - low + 1

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
    import sys
    sys.stdout.reconfigure(encoding="utf-8")  # emojis no console do Windows (cp1252)
    print("🧪 Executando testes unitários no seu algoritmo autoral...")
    unittest.main(verbosity=2)
