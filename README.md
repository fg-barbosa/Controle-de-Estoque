# Controle de Estoque

Programa em Python para controlar produtos pelo terminal. Permite cadastrar itens, consultar o estoque e registrar entradas e saídas usando um menu de opções.

## O que dá para fazer

- Cadastrar produtos com código, nome, valor e quantidade.
- Listar os produtos e buscar por código, nome ou valor.
- Buscar por parte do nome, sem diferenciar maiúsculas e minúsculas.
- Alterar o nome, o valor ou a quantidade de um produto.
- Remover produtos.
- Registrar entradas e saídas do estoque.

O programa impede códigos duplicados, nomes vazios, valores inválidos e saídas maiores que a quantidade disponível.

## Como executar

É necessário ter o Python 3 instalado. O projeto usa apenas a biblioteca padrão, então não precisa instalar pacotes adicionais.

Baixe o repositório ou clone com o Git:

```bash
git clone https://github.com/fg-barbosa/Controle-de-Estoque.git
cd Controle-de-Estoque
```

Na pasta do projeto, execute:

```bash
python Controle_de_estoque.py
```

No Windows, se o comando `python` não estiver disponível, tente `py`. No Linux e no macOS, pode ser necessário usar `python3`.

O menu será exibido no terminal:

```text
===== ESTOQUE =====
1 - Cadastrar produto
2 - Listar produtos
3 - Buscar produto
4 - Alterar estoque
5 - Remover produto
6 - Registrar entrada
7 - Registrar saída
0 - Sair
```

Para experimentar, escolha `1` e cadastre um produto com código `1`, nome `Arroz`, valor `10.50` e quantidade `5`. Depois, use a opção `6` para registrar a entrada de mais `3` unidades desse código. Ao listar os produtos na opção `2`, a quantidade será `8`.

Na opção `3`, digite `ARR` para encontrar o produto `Arroz`. A busca ignora espaços no começo e no fim do texto; se você deixar o campo vazio, nenhum produto será encontrado. Para buscar por código, digite o código completo. Para valores, pode usar vírgula ou ponto: `10,50` e `10.50` encontram o mesmo preço.

Na listagem e nos resultados da busca, os valores aparecem sempre com duas casas decimais, como `10.00`.

No cadastro e na alteração de preços, use vírgula ou ponto como separador decimal, por exemplo `10,50` ou `10.50`, sem separador de milhar. As quantidades devem ser números inteiros; nas entradas e saídas, devem ser maiores que zero.

## Testes

Na pasta do projeto, execute:

```bash
python -m unittest -v
```

Os testes verificam cadastro, busca, alteração, exclusão, movimentações de estoque e o fluxo do menu, incluindo situações como dados inválidos e estoque insuficiente.

## Arquivos principais

- `Controle_de_estoque.py`: funções do estoque e interação pelo terminal. As regras ficam em funções separadas da leitura e exibição de dados.
- `test_estoque.py`: testes automatizados com `unittest`.

## Limitações atuais

Os produtos ficam apenas na memória: ao encerrar o programa, os dados são perdidos. Ainda não há salvamento em arquivo ou banco de dados.
