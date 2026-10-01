"""
Framework de Benchmarking e Comparação de Algoritmos de Ordenação.
Gera tabelas estatísticas em Markdown, CSV e gráficos comparativos PNG.
"""

import argparse
from collections import defaultdict
import csv
import gc
import math
import os
import platform
import random
import statistics
import sys
import time
from typing import Callable, Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from authorial import dpes_sort
from classical import (
    bubble_sort,
    insertion_sort,
    merge_sort,
    quick_sort,
    selection_sort,
)
from student_template import my_authorial_sort

# O Quick Sort recursivo e o Mirror-Merge chegam a profundidades maiores em N = 10^4.
sys.setrecursionlimit(10000)

QUADRATIC = ("Bubble Sort", "Selection Sort", "Insertion Sort")
QUADRATIC_MAX_N = 2500  # acima disso os O(n^2) em Python levam minutos por medição


def generate_dataset(n: int, distribution: str) -> List[int]:
    """Gera vetores para testes com diferentes distribuições de dados."""
    if distribution == "random":
        return [random.randint(0, 10 * n) for _ in range(n)]
    elif distribution == "sorted":
        return list(range(n))
    elif distribution == "reverse":
        return list(range(n, 0, -1))
    elif distribution == "duplicates":
        return [random.choice([1, 2, 3, 5, 8]) for _ in range(n)]
    elif distribution == "almost_sorted":
        arr = list(range(n))
        swaps = max(1, n // 20)  # ~5% de trocas aleatórias
        for _ in range(swaps):
            i = random.randint(0, n - 1)
            j = random.randint(0, n - 1)
            arr[i], arr[j] = arr[j], arr[i]
        return arr
    else:
        raise ValueError(f"Distribuição desconhecida: {distribution}")


def run_benchmark(
    algorithms: Dict[str, Callable[[List], Tuple[List, int, int]]],
    sizes: List[int],
    distributions: List[str],
    trials: int = 3,
) -> Dict[str, Dict[str, Dict[int, Dict[str, float]]]]:
    """
    Executa medições de tempo, comparações e movimentações para cada algoritmo,
    tamanho e distribuição.
    """
    # results[dist][alg_name][size] = {'time_ms' (mediana), 'time_mean_ms', 'time_std_ms', 'comps', 'moves'}
    results = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

    for dist in distributions:
        print(f"\n📊 Executando benchmarks para distribuição: [{dist.upper()}]")
        for size in sizes:
            print(f"  -> Tamanho N = {size}...")
            # Gera datasets fixos por repetição para garantir comparação justa
            datasets = [generate_dataset(size, dist) for _ in range(trials)]

            active = {
                name: fn for name, fn in algorithms.items()
                # Para Bubble/Selection/Insertion, evita tamanhos excessivos que demoram muito
                if not (size > QUADRATIC_MAX_N and name in QUADRATIC)
            }
            samples = {name: {"times": [], "comps": [], "moves": []} for name in active}

            # Repetições intercaladas: em cada repetição todos os algoritmos rodam sobre o mesmo
            # vetor, em ordem embaralhada, para que variações de carga/temperatura da máquina
            # afetem todos igualmente. O GC fica desligado durante a medição (como no timeit).
            order = list(active)
            for data in datasets:
                random.shuffle(order)
                for name in order:
                    data_copy = list(data)
                    gc.disable()
                    start = time.perf_counter()
                    res, c, m = active[name](data_copy)
                    elapsed_ms = (time.perf_counter() - start) * 1000.0
                    gc.enable()

                    # Validação de sanidade
                    assert res == sorted(data), f"Erro de ordenação em {name}!"

                    samples[name]["times"].append(elapsed_ms)
                    samples[name]["comps"].append(c)
                    samples[name]["moves"].append(m)

            for name, smp in samples.items():
                times = smp["times"]
                results[dist][name][size] = {
                    "time_ms": statistics.median(times),
                    "time_mean_ms": statistics.mean(times),
                    "time_std_ms": statistics.stdev(times) if len(times) > 1 else 0.0,
                    "comps": statistics.mean(smp["comps"]),
                    "moves": statistics.mean(smp["moves"]),
                }

    return results


def print_markdown_summary(results: dict, sizes: List[int], output_path: str = None):
    """Imprime (e opcionalmente salva) tabelas Markdown de tempo médio ± desvio-padrão."""
    lines = [
        "# Resultados do benchmark (tempo em ms, mediana ± desvio-padrão)",
        "",
        f"Python {platform.python_version()} | {platform.system()} {platform.release()} | {platform.processor()}",
    ]
    for dist, algs in results.items():
        lines += ["", f"### Distribuição `{dist}`", ""]
        lines.append("| Algoritmo | " + " | ".join(f"N={s}" for s in sizes) + " |")
        lines.append("| :--- | " + " | ".join(":---:" for _ in sizes) + " |")
        for alg_name, size_data in algs.items():
            row = [alg_name]
            for s in sizes:
                if s in size_data:
                    row.append(f"{size_data[s]['time_ms']:.3f} ± {size_data[s]['time_std_ms']:.3f}")
                else:
                    row.append("não medido")
            lines.append("| " + " | ".join(row) + " |")
    text = "\n".join(lines) + "\n"
    print(text)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"📝 Tabelas salvas em: {output_path}")


def save_csv(results: dict, output_path: str):
    """Salva todas as medições em CSV (uma linha por distribuição/algoritmo/N)."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["distribuicao", "algoritmo", "n", "tempo_mediana_ms", "tempo_media_ms", "tempo_desvio_ms",
                    "comparacoes", "movimentacoes", "comps_sobre_nlog2n"])
        for dist, algs in results.items():
            for alg_name, size_map in algs.items():
                for n in sorted(size_map):
                    d = size_map[n]
                    ratio = d["comps"] / (n * math.log2(n)) if n > 1 else 0.0
                    w.writerow([dist, alg_name, n, f"{d['time_ms']:.4f}", f"{d['time_mean_ms']:.4f}", f"{d['time_std_ms']:.4f}",
                                f"{d['comps']:.1f}", f"{d['moves']:.1f}", f"{ratio:.4f}"])
    print(f"📄 CSV salvo em: {output_path}")


# Paleta categórica em ordem fixa (cor segue o algoritmo em todos os painéis)
# + marcadores distintos para não depender só da cor.
STYLE = {
    "Mirror-Merge Sort (Autoral)": ("#2a78d6", "o"),
    "Merge Sort": ("#eb6834", "s"),
    "Quick Sort": ("#1baf7a", "^"),
    "Authorial (DPES)": ("#eda100", "D"),
    "Insertion Sort": ("#e87ba4", "v"),
    "Selection Sort": ("#008300", "P"),
    "Bubble Sort": ("#4a3aa7", "X"),
}


def plot_benchmark_results(results: dict, output_path: str = "benchmark_results.png"):
    """Gera gráficos (escala log-log) de tempo, comparações e movimentações × N."""
    distributions = list(results.keys())
    metrics = [("time_ms", "Tempo mediano (ms)"), ("comps", "Comparações"), ("moves", "Movimentações")]
    fig, axes = plt.subplots(len(distributions), 3, figsize=(18, 4.2 * len(distributions)), squeeze=False)

    for idx, dist in enumerate(distributions):
        for col, (key, label) in enumerate(metrics):
            ax = axes[idx][col]
            for alg_name, size_map in results[dist].items():
                # Escala log não representa zero (ex.: Quick/Selection sem movimentações em vetor ordenado)
                sizes = [s for s in sorted(size_map.keys()) if size_map[s][key] > 0]
                values = [size_map[s][key] for s in sizes]
                if not sizes:
                    continue
                color, marker = STYLE.get(alg_name, ("#52514e", "."))
                lw = 2.6 if "Mirror" in alg_name else 1.6
                ax.plot(sizes, values, marker=marker, markersize=6, linewidth=lw, color=color, label=alg_name)
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_title(f"{label} × N [{dist}]", fontsize=10)
            ax.set_xlabel("N (escala log)")
            ax.set_ylabel(label)
            ax.grid(True, which="major", linestyle="--", alpha=0.35)
            for spine in ("top", "right"):
                ax.spines[spine].set_visible(False)
        axes[idx][0].legend(fontsize=8, frameon=False)

    plt.tight_layout()
    plt.savefig(output_path, dpi=130)
    plt.close(fig)
    print(f"\n🖼️ Gráfico salvo com sucesso em: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Benchmark de Algoritmos de Ordenação (APA)")
    parser.add_argument("--trials", type=int, default=10, help="Número de repetições por teste")
    parser.add_argument("--plot", type=str, default="benchmark_results.png", help="Caminho para salvar o gráfico")
    parser.add_argument("--csv", type=str, default="benchmark_results.csv", help="Caminho para salvar o CSV")
    parser.add_argument("--md", type=str, default="benchmark_output.md", help="Caminho para salvar as tabelas Markdown")
    parser.add_argument("--seed", type=int, default=42, help="Semente dos geradores de dados")
    parser.add_argument("--max-n", type=int, default=10000, help="Maior N a medir")
    args = parser.parse_args()
    # Evita UnicodeEncodeError dos emojis no console do Windows (cp1252)
    sys.stdout.reconfigure(encoding="utf-8")

    algorithms = {
        "Bubble Sort": bubble_sort,
        "Selection Sort": selection_sort,
        "Insertion Sort": insertion_sort,
        "Merge Sort": merge_sort,
        "Quick Sort": quick_sort,
        "Authorial (DPES)": dpes_sort,
        "Mirror-Merge Sort (Autoral)": my_authorial_sort,
    }

    sizes = [n for n in (10, 100, 500, 1000, 2500, 5000, 10000) if n <= args.max_n]
    distributions = ["random", "sorted", "reverse", "duplicates", "almost_sorted"]

    random.seed(args.seed)
    results = run_benchmark(algorithms, sizes, distributions, trials=args.trials)
    print_markdown_summary(results, sizes, args.md)
    save_csv(results, args.csv)
    plot_benchmark_results(results, args.plot)


if __name__ == "__main__":
    main()
