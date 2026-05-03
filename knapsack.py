"""
Módulo de lógica do Problema da Mochila (Knapsack Problem).

Contém a estrutura do problema, geração de instâncias, avaliação de soluções
e os algoritmos heurísticos: Subida de Encosta (SE), Subida de Encosta com
Tentativas (SET) e Têmpera Simulada (TE).
"""

import math
import random
from dataclasses import dataclass
from typing import List, Tuple

import pandas as pd


# ---------------------------------------------------------------------------
# Estrutura de Dados
# ---------------------------------------------------------------------------

@dataclass
class KnapsackProblem:
    """Representa uma instância do Problema da Mochila."""
    n: int
    pesos: List[int]
    valores: List[int]
    capacidade: int


# ---------------------------------------------------------------------------
# Instância Fixa (FIXO)
# ---------------------------------------------------------------------------

PROBLEMA_FIXO = KnapsackProblem(
    n=10,
    pesos=[5, 4, 3, 8, 2, 7, 6, 3, 9, 1],
    valores=[10, 9, 5, 14, 4, 11, 8, 6, 13, 2],
    capacidade=20,
)
"""
Configuração fixa para fins didáticos:
  Itens : [1..10]
  Pesos : [5, 4, 3, 8, 2, 7, 6, 3, 9, 1]
  Valores: [10, 9, 5, 14, 4, 11, 8, 6, 13, 2]
  Capacidade: 20
"""


# ---------------------------------------------------------------------------
# Geração de Problemas
# ---------------------------------------------------------------------------

def gerar_problema_aleatorio(n: int) -> KnapsackProblem:
    """Gera uma instância aleatória com *n* itens.

    A capacidade é fixada em 50% da soma total dos pesos, garantindo que a
    solução ótima selecione aproximadamente metade dos itens.
    """
    pesos = [random.randint(1, 20) for _ in range(n)]
    valores = [random.randint(1, 50) for _ in range(n)]
    capacidade = max(1, int(sum(pesos) * 0.5))
    return KnapsackProblem(n=n, pesos=pesos, valores=valores, capacidade=capacidade)


# ---------------------------------------------------------------------------
# Avaliação
# ---------------------------------------------------------------------------

def avaliar_solucao(solucao: List[int], problema: KnapsackProblem) -> int:
    """Avalia o valor total de uma solução binária.

    Retorna 0 para soluções inviáveis (peso excede a capacidade).
    """
    peso = sum(problema.pesos[i] for i in range(problema.n) if solucao[i] == 1)
    valor = sum(problema.valores[i] for i in range(problema.n) if solucao[i] == 1)
    return valor if peso <= problema.capacidade else 0


def calcular_peso(solucao: List[int], problema: KnapsackProblem) -> int:
    """Retorna o peso total de uma solução (independente de viabilidade)."""
    return sum(problema.pesos[i] for i in range(problema.n) if solucao[i] == 1)


def calcular_valor_bruto(solucao: List[int], problema: KnapsackProblem) -> int:
    """Retorna o valor total de uma solução sem verificar viabilidade."""
    return sum(problema.valores[i] for i in range(problema.n) if solucao[i] == 1)


# ---------------------------------------------------------------------------
# Solução Inicial (Gulosa)
# ---------------------------------------------------------------------------

def gerar_solucao_inicial(problema: KnapsackProblem) -> List[int]:
    """Gera uma solução inicial usando heurística gulosa.

    Ordena os itens pela razão valor/peso (rentabilidade) e os insere na
    mochila enquanto houver capacidade disponível.
    """
    indices = sorted(
        range(problema.n),
        key=lambda i: problema.valores[i] / problema.pesos[i],
        reverse=True,
    )
    solucao = [0] * problema.n
    peso_acum = 0
    for i in indices:
        if peso_acum + problema.pesos[i] <= problema.capacidade:
            solucao[i] = 1
            peso_acum += problema.pesos[i]
    return solucao


# ---------------------------------------------------------------------------
# Operador de Vizinhança
# ---------------------------------------------------------------------------

def _get_vizinho(solucao: List[int], idx: int) -> List[int]:
    """Retorna um vizinho obtido invertendo o bit *idx* da solução."""
    vizinho = solucao.copy()
    vizinho[idx] ^= 1
    return vizinho


# ---------------------------------------------------------------------------
# Heurística 1 — Subida de Encosta (SE)
# ---------------------------------------------------------------------------

def subida_de_encosta(
    solucao_inicial: List[int],
    problema: KnapsackProblem,
) -> Tuple[List[int], int, List[int]]:
    """Algoritmo Subida de Encosta (Best-Improvement Hill Climbing).

    Em cada passo, avalia todos os N vizinhos por inversão de bit e move-se
    para o melhor, encerrando ao atingir um ótimo local.

    Returns:
        (melhor_solucao, melhor_valor, historico_de_valores)
    """
    atual = solucao_inicial.copy()
    valor_atual = avaliar_solucao(atual, problema)
    historico: List[int] = [valor_atual]

    while True:
        melhor_vizinho = None
        melhor_valor = valor_atual

        for i in range(problema.n):
            vizinho = _get_vizinho(atual, i)
            val = avaliar_solucao(vizinho, problema)
            if val > melhor_valor:
                melhor_vizinho = vizinho
                melhor_valor = val

        if melhor_vizinho is None:
            break

        atual = melhor_vizinho
        valor_atual = melhor_valor
        historico.append(valor_atual)

    return atual, valor_atual, historico


# ---------------------------------------------------------------------------
# Heurística 2 — Subida de Encosta com Tentativas (SET)
# ---------------------------------------------------------------------------

def subida_de_encosta_tentativas(
    solucao_inicial: List[int],
    problema: KnapsackProblem,
    tmax: int,
) -> Tuple[List[int], int, List[int]]:
    """Subida de Encosta com *tmax* reinicializações aleatórias (SET).

    Executa a SE a partir da solução inicial e de (tmax - 1) soluções
    geradas aleatoriamente, mantendo a melhor solução global encontrada.

    Returns:
        (melhor_solucao, melhor_valor, historico_de_valores)
    """
    melhor_sol = solucao_inicial.copy()
    melhor_val = avaliar_solucao(melhor_sol, problema)
    historico: List[int] = [melhor_val]

    # Primeira tentativa a partir da solução inicial
    sol, val, hist = subida_de_encosta(solucao_inicial, problema)
    historico.extend(hist[1:])
    if val > melhor_val:
        melhor_sol, melhor_val = sol, val

    # Tentativas com reinicializações aleatórias
    for _ in range(tmax - 1):
        rand_sol = [random.randint(0, 1) for _ in range(problema.n)]
        sol, val, hist = subida_de_encosta(rand_sol, problema)
        historico.extend(hist)
        if val > melhor_val:
            melhor_sol, melhor_val = sol, val
        historico.append(melhor_val)

    return melhor_sol, melhor_val, historico


# ---------------------------------------------------------------------------
# Heurística 3 — Têmpera Simulada (TE)
# ---------------------------------------------------------------------------

def tempera_simulada(
    solucao_inicial: List[int],
    problema: KnapsackProblem,
    ti: float,
    tf: float,
    fr: float,
) -> Tuple[List[int], int, List[int]]:
    """Algoritmo Têmpera Simulada (Simulated Annealing).

    A temperatura *T* começa em *ti* e é multiplicada por *fr* a cada passo,
    encerrando quando T < *tf*. Movimentos piores são aceitos com probabilidade
    exp(delta / T), onde delta = valor_vizinho - valor_atual.

    Returns:
        (melhor_solucao, melhor_valor, historico_de_melhores_valores)
    """
    atual = solucao_inicial.copy()
    valor_atual = avaliar_solucao(atual, problema)
    melhor = atual.copy()
    melhor_val = valor_atual
    historico: List[int] = [valor_atual]

    T = float(ti)
    while T > tf:
        idx = random.randint(0, problema.n - 1)
        vizinho = _get_vizinho(atual, idx)
        valor_vizinho = avaliar_solucao(vizinho, problema)
        delta = valor_vizinho - valor_atual

        if delta > 0 or (T > 0 and random.random() < math.exp(delta / T)):
            atual = vizinho
            valor_atual = valor_vizinho
            if valor_atual > melhor_val:
                melhor = atual.copy()
                melhor_val = valor_atual

        historico.append(melhor_val)
        T *= fr

    return melhor, melhor_val, historico


# ---------------------------------------------------------------------------
# Análise Comparativa
# ---------------------------------------------------------------------------

def analise_comparativa(
    solucao_inicial: List[int],
    problema: KnapsackProblem,
) -> pd.DataFrame:
    """Executa todas as configurações predefinidas e consolida os resultados.

    Returns:
        DataFrame com colunas ["Método", "Observação", "Valor Final", "Ganho"].
    """
    N = problema.n
    valor_ini = avaliar_solucao(solucao_inicial, problema)

    configs = [
        ("SE",  "—",
         lambda: subida_de_encosta(solucao_inicial, problema)),
        ("SET", "—",
         lambda: subida_de_encosta_tentativas(solucao_inicial, problema, 1)),
        ("SET", f"TMAX = 2×N  ({2 * N})",
         lambda: subida_de_encosta_tentativas(solucao_inicial, problema, 2 * N)),
        ("SET", f"TMAX = N/2  ({max(1, N // 2)})",
         lambda: subida_de_encosta_tentativas(solucao_inicial, problema, max(1, N // 2))),
        ("SET", f"TMAX = N  ({N})",
         lambda: subida_de_encosta_tentativas(solucao_inicial, problema, N)),
        ("TE",  "TI=100,  TF=0.1,  FR=0.8",
         lambda: tempera_simulada(solucao_inicial, problema, 100,  0.1,  0.8)),
        ("TE",  "TI=200,  TF=0.1,  FR=0.8",
         lambda: tempera_simulada(solucao_inicial, problema, 200,  0.1,  0.8)),
        ("TE",  "TI=500,  TF=0.1,  FR=0.8",
         lambda: tempera_simulada(solucao_inicial, problema, 500,  0.1,  0.8)),
        ("TE",  "TI=200,  TF=0.1,  FR=0.9",
         lambda: tempera_simulada(solucao_inicial, problema, 200,  0.1,  0.9)),
        ("TE",  "TI=500,  TF=0.1,  FR=0.9",
         lambda: tempera_simulada(solucao_inicial, problema, 500,  0.1,  0.9)),
        ("TE",  "TI=200,  TF=0.01, FR=0.9",
         lambda: tempera_simulada(solucao_inicial, problema, 200,  0.01, 0.9)),
        ("TE",  "TI=500,  TF=0.01, FR=0.9",
         lambda: tempera_simulada(solucao_inicial, problema, 500,  0.01, 0.9)),
    ]

    rows = []
    for metodo, obs, fn in configs:
        _, val, _ = fn()
        ganho = val - valor_ini
        rows.append({
            "Método": metodo,
            "Observação": obs,
            "Valor Final": val,
            "Ganho": ganho,
        })

    return pd.DataFrame(rows)
