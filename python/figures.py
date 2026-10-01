"""
Gera as figuras do relatório a partir dos CSVs dos benchmarks.

    python python/figures.py

Entradas: cpp/benchmark_results_cpp.csv e python/benchmark_results.csv.
Saídas (em figuras/):
    fig1_comparacoes_normalizadas.png   comparações / (n lg n) × N
    fig2_ordenado_reverso.png           comparações × N nos vetores ordenado e reverso
    fig3_tempo_cpp.png                  tempo em C++ com N = 10^4, por cenário
    anexo_grade_python.png              grade completa do benchmark Python
"""

import csv
import math
import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "figuras")

# Tokens de cor (paleta categórica validada, ordem fixa) e tinta neutra.
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"

FINAL = "Mirror-Merge Sort (Autoral)"
BASIC = "Mirror-Merge (sem atalho)"
V1 = "Mirror-Merge v1 (original)"
MERGE = "Merge Sort"

# Séries das figuras focadas: (rótulo, cor, marcador, estilo de linha)
SERIES = {
    FINAL: ("Mirror-Merge (final)", "#2a78d6", "o", "-"),
    MERGE: ("Merge Sort clássico", "#eb6834", "s", "-"),
    BASIC: ("Mirror-Merge sem atalho", "#1baf7a", "^", "--"),
    V1: ("Mirror-Merge v1 (original)", "#eda100", "D", ":"),
}

# Grade completa (anexo): uma cor por algoritmo, na mesma ordem fixa.
GRID_STYLE = {
    FINAL: ("#2a78d6", "o"),
    MERGE: ("#eb6834", "s"),
    "Quick Sort": ("#1baf7a", "^"),
    "Authorial (DPES)": ("#eda100", "D"),
    "Insertion Sort": ("#e87ba4", "v"),
    "Selection Sort": ("#008300", "P"),
    "Bubble Sort": ("#4a3aa7", "X"),
}

DIST_LABEL = {
    "random": "Aleatório",
    "sorted": "Ordenado",
    "reverse": "Reverso",
    "duplicates": "Repetidos",
    "almost_sorted": "Quase ordenado",
}

plt.rcParams.update({
    "font.family": ["Segoe UI", "DejaVu Sans"],
    "font.size": 10,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": AXIS,
    "axes.labelcolor": INK_2,
    "axes.titlecolor": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
})


def load(path):
    """data[dist][alg][n] = linha do CSV."""
    data = defaultdict(lambda: defaultdict(dict))
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            data[row["distribuicao"]][row["algoritmo"]][int(row["n"])] = row
    return data


def style_axes(ax):
    ax.grid(True, which="major", axis="y")
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def line(ax, xs, ys, alg, label=True):
    name, color, marker, ls = SERIES[alg]
    ax.plot(xs, ys, color=color, marker=marker, markersize=6, linewidth=2, linestyle=ls,
            markeredgecolor=SURFACE, markeredgewidth=1.5, label=name if label else None)


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(fig)
    print(f"figura salva: {os.path.relpath(path, ROOT)}")


def fig1_normalized(cpp):
    """Comparações / (n lg n) × N em três cenários (pequenos múltiplos, mesmo eixo y)."""
    dists = ["random", "sorted", "reverse"]
    algs = [FINAL, MERGE, BASIC, V1]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2), sharey=True)
    for ax, dist in zip(axes, dists):
        for alg in algs:
            ns = sorted(n for n in cpp[dist][alg] if n >= 10)
            ys = [float(cpp[dist][alg][n]["comparacoes"]) / (n * math.log2(n)) for n in ns]
            line(ax, ns, ys, alg)
        ax.set_xscale("log")
        ax.set_title(DIST_LABEL[dist], fontsize=11, loc="left")
        ax.set_xlabel("N (escala log)")
        ax.set_ylim(0, 1.15)
        style_axes(ax)
    axes[0].set_ylabel("comparações / (n · lg n)")

    # Rótulos diretos no painel em que as curvas estão bem separadas (ordenado).
    ax = axes[1]
    n_last = 10000
    offsets = {FINAL: 8, MERGE: 8, BASIC: -15, V1: 8}  # sem atalho fica abaixo da própria linha
    for alg in algs:
        y = float(cpp["sorted"][alg][n_last]["comparacoes"]) / (n_last * math.log2(n_last))
        ax.annotate(SERIES[alg][0], (n_last, y), xytext=(-6, offsets[alg]), textcoords="offset points",
                    ha="right", fontsize=8.5, color=INK_2)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.suptitle("")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    save(fig, "fig1_comparacoes_normalizadas.png")


def fig3_time_cpp(cpp):
    """Tempo mediano em C++ com N = 10^4: barras agrupadas por cenário."""
    n = 10000
    dists = ["random", "sorted", "reverse", "duplicates", "almost_sorted"]
    algs = [V1, BASIC, FINAL, MERGE]
    width = 0.19
    gap = 0.015  # espaço visível entre barras vizinhas
    fig, ax = plt.subplots(figsize=(11, 4.4))
    for i, alg in enumerate(algs):
        name, color, _, _ = SERIES[alg]
        xs = [d + (i - (len(algs) - 1) / 2) * width for d in range(len(dists))]
        ys = [float(cpp[dist][alg][n]["tempo_mediana_ms"]) for dist in dists]
        ax.bar(xs, ys, width=width - gap, color=color, label=name, zorder=2)
    ax.set_xticks(range(len(dists)))
    ax.set_xticklabels([DIST_LABEL[d] for d in dists], color=INK_2)
    ax.set_ylabel("tempo mediano (ms)")
    ax.set_ylim(0, None)
    style_axes(ax)
    ax.legend(loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 1.13))
    fig.tight_layout()
    save(fig, "fig3_tempo_cpp.png")


def fig2_sorted_reverse(cpp):
    """Comparações × N (log-log) nos vetores ordenado e reverso, com as cotas n - 1 e 2(n - 1)."""
    algs = [FINAL, MERGE, BASIC]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
    for ax, dist in zip(axes, ["sorted", "reverse"]):
        ns = sorted(n for n in cpp[dist][FINAL] if n >= 10)
        for ref, label in ((lambda n: 2 * (n - 1), "2(n − 1)"), (lambda n: n - 1, "n − 1")):
            ax.plot(ns, [ref(n) for n in ns], color=MUTED, linewidth=1, linestyle=(0, (4, 3)), zorder=1)
            ax.annotate(label, (ns[-1], ref(ns[-1])), xytext=(14, 0), textcoords="offset points",
                        va="center", fontsize=8.5, color=MUTED)
        for alg in algs:
            line(ax, ns, [float(cpp[dist][alg][n]["comparacoes"]) for n in ns], alg)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(DIST_LABEL[dist], fontsize=11, loc="left")
        ax.set_xlabel("N (escala log)")
        ax.set_xlim(right=ns[-1] * 3)
        style_axes(ax)
    axes[0].set_ylabel("comparações (escala log)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    save(fig, "fig2_ordenado_reverso.png")


def annex_grid(py):
    """Grade completa do benchmark Python: tempo, comparações e movimentações × N (log-log)."""
    dists = ["random", "sorted", "reverse", "duplicates", "almost_sorted"]
    metrics = [("tempo_mediana_ms", "Tempo mediano (ms)"), ("comparacoes", "Comparações"),
               ("movimentacoes", "Movimentações")]
    fig, axes = plt.subplots(len(dists), 3, figsize=(16, 4 * len(dists)), squeeze=False)
    for r, dist in enumerate(dists):
        for c, (key, label) in enumerate(metrics):
            ax = axes[r][c]
            for alg, (color, marker) in GRID_STYLE.items():
                size_map = py[dist].get(alg, {})
                ns = [n for n in sorted(size_map) if float(size_map[n][key]) > 0]
                if not ns:
                    continue
                ax.plot(ns, [float(size_map[n][key]) for n in ns], color=color, marker=marker,
                        markersize=5, linewidth=2.4 if alg == FINAL else 1.5, label=alg)
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_title(f"{label} × N [{DIST_LABEL[dist]}]", fontsize=10, loc="left")
            ax.set_xlabel("N (escala log)")
            style_axes(ax)
        axes[r][0].legend(fontsize=8, frameon=False)
    fig.tight_layout()
    save(fig, "anexo_grade_python.png")


def main():
    cpp = load(os.path.join(ROOT, "cpp", "benchmark_results_cpp.csv"))
    py = load(os.path.join(ROOT, "python", "benchmark_results.csv"))
    fig1_normalized(cpp)
    fig2_sorted_reverse(cpp)
    fig3_time_cpp(cpp)
    annex_grid(py)


if __name__ == "__main__":
    main()
