import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
from unittest.mock import patch

import Controle_de_estoque as estoque


class RegrasEstoqueTest(unittest.TestCase):
    def setUp(self):
        self.produtos = [
            {"codigo": 1, "nome": "Arroz", "valor": 10.0, "quantidade": 5},
            {"codigo": 2, "nome": "Feijão", "valor": 20.0, "quantidade": 8},
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
        for busca in ('2', 'Feijão', '20.0'):
            self.assertEqual(estoque.pesquisar_produtos(self.produtos, busca), [self.produtos[1]])
        self.assertEqual(estoque.pesquisar_produtos(self.produtos, 'ausente'), [])

    def test_exclusao(self):
        estoque.excluir_produto(self.produtos, 2)
        self.assertEqual([p['codigo'] for p in self.produtos], [1])
        with self.assertRaisesRegex(ValueError, 'Produto não encontrado'):
            estoque.excluir_produto(self.produtos, 2)


class TerminalEstoqueTest(unittest.TestCase):
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
            '1', '2', 'Feijão', '20', '8',
            '6', '2', '3', '7', '2', '4',
            '4', '2', '1', 'Café', '3', 'Café', '2',
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
        ):
            self.assertIn(mensagem, saida.getvalue())


if __name__ == '__main__':
    unittest.main()
