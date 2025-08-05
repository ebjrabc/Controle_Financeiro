import streamlit as st
import sqlite3
import pandas as pd
import os
import subprocess
import sys

def dim_rel_categoria():
    # 🛠️ Configuração da página
    st.set_page_config(page_title='📊 Relatório de Categorias', layout='wide')

    # 🎨 Estilo visual
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
        <div class="titulo-menor">📊 Relatório de Categorias</div>
        <br>
    """, unsafe_allow_html=True)

    # 🔗 Conecta ao banco
    conn = sqlite3.connect(r'Dados\\financeiro.db', check_same_thread=False)
    df = pd.read_sql_query('SELECT * FROM categoria', conn)
    conn.close()

    # 🏷️ Renomeia colunas
    df.rename(columns={
        'id': 'Código',
        'nm_categoria': 'Categoria',
        'nm_grupo': 'Grupo',
        'nm_tipo': 'Tipo',
        'in_fixo': 'Fixo',
        'in_ativo': 'Ativo'
    }, inplace=True)

    # 🔄 Converte valores booleanos
    df['Ativo'] = df['Ativo'].map({'s': 'Sim', 'n': 'Não'})
    df['Fixo'] = df['Fixo'].map({'s': 'Sim', 'n': 'Não'})

    # 📋 Exibe a tabela
    st.dataframe(df, use_container_width=True)