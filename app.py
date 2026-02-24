import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Simulador IRRF + PSS",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Simulador de Descontos")
st.caption("Servidor Público Federal — IRRF + PSS")

# ===============================
# SIDEBAR
# ===============================
st.sidebar.header("⚙️ Parâmetros")

salario = st.sidebar.number_input(
    "Salário Bruto (R$)",
    min_value=0.0,
    value=21576.86,
    step=100.0
)

dependentes = st.sidebar.number_input(
    "Número de Dependentes",
    min_value=0,
    value=0,
    step=1
)

DEDUCAO_DEPENDENTE = 189.59

# ===============================
# FUNÇÕES
# ===============================
def calcular_pss_detalhado(salario_bruto):

    faixas = [
        (1621.00, 0.075),
        (2902.84, 0.09),
        (4354.27, 0.12),
        (8475.55, 0.14),
        (14514.30, 0.145),
        (29028.57, 0.165),
        (float("inf"), 0.19),
    ]

    pss_total = 0
    limite_anterior = 0
    detalhes = []

    for limite, aliquota in faixas:
        if salario_bruto > limite_anterior:
            base = min(salario_bruto, limite) - limite_anterior
            valor = base * aliquota
            pss_total += valor

            detalhes.append({
                "Faixa até (R$)": limite,
                "Base na faixa (R$)": round(base, 2),
                "Alíquota": f"{aliquota*100:.1f}%",
                "Contribuição (R$)": round(valor, 2)
            })

            limite_anterior = limite
        else:
            break

    return round(pss_total, 2), pd.DataFrame(detalhes)


def calcular_irrf(base_calculo):

    tabela_ir = [
        (2428.80, 0.0, 0.0),
        (2826.65, 0.075, 182.16),
        (3751.05, 0.15, 394.16),
        (4664.68, 0.225, 675.49),
        (float("inf"), 0.275, 908.73),
    ]

    for limite, aliquota, deducao in tabela_ir:
        if base_calculo <= limite:
            imposto = base_calculo * aliquota - deducao
            return round(max(imposto, 0), 2)

    return 0.0


# ===============================
# CÁLCULO
# ===============================
pss_total, df_pss = calcular_pss_detalhado(salario)
base_ir = salario - pss_total - (dependentes * DEDUCAO_DEPENDENTE)
irrf = calcular_irrf(base_ir)
liquido = salario - pss_total - irrf

# ===============================
# MÉTRICAS
# ===============================
col1, col2, col3, col4 = st.columns(4)

col1.metric("💼 Bruto", f"R$ {salario:,.2f}")
col2.metric("🏛️ PSS", f"R$ {pss_total:,.2f}")
col3.metric("🧾 IRRF", f"R$ {irrf:,.2f}")
col4.metric("💵 Líquido", f"R$ {liquido:,.2f}")

st.divider()

# ===============================
# GRÁFICO INTERATIVO
# ===============================
dados = pd.DataFrame({
    "Categoria": ["PSS", "IRRF", "Líquido"],
    "Valor": [pss_total, irrf, liquido]
})

fig = px.pie(
    dados,
    names="Categoria",
    values="Valor",
    hole=0.5,
)

fig.update_layout(
    title="Distribuição do Salário",
    legend_title="Componentes"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ===============================
# TABELA
# ===============================
st.subheader("📑 Detalhamento do PSS")
st.dataframe(df_pss, use_container_width=True)

st.success(f"Salário líquido estimado: R$ {liquido:,.2f}")
