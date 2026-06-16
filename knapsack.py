import math
import random
from dataclasses import dataclass
from math import ceil
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

# ===========================================================================
# ALGORITMO GENÉTICO
# ===========================================================================

def _ag_cromossomo_aleatorio(prob: KnapsackProblem) -> List[int]:
    return [random.randint(0, 1) for _ in range(prob.n)]


def _ag_ajusta_restricao(sol: List[int], prob: KnapsackProblem) -> List[int]:
    """Remove itens aleatórios até o peso respeitar a capacidade.

    Melhoria sobre o método básico: prioriza remover itens com pior
    relação valor/peso (menor custo de remoção), tornando a correção
    mais inteligente do que uma remoção puramente aleatória.
    """
    s = sol.copy()
    peso = calcular_peso(s, prob)
    while peso > prob.capacidade:
        selecionados = [i for i in range(prob.n) if s[i] == 1]
        if not selecionados:
            break
        # Remove o item com pior relação valor/peso entre os selecionados
        pior = min(selecionados, key=lambda i: prob.valores[i] / prob.pesos[i])
        s[pior] = 0
        peso -= prob.pesos[pior]
    return s


def _ag_pop_inicial(prob: KnapsackProblem, tp: int) -> List[List[int]]:
    pop = []
    # Inclui a solução gulosa como primeiro indivíduo (diversidade + qualidade)
    pop.append(gerar_solucao_inicial(prob))
    for _ in range(tp - 1):
        c = _ag_cromossomo_aleatorio(prob)
        pop.append(_ag_ajusta_restricao(c, prob))
    return pop


def _ag_aptidao(pop: List[List[int]], prob: KnapsackProblem) -> List[float]:
    fit = [float(avalia(s, prob)) for s in pop]
    soma = sum(fit)
    if soma == 0:
        return [1.0 / len(pop)] * len(pop)
    return [f / soma for f in fit]


def _ag_roleta(fit: List[float]) -> int:
    ale = random.random()
    soma = 0.0
    for i, f in enumerate(fit):
        soma += f
        if soma >= ale:
            return i
    return len(fit) - 1


def _ag_ordena(
    pop: List[List[int]], fit: List[float]
) -> Tuple[List[List[int]], List[float]]:
    pares = sorted(zip(pop, fit), key=lambda x: x[1], reverse=True)
    pop_s, fit_s = zip(*pares)
    return list(pop_s), list(fit_s)


def _ag_cruzamento(
    p1: List[int], p2: List[int], ponto: int
) -> Tuple[List[int], List[int]]:
    d1 = p1[:ponto] + p2[ponto:]
    d2 = p2[:ponto] + p1[ponto:]
    return d1, d2


def _ag_mutacao(d: List[int]) -> List[int]:
    s = d.copy()
    pos = random.randrange(len(s))
    s[pos] = 1 - s[pos]
    return s


def _ag_nova_pop(
    pop: List[List[int]], desc: List[List[int]], tp: int, ig: float
) -> List[List[int]]:
    elite = ceil(ig * tp)
    return pop[:elite] + desc[: tp - elite]


def algoritmo_genetico(
    prob: KnapsackProblem,
    tp: int,
    ng: int,
    tc: float,
    tm: float,
    ig: float,
) -> Tuple[List[int], List[int], int, int, List[int]]:
    """Executa o Algoritmo Genético para o Problema da Mochila.

    Retorna: (solucao_inicial, solucao_final, valor_inicial, valor_final, historico)
    O histórico registra apenas melhorias, permitindo traçar a curva de convergência.
    """
    pop = _ag_pop_inicial(prob, tp)
    fit = _ag_aptidao(pop, prob)
    pop, fit = _ag_ordena(pop, fit)

    si = pop[0].copy()
    vi = avalia(si, prob)
    historico: List[int] = [vi]

    for _ in range(ng):
        desc: List[List[int]] = []
        corte = random.randint(1, prob.n - 1)

        while len(desc) < 2 * tp:
            p1 = pop[_ag_roleta(fit)]
            p2 = pop[_ag_roleta(fit)]

            if random.random() <= tc:
                d1, d2 = _ag_cruzamento(p1, p2, corte)
            else:
                d1, d2 = p1.copy(), p2.copy()

            if random.random() <= tm:
                d1 = _ag_mutacao(d1)
            if random.random() <= tm:
                d2 = _ag_mutacao(d2)

            desc.append(_ag_ajusta_restricao(d1, prob))
            desc.append(_ag_ajusta_restricao(d2, prob))

        fit_d = _ag_aptidao(desc, prob)
        desc, fit_d = _ag_ordena(desc, fit_d)
        pop = _ag_nova_pop(pop, desc, tp, ig)
        fit = _ag_aptidao(pop, prob)
        pop, fit = _ag_ordena(pop, fit)

        melhor_val = avalia(pop[0], prob)
        if melhor_val > historico[-1]:
            historico.append(melhor_val)

    sf = pop[0].copy()
    vf = avalia(sf, prob)
    return si, sf, vi, vf, historico


# ===========================================================================
# ANÁLISE COMPARATIVA (heurísticas clássicas)
# ===========================================================================

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