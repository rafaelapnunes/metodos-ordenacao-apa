# Mirror-Merge Sort: TP1 de Análise e Projetos de Algoritmos (APA)

Trabalho Prático 1 de Rafaela Pacheco. O repositório contém o algoritmo autoral **Mirror-Merge Sort** (Ordenação por Fusão Espelhada), sua suíte de testes, o framework de benchmark e o relatório técnico.

O Mirror-Merge Sort é uma adaptação declarada do Merge Sort: ordena a metade esquerda em um sentido e a direita no sentido oposto, formando uma sequência bitônica que é fundida por dois ponteiros vindos das extremidades, sem testes de fronteira por metade. Antes de fundir, um atalho adaptativo testa se as metades já estão separadas, o que faz vetores ordenados e reversos usarem no máximo 2(n − 1) comparações. A origem das técnicas (Sedgewick e Batcher), a análise assintótica e os resultados experimentais estão no relatório.

📄 **Relatório técnico:** [`relatorio.md`](relatorio.md)

---

## 📂 Estrutura de Arquivos

```text
.
├── relatorio.md                      # Relatório técnico (entregável, Opção A)
├── requirements.txt                  # Dependências Python (matplotlib)
├── Makefile                          # Automação de testes, benchmarks e figuras
├── figuras/                          # Figuras do relatório (geradas por python/figures.py)
│
├── python/
│   ├── student_template.py           # ★ Mirror-Merge Sort: função my_authorial_sort
│   ├── test_suite.py                 # Suíte de testes obrigatória (unittest)
│   ├── benchmark.py                  # Benchmark: tempo, comparações e movimentações × N
│   ├── figures.py                    # Gera as figuras do relatório a partir dos CSVs
│   ├── benchmark_results.png         # Gráficos gerados pelo benchmark
│   ├── benchmark_results.csv         # Todas as medições
│   ├── benchmark_output.md           # Tabelas de tempo (mediana ± desvio-padrão)
│   ├── classical.py                  # Baselines do professor (Bubble, Selection, Insertion, Merge, Quick)
│   ├── authorial.py                  # Algoritmo de referência do professor (DPES), usado só como baseline
│   └── metrics.py                    # Utilitários de instrumentação do professor
│
└── cpp/
    ├── mirror_merge.hpp / .cpp       # ★ Mirror-Merge Sort em C++17 (com e sem atalho)
    ├── test_runner.cpp               # Suíte de testes em C++
    ├── benchmark.cpp                 # Benchmark em C++ (inclui a versão original v1 como referência)
    ├── benchmark_results_cpp.csv     # Todas as medições em C++
    ├── benchmark_output_cpp.md       # Tabelas de tempo, comparações e movimentações em C++
    └── classical.* / authorial.*     # Baselines e DPES do professor
```

`my_authorial_sort(arr)` usa o atalho adaptativo por padrão; `my_authorial_sort(arr, adaptive=False)` executa a versão sem atalho, usada nos testes de fórmula exata e no benchmark.

---

## 🚀 Como Executar

### Python

Requisitos: Python 3.8+ e as dependências de `requirements.txt`.

```bash
pip install -r requirements.txt
```

**Suíte de testes:**

```bash
python python/test_suite.py
```

Executa os cenários obrigatórios do enunciado para o Mirror-Merge Sort (com e sem atalho) e para os baselines: vetor vazio, unitário, ordenado, reverso, com repetições e aleatório, com N = 10, 10², 10³ e 10⁴. Também verifica as fórmulas de comparações e movimentações deduzidas no relatório, entradas que atingem exatamente o melhor e o pior caso e o contraexemplo de instabilidade.

Para rodar só os testes embutidos no template:

```bash
python python/student_template.py
```

**Benchmark:**

```bash
python python/benchmark.py --trials 10 --plot python/benchmark_results.png --csv python/benchmark_results.csv --md python/benchmark_output.md
```

Mede, para N de 10 a 10⁴ e cinco distribuições (aleatória, ordenada, reversa, com repetições e quase ordenada), o tempo mediano com desvio-padrão, as comparações e as movimentações. A semente padrão é 42 (`--seed`). Os algoritmos Θ(n²) param em N = 2500.

### C++

Requisitos: um compilador C++17 (g++) e `make`. No Windows, instale o MSYS2 (`winget install MSYS2.MSYS2`), abra o terminal "MSYS2 UCRT64", rode `pacman -S mingw-w64-ucrt-x86_64-gcc make` e adicione `C:\msys64\ucrt64\bin` e `C:\msys64\usr\bin` ao PATH.

```bash
make test_cpp            # compila e roda a suíte de testes em C++
make run_benchmark_cpp   # 100 repetições; gera cpp/benchmark_output_cpp.md e cpp/benchmark_results_cpp.csv
```

### Figuras do relatório

Depois de rodar os dois benchmarks:

```bash
python python/figures.py
```

Lê `cpp/benchmark_results_cpp.csv` e `python/benchmark_results.csv` e gera em `figuras/` as Figuras 1 a 3 e a grade do Anexo A.

### Usando o Makefile para Python (Linux/macOS)

```bash
make install_python
make test_python
make benchmark_python
make figures
```

No Windows, onde `python3` costuma não existir, passe o interpretador: `make PYTHON=python test_python`.
