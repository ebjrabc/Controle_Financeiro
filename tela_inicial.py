import tkinter as tk
import subprocess
import os

# Função para executar um script Python
def executar_script(nome_arquivo):
    caminho = os.path.join(os.getcwd(), nome_arquivo)
    subprocess.run(["python", caminho])

# Criando a janela principal
janela = tk.Tk()
janela.title("Sistema Financeiro")
janela.geometry("400x300")
janela.configure(bg="#f0f0f0")

# Título
titulo = tk.Label(janela, text="Tela Inicial", font=("Arial", 16, "bold"), bg="#f0f0f0")
titulo.pack(pady=20)

# Botões
botoes = [
    ("Cadastro de Categorias", "dim_cad_categoria.py"),
    ("Fluxo de Caixa", "ft_fluxo_caixa.py"),
    ("Relatório de Categorias", "relatorio_categoria.py"),
    ("Relatório de Fluxo de Caixa", "relatorio_fluxo_caixa.py")
]

for texto, arquivo in botoes:
    btn = tk.Button(janela, text=texto, width=30, height=2,
                    command=lambda a=arquivo: executar_script(a),
                    bg="#4CAF50", fg="white", font=("Arial", 12))
    btn.pack(pady=5)

# Iniciar a interface
janela.mainloop()