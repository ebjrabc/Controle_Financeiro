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
app_code = f'''
import streamlit as st
import sqlite3
import subprocess
import sys
import time
from datetime import date

conn = sqlite3.connect(r"{db_path}", check_same_thread=False)
cursor = conn.cursor()

# 🛠️ Criação da tabela de fluxo de caixa
cursor.execute(\"\"\"
    CREATE TABLE IF NOT EXISTS fluxo_caixa (
        cd_transacao INTEGER PRIMARY KEY AUTOINCREMENT,
        cd_categoria INTEGER,
        nr_nota_fiscal INTEGER,
        dt_transacao TEXT NOT NULL,
        nm_descricao TEXT,
        vl_valor_fluxo DOUBLE NOT NULL,
        FOREIGN KEY (cd_categoria) REFERENCES categoria(cd_categoria)
    )
\"\"\")
conn.commit()

st.set_page_config(page_title="💰 Fluxo de Caixa", layout="wide")

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
    <div class="titulo-menor">💰 Fluxo de Caixa</div>
    <br>
\"\"\", unsafe_allow_html=True)

# 🔍 Carrega categorias ativas
categorias_ativas = cursor.execute(
    "SELECT cd_categoria, nm_categoria, nm_grupo, nm_tipo FROM categoria WHERE in_ativo = 's'"
).fetchall()

if categorias_ativas:
    grupos = sorted(set([cat[2] for cat in categorias_ativas]))
    grupo_selecionado = st.selectbox("Grupo da Categoria", options=grupos)

    categorias_do_grupo = [cat for cat in categorias_ativas if cat[2] == grupo_selecionado]
    nomes = sorted(set([cat[1] for cat in categorias_do_grupo]))
    nome_selecionado = st.selectbox("Nome da Categoria", options=nomes)

    categoria_escolhida = next(
        (cat for cat in categorias_do_grupo if cat[1] == nome_selecionado),
        None
    )

    if categoria_escolhida:
        tipo_selecionado = categoria_escolhida[3]
        cd_categoria = categoria_escolhida[0]
        st.text_input("Tipo da Categoria", value=tipo_selecionado, disabled=True)
    else:
        st.warning("⚠️ Categoria não encontrada.")
        st.stop()
    if "nota_fiscal" not in st.session_state:
        st.session_state.nota_fiscal = 0
    nota_fiscal = st.number_input("Número da Nota Fiscal (opcional)",key="nota_fiscal", step=1, format="%d") 
    meses = {{
        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro"
    }}

    anos = list(range(2000, date.today().year + 1))

    col1, col2 = st.columns(2)
    mes_selecionado = col1.selectbox("Mês da Transação", options=list(meses.keys()), format_func=lambda x: meses[x])
    ano_selecionado = col2.selectbox("Ano da Transação", options=anos, index=anos.index(date.today().year))

    data_transacao = f"{{mes_selecionado:02d}}-{{ano_selecionado:04d}}"
    if "descricao" not in st.session_state:
        st.session_state.descricao = "opcional"
    descricao = st.text_input("Descrição", key="descricao")
    
    # Definir valor inicial antes de criar o widget
    if "valor" not in st.session_state:
        st.session_state.valor = 0.0

    # Criar o widget
    valor = st.number_input("Valor da transação", key="valor")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("✅ Incluir Transação"):
            if cd_categoria and data_transacao and valor > 0:
                try:
                    cursor.execute("""
                        INSERT INTO fluxo_caixa (nr_nota_fiscal, dt_transacao, nm_descricao, cd_categoria, vl_valor_fluxo)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        nota_fiscal if nota_fiscal else None,
                        data_transacao,
                        descricao,
                        cd_categoria,
                        valor
                    ))
                    conn.commit()
                    st.success("✅ Transação incluída com sucesso!")
                    for key in st.session_state.keys():
                        del st.session_state[key]
                    
                    time.sleep(1.5)  # ⏸️ Pausa leve para o usuário ver a mensagem
                    # 🔁 Dá refresh na página
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Erro ao incluir transação: {{e}}")
                    time.sleep(3)  # ⏸️ Pausa maior para o usuário ler o erro
            else:
                st.warning("⚠️ Preencha os campos obrigatórios.")
                time.sleep(3)  # ⏸️ Pausa maior para o usuário ler o erro
    with col2:
        if st.button("🗑️ Excluir Transação"):
            st.session_state.confirmar_exclusao = True

    with col3:
        if st.button("✏️ Alterar Transação"):
            st.session_state.alterar_transacao = True

    with col4:
        if st.button("📊 Relatório"):
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", "relatorio_fluxo_caixa.py"])
            st.success("✅ Relatório aberto em nova aba. Verifique seu navegador.")

    if st.session_state.get("confirmar_exclusao", False):
        transacoes = cursor.execute(\"\"\"
            SELECT cd_transacao, dt_transacao, vl_valor_fluxo FROM fluxo_caixa ORDER BY dt_transacao DESC
        \"\"\").fetchall()
        if transacoes:
            transacao_id = st.selectbox("Selecione a transação para excluir", options=["{{}} | {{}} | R$ {{:.2f}}".format(trans[0], trans[1], trans[2]) for trans in transacoes])
            cd_transacao = int(transacao_id.split(" | ")[0])
            col_confirmar, col_cancelar = st.columns(2)
            with col_confirmar:
                if st.button("✅ Sim, excluir"):
                    cursor.execute("DELETE FROM fluxo_caixa WHERE cd_transacao = ?", (cd_transacao,))
                    conn.commit()
                    st.success("🗑️ Transação excluída com sucesso.")
                    st.session_state.confirmar_exclusao = False
                    st.rerun()
            with col_cancelar:
                if st.button("❌ Não, cancelar"):
                    st.session_state.confirmar_exclusao = False
                    st.rerun()
        else:
            st.info("ℹ️ Nenhuma transação para excluir.")
            st.session_state.confirmar_exclusao = False

    if st.session_state.get("alterar_transacao", False):
        st.subheader("✏️ Alterar Transação")
        transacoes = cursor.execute(\"\"\"
            SELECT cd_transacao, nr_nota_fiscal, dt_transacao, nm_descricao, cd_categoria, vl_valor_fluxo
            FROM fluxo_caixa ORDER BY dt_transacao DESC
        \"\"\").fetchall()

        if transacoes:
            transacao_opcoes = ["{{}} | {{}} | R$ {{:.2f}}".format(t[0], t[2], t[5]) for t in transacoes]
            transacao_escolhida = st.selectbox("Selecione a transação para alterar", options=transacao_opcoes)
            transacao_dados = [t for t in transacoes if str(t[0]) == transacao_escolhida.split(" | ")[0]][0]

            novo_nota = st.number_input("Novo número da nota fiscal", value=int(transacao_dados[1]) if transacao_dados[1] else 0, step=1, format="%d")
            nova_data = st.date_input("Nova data da transação", value=date.fromisoformat(transacao_dados[2]))
            nova_descricao = st.text_input("Nova descrição", value=transacao_dados[3] if transacao_dados[3] else "", key="descricao_alteracao")
            novo_valor = st.number_input("Novo valor", value=transacao_dados[5], format="%.2f")

            nova_categoria = next((cat for cat in categorias_ativas if cat[0] == transacao_dados[4]), None)
            if nova_categoria:
                grupo_atual = nova_categoria[2]
                nome_atual = nova_categoria[1]
                tipo_atual = nova_categoria[3]

                grupo_selecionado = st.selectbox("Novo grupo", options=grupos, index=grupos.index(grupo_atual))
                categorias_do_grupo = [cat for cat in categorias_ativas if cat[2] == grupo_selecionado]
                nomes = sorted(set([cat[1] for cat in categorias_do_grupo]))
                nome_selecionado = st.selectbox("Novo nome", options=nomes, index=nomes.index(nome_atual))

                nova_categoria_escolhida = next(
                    (cat for cat in categorias_do_grupo if cat[1] == nome_selecionado),
                    None
                )
                novo_cd_categoria = nova_categoria_escolhida[0]
                novo_tipo = nova_categoria_escolhida[3]
                st.text_input("Novo tipo", value=novo_tipo, disabled=True)

                if st.button("✅ Confirmar Alteração"):
                    cursor.execute(\"\"\"
                        UPDATE fluxo_caixa
                        SET nr_nota_fiscal = ?,
                            dt_transacao = ?,
                            nm_descricao = ?,
                            cd_categoria = ?,
                            vl_valor_fluxo = ?
                            WHERE cd_transacao = ?
                    \"\"\", (
                        novo_nota if novo_nota else None,
                        nova_data,
                        nova_descricao,
                        novo_cd_categoria,
                        novo_valor,
                        transacao_dados[0]
                    ))
                    conn.commit()
                    st.success("✏️ Transação alterada com sucesso.")
                    st.session_state.alterar_transacao = False
                    st.rerun()
            else:
                st.warning("⚠️ Categoria da transação não encontrada.")
        else:
            st.info("ℹ️ Nenhuma transação para alterar.")
            st.session_state.alterar_transacao = False
else:
    st.warning("⚠️ Nenhuma categoria ativa encontrada. Cadastre pelo módulo de categorias.")
    st.stop()

conn.close()
'''

# 📝 Cria o arquivo app.py
with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)

# 🚀 Executa o app
subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])