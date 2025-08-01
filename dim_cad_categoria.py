import os
import subprocess
import sys

# ✅ Instala o Streamlit se necessário
try:
    import streamlit
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])

# 📁 Garante que a pasta Dados existe
os.makedirs("Dados", exist_ok=True)
db_path = os.path.join("Dados", "financeiro.db")

# 📝 Código do app principal
app_code = f"""
import streamlit as st
import sqlite3
import subprocess
import sys

conn = sqlite3.connect(r'{db_path}', check_same_thread=False)
cursor = conn.cursor()

# 🛠️ Criação da tabela
cursor.execute(\"\"\"
    CREATE TABLE IF NOT EXISTS categoria (
        cd_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
        nm_categoria TEXT NOT NULL,
        nm_grupo TEXT NOT NULL,
        nm_tipo TEXT NOT NULL,
        in_fixo TEXT DEFAULT 'n',
        in_ativo TEXT DEFAULT 's'
    )
\"\"\")
conn.commit()

st.set_page_config(page_title='📂 Cadastro de Categorias', layout='wide')

# 🎨 Estilo visual
st.markdown(\"\"\"
    <style>
    .block-container {{
        padding-top: 1rem;
    }}
    .titulo-menor {{
        font-size: 22px;
        font-weight: bold;
        color: #333333;
        margin-bottom: 5px;
    }}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    </style>
    <div class="titulo-menor">📂 Cadastro de Categorias</div>
    <br>
\"\"\", unsafe_allow_html=True)

# 🔍 Grupos existentes
grupos_existentes = cursor.execute(
    "SELECT DISTINCT nm_grupo FROM categoria WHERE in_ativo = 's'"
).fetchall()
grupo_opcoes = sorted([g[0] for g in grupos_existentes])

grupo_selecionado = st.selectbox("Grupo da Categoria (existente ou novo)", options=grupo_opcoes + ["Novo_Cadastro"])
grupo = st.text_input("Digite novo grupo da categoria") if grupo_selecionado == "Novo_Cadastro" else grupo_selecionado

# 🔍 Categorias do grupo
categorias_do_grupo = cursor.execute(
    "SELECT nm_categoria FROM categoria WHERE nm_grupo = ? AND in_ativo = 's'", (grupo,)
).fetchall()
nome_opcoes = sorted(list(set([cat[0] for cat in categorias_do_grupo])))

nome_selecionado = st.selectbox("Nome da Categoria (existente ou novo)", options=nome_opcoes + ["Novo_Cadastro"])
nome = st.text_input("Digite novo nome da categoria") if nome_selecionado == "Novo_Cadastro" else nome_selecionado

# 🔽 Tipo da categoria
tipo = st.selectbox("Tipo da Categoria", options=["Entrada", "Despesa"])

# ✅ Checkbox para categoria fixa
fixa = st.checkbox("Esta categoria é fixa? (Ex: aluguel, salário, mensalidades)")
in_fixo = "s" if fixa else "n"
st.caption("✔️ Se marcado, indica que a categoria ocorre regularmente todo mês.")

# 🔘 Botões de ação
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("✅ Incluir Categoria"):
        if nome and grupo and tipo:
            cursor.execute("SELECT * FROM categoria WHERE nm_categoria = ? AND nm_grupo = ? AND in_ativo = 's'", (nome, grupo))
            existe_ativa = cursor.fetchone()

            cursor.execute("SELECT * FROM categoria WHERE nm_categoria = ? AND nm_grupo = ? AND in_ativo = 'n'", (nome, grupo))
            existe_excluida = cursor.fetchone()

            if existe_ativa:
                st.warning("⚠️ Categoria já cadastrada.")
            elif existe_excluida:
                cursor.execute("UPDATE categoria SET in_ativo = 's', nm_tipo = ?, in_fixo = ? WHERE nm_categoria = ? AND nm_grupo = ?", (tipo, in_fixo, nome, grupo))
                conn.commit()
                st.success("✅ Categoria reativada com sucesso!")
                st.rerun()
            else:
                cursor.execute("INSERT INTO categoria (nm_categoria, nm_grupo, nm_tipo, in_fixo) VALUES (?, ?, ?, ?)", (nome, grupo, tipo, in_fixo))
                conn.commit()
                st.success("✅ Categoria incluída com sucesso!")
                st.rerun()
        else:
            st.warning("⚠️ Preencha todos os campos.")

with col2:
    if nome_selecionado != "Novo_Cadastro":
        if st.button("🗑️ Excluir Categoria"):
            st.session_state.confirmar_exclusao = True

with col3:
    if st.button("✏️ Alterar Categoria"):
        st.session_state.alterar_categoria = True

with col4:
    if st.button("📊 Relatório"):
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", "relatorio_categoria.py"])
        st.success("✅ Relatório aberto em nova aba. Verifique seu navegador.")

# 🗑️ Confirmação de exclusão
if st.session_state.get("confirmar_exclusao", False):
    st.warning(f"Tem certeza que deseja excluir a categoria **{{{{nome_selecionado}}}}** do grupo **{{{{grupo}}}}**?")
    col_confirmar, col_cancelar = st.columns(2)
    with col_confirmar:
        if st.button("✅ Sim, excluir"):
            cursor.execute(
                "UPDATE categoria SET in_ativo = 'n' WHERE nm_categoria = ? AND nm_grupo = ? AND in_ativo = 's'",
                (nome_selecionado, grupo)
            )
            conn.commit()
            st.success("🗑️ Categoria excluída logicamente.")
            st.session_state.confirmar_exclusao = False
            st.rerun()
    with col_cancelar:
        if st.button("❌ Não, cancelar"):
            st.session_state.confirmar_exclusao = False
            st.rerun()

# ✏️ Alteração de categoria
if st.session_state.get("alterar_categoria", False):
    st.subheader("✏️ Alterar Categoria")

    todas_categorias = cursor.execute("SELECT nm_categoria, nm_grupo, nm_tipo, in_fixo, in_ativo FROM categoria").fetchall()
    nomes_todos = sorted(list(set([cat[0] for cat in todas_categorias])))
    grupos_todos = sorted(list(set([cat[1] for cat in todas_categorias])))

    categoria_selecionada = st.selectbox("Selecione a categoria para alterar", options=nomes_todos)
    dados_atuais = cursor.execute(
        "SELECT nm_grupo, nm_tipo, in_fixo, in_ativo FROM categoria WHERE nm_categoria = ? LIMIT 1", (categoria_selecionada,)
    ).fetchone()

    grupo_atual, tipo_atual, fixo_atual, ativo_atual = dados_atuais if dados_atuais else ("", "Despesa", "n", "s")

    novo_nome = st.text_input("Novo nome da categoria", value=categoria_selecionada)
    novo_grupo = st.selectbox("Novo grupo da categoria", options=grupos_todos + ["Novo_Cadastro"])
    if novo_grupo == "Novo_Cadastro":
        novo_grupo = st.text_input("Digite novo grupo")

    novo_tipo = st.selectbox("Novo tipo da categoria", options=["Entrada", "Despesa"], index=["Entrada", "Despesa"].index(tipo_atual))
    novo_fixo = st.checkbox("Esta categoria é fixa?", value=(fixo_atual == "s"))
    novo_ativo = st.checkbox("Categoria está ativa", value=(ativo_atual == "s"))

    if st.button("✅ Confirmar Alteração"):
        if novo_nome and novo_grupo and novo_tipo:
            cursor.execute(
                "UPDATE categoria SET nm_categoria = ?, nm_grupo = ?, nm_tipo = ?, in_fixo = ?, in_ativo = ? WHERE nm_categoria = ? AND nm_grupo = ?",
                (novo_nome, novo_grupo, novo_tipo, "s" if novo_fixo else "n", "s" if novo_ativo else "n", categoria_selecionada, grupo_atual)
            )
            conn.commit()
            st.success("✏️ Categoria alterada com sucesso.")
            st.session_state.alterar_categoria = False
            st.rerun()
        else:
            st.warning("⚠️ Preencha todos os campos para alterar.")

conn.close()
"""

# 📝 Cria o arquivo app.py
with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)

# 🚀 Executa o app
subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])