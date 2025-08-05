import streamlit as st
import sqlite3
import re
import menu_principal  # Certifique-se de que este arquivo existe e tem a função exibir()

# 🔧 Configuração da página inicial
st.set_page_config(page_title="🔐 Login", layout="centered")

# ✅ CSS para ocultar botão Deploy e exibir nome do usuário
def aplicar_estilo(usuario=None):
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
        .stAppDeployButton {{
            display: none;
        }}
        </style>
        {f"<div class='user-info'>👤 {usuario}</div>" if usuario else ""}
    """, unsafe_allow_html=True)

# 🔗 Banco de dados
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

# 🔐 Validação de senha forte
def senha_forte(senha):
    return (
        len(senha) >= 8 and
        re.search(r"[A-Z]", senha) and
        re.search(r"[a-z]", senha) and
        re.search(r"[0-9]", senha) and
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha)
    )

# 🧠 Geração de código único
def gerar_codigo_usuario():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuario")
    total = cursor.fetchone()[0]
    conn.close()
    return f"USR{total + 1:03d}"

# 🔒 Autenticação
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

# 📝 Cadastro
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

# 🔄 Controle de navegação
if "pagina" not in st.session_state:
    st.session_state.pagina = "login"
if "subpagina" not in st.session_state:
    st.session_state.subpagina = "login"

# 🔐 Tela de login
if st.session_state.pagina == "login":
    if st.session_state.subpagina == "login":
        st.markdown("""
            <h1 style='font-size:20px;'>🔐 Login do Sistema</h1>
        """, unsafe_allow_html=True)


        login = st.text_input("Login", key="login_usuario")
        senha = st.text_input("Senha", type="password", key="login_senha")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Entrar"):
                resultado = autenticar_usuario(login, senha)
                if resultado == "nao_cadastrado":
                    st.warning("Usuário não cadastrado.")
                elif resultado == "senha_incorreta":
                    st.error("Senha incorreta.")
                else:
                    st.session_state.codigo_usuario = resultado["codigo_usuario"]
                    st.session_state.usuario_logado = resultado["nome_completo"]
                    st.session_state.pagina = "menu"
                    st.rerun()

        with col_btn2:
            if st.button("Cadastrar"):
                st.session_state.subpagina = "cadastro"
                st.rerun()

    elif st.session_state.subpagina == "cadastro":
        st.title("📝 Cadastro de Novo Usuário")
        st.caption("🔒 A senha deve conter pelo menos 8 caracteres, incluindo letra maiúscula, minúscula, número e caractere especial.")

        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome", key="cadastro_nome")
            sobrenome = st.text_input("Sobrenome", key="cadastro_sobrenome")
        with col2:
            novo_login = st.text_input("Login de acesso", key="cadastro_login")
            nova_senha = st.text_input("Senha", type="password", key="cadastro_senha")

        col_btn = st.columns(3)
        with col_btn[1]:
            if st.button("Confirmar Cadastro"):
                if not nome or not sobrenome or not novo_login or not nova_senha:
                    st.warning("Preencha todos os campos.")
                elif not senha_forte(nova_senha):
                    st.error("A senha não atende aos requisitos de segurança.")
                else:
                    resultado = cadastrar_usuario(nome, sobrenome, novo_login, nova_senha)
                    if resultado == "sucesso":
                        st.success("Usuário cadastrado com sucesso! Redirecionando para a tela de login...")
                        st.session_state.subpagina = "login"
                        st.rerun()
                    elif resultado == "login_existente":
                        st.error("Login já existe. Escolha outro.")

elif st.session_state.pagina == "menu":
    import menu_principal
    menu_principal.exibir_menu(st.session_state.usuario_logado)