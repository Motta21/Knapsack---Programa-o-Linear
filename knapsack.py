import math
import random
from dataclasses import dataclass
from typing import List, Tuple

import pandas as pd

@dataclass
class KnapsackProblem:
    n: int
    pesos: List[int]
    valores: List[int]
    capacidade: int

PROBLEMA_FIXO = KnapsackProblem(
    n=10,
    pesos  =[5,  4, 3, 8, 2,  7, 6, 3,  9, 1],
    valores=[10, 9, 5, 14, 4, 11, 8, 6, 13, 2],
    capacidade=20,
)

def gerar_problema_aleatorio(n: int) -> KnapsackProblem:
    pesos     = [random.randint(1, 20) for _ in range(n)]
    valores   = [random.randint(1, 50) for _ in range(n)]
    capacidade = max(1, int(sum(pesos) * 0.5))
    return KnapsackProblem(n=n, pesos=pesos, valores=valores, capacidade=capacidade)

def avalia(solucao: List[int], prob: KnapsackProblem) -> int:
    peso  = sum(prob.pesos[i]   for i in range(prob.n) if solucao[i] == 1)
    valor = sum(prob.valores[i] for i in range(prob.n) if solucao[i] == 1)
    return valor if peso <= prob.capacidade else 0

avaliar_solucao = avalia


def calcular_peso(solucao: List[int], prob: KnapsackProblem) -> int:
    return sum(prob.pesos[i] for i in range(prob.n) if solucao[i] == 1)

def gerar_solucao_inicial(prob: KnapsackProblem) -> List[int]:
    indices = sorted(
        range(prob.n),
        key=lambda i: prob.valores[i] / prob.pesos[i],
        reverse=True,
    )
    SUC = [0] * prob.n
    VS  = 0
    for i in indices:
        SUC[i] = 1
        VS += prob.pesos[i]
        if VS > prob.capacidade:
            SUC[i] = 0
            VS -= prob.pesos[i]
    return SUC

def sucessor(
    S: List[int],
    prob: KnapsackProblem,
) -> Tuple[List[int], int]:
    N   = prob.n
    SUC = S.copy()

    while True:
        p1 = random.randint(0, N - 1)
        if SUC[p1] == 1:
            SUC[p1] = 0
            break

    VS = sum(prob.pesos[i] for i in range(N) if SUC[i] == 1)

    indices = sorted(
        [i for i in range(N) if SUC[i] == 0 and i != p1],
        key=lambda i: prob.valores[i] / prob.pesos[i],
        reverse=True,
    )

    for i in indices:
        SUC[i] = 1
        VS += prob.pesos[i]
        if VS > prob.capacidade:
            SUC[i] = 0
            VS -= prob.pesos[i]

    SUC[p1] = 0

    VN = avalia(SUC, prob)
    return SUC, VN

def subida_encosta(
    SI: List[int],
    VI: int,
    prob: KnapsackProblem,
) -> Tuple[List[int], int, List[int]]:
    ATUAL    = SI.copy()
    VA       = VI
    historico: List[int] = [VA]

    while True:
        NOVO, VN = sucessor(ATUAL, prob)
        if VN > VA:
            ATUAL = NOVO
            VA    = VN
            historico.append(VA)
        else:
            return ATUAL, VA, historico
        
def subida_encosta_tentativas(
    SI: List[int],
    VI: int,
    prob: KnapsackProblem,
    TMAX: int,
) -> Tuple[List[int], int, List[int]]:
    ATUAL    = SI.copy()
    VA       = VI
    T        = 0
    historico: List[int] = [VA]

    while T < TMAX:
        NOVO, VN = sucessor(ATUAL, prob)
        if VN > VA:
            ATUAL = NOVO
            VA    = VN
            T     = 0
            historico.append(VA)
        else:
            T += 1

    return ATUAL, VA, historico

def tempera_simulada(
    SI: List[int],
    VI: int,
    prob: KnapsackProblem,
    TI: float,
    TF: float,
    FR: float,
) -> Tuple[List[int], int, List[int]]:
    ATUAL    = SI.copy()
    VA       = VI
    MELHOR   = ATUAL.copy()
    VM       = VA
    T        = float(TI)
    historico: List[int] = [VM]

    while T >= TF:
        NOVO, VN = sucessor(ATUAL, prob)

        if VN > VA:
            ATUAL = NOVO
            VA    = VN
            if VA > VM:
                MELHOR = ATUAL.copy()
                VM     = VA
                historico.append(VM)
        else:
            D   = VA - VN
            AUX = math.exp(-D / T) if T > 0 else 0.0
            ALE = random.random()
            if ALE < AUX:
                ATUAL = NOVO
                VA    = VN

        T *= FR

    return MELHOR, VM, historico

def analise_comparativa(
    SI: List[int],
    VI: int,
    prob: KnapsackProblem,
) -> pd.DataFrame:
    N = prob.n

    configs = [
        ("SE",  "—",
         lambda: subida_encosta(SI, VI, prob)),
        ("SET", f"TMAX = N  ({N})",
         lambda: subida_encosta_tentativas(SI, VI, prob, N)),
        ("SET", f"TMAX = 2×N  ({2 * N})",
         lambda: subida_encosta_tentativas(SI, VI, prob, 2 * N)),
        ("SET", f"TMAX = N/2  ({max(1, N // 2)})",
         lambda: subida_encosta_tentativas(SI, VI, prob, max(1, N // 2))),
        ("TE",  "TI=100,  TF=0.1,  FR=0.8",
         lambda: tempera_simulada(SI, VI, prob, 100,  0.1,  0.8)),
        ("TE",  "TI=200,  TF=0.1,  FR=0.8",
         lambda: tempera_simulada(SI, VI, prob, 200,  0.1,  0.8)),
        ("TE",  "TI=500,  TF=0.1,  FR=0.8",
         lambda: tempera_simulada(SI, VI, prob, 500,  0.1,  0.8)),
        ("TE",  "TI=200,  TF=0.1,  FR=0.9",
         lambda: tempera_simulada(SI, VI, prob, 200,  0.1,  0.9)),
        ("TE",  "TI=500,  TF=0.1,  FR=0.9",
         lambda: tempera_simulada(SI, VI, prob, 500,  0.1,  0.9)),
        ("TE",  "TI=200,  TF=0.01, FR=0.9",
         lambda: tempera_simulada(SI, VI, prob, 200,  0.01, 0.9)),
        ("TE",  "TI=500,  TF=0.01, FR=0.9",
         lambda: tempera_simulada(SI, VI, prob, 500,  0.01, 0.9)),
    ]

    rows = []
    for metodo, obs, fn in configs:
        _, val, _ = fn()
        ganho = val - VI
        rows.append({
            "Método":      metodo,
            "Observação":  obs,
            "Valor Final": val,
            "Ganho":       ganho,
        })

    return pd.DataFrame(rows)