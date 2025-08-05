def dim_cad_categoria():
    import streamlit as st
    import sqlite3
    import os

    os.makedirs("Dados", exist_ok=True)
    db_path = os.path.join("Dados", "financeiro.db")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categoria (
            cd_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
            nm_categoria TEXT NOT NULL,
            nm_grupo TEXT NOT NULL,
            nm_tipo TEXT NOT NULL,
            in_fixo TEXT DEFAULT 'n',
            in_ativo TEXT DEFAULT 's'
        )
    """)
    conn.commit()

    st.set_page_config(page_title='📂 Cadastro de Categorias', layout='wide')

    st.markdown("""
        <style>
        .block-container {
            padding-top: 1rem;
        }
        .titulo-menor {
            font-size: 22px;
            font-weight: bold;
            color: #333333;
            margin-bottom: 5px;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        <div class="titulo-menor">📂 Cadastro de Categorias</div>
        <br>
    """, unsafe_allow_html=True)

    with st.container():
        #st.subheader("📅 Data e Valor")
        col1_data, col2_data, col3_data = st.columns(3)
                        
        with col1_data:
            # 🔍 Grupos existentes
            grupos_existentes = cursor.execute(
                "SELECT DISTINCT nm_grupo FROM categoria WHERE in_ativo = 's'"
            ).fetchall()
            grupo_opcoes = sorted([g[0] for g in grupos_existentes])

            grupo_selecionado = st.selectbox("Grupo da Categoria (existente ou novo)", options=grupo_opcoes + ["Novo_Cadastro"])
            grupo = st.text_input("Digite novo grupo da categoria") if grupo_selecionado == "Novo_Cadastro" else grupo_selecionado

        with col2_data:
            categorias_do_grupo = cursor.execute(
                "SELECT nm_categoria FROM categoria WHERE nm_grupo = ? AND in_ativo = 's'", (grupo,)
            ).fetchall()
            nome_opcoes = sorted(list(set([cat[0] for cat in categorias_do_grupo])))

            nome_selecionado = st.selectbox("Nome da Categoria (existente ou novo)", options=nome_opcoes + ["Novo_Cadastro"])
            nome = st.text_input("Digite novo nome da categoria") if nome_selecionado == "Novo_Cadastro" else nome_selecionado

        with col3_data:
            tipo = st.selectbox("Tipo da Categoria", options=["Entrada", "Despesa"])

    # 🔻 Separador visual
    st.divider() 
 
    with st.container():    
        col_1 = st.columns(1)
        fixa = st.checkbox("Esta categoria é fixa? (Ex: aluguel, salário, mensalidades)")
        in_fixo = "s" if fixa else "n"
        st.caption("✔️ Se marcado, indica que a categoria ocorre regularmente todo mês.")

    # 🔻 Separador visual
    st.divider()

    with st.container():
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
        with col_btn1:
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

        with col_btn2:
            if nome_selecionado != "Novo_Cadastro":
                if st.button("🗑️ Excluir Categoria"):
                    st.session_state.confirmar_exclusao = True

        with col_btn3:
            if st.button("✏️ Alterar Categoria"):
                st.session_state.alterar_categoria = True

        with col_btn4:
            if st.button("📊 Relatório"):
                from relatorio_categoria import mostrar_relatorio_categoria
                mostrar_relatorio_categoria()

        if st.session_state.get("confirmar_exclusao", False):
            st.warning(f"Tem certeza que deseja excluir a categoria **{nome_selecionado}** do grupo **{grupo}**?")
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