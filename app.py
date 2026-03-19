import streamlit as st
import pandas as pd
import random

# ==========================================
# 1. ROTINAS LOGÍSTICAS (LÓGICA DO PROBLEMA)
# ==========================================

def gerar_cargas(num_cargas, max_peso, max_lucro):
    """Gera uma lista de cargas disponíveis para transporte."""
    cargas = []
    for i in range(num_cargas):
        cargas.append({
            'Selecionar': False, # Nova coluna para a seleção manual
            'Carga_ID': f'Carga {i+1}',
            'Peso (kg)': random.randint(100, max_peso),
            'Lucro do Frete (R$)': random.randint(500, max_lucro)
        })
    return pd.DataFrame(cargas)

def solucao_inicial_gulosa(df_cargas, capacidade_caminhao):
    """Algoritmo Guloso: Enche o caminhão priorizando as cargas mais rentáveis por kg."""
    df = df_cargas.copy()
    df['Rentabilidade (R$/kg)'] = df['Lucro do Frete (R$)'] / df['Peso (kg)']
    df = df.sort_values(by='Rentabilidade (R$/kg)', ascending=False)
    
    peso_acumulado = 0
    cargas_embarcadas = []
    
    for index, row in df.iterrows():
        if peso_acumulado + row['Peso (kg)'] <= capacidade_caminhao:
            peso_acumulado += row['Peso (kg)']
            cargas_embarcadas.append(row['Carga_ID'])
            
    return cargas_embarcadas

def avaliar_embarque(df_cargas, selecao, capacidade_caminhao):
    """Avalia se a combinação de cargas é possível (viável) ou não (inviável)."""
    df_selecionados = df_cargas[df_cargas['Carga_ID'].isin(selecao)]
    
    peso_total = int(df_selecionados['Peso (kg)'].sum())
    lucro_total = int(df_selecionados['Lucro do Frete (R$)'].sum())
    viavel = peso_total <= capacidade_caminhao
    
    return peso_total, lucro_total, viavel, df_selecionados

# ==========================================
# 2. INTERFACE GRÁFICA (STREAMLIT)
# ==========================================

st.set_page_config(page_title="Otimização Logística", page_icon="🚚", layout="wide")

st.title("🚚 Otimização Logística: Carregamento de Caminhão Baú")
st.markdown("Selecione as cargas para maximizar o lucro do frete sem exceder a capacidade do veículo.")

# Inicializa as variáveis na memória do Streamlit
if 'df_problema' not in st.session_state:
    st.session_state['df_problema'] = None
if 'solucao_algoritmo' not in st.session_state:
    st.session_state['solucao_algoritmo'] = None

# --- MENU LATERAL ---
with st.sidebar:
    st.header("⚙️ Configurações da Frota")
    num_cargas = st.number_input("Qtd. de Cargas no Pátio", min_value=5, max_value=100, value=15)
    capacidade = st.number_input("Capacidade do Caminhão (kg)", min_value=500, max_value=10000, value=3000, step=100)
    
    st.markdown("---")
    if st.button("🔄 1. Gerar Novas Cargas", use_container_width=True):
        st.session_state['df_problema'] = gerar_cargas(num_cargas, 1000, 5000)
        st.session_state['solucao_algoritmo'] = None

# --- ÁREA PRINCIPAL ---
if st.session_state['df_problema'] is not None:
    df = st.session_state['df_problema']
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.subheader("📦 Cargas Disponíveis no Pátio")
        st.caption("Marque a caixinha 'Embarcar?' para testar sua própria combinação.")
        
        # Cria uma tabela interativa onde apenas a coluna 'Selecionar' pode ser editada
        df_editado = st.data_editor(
            df,
            column_config={
                "Selecionar": st.column_config.CheckboxColumn(
                    "Embarcar?",
                    help="Selecione as cargas para testar manualmente",
                    default=False,
                )
            },
            disabled=["Carga_ID", "Peso (kg)", "Lucro do Frete (R$)"], # Bloqueia a edição dos dados reais
            hide_index=True,
            use_container_width=True
        )
        
    with col2:
        st.subheader("🚀 Avaliação e Planejamento")
        
        # Cria duas abas visuais para organizar a tela
        tab_manual, tab_algoritmo = st.tabs(["🖐️ Sua Seleção Manual", "🤖 Algoritmo Guloso"])
        
        # --- ABA 1: AVALIAÇÃO MANUAL ---
        with tab_manual:
            # Filtra apenas as cargas que o usuário marcou com "True" na tabela
            selecao_manual = df_editado[df_editado['Selecionar'] == True]['Carga_ID'].tolist()
            
            if len(selecao_manual) > 0:
                peso_man, lucro_man, viavel_man, _ = avaliar_embarque(df, selecao_manual, capacidade)
                
                if viavel_man:
                    st.success("✅ **STATUS: POSSÍVEL (VIÁVEL)** - O caminhão suporta!")
                else:
                    st.error("❌ **STATUS: IMPOSSÍVEL (INVIÁVEL)** - Excesso de peso!")
                    
                m1, m2 = st.columns(2)
                m1.metric("Lucro do seu Frete", f"R$ {lucro_man}")
                m2.metric("Peso Utilizado", f"{peso_man} kg / {capacidade} kg", 
                          delta=f"{capacidade - peso_man} kg livres", delta_color="normal")
            else:
                st.info("Nenhuma carga selecionada. Marque as caixinhas na tabela ao lado!")

        # --- ABA 2: ALGORITMO GULOSO ---
        with tab_algoritmo:
            if st.button("🧠 2. Gerar Solução (Algoritmo Guloso)"):
                st.session_state['solucao_algoritmo'] = solucao_inicial_gulosa(df, capacidade)
                
            if st.session_state['solucao_algoritmo'] is not None:
                selecao_algoritmo = st.session_state['solucao_algoritmo']
                peso_alg, lucro_alg, viavel_alg, df_sol_alg = avaliar_embarque(df, selecao_algoritmo, capacidade)
                
                if viavel_alg:
                    st.success("✅ **STATUS: POSSÍVEL (VIÁVEL)**")
                else:
                    st.error("❌ **STATUS: IMPOSSÍVEL (INVIÁVEL)**")
                
                m1, m2 = st.columns(2)
                m1.metric("Lucro do Algoritmo", f"R$ {lucro_alg}")
                m2.metric("Peso Utilizado", f"{peso_alg} kg / {capacidade} kg", 
                          delta=f"{capacidade - peso_alg} kg livres", delta_color="normal")
                
                with st.expander("Ver Manifesto de Carga do Algoritmo"):
                    st.dataframe(df_sol_alg[['Carga_ID', 'Peso (kg)', 'Lucro do Frete (R$)']], hide_index=True, use_container_width=True)
else:
    st.info("👈 Use o menu lateral para gerar as cargas do dia e iniciar o planejamento!")