import re
import unittest
from copy import deepcopy
from decimal import Decimal
from threading import Event, Lock, Thread, current_thread
from unittest.mock import patch

from backend import Controle_de_estoque as estoque
from backend.app import create_app


class FlaskEstoqueTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True, "SECRET_KEY": "chave-apenas-para-testes"})
        self.client = self.app.test_client()
        self.produtos = self.app.extensions["estoque"]

    def cadastrar(self, **alteracoes):
        formulario = self.client.get("/cadastrar").get_data(as_text=True)
        token = re.search(r'name="csrf_token" value="([^"]+)"', formulario).group(1)
        dados = {
            "codigo": "1", "nome": " Arroz ", "valor": "10,50",
            "quantidade": "5", "csrf_token": token,
        }
        dados.update(alteracoes)
        return self.client.post("/cadastrar", data=dados)

    def test_paginas_e_css_carregam(self):
        for caminho, texto in [
            ("/", "Seu estoque em um só lugar"),
            ("/cadastrar", "Salvar produto"),
            ("/produtos", "Nenhum produto cadastrado"),
            ("/static/style.css", ".cabecalho"),
        ]:
            with self.subTest(caminho=caminho):
                resposta = self.client.get(caminho)
                self.assertEqual(resposta.status_code, 200)
                self.assertIn(texto, resposta.get_data(as_text=True))
                resposta.close()

    def test_cadastro_redireciona_lista_e_nao_duplica_ao_recarregar(self):
        resposta = self.cadastrar()
        self.assertEqual(resposta.status_code, 303)
        self.assertEqual(resposta.headers["Location"], "/produtos")
        pagina = self.client.get(resposta.headers["Location"]).get_data(as_text=True)
        self.assertIn("Produto cadastrado com sucesso!", pagina)
        self.assertIn("Arroz", pagina)
        self.assertIn("R$ 10,50", pagina)
        self.client.get("/produtos")
        self.assertEqual(self.produtos, [
            {"codigo": 1, "nome": "Arroz", "valor": 10.5, "quantidade": 5},
        ])
        self.assertIn("<strong>1</strong>", self.client.get("/").get_data(as_text=True))

    def test_preco_com_ponto_e_quantidade_zero(self):
        self.assertEqual(self.cadastrar(valor="20.75", quantidade="0").status_code, 303)
        self.assertEqual(self.produtos[0]["valor"], 20.75)
        self.assertEqual(self.produtos[0]["quantidade"], 0)

    def test_precos_preservam_centavos_no_estoque_e_na_listagem(self):
        for codigo, entrada, esperado in [
            (1, "10,10", "10.10"),
            (2, "10.10", "10.10"),
            (3, "9007199254740993,01", "9007199254740993.01"),
        ]:
            with self.subTest(entrada=entrada):
                resposta = self.cadastrar(codigo=str(codigo), valor=entrada)
                self.assertEqual(resposta.status_code, 303)
                valor = self.produtos[-1]["valor"]
                self.assertIsInstance(valor, Decimal)
                self.assertEqual(valor, Decimal(esperado))
                pagina = self.client.get("/produtos").get_data(as_text=True)
                self.assertIn("<td>R$ " + esperado.replace(".", ",") + "</td>", pagina)

    def test_fracoes_de_centavo_nao_cadastram_nem_alteram_estoque(self):
        self.cadastrar()
        antes = deepcopy(self.produtos)
        for valor in ("0,001", "2,675"):
            with self.subTest(valor=valor):
                resposta = self.cadastrar(codigo="2", valor=valor)
                self.assertEqual(resposta.status_code, 400)
                pagina = resposta.get_data(as_text=True)
                self.assertIn('role="alert"', pagina)
                self.assertIn('value="' + valor + '"', pagina)
                self.assertEqual(self.produtos, antes)

    def test_codigo_duplicado_preserva_estoque_e_formulario(self):
        self.cadastrar()
        antes = deepcopy(self.produtos)
        resposta = self.cadastrar(nome="Feijão")
        self.assertEqual(resposta.status_code, 400)
        pagina = resposta.get_data(as_text=True)
        self.assertIn("Já existe um produto com este código!", pagina)
        self.assertIn('value="Feijão"', pagina)
        self.assertEqual(self.produtos, antes)

    def test_dados_invalidos_nao_inserem_produto(self):
        for campo, valor in [
            ("codigo", "abc"), ("codigo", "1.5"), ("codigo", ""),
            ("nome", " "), ("valor", "abc"), ("valor", "10,5.0"),
            ("valor", "0"), ("valor", "-1"), ("valor", "nan"),
            ("valor", "inf"), ("quantidade", "-1"),
            ("quantidade", "1.5"), ("quantidade", ""),
        ]:
            with self.subTest(campo=campo, valor=valor):
                resposta = self.cadastrar(**{campo: valor})
                self.assertEqual(resposta.status_code, 400)
                self.assertIn('role="alert"', resposta.get_data(as_text=True))
                self.assertEqual(self.produtos, [])

    def test_campos_ausentes_retornam_erro(self):
        self.client.get("/cadastrar")
        with self.client.session_transaction() as sessao:
            token = sessao["csrf_token"]
        resposta = self.client.post("/cadastrar", data={"csrf_token": token})
        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(self.produtos, [])

    def test_busca_por_nome_codigo_e_preco(self):
        self.cadastrar()
        self.cadastrar(codigo="2", nome="Feijão", valor="20.00")
        for busca in ("ARR", " arroz ", "1", "10,50", "10.50"):
            with self.subTest(busca=busca):
                resposta = self.client.get("/produtos", query_string={"busca": busca})
                self.assertEqual(resposta.status_code, 200)
                pagina = resposta.get_data(as_text=True)
                self.assertIn("<td>Arroz</td>", pagina)
                self.assertNotIn("<td>Feijão</td>", pagina)
        vazia = self.client.get("/produtos?busca=ausente").get_data(as_text=True)
        self.assertIn("Nenhum produto encontrado", vazia)
        todos = self.client.get("/produtos?busca=+").get_data(as_text=True)
        self.assertIn("<td>Arroz</td>", todos)
        self.assertIn("<td>Feijão</td>", todos)

    def test_busca_por_preco_inteiro_aceita_formatos_equivalentes(self):
        self.cadastrar(codigo="7", nome="Arroz", valor="10")
        self.cadastrar(codigo="8", nome="Feijão", valor="100")
        for busca in ("10", "10,0", "10.00"):
            with self.subTest(busca=busca):
                resposta = self.client.get("/produtos", query_string={"busca": busca})
                self.assertEqual(resposta.status_code, 200)
                pagina = resposta.get_data(as_text=True)
                self.assertIn("<td>Arroz</td>", pagina)
                self.assertNotIn("<td>Feijão</td>", pagina)

    def test_cadastros_concorrentes_nao_duplicam_codigo(self):
        primeiro_em_validacao = Event()
        segunda_tentativa = Event()
        liberar_primeiro = Event()
        validar_original = estoque.validar_dados_produto

        class LockObservavel:
            def __init__(self):
                self.lock = Lock()

            def __enter__(self):
                if current_thread().name == "cadastro-segundo":
                    segunda_tentativa.set()
                return self.lock.__enter__()

            def __exit__(self, *args):
                return self.lock.__exit__(*args)

        def validar_com_pausa(*args, **kwargs):
            if current_thread().name == "cadastro-primeiro":
                primeiro_em_validacao.set()
                if not liberar_primeiro.wait(timeout=5):
                    raise AssertionError("O primeiro cadastro não foi liberado.")
            elif current_thread().name == "cadastro-segundo":
                # Sem o lock, o segundo pedido também passa pela checagem de código.
                segunda_tentativa.set()
            return validar_original(*args, **kwargs)

        resultados = [None, None]
        erros = []
        threads = []
        with patch("backend.app.Lock", LockObservavel, create=True), \
                patch.object(estoque, "validar_dados_produto", validar_com_pausa):
            app = create_app({"TESTING": True, "SECRET_KEY": "teste-concorrencia"})
            clientes = [app.test_client(), app.test_client()]
            tokens = []
            for cliente in clientes:
                cliente.get("/cadastrar")
                with cliente.session_transaction() as sessao:
                    tokens.append(sessao["csrf_token"])

            def cadastrar_em_paralelo(indice):
                try:
                    resposta = clientes[indice].post("/cadastrar", data={
                        "codigo": "1", "nome": "Produto " + str(indice),
                        "valor": "10,10", "quantidade": "1", "csrf_token": tokens[indice],
                    })
                    resultados[indice] = resposta.status_code
                except Exception as erro:
                    erros.append(erro)

            try:
                primeiro = Thread(target=cadastrar_em_paralelo, args=(0,),
                                  name="cadastro-primeiro", daemon=True)
                threads.append(primeiro)
                primeiro.start()
                self.assertTrue(primeiro_em_validacao.wait(timeout=5))
                segundo = Thread(target=cadastrar_em_paralelo, args=(1,),
                                 name="cadastro-segundo", daemon=True)
                threads.append(segundo)
                segundo.start()
                # Espera a tentativa real do segundo pedido, sem depender de sleeps.
                self.assertTrue(segunda_tentativa.wait(timeout=5))
            finally:
                liberar_primeiro.set()
                for thread in threads:
                    thread.join(timeout=5)

            self.assertFalse(any(thread.is_alive() for thread in threads))
            self.assertEqual(erros, [])
            self.assertEqual(resultados, [303, 400])
            self.assertEqual(len(app.extensions["estoque"]), 1)
            self.assertEqual(app.extensions["estoque"][0]["nome"], "Produto 0")

    def test_nome_e_busca_sao_escapados_no_html(self):
        nome = "<script>alert(1)</script>"
        self.cadastrar(nome=nome)
        pagina = self.client.get("/produtos", query_string={"busca": nome}).get_data(as_text=True)
        self.assertNotIn(nome, pagina)
        self.assertIn("&lt;script&gt;", pagina)

    def test_post_sem_token_ou_com_token_invalido_nao_cadastra(self):
        resposta = self.client.post("/cadastrar", data={"codigo": "1"})
        self.assertEqual(resposta.status_code, 400)
        for token in ("", "invalido", "á"):
            with self.subTest(token=token):
                self.assertEqual(self.cadastrar(csrf_token=token).status_code, 400)
        self.assertEqual(self.produtos, [])

    def test_estoque_compartilhado_entre_clientes_e_isolado_entre_apps(self):
        self.cadastrar()
        outro_cliente = self.app.test_client()
        self.assertIn("<td>Arroz</td>", outro_cliente.get("/produtos").get_data(as_text=True))
        outra_app = create_app({"TESTING": True})
        self.assertEqual(outra_app.extensions["estoque"], [])


if __name__ == "__main__":
    unittest.main()
