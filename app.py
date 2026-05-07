import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Painel dos Sensores",
    page_icon="☀️",
    layout="wide"
)

# ============================================================
# ESTILO
# ============================================================
st.markdown("""
<style>
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 1.2rem;
}
h1, h2, h3 {
    color: #1f2937;
}
div[data-testid="stMetric"] {
    background-color: #f8fafc;
    border: 1px solid #e5e7eb;
    padding: 12px;
    border-radius: 14px;
}
</style>
""", unsafe_allow_html=True)

st.title("☀️ Painel Didático dos Sensores")
st.caption("Visualização dos sensores J8, J11 e J9 em Lux, W/m² e W/m² calibrado")

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================
@st.cache_data
def carregar_dados_excel(fonte):
    return pd.read_excel(fonte, sheet_name="Sheet1")

def validar_colunas(df, colunas_necessarias):
    faltantes = [c for c in colunas_necessarias if c not in df.columns]
    return faltantes

# ============================================================
# ENTRADA DO ARQUIVO
# ============================================================
st.sidebar.header("Configurações")

uploaded_file = st.sidebar.file_uploader(
    "Carregue o arquivo Excel",
    type=["xlsx", "xls"]
)

usar_arquivo_local = st.sidebar.checkbox("Usar caminho local fixo", value=False)
caminho_local = r"/mnt/data/DadosConsolidadosLUX3sensores_Wm2_calibrado.xlsx"

if uploaded_file is not None:
    df = carregar_dados_excel(uploaded_file)
elif usar_arquivo_local:
    df = carregar_dados_excel(caminho_local)
else:
    st.info("Carregue o arquivo Excel na barra lateral ou marque a opção de caminho local.")
    st.stop()

# ============================================================
# PREPARAÇÃO DOS DADOS
# ============================================================
colunas_esperadas = [
    "timestamp",
    "J8_lux", "J11_lux", "J9_lux",
    "batt_V",
    "J8_Wm2", "J11_Wm2", "J9_Wm2",
    "interval_duration_hours",
    "J8_Wm2_calibrado", "J11_Wm2_calibrado", "J9_Wm2_calibrado"
]

faltantes = validar_colunas(df, colunas_esperadas)
if faltantes:
    st.error("O arquivo não contém todas as colunas esperadas.")
    st.write("Colunas faltantes:", faltantes)
    st.stop()

df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)

colunas_numericas = [
    "J8_lux", "J11_lux", "J9_lux",
    "batt_V",
    "J8_Wm2", "J11_Wm2", "J9_Wm2",
    "interval_duration_hours",
    "J8_Wm2_calibrado", "J11_Wm2_calibrado", "J9_Wm2_calibrado"
]

for c in colunas_numericas:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# Se interval_duration_hours vier vazio, tenta reconstruir
if df["interval_duration_hours"].isna().all():
    df["next_timestamp"] = df["timestamp"].shift(-1)
    df["interval_duration_hours"] = (
        (df["next_timestamp"] - df["timestamp"]).dt.total_seconds() / 3600.0
    )
    df["interval_duration_hours"] = df["interval_duration_hours"].fillna(0)

df["data"] = df["timestamp"].dt.date
df["hora"] = df["timestamp"].dt.hour

# ============================================================
# FILTROS
# ============================================================
st.sidebar.subheader("Filtros")

data_min = df["timestamp"].min().date()
data_max = df["timestamp"].max().date()

intervalo = st.sidebar.date_input(
    "Período",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max
)

if isinstance(intervalo, tuple) and len(intervalo) == 2:
    data_ini, data_fim = intervalo
else:
    data_ini, data_fim = data_min, data_max

sensores_escolhidos = st.sidebar.multiselect(
    "Sensores",
    options=["J8", "J11", "J9"],
    default=["J8", "J11", "J9"]
)

grandeza = st.sidebar.radio(
    "Grandeza principal",
    ["Lux", "W/m²", "W/m² calibrado"],
    index=2
)

limiar = st.sidebar.number_input(
    "Limiar para brilho solar (W/m²)",
    min_value=0.0,
    value=120.0,
    step=1.0
)

mask = (df["timestamp"].dt.date >= data_ini) & (df["timestamp"].dt.date <= data_fim)
df_f = df.loc[mask].copy()

if df_f.empty:
    st.warning("Não há dados no intervalo selecionado.")
    st.stop()

# ============================================================
# MAPAS DE COLUNAS
# ============================================================
mapa_lux = {
    "J8": "J8_lux",
    "J11": "J11_lux",
    "J9": "J9_lux",
}
mapa_wm2 = {
    "J8": "J8_Wm2",
    "J11": "J11_Wm2",
    "J9": "J9_Wm2",
}
mapa_wm2_cal = {
    "J8": "J8_Wm2_calibrado",
    "J11": "J11_Wm2_calibrado",
    "J9": "J9_Wm2_calibrado",
}

if grandeza == "Lux":
    mapa_ativo = mapa_lux
    y_label = "Lux"
elif grandeza == "W/m²":
    mapa_ativo = mapa_wm2
    y_label = "W/m²"
else:
    mapa_ativo = mapa_wm2_cal
    y_label = "W/m² calibrado"

# ============================================================
# MÉTRICAS DO TOPO
# ============================================================
st.subheader("Resumo instantâneo")

cols = st.columns(len(sensores_escolhidos) + 1)

for i, sensor in enumerate(sensores_escolhidos):
    col = mapa_ativo[sensor]
    serie = df_f[col].dropna()

    if len(serie) > 0:
        ultimo = serie.iloc[-1]
        delta = serie.iloc[-1] - serie.iloc[-2] if len(serie) > 1 else np.nan
        cols[i].metric(
            label=f"{sensor} ({y_label})",
            value=f"{ultimo:.2f}",
            delta=None if pd.isna(delta) else f"{delta:+.2f}"
        )
    else:
        cols[i].metric(label=f"{sensor} ({y_label})", value="--")

bat = df_f["batt_V"].dropna()
if len(bat) > 0:
    ultimo_bat = bat.iloc[-1]
    delta_bat = bat.iloc[-1] - bat.iloc[-2] if len(bat) > 1 else np.nan
    cols[-1].metric(
        label="Bateria (V)",
        value=f"{ultimo_bat:.3f}",
        delta=None if pd.isna(delta_bat) else f"{delta_bat:+.3f}"
    )
else:
    cols[-1].metric(label="Bateria (V)", value="--")

# ============================================================
# ABAS
# ============================================================
aba1, aba2, aba3, aba4, aba5 = st.tabs([
    "Série temporal",
    "Comparação diária",
    "Horas > 120 W/m²",
    "Bateria",
    "Tabela"
])

# ============================================================
# ABA 1 - SÉRIE TEMPORAL
# ============================================================
with aba1:
    st.subheader(f"Série temporal - {grandeza}")

    fig = go.Figure()

    for sensor in sensores_escolhidos:
        fig.add_trace(go.Scatter(
            x=df_f["timestamp"],
            y=df_f[mapa_ativo[sensor]],
            mode="lines",
            name=sensor,
            hovertemplate="%{x|%d/%m/%Y %H:%M}<br>%{y:.2f}<extra>" + sensor + "</extra>"
        ))

    if grandeza in ["W/m²", "W/m² calibrado"]:
        fig.add_hline(
            y=limiar,
            line_dash="dash",
            annotation_text=f"Limiar = {limiar:.0f} W/m²",
            annotation_position="top left"
        )

    fig.update_layout(
        height=520,
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", y=1.02, x=0),
        xaxis_title="Tempo",
        yaxis_title=y_label
    )

    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# ABA 2 - COMPARAÇÃO DIÁRIA
# ============================================================
with aba2:
    st.subheader(f"Comparação diária - {grandeza}")

    registros = []

    for sensor in sensores_escolhidos:
        col = mapa_ativo[sensor]

        temp = (
            df_f.groupby("data")
                .agg(
                    media=(col, "mean"),
                    maximo=(col, "max"),
                    minimo=(col, "min")
                )
                .reset_index()
        )

        temp["sensor"] = sensor
        registros.append(temp)

    df_daily = pd.concat(registros, ignore_index=True)

    fig2 = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        subplot_titles=("Média diária", "Máximo diário")
    )

    for sensor in sensores_escolhidos:
        d = df_daily[df_daily["sensor"] == sensor]

        fig2.add_trace(
            go.Scatter(
                x=d["data"],
                y=d["media"],
                mode="lines+markers",
                name=f"{sensor} média"
            ),
            row=1, col=1
        )

        fig2.add_trace(
            go.Scatter(
                x=d["data"],
                y=d["maximo"],
                mode="lines+markers",
                name=f"{sensor} máximo"
            ),
            row=2, col=1
        )

    fig2.update_layout(
        height=650,
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", y=1.05, x=0)
    )

    fig2.update_yaxes(title_text=f"Média ({y_label})", row=1, col=1)
    fig2.update_yaxes(title_text=f"Máximo ({y_label})", row=2, col=1)
    fig2.update_xaxes(title_text="Data", row=2, col=1)

    st.plotly_chart(fig2, use_container_width=True)

# ============================================================
# ABA 3 - HORAS DIÁRIAS ACIMA DO LIMIAR
# ============================================================
with aba3:
    st.subheader(f"Horas diárias acima de {limiar:.0f} W/m²")
    st.caption("Cálculo feito com base em interval_duration_hours.")

    registros_horas = []

    for sensor in sensores_escolhidos:
        col = mapa_wm2_cal[sensor]

        temp = df_f[["data", col, "interval_duration_hours"]].copy()
        temp["acima"] = temp[col] > limiar
        temp["horas_acima"] = np.where(temp["acima"], temp["interval_duration_hours"], 0.0)

        diario = temp.groupby("data", as_index=False)["horas_acima"].sum()
        diario["sensor"] = sensor
        registros_horas.append(diario)

    df_horas = pd.concat(registros_horas, ignore_index=True)

    fig3 = go.Figure()

    for sensor in sensores_escolhidos:
        d = df_horas[df_horas["sensor"] == sensor]
        fig3.add_trace(go.Bar(
            x=d["data"],
            y=d["horas_acima"],
            name=sensor
        ))

    fig3.update_layout(
        height=480,
        barmode="group",
        template="plotly_white",
        hovermode="x unified",
        xaxis_title="Data",
        yaxis_title="Horas acima do limiar"
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("#### Estatísticas resumidas")
    resumo_horas = df_horas.pivot(index="data", columns="sensor", values="horas_acima").reset_index()
    st.dataframe(resumo_horas, use_container_width=True)

# ============================================================
# ABA 4 - BATERIA
# ============================================================
with aba4:
    st.subheader("Tensão da bateria")

    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=df_f["timestamp"],
        y=df_f["batt_V"],
        mode="lines",
        name="batt_V",
        hovertemplate="%{x|%d/%m/%Y %H:%M}<br>%{y:.3f} V<extra></extra>"
    ))

    fig4.update_layout(
        height=420,
        template="plotly_white",
        hovermode="x unified",
        xaxis_title="Tempo",
        yaxis_title="Tensão (V)"
    )

    st.plotly_chart(fig4, use_container_width=True)

# ============================================================
# ABA 5 - TABELA
# ============================================================
with aba5:
    st.subheader("Tabela filtrada")

    colunas_tabela = [
        "timestamp",
        "J8_lux", "J11_lux", "J9_lux",
        "batt_V",
        "J8_Wm2", "J11_Wm2", "J9_Wm2",
        "interval_duration_hours",
        "J8_Wm2_calibrado", "J11_Wm2_calibrado", "J9_Wm2_calibrado"
    ]

    tabela = df_f[colunas_tabela].copy()
    st.dataframe(tabela, use_container_width=True)

    csv = tabela.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Baixar tabela filtrada em CSV",
        data=csv,
        file_name="dados_filtrados.csv",
        mime="text/csv"
    )
