"""Execute na raiz com: python -m flask --app backend.app run."""

import os
from pathlib import Path
from secrets import compare_digest, token_hex
from threading import Lock

from flask import Flask, flash, redirect, render_template, request, session, url_for

from backend.Controle_de_estoque import adicionar_produto, pesquisar_produtos


def create_app(test_config=None):
    raiz = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(raiz / "frontend"),
        static_folder=str(raiz / "design"),
        static_url_path="/static",
    )
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY") or token_hex(32),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        MAX_CONTENT_LENGTH=16 * 1024,
    )
    if test_config is not None:
        app.config.update(test_config)

    # Cada instância possui seu próprio estoque; não há persistência nesta etapa.
    produtos = []
    lock_estoque = Lock()
    app.extensions["estoque"] = produtos

    @app.context_processor
    def disponibilizar_csrf():
        if "csrf_token" not in session:
            session["csrf_token"] = token_hex(32)
        return {"csrf_token": session["csrf_token"]}

    @app.get("/")
    def index():
        with lock_estoque:
            total = len(produtos)
        return render_template("index.html", total_produtos=total)

    @app.get("/produtos")
    def listar_produtos():
        busca = request.args.get("busca", "").strip()
        with lock_estoque:
            copia_produtos = produtos.copy()
        encontrados = pesquisar_produtos(copia_produtos, busca) if busca else copia_produtos
        return render_template("produtos.html", produtos=encontrados, busca=busca)

    @app.route("/cadastrar", methods=["GET", "POST"])
    def cadastrar():
        dados = request.form if request.method == "POST" else {}
        if request.method == "POST":
            token = session.get("csrf_token", "")
            enviado = request.form.get("csrf_token", "")
            if not token or not compare_digest(token.encode(), enviado.encode()):
                return render_template(
                    "cadastrar.html", dados=dados,
                    erro="O formulário expirou. Tente enviar novamente.",
                ), 400

            try:
                codigo = int(dados.get("codigo", ""))
                quantidade = int(dados.get("quantidade", ""))
            except ValueError:
                return render_template(
                    "cadastrar.html", dados=dados,
                    erro="Informe código e quantidade inteiros.",
                ), 400

            try:
                # A verificação do código e a inserção formam uma única operação.
                with lock_estoque:
                    adicionar_produto(
                        produtos, codigo, dados.get("nome", ""),
                        dados.get("valor", ""), quantidade,
                    )
            except ValueError as erro:
                return render_template("cadastrar.html", dados=dados, erro=str(erro)), 400

            flash("Produto cadastrado com sucesso!", "sucesso")
            return redirect(url_for("listar_produtos"), code=303)

        return render_template("cadastrar.html", dados=dados)

    return app
