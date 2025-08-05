import streamlit as st
import sqlite3
import re

def exibir(usuario):
    st.set_page_config(page_title="📊 Menu Principal", layout="wide")
    st.title("📊 Menu Principal")

    st.markdown(f"""
        <style>
        .user-info {{
            position: fixed;
            top: 10px;
            right: 20px;
            font-size: 16px;
            font-weight: 500;
            color: #333;
            background-color: #f0f0f0;
            padding: 6px 12px;
            border-radius: 8px;
            z-index: 9999;
        }}
        </style>
        <div class='user-info'>👤 {usuario}</div>
    """, unsafe_allow_html=True)

def conectar_banco():
    conn = sqlite3.connect("Dados/financeiro.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuario (
            codigo_usuario TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            sobrenome TEXT NOT NULL,
            login TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn

def gerar_codigo_usuario():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuario")
    total = cursor.fetchone()[0]
    conn.close()
    return f"USR{total + 1:03d}"

def senha_forte(senha):
    if len(senha) < 8:
        return False
    if not re.search(r"[A-Z]", senha):
        return False
    if not re.search(r"[a-z]", senha):
        return False
    if not re.search(r"[0-9]", senha):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha):
        return False
    return True

def autenticar_usuario(login, senha):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT codigo_usuario, nome, sobrenome, senha FROM usuario WHERE login = ?", (login,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado is None:
        return "nao_cadastrado"
    elif resultado[3] != senha:
        return "senha_incorreta"
    else:
        nome_completo = f"{resultado[1]} {resultado[2]}"
        return {"codigo_usuario": resultado[0], "nome_completo": nome_completo}

def cadastrar_usuario(nome, sobrenome, login, senha):
    conn = conectar_banco()
    cursor = conn.cursor()
    codigo = gerar_codigo_usuario()
    try:
        cursor.execute(
            "INSERT INTO usuario (codigo_usuario, nome, sobrenome, login, senha) VALUES (?, ?, ?, ?, ?)",
            (codigo, nome, sobrenome, login, senha)
        )
        conn.commit()
        return "sucesso"
    except sqlite3.IntegrityError:
        return "login_existente"
    finally:
        conn.close()

# Inicializa sessão
if "pagina" not in st.session_state:
    st.session_state.pagina = "login"

if st.session_state.pagina == "login":
    st.title("🔐 Login do Sistema")
    menu = st.sidebar.selectbox("Menu", ["Login", "Cadastro"])

    if menu == "Login":
        login = st.text_input("Login")
        senha = st.text_input("Senha", type="password")

        col_btn1, col_btn2 = st.columns(2)
        login_resultado = None
        with col_btn1:
            if st.button("Entrar"):
                login_resultado = autenticar_usuario(login, senha)
        with col_btn2:
            st.info("Use o Menu a esqueda na aba 'Cadastro' para criar uma conta.")

        if login_resultado:
            if login_resultado == "nao_cadastrado":
                st.warning("Usuário não cadastrado. Use o Menu a esqueda na aba 'Cadastro' para criar uma conta'.")
            elif login_resultado == "senha_incorreta":
                st.error("Senha incorreta.")
            else:
                st.session_state.codigo_usuario = login_resultado["codigo_usuario"]
                st.session_state.usuario_logado = login_resultado["nome_completo"]
                st.session_state.pagina = "menu"
                st.rerun()

    elif menu == "Cadastro":
        st.subheader("📝 Cadastro de Novo Usuário")

        st.caption("🔒 A senha deve conter pelo menos 8 caracteres, incluindo letra maiúscula, minúscula, número e caractere especial.")

        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome")
            sobrenome = st.text_input("Sobrenome")
        with col2:
            novo_login = st.text_input("Login de acesso")
            nova_senha = st.text_input("Senha", type="password")

        cadastro_resultado = None
        col_btn = st.columns(3)
        with col_btn[1]:
            if st.button("Cadastrar"):
                if not nome or not sobrenome or not novo_login or not nova_senha:
                    cadastro_resultado = "campos_vazios"
                elif not senha_forte(nova_senha):
                    cadastro_resultado = "senha_fraca"
                else:
                    cadastro_resultado = cadastrar_usuario(nome, sobrenome, novo_login, nova_senha)

        if cadastro_resultado:
            if cadastro_resultado == "campos_vazios":
                st.warning("Preencha todos os campos.")
            elif cadastro_resultado == "senha_fraca":
                st.error("A senha não atende aos requisitos de segurança.")
            elif cadastro_resultado == "sucesso":
                st.success("Usuário cadastrado com sucesso! Volte para a aba 'Login'.")
            elif cadastro_resultado == "login_existente":
                st.error("Login já existe. Escolha outro.")

elif st.session_state.pagina == "menu":
    import menu_principal
    menu_principal.exibir_menu(st.session_state.usuario_logado)