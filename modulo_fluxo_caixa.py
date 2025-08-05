def ft_fluxo_caixa():
    import streamlit as st
    import sqlite3
    import subprocess
    import sys
    import time
    from datetime import date
    import os

    if "codigo_usuario" not in st.session_state:
        st.error("Usuário não autenticado. Faça login para continuar.")
        st.stop()

    cd_usuario = st.session_state["codigo_usuario"]

    # Criar pasta e banco
    os.makedirs("Dados", exist_ok=True)
    db_path = os.path.join("Dados", "financeiro.db")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()

    # Criar tabela com coluna cd_usuario
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fluxo_caixa (
            cd_transacao INTEGER PRIMARY KEY AUTOINCREMENT,
            cd_usuario INTEGER NOT NULL,
            cd_categoria INTEGER,
            nr_nota_fiscal INTEGER,
            dt_transacao DATE NOT NULL,
            vl_valor_fluxo DOUBLE NOT NULL,
            in_forma_pgto CHAR NULL,
            FOREIGN KEY (cd_categoria) REFERENCES categoria(cd_categoria),
            FOREIGN KEY (cd_usuario) REFERENCES usuario(cd_usuario)
        )
    """)
    conn.commit()

    st.set_page_config(page_title="💰 Fluxo de Caixa", layout="wide")

    st.markdown("""
        <style>
        .block-container { padding-top: 1rem; }
        .titulo-menor { font-size: 22px; font-weight: bold; color: #333333; margin-bottom: 5px; }
        #MainMenu, footer, header { visibility: hidden; }
        </style>
        <div class="titulo-menor">💰 Fluxo de Caixa</div><br>
    """, unsafe_allow_html=True)

    # Entradas principais
    with st.container():
        col1, col2, col3, col4 = st.columns(4)

        categorias_ativas = cursor.execute(
            "SELECT cd_categoria, nm_categoria, nm_grupo, nm_tipo FROM categoria WHERE in_ativo = 's'"
        ).fetchall()

        with col1:
            grupos = sorted(set(cat[2] for cat in categorias_ativas))
            grupo_selecionado = st.selectbox("Grupo da Categoria", options=grupos)

        with col2:
            categorias_do_grupo = [cat for cat in categorias_ativas if cat[2] == grupo_selecionado]
            nomes = sorted(set(cat[1] for cat in categorias_do_grupo))
            nome_selecionado = st.selectbox("Nome da Categoria", options=nomes)
            categoria_escolhida = next((cat for cat in categorias_do_grupo if cat[1] == nome_selecionado), None)

        with col3:
            if categoria_escolhida:
                tipo_selecionado = categoria_escolhida[3]
                cd_categoria = categoria_escolhida[0]
                st.text_input("Tipo da Categoria", value=tipo_selecionado, disabled=True)
            else:
                st.warning("⚠️ Categoria não encontrada.")
                st.stop()

        with col4:
            nota_fiscal = st.number_input("Número da Nota Fiscal (opcional)", key="nota_fiscal", step=1, format="%d")

    st.divider()

    with st.container():
        col1_data, col2_data, col3_data, col4_data, col5_data = st.columns(5)

        meses = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }
        anos = list(range(2000, date.today().year + 1))

        dia_selecionado = col1_data.number_input("Dia", min_value=1, max_value=31, step=1, key="dia_selecionado", format="%d")
        mes_selecionado = col2_data.selectbox("Mês", options=list(meses.keys()), format_func=lambda x: meses[x])
        ano_selecionado = col3_data.selectbox("Ano", options=anos, index=anos.index(date.today().year))
        data_transacao = f"{int(dia_selecionado):02d}/{mes_selecionado:02d}/{ano_selecionado:04d}"

        forma_pgto = col4_data.selectbox("Forma de Pagamento", options=["À vista", "Voucher"])
        in_forma_pgto = {"À vista": "av", "Voucher": "vo"}[forma_pgto]

        valor = col5_data.number_input("Valor da transação", key="valor", format="%.2f")

    st.divider()

    mensagem_alerta = None

    # Função para listar transações do usuário (usada para excluir e alterar)
    def listar_transacoes_usuario():
        return cursor.execute("""
            SELECT cd_transacao, dt_transacao, vl_valor_fluxo, nr_nota_fiscal, cd_categoria
            FROM fluxo_caixa
            WHERE cd_usuario = ?
            ORDER BY dt_transacao DESC
        """, (cd_usuario,)).fetchall()

    with st.container():
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)

        # INCLUIR
        with col_btn1:
            if st.button("✅ Incluir Transação"):
                if cd_categoria and valor > 0 and data_transacao:
                    if nota_fiscal:
                        nota_existente = cursor.execute(
                            "SELECT cd_transacao FROM fluxo_caixa WHERE nr_nota_fiscal = ? AND cd_usuario = ?",
                            (nota_fiscal, cd_usuario)
                        ).fetchone()

                        if nota_existente:
                            mensagem_alerta = f"⚠️ Nota fiscal nº {nota_fiscal} já está registrada para você."
                        else:
                            try:
                                cursor.execute("""
                                    INSERT INTO fluxo_caixa (cd_usuario, nr_nota_fiscal, dt_transacao, cd_categoria, vl_valor_fluxo, in_forma_pgto)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                """, (
                                    cd_usuario,
                                    nota_fiscal if nota_fiscal else None,
                                    data_transacao,
                                    cd_categoria,
                                    valor,
                                    in_forma_pgto
                                ))
                                conn.commit()
                                mensagem_alerta = "✅ Transação incluída com sucesso!"
                                for key in list(st.session_state.keys()):
                                    del st.session_state[key]
                                time.sleep(1)
                                st.experimental_rerun()
                            except Exception as e:
                                mensagem_alerta = f"❌ Erro ao incluir transação: {e}"
                    else:
                        try:
                            cursor.execute("""
                                INSERT INTO fluxo_caixa (cd_usuario, nr_nota_fiscal, dt_transacao, cd_categoria, vl_valor_fluxo, in_forma_pgto)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (
                                cd_usuario,
                                None,
                                data_transacao,
                                cd_categoria,
                                valor,
                                in_forma_pgto
                            ))
                            conn.commit()
                            mensagem_alerta = "✅ Transação incluída com sucesso!"
                            for key in list(st.session_state.keys()):
                                del st.session_state[key]
                            time.sleep(1)
                            st.experimental_rerun()
                        except Exception as e:
                            mensagem_alerta = f"❌ Erro ao incluir transação: {e}"
                else:
                    mensagem_alerta = "⚠️ Preencha os campos obrigatórios."

        # EXCLUIR
        with col_btn2:
            if st.button("🗑️ Excluir Transação"):
                transacoes = listar_transacoes_usuario()
                if not transacoes:
                    st.warning("⚠️ Nenhuma transação para excluir.")
                else:
                    # Selecionar transação para excluir
                    options = [f"{t[0]} - {t[1]} - R$ {t[2]:.2f}" for t in transacoes]
                    selecionado = st.selectbox("Selecione a transação para excluir", options)
                    if st.button("Confirmar exclusão"):
                        cd_transacao_selecionada = int(selecionado.split(" - ")[0])
                        try:
                            cursor.execute("DELETE FROM fluxo_caixa WHERE cd_transacao = ? AND cd_usuario = ?", (cd_transacao_selecionada, cd_usuario))
                            conn.commit()
                            mensagem_alerta = "✅ Transação excluída com sucesso!"
                            time.sleep(1)
                            st.experimental_rerun()
                        except Exception as e:
                            mensagem_alerta = f"❌ Erro ao excluir transação: {e}"

        # ALTERAR
        with col_btn3:
            if st.button("✏️ Alterar Transação"):
                transacoes = listar_transacoes_usuario()
                if not transacoes:
                    st.warning("⚠️ Nenhuma transação para alterar.")
                else:
                    options = [f"{t[0]} - {t[1]} - R$ {t[2]:.2f}" for t in transacoes]
                    selecionado = st.selectbox("Selecione a transação para alterar", options, key="alterar_select")

                    # Buscar dados atuais da transação selecionada
                    cd_transacao_sel = int(selecionado.split(" - ")[0])
                    cursor.execute("""
                        SELECT nr_nota_fiscal, dt_transacao, cd_categoria, vl_valor_fluxo, in_forma_pgto
                        FROM fluxo_caixa WHERE cd_transacao = ? AND cd_usuario = ?
                    """, (cd_transacao_sel, cd_usuario))
                    dados = cursor.fetchone()

                    if dados:
                        nota_atual, data_atual, categoria_atual, valor_atual, forma_pgto_atual = dados

                        st.write("### Editar dados da transação selecionada")

                        nota_nova = st.number_input("Número da Nota Fiscal (opcional)", value=nota_atual if nota_atual else 0, step=1, format="%d", key="nota_alterar")
                        
                        # Data editar (parse data_atual dd/mm/yyyy)
                        try:
                            dia_atual, mes_atual, ano_atual = map(int, data_atual.split("/"))
                        except:
                            dia_atual, mes_atual, ano_atual = 1, 1, date.today().year

                        dia_novo = st.number_input("Dia", min_value=1, max_value=31, value=dia_atual, key="dia_alterar")
                        mes_novo = st.selectbox("Mês", options=list(meses.keys()), index=meses.keys().__iter__().__index__(mes_atual) if mes_atual in meses else 0, format_func=lambda x: meses[x], key="mes_alterar")
                        ano_novo = st.selectbox("Ano", options=anos, index=anos.index(ano_atual) if ano_atual in anos else 0, key="ano_alterar")
                        data_nova = f"{dia_novo:02d}/{mes_novo:02d}/{ano_novo:04d}"

                        # Categoria para alterar
                        categorias_do_grupo = [cat for cat in categorias_ativas if cat[2] == grupo_selecionado]
                        nomes = sorted(set(cat[1] for cat in categorias_do_grupo))
                        nome_novo = st.selectbox("Nome da Categoria", options=nomes, index=0, key="nome_alterar")
                        categoria_nova = next((cat for cat in categorias_do_grupo if cat[1] == nome_novo), None)
                        cd_categoria_nova = categoria_nova[0] if categoria_nova else categoria_atual

                        valor_novo = st.number_input("Valor da transação", value=valor_atual, format="%.2f", key="valor_alterar")

                        forma_pgto_novo = st.selectbox("Forma de Pagamento", options=["À vista", "Voucher"], index=0 if forma_pgto_atual == "av" else 1, key="forma_pgto_alterar")
                        in_forma_pgto_novo = {"À vista": "av", "Voucher": "vo"}[forma_pgto_novo]

                        if st.button("Salvar Alterações"):
                            try:
                                cursor.execute("""
                                    UPDATE fluxo_caixa SET
                                        nr_nota_fiscal = ?,
                                        dt_transacao = ?,
                                        cd_categoria = ?,
                                        vl_valor_fluxo = ?,
                                        in_forma_pgto = ?
                                    WHERE cd_transacao = ? AND cd_usuario = ?
                                """, (
                                    nota_nova if nota_nova > 0 else None,
                                    data_nova,
                                    cd_categoria_nova,
                                    valor_novo,
                                    in_forma_pgto_novo,
                                    cd_transacao_sel,
                                    cd_usuario
                                ))
                                conn.commit()
                                mensagem_alerta = "✅ Transação alterada com sucesso!"
                                time.sleep(1)
                                st.experimental_rerun()
                            except Exception as e:
                                mensagem_alerta = f"❌ Erro ao alterar transação: {e}"
                    else:
                        st.warning("⚠️ Transação não encontrada ou você não tem permissão.")

        # RELATÓRIO
        with col_btn4:
            if st.button("📊 Relatório"):
                subprocess.Popen([sys.executable, "-m", "streamlit", "run", "relatorio_fluxo_caixa.py"])
                mensagem_alerta = "✅ Relatório aberto em nova aba. Verifique seu navegador."

    if mensagem_alerta:
        if "⚠️" in mensagem_alerta:
            st.warning(mensagem_alerta)
        elif "❌" in mensagem_alerta:
            st.error(mensagem_alerta)
        else:
            st.success(mensagem_alerta)
        time.sleep(3)
