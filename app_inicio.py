import subprocess
import os
import sys

# Instalar Flask automaticamente se não estiver instalado
try:
    import flask
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])

from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

# Função para executar scripts
def executar_script(nome_arquivo):
    caminho = os.path.join(os.getcwd(), nome_arquivo)
    subprocess.Popen([sys.executable, caminho])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/executar/<script>")
def executar(script):
    scripts = {
        "cadastro": "dim_cad_categoria.py",
        "fluxo": "ft_fluxo_caixa.py",
        "rel_categoria": "relatorio_categoria.py",
        "rel_fluxo": "relatorio_fluxo_caixa.py"
    }
    if script in scripts:
        executar_script(scripts[script])
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)