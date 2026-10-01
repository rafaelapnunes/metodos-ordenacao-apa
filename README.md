# Mirror-Merge Sort: TP1 de Análise e Projetos de Algoritmos (APA)

Trabalho Prático 1 de Rafaela Pacheco. O repositório contém o algoritmo autoral **Mirror-Merge Sort** (Ordenação por Fusão Espelhada), sua suíte de testes, o framework de benchmark e o relatório técnico.

O Mirror-Merge Sort é uma adaptação declarada do Merge Sort: ordena a metade esquerda em um sentido e a direita no sentido oposto, formando uma sequência bitônica que é fundida por dois ponteiros vindos das extremidades, sem testes de fronteira por metade. A origem das técnicas (Sedgewick e Batcher), a análise assintótica e os resultados experimentais estão no relatório.

📄 **Relatório técnico:** [`relatorio.md`](relatorio.md)

---

## 📂 Estrutura de Arquivos

```text
.
├── relatorio.md                      # Relatório técnico (entregável, Opção A)
├── requirements.txt                  # Dependências Python (matplotlib)
├── Makefile                          # Automação de testes e benchmarks
│
├── python/
│   ├── student_template.py           # ★ Mirror-Merge Sort: função my_authorial_sort
│   ├── test_suite.py                 # Suíte de testes obrigatória (unittest)
│   ├── benchmark.py                  # Benchmark: tempo, comparações e movimentações × N
│   ├── benchmark_results.png         # Gráficos gerados pelo benchmark
│   ├── benchmark_results.csv         # Todas as medições
│   ├── benchmark_output.md           # Tabelas de tempo (média ± desvio-padrão)
│   ├── classical.py                  # Baselines do professor (Bubble, Selection, Insertion, Merge, Quick)
│   ├── authorial.py                  # Algoritmo de referência do professor (DPES), usado só como baseline
│   └── metrics.py                    # Utilitários de instrumentação do professor
│
└── cpp/                              # Pacote C++17 do professor (baselines e DPES)
```

> O Mirror-Merge Sort está implementado **apenas em Python**. A pasta `cpp/` é o pacote original fornecido pelo professor e não contém o algoritmo autoral.

---

## 🚀 Como Executar

Requisitos: Python 3.8+ e as dependências de `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 1. Suíte de testes

```bash
python python/test_suite.py
```

Executa os cenários obrigatórios do enunciado para o Mirror-Merge Sort e para os baselines: vetor vazio, unitário, ordenado, reverso, com repetições e aleatório, com N = 10, 10², 10³ e 10⁴. Também verifica a fórmula exata de comparações e movimentações deduzida no relatório e o contraexemplo de instabilidade.

Para rodar só os testes embutidos no template:

```bash
python python/student_template.py
```

### 2. Benchmark

```bash
python python/benchmark.py --trials 10 --plot python/benchmark_results.png --csv python/benchmark_results.csv --md python/benchmark_output.md
```

Mede, para N de 10 a 10⁴ e cinco distribuições (aleatória, ordenada, reversa, com repetições e quase ordenada), o tempo médio com desvio-padrão, as comparações e as movimentações. A semente padrão é 42 (`--seed`). Os algoritmos Θ(n²) param em N = 2500.

### 3. Usando o Makefile (Linux/macOS)

```bash
make install_python
make test_python
make benchmark_python
```

No Windows, onde `python3` costuma não existir, passe o interpretador: `make PYTHON=python test_python`.
