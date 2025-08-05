import streamlit as st
from modulo_categorias import dim_cad_categoria
from modulo_relatorio import dim_rel_categoria
from modulo_fluxo_caixa import ft_fluxo_caixa
#from modulo_relatorio import dim_cad_ativos

st.set_page_config(page_title="📋 Menu Principal", layout="wide")

# 🔄 Inicializa estados
if "tela" not in st.session_state:
    st.session_state["tela"] = "inicio"
if "submenu_cadastros" not in st.session_state:
    st.session_state["submenu_cadastros"] = False

# 🎨 Estilo visual
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    .menu-button { font-size: 18px; font-weight: 500; padding: 0.5rem; border-radius: 8px; background-color: #f0f2f6; border: 1px solid #dcdcdc; cursor: pointer; text-align: center; }
    .menu-button:hover { background-color: #e0e0e0; }
    .menu-button.selected { background-color: #ffcccc !important; border-color: #cc0000; font-weight: bold; color: #660000; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 🧭 Menu principal
col1, col2, col3, col4 = st.columns([1.5, 2.5, 2, 2])

with col1:
    if st.button("🏠 Tela Inicial"):
        st.session_state["tela"] = "inicio"
        st.session_state["submenu_cadastros"] = False

with col2:
    if st.button("📁 Cadastros"):
        st.session_state["submenu_cadastros"] = not st.session_state["submenu_cadastros"]

    # 📁 Submenu diretamente abaixo do botão
    if st.session_state["submenu_cadastros"]:
        if st.button("📂 Categoria"):
            st.session_state["tela"] = "categorias"
            st.session_state["submenu_cadastros"] = False
            st.rerun()
        if st.button("🧾 Ativos"):
            st.session_state["tela"] = "ativos"
            st.session_state["submenu_cadastros"] = False
            st.rerun()

with col3:
    if st.button("📊 Relatório de Categorias"):
        st.session_state["tela"] = "relatorio"
        st.session_state["submenu_cadastros"] = False

with col4:
    if st.button("💰 Fluxo de Caixa"):
        st.session_state["tela"] = "Fluxo_Caixa"
        st.session_state["submenu_cadastros"] = False

# 📦 Linha separadora
st.markdown("<hr style='margin-top: -10px; margin-bottom: 20px;'>", unsafe_allow_html=True)

# 📦 Conteúdo principal
if st.session_state["tela"] == "inicio":
    st.info("👋 Bem-vindo ao sistema financeiro. Escolha uma opção acima.")
elif st.session_state["tela"] == "categorias":
    dim_cad_categoria()
elif st.session_state["tela"] == "relatorio":
    dim_rel_categoria()
elif st.session_state["tela"] == "Fluxo_Caixa":
    ft_fluxo_caixa()
elif st.session_state["tela"] == "ativos":
    dim_cad_ativos()

# ✅ Botão ativo destacado
botao_html = {
    "inicio": "🏠 Tela Inicial",
    "categorias": "📂 Categoria",
    "relatorio": "📊 Relatório de Categorias",
    "Fluxo_Caixa": "💰 Fluxo de Caixa",
    "ativos": "🧾 Ativos"
}

st.markdown(f"""
    <script>
    const buttons = window.parent.document.querySelectorAll('.stButton button');
    buttons.forEach(btn => {{
        if (btn.innerText === "{botao_html.get(st.session_state['tela'], '')}") {{
            btn.classList.add("selected");
        }} else {{
            btn.classList.remove("selected");
        }}
    }});
    </script>
""", unsafe_allow_html=True)