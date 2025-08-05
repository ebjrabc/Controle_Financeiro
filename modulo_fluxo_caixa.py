def ft_fluxo_caixa():
    import streamlit as st
    import sqlite3
    import subprocess
    import sys
    import time
    from datetime import date
    import os

    # 📁 Garantir pasta e banco
    os.makedirs("Dados", exist_ok=True)
    db_path = os.path.join("Dados", "financeiro.db")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()

    # 🛠️ Criação da tabela
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fluxo_caixa (
            cd_transacao INTEGER PRIMARY KEY AUTOINCREMENT,
            cd_categoria INTEGER,
            nr_nota_fiscal INTEGER,
            dt_transacao DATE NOT NULL,
            vl_valor_fluxo DOUBLE NOT NULL,
            in_forma_pgto CHAR NULL,
            FOREIGN KEY (cd_categoria) REFERENCES categoria(cd_categoria)
        )
    """)
    conn.commit()

    st.set_page_config(page_title="💰 Fluxo de Caixa", layout="wide")

    # 🎨 Estilo visual
    st.markdown("""
        <style>
        .block-container { padding-top: 1rem; }
        .titulo-menor { font-size: 22px; font-weight: bold; color: #333333; margin-bottom: 5px; }
        #MainMenu, footer, header { visibility: hidden; }
        </style>
        <div class="titulo-menor">💰 Fluxo de Caixa</div><br>
    """, unsafe_allow_html=True)

    # 📦 Container de entrada
    with st.container():
        #st.subheader("📁 Informações da Transação")
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

    # 🔻 Separador visual
    st.divider()

    # 📦 Container de data e valor
    with st.container():
        #st.subheader("📅 Data e Valor")
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

    # 📦 Container de ações
    mensagem_alerta = None  # 🔔 Variável para armazenar mensagens

    with st.container():
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)

        with col_btn1:
            if st.button("✅ Incluir Transação"):
                if cd_categoria and valor > 0 and data_transacao:
                    # 🔍 Verifica se a nota fiscal já existe
                    if nota_fiscal:
                        nota_existente = cursor.execute(
                            "SELECT cd_transacao FROM fluxo_caixa WHERE nr_nota_fiscal = ?", (nota_fiscal,)
                        ).fetchone()

                        if nota_existente:
                            mensagem_alerta = f"⚠️ Nota fiscal nº {nota_fiscal} já está registrada no sistema."
                        else:
                            try:
                                cursor.execute("""
                                    INSERT INTO fluxo_caixa (nr_nota_fiscal, dt_transacao, cd_categoria, vl_valor_fluxo, in_forma_pgto)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (
                                    nota_fiscal if nota_fiscal else None,
                                    data_transacao,
                                    cd_categoria,
                                    valor,
                                    in_forma_pgto
                                ))
                                conn.commit()
                                mensagem_alerta = "✅ Transação incluída com sucesso!"
                                for key in st.session_state.keys():
                                    del st.session_state[key]
                                time.sleep(1.5)
                                st.rerun()
                            except Exception as e:
                                mensagem_alerta = f"❌ Erro ao incluir transação: {e}"
                    else:
                        try:
                            cursor.execute("""
                                INSERT INTO fluxo_caixa (nr_nota_fiscal, dt_transacao, cd_categoria, vl_valor_fluxo, in_forma_pgto)
                                VALUES (?, ?, ?, ?, ?)
                            """, (
                                None,
                                data_transacao,
                                cd_categoria,
                                valor,
                                in_forma_pgto
                            ))
                            conn.commit()
                            mensagem_alerta = "✅ Transação incluída com sucesso!"
                            for key in st.session_state.keys():
                                del st.session_state[key]
                            time.sleep(1.5)
                            st.rerun()
                        except Exception as e:
                            mensagem_alerta = f"❌ Erro ao incluir transação: {e}"
                else:
                    mensagem_alerta = "⚠️ Preencha os campos obrigatórios."

        with col_btn2:
            if st.button("🗑️ Excluir Transação"):
                st.session_state.confirmar_exclusao = True

        with col_btn3:
            if st.button("✏️ Alterar Transação"):
                st.session_state.alterar_transacao = True

        with col_btn4:
            if st.button("📊 Relatório"):
                subprocess.Popen([sys.executable, "-m", "streamlit", "run", "relatorio_fluxo_caixa.py"])
                mensagem_alerta = "✅ Relatório aberto em nova aba. Verifique seu navegador."

    # 🖥️ Exibe a mensagem em tela cheia
    if mensagem_alerta:
        if "⚠️" in mensagem_alerta:
            st.warning(mensagem_alerta)
        elif "❌" in mensagem_alerta:
            st.error(mensagem_alerta)
        else:
            st.success(mensagem_alerta)
        time.sleep(3)