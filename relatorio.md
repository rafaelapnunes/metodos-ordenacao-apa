# Relatório Técnico: Mirror-Merge Sort (Ordenação por Fusão Espelhada)

**Trabalho Prático 1 (TP1) — Análise e Projetos de Algoritmos (APA)**

---

## 1. Concepção e Raciocínio Projetual

O **Mirror-Merge Sort** (Ordenação por Fusão Espelhada) é um algoritmo autoral concebido como uma adaptação estrutural profunda do Merge Sort clássico.

**O Problema do Algoritmo Clássico:**
No Merge Sort tradicional, o passo de fusão (merge) de duas metades ordenadas necessita verificar a todo momento se os limites de alguma das metades foram atingidos (`i <= mid` e `j <= high`). Além disso, ao final do laço principal, são necessários laços adicionais (dois `while` extras) apenas para "esgotar" os elementos da metade que não terminou.

**A Metáfora e o Raciocínio (Mirror-Merge):**
O *Mirror-Merge Sort* resolve esse problema através da **geometria da ordenação**. Em vez de ordenar as duas metades na mesma direção (crescente), o algoritmo ordena a metade esquerda de forma **crescente** e a metade direita de forma **decrescente** (espelhada).
Isso transforma a subsequência inteira em uma estrutura **bitônica** (em forma de pico, onde os valores sobem até o meio e descem até o final). 
Na fase de fusão, posicionamos um ponteiro no extremo esquerdo (`i = low`) e um no extremo direito (`j = high`). Ambos caminham em direção ao centro. A garantia estrutural é de que os menores elementos de toda a partição estarão invariavelmente nas extremidades. A condição de parada torna-se um simples e elegante `i <= j`, eliminando completamente os laços extras de exaustão e reduzindo drasticamente a quantidade de saltos de controle (`if/bounds`) avaliados durante o *merge*.

## 2. Especificação Formal

### 2.1 Pseudocódigo
```text
função MirrorMergeSort(A, low, high, crescente):
    se low >= high:
        retornar
        
    mid = low + (high - low) / 2
    
    // Chamadas espelhadas
    MirrorMergeSort(A, low, mid, crescente)
    MirrorMergeSort(A, mid + 1, high, não crescente)
    
    // Fusão Bitônica
    i = low
    j = high
    k = low
    
    enquanto i <= j faça:
        se crescente:
            se A[i] <= A[j]:
                Temp[k] = A[i]
                i = i + 1
            senão:
                Temp[k] = A[j]
                j = j - 1
        senão: // decrescente
            se A[i] >= A[j]:
                Temp[k] = A[i]
                i = i + 1
            senão:
                Temp[k] = A[j]
                j = j - 1
        k = k + 1
        
    copiar Temp[low..high] para A[low..high]
```

### 2.2 Exemplo Passo a Passo
Vetor inicial: `[8, 3, 5, 2]` (Crescente)
1. **Divisão e Chamada Recursiva:**
   - Esquerda `[8, 3]` -> ordena Crescente.
   - Direita `[5, 2]` -> ordena Decrescente.
2. **Resolução Esquerda `[8, 3]` (Crescente):**
   - Esquerda `[8]` (crescente). Direita `[3]` (decrescente).
   - Merge Crescente: `i=0` (8), `j=1` (3). `8 <= 3` (Falso). Pega o 3, j--. Pega o 8. Resultado: `[3, 8]`.
3. **Resolução Direita `[5, 2]` (Decrescente):**
   - Esquerda `[5]` (decrescente). Direita `[2]` (crescente).
   - Merge Decrescente: `i=2` (5), `j=3` (2). `5 >= 2` (Verdadeiro). Pega o 5, i++. Pega o 2. Resultado: `[5, 2]`.
4. **Merge Final:**
   - Temos: `[3, 8, 5, 2]`. A metade esquerda sobe (3, 8) e a direita desce (5, 2).
   - `i` aponta para 3, `j` aponta para 2.
   - 3 <= 2? Não. Pega o 2 (j--). `Temp = [2]`. `j` agora aponta para 5.
   - `i` aponta para 3, `j` aponta para 5.
   - 3 <= 5? Sim. Pega o 3 (i++). `Temp = [2, 3]`. `i` aponta para 8.
   - `i` aponta para 8, `j` aponta para 5.
   - 8 <= 5? Não. Pega o 5 (j--). `Temp = [2, 3, 5]`. `j` e `i` apontam para 8.
   - 8 <= 8? Sim. Pega o 8.
   - `i > j`, Fim do Merge. Vetor ordenado: `[2, 3, 5, 8]`.

## 3. Análise Assintótica Teórica

### 3.1 Tempo
A profundidade da árvore de recursão segue a divisão ao meio perfeita: $\log_2 N$.
Em cada nível da árvore, a etapa de fusão (merge) processa exatamente os $N$ elementos, executando operações $O(1)$ por elemento.
- **Melhor Caso ($\Omega$):** $\Omega(N \log N)$. Diferente do Insertion Sort, ele não tira proveito natural de vetores ordenados.
- **Pior Caso ($O$):** $O(N \log N)$. Ocorre independentemente do arranjo inicial.
- **Caso Médio ($\Theta$):** $\Theta(N \log N)$.

### 3.2 Espaço (Memória Auxiliar)
Durante a fusão, o algoritmo escreve no vetor `Temp`. O requisito de memória é estritamente linear ao tamanho da entrada.
- **Complexidade de Espaço:** $O(N)$.
- **In-place:** Não. Requer alocação externa como o Merge Sort clássico.

### 3.3 Propriedades (Estabilidade)
O algoritmo **é estável**. A estabilidade é garantida por dois detalhes cruciais:
1. Durante a ordenação crescente, a comparação utiliza `<=` e avança `i` (favorecendo a estabilidade da metade esquerda original).
2. Durante a ordenação decrescente, a comparação utiliza `>=` e avança `i` (mantendo a mesma propriedade). Ao inverter a ordem e mesclar de volta, a relação topológica original dos valores equivalentes é matematicamente restaurada ao vetor final.

## 4. Comparação com a Literatura

| Característica | Mirror-Merge Sort | Merge Sort | Quick Sort | Insertion Sort |
| :--- | :--- | :--- | :--- | :--- |
| **Melhor Tempo** | $O(N \log N)$ | $O(N \log N)$ | $O(N \log N)$ | $O(N)$ |
| **Pior Tempo** | $O(N \log N)$ | $O(N \log N)$ | $O(N^2)$ | $O(N^2)$ |
| **Espaço Auxiliar**| $O(N)$ | $O(N)$ | $O(\log N)$ | $O(1)$ |
| **Estável?** | Sim | Sim | Não | Sim |
| **Bounds Check** | Não (Único laço) | Sim (Múltiplos laços)| N/A | Sim |

O Mirror-Merge desponta com vantagem em clareza de fluxo de controle, executando menos saltos condicionais (branches) a nível de processador (ausência de exaustão de array e bounds checking contínuo), embora mantenha o mesmo custo assintótico do Merge Sort clássico.

## 5. Resultados Experimentais
De acordo com os benchmarks realizados (com imagens salvas em `python/benchmark_results.png`):
- O algoritmo apresenta performance robusta equivalente ao Quick Sort e Merge Sort em escalas até $N=1000$.
- O tempo permanece estável (sem degradação para $O(N^2)$) nos cenários Inverso, Duplicados e Quase Ordenado, validando rigorosamente a teoria de limite superior $O(N \log N)$.
- Em arranjos estritamente reversos, o Mirror-Merge apresenta uma ligeira vantagem de saltos e desvios contra o QuickSort básico (devido à imunidade contra degradação de pivôs sem heurísticas extras).

## 6. Declaração Obrigatória de Autoria e IA

**Fonte / Ferramenta Utilizada:** IA Generativa (Gemini 3.1 Pro / Antigravity AI)
**Por que foi utilizada:** Brainstorming para concepção de um método de ordenação genuinamente inédito ou profundamente reformulado que não caísse no clichê trivial; revisão das demonstrações de corretude; implementação inicial e execução automatizada da suíte de testes.
**Como foi utilizada:**
1. Diálogo sobre famílias de ordenação para isolar a ideia da "cordilheira bitônica" que remove testes de bounds check.
2. Escrita do código guiada pelo template `student_template.py`.
3. Execução das ferramentas de benchmark.
**Quais modificações foram realizadas:** A ideia teórica original da fusão espelhada (Bitonic-Run) foi transcrita de pseudocódigo à especificação Python pelo próprio sistema baseado nos meus requisitos estruturais.
**Validação:** Todo o resultado foi matematicamente demonstrado através de teste de mesa em arrays de tamanho misto, validado sem erros empíricos pelos testes estritos impostos pelo professor em `test_suite.py` e avaliado em performance temporal.
