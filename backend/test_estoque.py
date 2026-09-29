import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from decimal import Decimal
from io import StringIO
from unittest.mock import patch

from backend import Controle_de_estoque as estoque


class RegrasEstoqueTest(unittest.TestCase):
    def setUp(self):
        self.produtos = [
            {"codigo": 1, "nome": "Arroz", "valor": Decimal("10.00"), "quantidade": 5},
            {"codigo": 2, "nome": "Feijão", "valor": Decimal("20.00"), "quantidade": 8},
        ]

    def test_movimentacoes_afetam_apenas_produto_escolhido_sem_terminal(self):
        with patch('builtins.input', side_effect=AssertionError("Usou input")), \
                patch('builtins.print', side_effect=AssertionError("Usou print")):
            self.assertEqual(estoque.dar_entrada(self.produtos, 2, 3), 11)
            self.assertEqual(estoque.dar_saida(self.produtos, 2, 4), 7)
        self.assertEqual(self.produtos[0]['quantidade'], 5)
        self.assertEqual(self.produtos[1]['quantidade'], 7)

    def test_saida_total_e_estoque_insuficiente(self):
        self.assertEqual(estoque.dar_saida(self.produtos, 2, 8), 0)
        antes = deepcopy(self.produtos)
        with self.assertRaisesRegex(ValueError, "Estoque insuficiente"):
            estoque.dar_saida(self.produtos, 2, 1)
        self.assertEqual(self.produtos, antes)

    def test_quantidades_invalidas_nao_alteram_estoque(self):
        for operacao in (estoque.dar_entrada, estoque.dar_saida):
            for quantidade in (0, -1, 1.5, True, float('nan'), float('inf')):
                with self.subTest(operacao=operacao.__name__, quantidade=quantidade):
                    antes = deepcopy(self.produtos)
                    with self.assertRaises(ValueError):
                        operacao(self.produtos, 2, quantidade)
                    self.assertEqual(self.produtos, antes)

    def test_produto_inexistente_e_lista_vazia(self):
        for operacao in (estoque.dar_entrada, estoque.dar_saida):
            for produtos in (self.produtos, []):
                with self.subTest(operacao=operacao.__name__, produtos=produtos):
                    antes = deepcopy(produtos)
                    with self.assertRaisesRegex(ValueError, "Produto não encontrado"):
                        operacao(produtos, 99, 1)
                    self.assertEqual(produtos, antes)

    def test_cadastro_e_codigo_duplicado(self):
        novo = estoque.adicionar_produto(self.produtos, 3, ' Café ', 15.0, 0)
        self.assertEqual(novo['nome'], 'Café')
        antes = deepcopy(self.produtos)
        with self.assertRaisesRegex(ValueError, "Já existe"):
            estoque.adicionar_produto(self.produtos, 3, 'Outro', 5.0, 1)
        self.assertEqual(self.produtos, antes)

    def test_cadastro_invalido_nao_insere_produto(self):
        for nome, valor, quantidade in [
            (' ', 10, 1), ('A', 0, 1), ('A', -1, 1),
            ('A', float('nan'), 1), ('A', float('inf'), 1),
            ('A', 10, -1), ('A', 10, 1.5),
        ]:
            with self.subTest(nome=nome, valor=valor, quantidade=quantidade):
                antes = deepcopy(self.produtos)
                with self.assertRaises(ValueError):
                    estoque.adicionar_produto(self.produtos, 3, nome, valor, quantidade)
                self.assertEqual(self.produtos, antes)

    def test_precos_sao_armazenados_em_centavos_sem_perder_precisao(self):
        for valor, esperado in [
            ("0,10", "0.10"), ("10,100", "10.10"),
            (" 10.00 ", "10.00"), (10, "10.00"), (10.1, "10.10"),
            (Decimal("10.10"), "10.10"),
            ("9007199254740993,01", "9007199254740993.01"),
            ("123456789012345678901234567890,12", "123456789012345678901234567890.12"),
        ]:
            with self.subTest(valor=valor):
                produto = estoque.adicionar_produto([], 1, "Arroz", valor, 1)
                self.assertIsInstance(produto['valor'], Decimal)
                self.assertEqual(str(produto['valor']), esperado)

    def test_fracoes_de_centavo_nao_cadastram_nem_alteram(self):
        for valor in ("0,001", "2.675", "10,101", Decimal("0.001"), 2.675):
            with self.subTest(valor=valor):
                antes = deepcopy(self.produtos)
                with self.assertRaisesRegex(ValueError, 'duas casas decimais'):
                    estoque.adicionar_produto(self.produtos, 3, "Café", valor, 1)
                with self.assertRaisesRegex(ValueError, 'duas casas decimais'):
                    estoque.atualizar_produto(self.produtos, 2, "valor", valor)
                self.assertEqual(self.produtos, antes)

    def test_preco_malformado_ou_nao_finito_retorna_erro_de_validacao(self):
        for valor in ("10,5.0", "10.", "abc", "", "1e999999999", "1_000",
                      "NaN", "sNaN", "Infinity", Decimal("sNaN"), True):
            with self.subTest(valor=valor):
                antes = deepcopy(self.produtos)
                with self.assertRaises(ValueError):
                    estoque.adicionar_produto(self.produtos, 3, "Café", valor, 1)
                self.assertEqual(self.produtos, antes)

    def test_alteracao_de_preco_preserva_centavos(self):
        produto = estoque.atualizar_produto(self.produtos, 2, "valor", "0,10")
        self.assertIsInstance(produto['valor'], Decimal)
        self.assertEqual(str(produto['valor']), "0.10")
        self.assertEqual(estoque.pesquisar_produtos(self.produtos, '0,1'), [produto])

    def test_alteracao_valida_e_invalida(self):
        for campo, valor in [('nome', ' Café '), ('valor', 30.0), ('quantidade', 0)]:
            estoque.atualizar_produto(self.produtos, 2, campo, valor)
        self.assertEqual(self.produtos[1], {
            'codigo': 2, 'nome': 'Café', 'valor': 30.0, 'quantidade': 0,
        })
        for campo, valor in [('nome', ' '), ('valor', -1), ('valor', float('nan')),
                             ('quantidade', -1), ('codigo', 3)]:
            with self.subTest(campo=campo, valor=valor):
                antes = deepcopy(self.produtos)
                with self.assertRaises(ValueError):
                    estoque.atualizar_produto(self.produtos, 2, campo, valor)
                self.assertEqual(self.produtos, antes)

    def test_busca_por_codigo_nome_e_valor(self):
        for busca in ('2', 'Feijão', 'FEIJÃO', 'FeI', 'JÃO', ' fei ',
                      '20', '20.0', '20.00', '20,0', '20,00', '20,000'):
            with self.subTest(busca=busca):
                self.assertEqual(estoque.pesquisar_produtos(self.produtos, busca), [self.produtos[1]])
        for busca in ('ausente', '', '   '):
            with self.subTest(busca=busca):
                self.assertEqual(estoque.pesquisar_produtos(self.produtos, busca), [])

    def test_busca_parcial_retorna_todos_os_nomes_correspondentes(self):
        integral = estoque.adicionar_produto(self.produtos, 3, 'Arroz integral', 15.5, 4)
        self.assertEqual(estoque.pesquisar_produtos(self.produtos, 'ARR'),
                         [self.produtos[0], integral])
        for busca in ('15.50', '15,50', ' 15,5 '):
            with self.subTest(busca=busca):
                self.assertEqual(estoque.pesquisar_produtos(self.produtos, busca), [integral])

    def test_busca_nao_usa_prefixos_de_codigos_ou_valores(self):
        estoque.adicionar_produto(self.produtos, 21, 'Café', 200.0, 1)
        self.assertEqual(estoque.pesquisar_produtos(self.produtos, '2'), [self.produtos[1]])
        self.assertEqual(estoque.pesquisar_produtos(self.produtos, '20.00'), [self.produtos[1]])
        self.assertEqual(estoque.pesquisar_produtos(self.produtos, '200.'), [])

    def test_busca_por_preco_nao_arredonda_e_preserva_busca_por_nome(self):
        produto = estoque.adicionar_produto(self.produtos, 3, 'Café', '2,67', 1)
        self.assertEqual(estoque.pesquisar_produtos(self.produtos, '2.67'), [produto])
        self.assertEqual(estoque.pesquisar_produtos(self.produtos, '2.675'), [])
        for busca in ('nan', 'sNaN', 'inf', '0', '-1', '200.', '1e999999999'):
            with self.subTest(busca=busca):
                self.assertEqual(estoque.pesquisar_produtos(self.produtos, busca), [])
        nome_numerico = estoque.adicionar_produto(self.produtos, 4, 'Peça 2.675', '5', 1)
        self.assertEqual(estoque.pesquisar_produtos(self.produtos, '2.675'), [nome_numerico])

    def test_exclusao(self):
        estoque.excluir_produto(self.produtos, 2)
        self.assertEqual([p['codigo'] for p in self.produtos], [1])
        with self.assertRaisesRegex(ValueError, 'Produto não encontrado'):
            estoque.excluir_produto(self.produtos, 2)


class TerminalEstoqueTest(unittest.TestCase):
    def test_terminal_preserva_decimal_do_cadastro_a_listagem_e_alteracao(self):
        produtos = []
        with patch('builtins.input', side_effect=['1', 'Arroz', '9007199254740993,01', '5']), \
                redirect_stdout(StringIO()):
            estoque.cadastrar_produto(produtos)
        self.assertIsInstance(produtos[0]['valor'], Decimal)
        self.assertEqual(str(produtos[0]['valor']), '9007199254740993.01')
        saida = StringIO()
        with redirect_stdout(saida):
            estoque.listar_produtos(produtos)
        self.assertIn('Valor: 9007199254740993.01', saida.getvalue())
        with patch('builtins.input', side_effect=['1', '2', '0,10']), \
                redirect_stdout(StringIO()):
            estoque.alterar_estoque(produtos)
        self.assertEqual(str(produtos[0]['valor']), '0.10')

    def test_cadastro_e_alteracao_aceitam_virgula_e_ponto(self):
        for valor_inicial, novo_valor in [('10,50', '20.75'), ('10.50', '20,75')]:
            with self.subTest(valor_inicial=valor_inicial, novo_valor=novo_valor):
                produtos = []
                with patch('builtins.input', side_effect=['1', 'Arroz', valor_inicial, '5']), \
                        redirect_stdout(StringIO()):
                    estoque.cadastrar_produto(produtos)
                self.assertEqual(produtos[0]['valor'], 10.5)
                with patch('builtins.input', side_effect=['1', '2', novo_valor]), \
                        redirect_stdout(StringIO()):
                    estoque.alterar_estoque(produtos)
                self.assertEqual(produtos[0]['valor'], 20.75)

    def test_preco_invalido_nao_cadastra_nem_altera_produto(self):
        for valor in ('10,5.0', '10,,50', 'abc', '', '-1,50', '0,00', 'nan', 'inf',
                      '0,001', '2,675'):
            with self.subTest(valor=valor):
                produtos = []
                with patch('builtins.input', side_effect=['1', 'Arroz', valor, '5']), \
                        redirect_stdout(StringIO()):
                    estoque.cadastrar_produto(produtos)
                self.assertEqual(produtos, [])
                estoque.adicionar_produto(produtos, 1, 'Arroz', 10.5, 5)
                antes = deepcopy(produtos)
                with patch('builtins.input', side_effect=['1', '2', valor]), \
                        redirect_stdout(StringIO()):
                    estoque.alterar_estoque(produtos)
                self.assertEqual(produtos, antes)

    def test_entrada_invalida_e_regra_exibem_mensagens(self):
        for respostas, mensagem in [(['abc'], 'números inteiros'),
                                     (['99', '1'], 'Produto não encontrado')]:
            with self.subTest(respostas=respostas):
                saida = StringIO()
                with patch('builtins.input', side_effect=respostas), redirect_stdout(saida):
                    estoque.registrar_saida([])
                self.assertIn(mensagem, saida.getvalue())

    def test_fluxo_completo_do_menu(self):
        respostas = [
            '1', '1', 'Arroz', '10', '5',
            '1', '2', 'Feijão', '20.5', '8',
            '6', '2', '3', '7', '2', '4',
            '4', '2', '1', 'Café', '3', 'AFÉ', '2',
            '5', '1', '7', '2', '8', '7', '2', '7',
            '9', '0',
        ]
        saida = StringIO()
        with patch('builtins.input', side_effect=respostas), redirect_stdout(saida):
            estoque.main()
        for mensagem in (
            'Entrada registrada! Estoque atual: 11',
            'Saída registrada! Estoque atual: 7',
            'Produto alterado com sucesso!', 'Nome: Café', 'Quantidade: 7',
            'Produto excluído com sucesso!', 'Estoque insuficiente.',
            'Saída registrada! Estoque atual: 0', 'Opção inválida.',
            'Nome: Arroz\nValor: 10.00\nQuantidade: 5',
        ):
            self.assertIn(mensagem, saida.getvalue())
        self.assertEqual(saida.getvalue().count('Nome: Café\nValor: 20.50\nQuantidade: 7'), 2)


if __name__ == '__main__':
    unittest.main()
