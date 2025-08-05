import os
import sqlite3
import requests
from bs4 import BeautifulSoup
import streamlit as st

# === Dicionário de tipos de ativo ===
TIPOS_ATIVO = {
    "A": "Ação",
    "FI": "Fundo Imobiliário",
    "C": "Criptoativo",
    "RD": "Renda Fixa",
    "ETF": "ETF",
    "U": "Unit",
    "FIDC": "FIDC",
    "TD": "Tesouro Direto"
}

# === Criar banco e tabela ===
def criar_tabela():
    os.makedirs("dados", exist_ok=True)
    db_path = os.path.join("dados", "financeiro.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Ativos_B3 (
        cd_ativo_b3 INTEGER PRIMARY KEY AUTOINCREMENT,
        cd_ativo TEXT NOT NULL UNIQUE,
        nm_ativo TEXT,
        nm_setor TEXT,
        nm_subsetor TEXT,
        nm_segmento TEXT,
        in_tipo TEXT CHECK(in_tipo IN ('A', 'FI', 'C', 'RD', 'ETF', 'U', 'FIDC', 'TD'))
    );
    """)
    conn.commit()
    conn.close()

# === Detectar tipo de ativo ===
def detectar_tipo_ativo(codigo):
    codigo = codigo.upper()
    if codigo.endswith("11"):
        return "FI"
    elif codigo.endswith(("3", "4", "5", "6")):
        return "A"
    elif "ETF" in codigo:
        return "ETF"
    elif codigo.startswith(("BTC", "ETH", "SOL", "ADA")):
        return "C"
    elif codigo.startswith(("TESOURO", "LFT", "NTN")):
        return "RD"
    else:
        return "A"

# === Buscar dados de classificação setorial na B3 ===
def buscar_classificacao_b3(codigo):
    url = f"https://sistemaswebb3-listados.b3.com.br/listedCompaniesPage/companyClassification/{codigo}?language=pt-br"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        try:
            data = response.json()
            setor = data.get("sector", "")
            subsetor = data.get("subSector", "")
            segmento = data.get("segment", "")
            return setor, subsetor, segmento
        except Exception:
            return "", "", ""
    return "", "", ""

# === Buscar dados no Status Invest ===
def buscar_status_invest(codigo):
    url = f"https://statusinvest.com.br/acoes/{codigo.lower()}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        try:
            nome = soup.find("h1").text.strip()
            tipo = detectar_tipo_ativo(codigo)
            setor, subsetor, segmento = buscar_classificacao_b3(codigo)

            return {
                "cd_ativo": codigo,
                "nm_ativo": nome,
                "nm_setor": setor,
                "nm_subsetor": subsetor,
                "nm_segmento": segmento,
                "in_tipo": tipo
            }
        except Exception as e:
            st.error(f"Erro ao extrair dados do Status Invest: {e}")
            return None
    else:
        st.error(f"Falha ao acessar Status Invest: {response.status_code}")
        return None

# === Inserir no banco ===
def inserir_ativo_no_banco(dados):
    db_path = os.path.join("dados", "financeiro.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO Ativos_B3 (
            cd_ativo, nm_ativo, nm_setor, nm_subsetor, nm_segmento, in_tipo
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        dados["cd_ativo"],
        dados["nm_ativo"],
        dados["nm_setor"],
        dados["nm_subsetor"],
        dados["nm_segmento"],
        dados["in_tipo"]
    ))
    conn.commit()
    conn.close()

# === Atualizar ativo no banco ===
def atualizar_ativo(dados):
    db_path = os.path.join("dados", "financeiro.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Ativos_B3 SET
            nm_ativo = ?, nm_setor = ?, nm_subsetor = ?, nm_segmento = ?, in_tipo = ?
        WHERE cd_ativo = ?
    """, (
        dados["nm_ativo"],
        dados["nm_setor"],
        dados["nm_subsetor"],
        dados["nm_segmento"],
        dados["in_tipo"],
        dados["cd_ativo"]
    ))
    conn.commit()
    conn.close()

# === Excluir ativo do banco ===
def excluir_ativo(codigo):
    db_path = os.path.join("dados", "financeiro.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Ativos_B3 WHERE cd_ativo = ?", (codigo,))
    conn.commit()
    conn.close()

# === Interface Streamlit ===
def dim_cad_ativos():
    criar_tabela()
    st.title("📊 Cadastro de Ativos da B3")

    codigo = st.text_input("Digite o código do ativo (ex: BBAS3, HGLG11):").strip().upper()

    if st.button("Buscar e Cadastrar"):
        if codigo:
            dados = buscar_status_invest(codigo)
            if dados:
                inserir_ativo_no_banco(dados)
                st.session_state["dados_ativo"] = dados

    # Exibir dados se houver
    if "dados_ativo" in st.session_state:
        dados = st.session_state["dados_ativo"]
        tipo_nome = TIPOS_ATIVO.get(dados["in_tipo"], "Desconhecido")

        st.subheader("📄 Informações do Ativo")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**🆔 Código:** `{dados['cd_ativo']}`")
            st.markdown(f"**🏢 Nome:** {dados['nm_ativo']}")
            st.markdown(f"**📦 Tipo de Ativo:** {tipo_nome}")

        with col2:
            st.markdown(f"**🏭 Setor:** {dados['nm_setor'] or 'N/A'}")
            st.markdown(f"**🔧 Subsetor:** {dados['nm_subsetor'] or 'N/A'}")
            st.markdown(f"**📊 Segmento:** {dados['nm_segmento'] or 'N/A'}")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✏️ Alterar"):
                st.session_state["modo_edicao"] = True
        with col_b:
            if st.button("🗑️ Excluir"):
                excluir_ativo(dados["cd_ativo"])
                st.success(f"Ativo {dados['cd_ativo']} excluído.")
                st.session_state.pop("dados_ativo", None)
                st.session_state.pop("modo_edicao", None)

    # Modo edição
    if st.session_state.get("modo_edicao"):
        st.subheader("✏️ Editar Ativo")
        dados = st.session_state["dados_ativo"]

        nome = st.text_input("Nome do Ativo", value=dados["nm_ativo"])
        tipo = st.selectbox("Tipo de Ativo", options=list(TIPOS_ATIVO.keys()), format_func=lambda x: TIPOS_ATIVO[x], index=list(TIPOS_ATIVO.keys()).index(dados["in_tipo"]))
        setor = st.text_input("Setor", value=dados["nm_setor"])
        subsetor = st.text_input("Subsetor", value=dados["nm_subsetor"])
        segmento = st.text_input("Segmento", value=dados["nm_segmento"])

        if st.button("💾 Gravar"):
            dados_atualizados = {
                "cd_ativo": dados["cd_ativo"],
                "nm_ativo": nome,
                "nm_setor": setor,
                "nm_subsetor": subsetor,
                "nm_segmento": segmento,
                "in_tipo": tipo
            }
            atualizar_ativo(dados_atualizados)
            st.success("✅ Alterações salvas com sucesso!")

            # Limpar sessão e reiniciar tela
            st.session_state.pop("dados_ativo", None)
            st.session_state.pop("modo_edicao", None)
            st.rerun()

# === Executar a função principal ===
if __name__ == "__main__":
    dim_cad_ativos()