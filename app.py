"""
Interface Streamlit — Problema da Mochila (Knapsack Problem).

Organização por páginas:
  • Métodos Básicos    — execução de heurísticas e análise comparativa
  • Algoritmos Genéticos — módulo em desenvolvimento
  • Sobre              — descrição do problema e autoria
"""

import pandas as pd
import streamlit as st

from knapsack import (
    PROBLEMA_FIXO,
    KnapsackProblem,
    analise_comparativa,
    avaliar_solucao,
    calcular_peso,
    calcular_valor_bruto,
    gerar_problema_aleatorio,
    gerar_solucao_inicial,
    subida_de_encosta,
    subida_de_encosta_tentativas,
    tempera_simulada,
)

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Knapsack — Otimização",
    page_icon="🎒",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Session State
# ---------------------------------------------------------------------------

_DEFAULTS: dict = {
    "problema": None,         # KnapsackProblem atual
    "solucao_inicial": None,  # List[int] — vetor binário
    "valor_inicial": 0,       # int — valor avaliado da solução inicial
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ---------------------------------------------------------------------------
# Menu lateral
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🎒 Knapsack")
    st.markdown("**Otimização do Baú de Caminhão**")
    st.divider()
    pagina = st.radio(
        "Navegação",
        ["Métodos Básicos", "Algoritmos Genéticos", "Sobre"],
        label_visibility="collapsed",
    )

# ===========================================================================
# PÁGINA: Algoritmos Genéticos
# ===========================================================================

if pagina == "Algoritmos Genéticos":
    st.title("Algoritmos Genéticos")
    st.warning("Módulo em desenvolvimento")

# ===========================================================================
# PÁGINA: Sobre
# ===========================================================================

elif pagina == "Sobre":
    st.title("Sobre o Projeto")

    st.markdown("""
## Problema da Mochila (Knapsack Problem)

O **Problema da Mochila** é um dos problemas clássicos de **Otimização Combinatória**,
enquadrado na categoria NP-difícil. O objetivo é selecionar um subconjunto de itens —
cada um com um peso e um valor associados — de forma a **maximizar o valor total**
sem exceder a capacidade máxima da mochila.

### Aplicação: Carregamento de Baú de Caminhão

Neste projeto, o problema é modelado no contexto logístico de carregamento de um
**baú de caminhão**:

| Elemento do Knapsack | Elemento Logístico          |
|----------------------|-----------------------------|
| Itens                | Cargas disponíveis no pátio |
| Peso do item         | Peso da carga (kg)          |
| Valor do item        | Lucro do frete (R$)         |
| Capacidade da mochila| Capacidade do caminhão (kg) |

A solução é representada como um **vetor binário** de tamanho N, onde o bit `1`
indica que a carga foi selecionada e `0` que foi descartada.

### Heurísticas Implementadas

| Sigla | Nome completo                         |
|-------|---------------------------------------|
| SE    | Subida de Encosta (Hill Climbing)     |
| SET   | Subida de Encosta com Tentativas      |
| TE    | Têmpera Simulada (Simulated Annealing)|

---

## Discente(s)

- **Mateus Motta**
""")

# ===========================================================================
# PÁGINA: Métodos Básicos
# ===========================================================================

else:
    st.title("🔬 Métodos Básicos de Otimização")

    # -----------------------------------------------------------------------
    # Coluna esquerda — configuração do problema
    # -----------------------------------------------------------------------
    col_esq, col_dir = st.columns([1, 1.6], gap="large")

    with col_esq:
        st.subheader("⚙️ Configuração do Problema")

        tipo = st.radio(
            "Tipo de Execução",
            ["FIXO", "ALEATÓRIO"],
            horizontal=True,
        )

        n_val: int = PROBLEMA_FIXO.n
        if tipo == "ALEATÓRIO":
            n_val = st.number_input(
                "Tamanho do Problema (N — número de itens)",
                min_value=5,
                max_value=200,
                value=20,
                step=1,
            )

        if st.button("📦 Gerar Problema", use_container_width=True, type="primary"):
            if tipo == "FIXO":
                st.session_state.problema = PROBLEMA_FIXO
            else:
                st.session_state.problema = gerar_problema_aleatorio(int(n_val))
            # Invalida a solução anterior ao gerar novo problema
            st.session_state.solucao_inicial = None
            st.session_state.valor_inicial = 0

        # Exibe o problema gerado
        if st.session_state.problema is not None:
            prob: KnapsackProblem = st.session_state.problema

            st.divider()
            c1, c2 = st.columns(2)
            c1.metric("N (itens)", prob.n)
            c2.metric("Capacidade (kg)", prob.capacidade)

            df_itens = pd.DataFrame(
                {
                    "Item": [f"Item {i + 1}" for i in range(prob.n)],
                    "Peso": prob.pesos,
                    "Valor": prob.valores,
                }
            )
            st.dataframe(df_itens, hide_index=True, use_container_width=True, height=220)

    # -----------------------------------------------------------------------
    # Coluna direita — solução inicial e heurísticas
    # -----------------------------------------------------------------------
    with col_dir:
        if st.session_state.problema is None:
            st.info("👈 Gere um problema para começar.")
        else:
            prob: KnapsackProblem = st.session_state.problema

            # --- Solução Inicial ---
            st.subheader("🎯 Solução Inicial (Gulosa)")

            if st.button("Gerar Solução Inicial", use_container_width=True):
                sol_ini = gerar_solucao_inicial(prob)
                st.session_state.solucao_inicial = sol_ini
                st.session_state.valor_inicial = avaliar_solucao(sol_ini, prob)

            if st.session_state.solucao_inicial is not None:
                sol_ini = st.session_state.solucao_inicial
                val_ini = st.session_state.valor_inicial
                peso_ini = calcular_peso(sol_ini, prob)

                c1, c2, c3 = st.columns(3)
                c1.metric("Valor Total", val_ini)
                c2.metric("Peso Utilizado", f"{peso_ini} / {prob.capacidade}")
                c3.metric("Itens Selecionados", sum(sol_ini))

                with st.expander("Ver vetor binário da solução inicial"):
                    st.code(
                        "  ".join(str(b) for b in sol_ini),
                        language=None,
                    )
                    sel = [f"Item {i+1}" for i, b in enumerate(sol_ini) if b == 1]
                    st.caption("Itens selecionados: " + ", ".join(sel))

                st.divider()

                # --- Seleção de Heurística ---
                st.subheader("🧠 Heurística")

                heuristica = st.selectbox(
                    "Selecione a Heurística",
                    [
                        "Subida de Encosta",
                        "Subida de Encosta com Tentativas",
                        "Têmpera Simulada",
                        "Análise Comparativa",
                    ],
                )

                # Parâmetros condicionais
                tmax: int = prob.n
                ti: float = 100.0
                tf: float = 0.1
                fr: float = 0.8

                if heuristica == "Subida de Encosta com Tentativas":
                    tmax = st.number_input(
                        "TMAX (número máximo de tentativas / reinicializações)",
                        min_value=1,
                        value=prob.n,
                        step=1,
                    )

                elif heuristica == "Têmpera Simulada":
                    col_a, col_b, col_c = st.columns(3)
                    ti = col_a.number_input(
                        "TI — Temperatura Inicial",
                        min_value=1.0,
                        value=100.0,
                        step=10.0,
                    )
                    tf = col_b.number_input(
                        "TF — Temperatura Final",
                        min_value=0.001,
                        value=0.1,
                        step=0.01,
                        format="%.3f",
                    )
                    fr = col_c.number_input(
                        "FR — Fator de Resfriamento",
                        min_value=0.01,
                        max_value=0.999,
                        value=0.8,
                        step=0.01,
                        format="%.3f",
                    )

                # --- Botão Executar ---
                if st.button("▶️ Executar", use_container_width=True, type="primary"):
                    sol_ini = st.session_state.solucao_inicial
                    val_ini = st.session_state.valor_inicial

                    # ............. Análise Comparativa .............
                    if heuristica == "Análise Comparativa":
                        with st.spinner("Executando todas as configurações…"):
                            df_comp = analise_comparativa(sol_ini, prob)

                        st.subheader("📊 Análise Comparativa")
                        st.caption(f"Valor da Solução Inicial (gulosa): **{val_ini}**")

                        # Destaca a linha de maior ganho
                        st.dataframe(
                            df_comp,
                            hide_index=True,
                            use_container_width=True,
                            column_config={
                                "Ganho": st.column_config.NumberColumn(
                                    "Ganho",
                                    help="Ganho em relação à solução inicial",
                                    format="%+d",
                                ),
                                "Valor Final": st.column_config.NumberColumn(
                                    "Valor Final",
                                    format="%d",
                                ),
                            },
                        )

                        melhor = df_comp.loc[df_comp["Ganho"].idxmax()]
                        st.success(
                            f"Melhor resultado: **{melhor['Método']}** "
                            f"({melhor['Observação']}) — "
                            f"Valor Final = {melhor['Valor Final']}, "
                            f"Ganho = {melhor['Ganho']:+d}"
                        )

                    # ............. Heurísticas Individuais .............
                    else:
                        with st.spinner("Executando heurística…"):
                            if heuristica == "Subida de Encosta":
                                sol_f, val_f, hist = subida_de_encosta(sol_ini, prob)
                                label = "Subida de Encosta (SE)"

                            elif heuristica == "Subida de Encosta com Tentativas":
                                sol_f, val_f, hist = subida_de_encosta_tentativas(
                                    sol_ini, prob, int(tmax)
                                )
                                label = f"SET  (TMAX = {int(tmax)})"

                            else:  # Têmpera Simulada
                                sol_f, val_f, hist = tempera_simulada(
                                    sol_ini, prob, ti, tf, fr
                                )
                                label = f"Têmpera Simulada  (TI={ti}, TF={tf}, FR={fr})"

                        ganho = val_f - val_ini

                        st.subheader(f"📈 Resultado — {label}")

                        c1, c2, c3 = st.columns(3)
                        c1.metric(
                            "Valor Final",
                            val_f,
                            delta=f"{ganho:+d}",
                            delta_color="normal" if ganho >= 0 else "inverse",
                        )
                        c2.metric(
                            "Peso Final",
                            f"{calcular_peso(sol_f, prob)} / {prob.capacidade}",
                        )
                        c3.metric("Ganho vs Solução Inicial", f"{ganho:+d}")

                        with st.expander("Ver vetor binário da solução final"):
                            st.code(
                                "  ".join(str(b) for b in sol_f),
                                language=None,
                            )
                            sel_f = [f"Item {i+1}" for i, b in enumerate(sol_f) if b == 1]
                            st.caption("Itens selecionados: " + ", ".join(sel_f))

                        if len(hist) > 1:
                            st.subheader("Curva de Convergência")
                            st.line_chart(
                                pd.DataFrame({"Melhor Valor": hist}),
                                use_container_width=True,
                            )
                        else:
                            st.info("A heurística convergiu em um único passo — sem evolução a exibir.")
