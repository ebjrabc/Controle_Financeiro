import streamlit as st
import sqlite3
import pandas as pd

# ✅ Instala o Streamlit se necessário
try:
    import plotly.express as px
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])

st.set_page_config(page_title="📊 Relatório Financeiro", layout="wide")

conn = sqlite3.connect("Dados/financeiro.db")
cursor = conn.cursor()

# 🔍 Consulta os dados
query = """
SELECT 
    f.dt_transacao,
    f.vl_valor_fluxo,
    f.nm_descricao,
    c.nm_categoria,
    c.nm_grupo,
    c.nm_tipo
FROM fluxo_caixa f
JOIN categoria c ON f.cd_categoria = c.cd_categoria
WHERE c.in_ativo = 's'
"""
df = pd.read_sql_query(query, conn)

# 🧼 Converte data
df["mes_ano"] = df["dt_transacao"]  # já está no formato "MM-YYYY"


# 📅 Cria coluna de mês/ano
df["mes_ano"] = df["dt_transacao"]  # já está no formato "MM-YYYY"


# 📊 Total por mês por tipo
st.subheader("💸 Total por Mês (Entrada vs Despesa)")
df_agrupado = df.groupby(["mes_ano", "nm_tipo"])["vl_valor_fluxo"].sum().reset_index()
fig1 = px.bar(df_agrupado, x="mes_ano", y="vl_valor_fluxo", color="nm_tipo", barmode="group", title="Total por Mês")
st.plotly_chart(fig1, use_container_width=True)

# 📊 Total por grupo
st.subheader("📁 Distribuição por Grupo")
df_grupo = df.groupby("nm_grupo")["vl_valor_fluxo"].sum().reset_index()
fig2 = px.pie(df_grupo, names="nm_grupo", values="vl_valor_fluxo", title="Distribuição por Grupo")
st.plotly_chart(fig2, use_container_width=True)

# 📊 Categorias mais movimentadas
st.subheader("🏷️ Categorias Mais Movimentadas")
df_cat = df.groupby("nm_categoria")["vl_valor_fluxo"].sum().reset_index().sort_values(by="vl_valor_fluxo", ascending=False)
fig3 = px.bar(df_cat.head(10), x="nm_categoria", y="vl_valor_fluxo", title="Top 10 Categorias")
st.plotly_chart(fig3, use_container_width=True)

# 📈 Evolução temporal
st.subheader("📈 Evolução do Saldo")
df["vl_entrada"] = df["vl_valor_fluxo"].where(df["nm_tipo"] == "entrada", 0)
df["vl_despesa"] = df["vl_valor_fluxo"].where(df["nm_tipo"] == "despesa", 0)
df_saldo = df.groupby("mes_ano")[["vl_entrada", "vl_despesa"]].sum().reset_index()
df_saldo["saldo"] = df_saldo["vl_entrada"] - df_saldo["vl_despesa"]
fig4 = px.line(df_saldo, x="mes_ano", y="saldo", title="Saldo Acumulado")
st.plotly_chart(fig4, use_container_width=True)

conn.close()