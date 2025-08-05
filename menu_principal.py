import streamlit as st
from modulo_categorias import dim_cad_categoria
from modulo_relatorio import dim_rel_categoria
from modulo_fluxo_caixa import ft_fluxo_caixa

def exibir_menu(usuario_logado):
    st.set_page_config(page_title="📋 Menu Principal", layout="wide")

    if "tela" not in st.session_state:
        st.session_state["tela"] = "inicio"

    st.markdown("""
        <style>
        #MainMenu, footer, header {visibility: hidden;}
        .user-info {
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
        }
        </style>
    """, unsafe_allow_html=True)

    # Exibe usuário logado
    st.markdown(f"<div class='user-info'>👤 {usuario_logado}</div>", unsafe_allow_html=True)

    # Menu
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🚪 Sair"):
            # Limpa sessão e redireciona para login
            st.session_state.clear()
            st.rerun()
    with col2:
        if st.button("📂 Cadastro de Categorias"):
            st.session_state["tela"] = "categorias"
    with col3:
        if st.button("📊 Relatório de Categorias"):
            st.session_state["tela"] = "relatorio"
    with col4:
        if st.button("💰 Fluxo de Caixa"):
            st.session_state["tela"] = "Fluxo_Caixa"

    st.markdown("<hr>", unsafe_allow_html=True)

    # Conteúdo
    if st.session_state.get("tela") == "inicio":
        st.info("👋 Bem-vindo ao sistema financeiro. Escolha uma opção acima.")
    elif st.session_state["tela"] == "categorias":
        dim_cad_categoria(st.session_state.get("codigo_usuario"))
    elif st.session_state["tela"] == "relatorio":
        dim_rel_categoria()
    elif st.session_state["tela"] == "Fluxo_Caixa":
        ft_fluxo_caixa()