from math import isfinite


# Regras do estoque: recebem dados e retornam resultados, sem input ou print.
def obter_produto(produtos, codigo):
    for produto in produtos:
        if produto["codigo"] == codigo:
            return produto
    raise ValueError("Produto não encontrado.")


def validar_dados_produto(nome, valor, quantidade):
    if not nome.strip():
        raise ValueError("O nome não pode estar vazio.")
    if not isfinite(valor) or valor <= 0:
        raise ValueError("O valor deve ser um número finito maior que 0.")
    if type(quantidade) is not int or quantidade < 0:
        raise ValueError("A quantidade deve ser um número inteiro maior ou igual a 0.")


def adicionar_produto(produtos, codigo, nome, valor, quantidade):
    if any(produto["codigo"] == codigo for produto in produtos):
        raise ValueError("Já existe um produto com este código!")
    validar_dados_produto(nome, valor, quantidade)
    produto = {
        "codigo": codigo,
        "nome": nome.strip(),
        "valor": valor,
        "quantidade": quantidade,
    }
    produtos.append(produto)
    return produto


def pesquisar_produtos(produtos, busca):
    return [
        produto for produto in produtos
        if busca in (str(produto["codigo"]), produto["nome"], str(produto["valor"]))
    ]


def atualizar_produto(produtos, codigo, campo, novo_dado):
    produto = obter_produto(produtos, codigo)
    if campo not in ("nome", "valor", "quantidade"):
        raise ValueError("Campo inválido.")
    atualizado = produto.copy()
    atualizado[campo] = novo_dado
    validar_dados_produto(atualizado["nome"], atualizado["valor"], atualizado["quantidade"])
    atualizado["nome"] = atualizado["nome"].strip()
    produto.update(atualizado)
    return produto


def excluir_produto(produtos, codigo):
    produto = obter_produto(produtos, codigo)
    produtos.remove(produto)
    return produto


def validar_movimentacao(quantidade):
    if type(quantidade) is not int or quantidade <= 0:
        raise ValueError("A quantidade deve ser um número inteiro maior que 0.")


def dar_entrada(produtos, codigo, quantidade):
    produto = obter_produto(produtos, codigo)
    validar_movimentacao(quantidade)
    produto["quantidade"] += quantidade
    return produto["quantidade"]


def dar_saida(produtos, codigo, quantidade):
    produto = obter_produto(produtos, codigo)
    validar_movimentacao(quantidade)
    if quantidade > produto["quantidade"]:
        raise ValueError("Estoque insuficiente.")
    produto["quantidade"] -= quantidade
    return produto["quantidade"]


# Interação pelo terminal: lê dados, chama as regras e exibe mensagens.
def exibir_menu():
    print("\n===== ESTOQUE =====")
    print("1 - Cadastrar produto")
    print("2 - Listar produtos")
    print("3 - Buscar produto")
    print("4 - Alterar estoque")
    print("5 - Remover produto")
    print("6 - Registrar entrada")
    print("7 - Registrar saída")
    print("0 - Sair")

    return input("Escolha: ")


def cadastrar_produto(produtos):
    print("Entrando no cadastro de produtos... ")

    try:
        codigo = int(input("Código do produto:"))
        nome = input("Nome do produto: ").strip()
        valor = float(input("Valor do produto: "))
        quantidade = int(input("Quantidade de produtos: "))
    except ValueError:
        print("Digite um valor válido!")
        return

    try:
        adicionar_produto(produtos, codigo, nome, valor, quantidade)
        print("Produto cadastrado com sucesso!")
    except ValueError as erro:
        print(erro)


def listar_produtos(produtos):
    if not produtos:
        print("Nenhum produto encontrado.")
        return
    for produto in produtos:
        print(f"Código: {produto['codigo']}\nNome: {produto['nome']}\n"
              f"Valor: {produto['valor']}\nQuantidade: {produto['quantidade']}")


def buscar_produto(produtos):
    busca = input("Digite código, nome ou valor do produto: ")

    encontrados = pesquisar_produtos(produtos, busca)
    listar_produtos(encontrados)


def alterar_estoque(produtos):
    try:
        codigo = int(input("Digite o código do produto: "))
    except ValueError:
        print("Digite um código inteiro válido.")
        return

    try:
        obter_produto(produtos, codigo)
    except ValueError as erro:
        print(erro)
        return

    print("1 - Alterar nome")
    print("2 - Alterar valor")
    print("3 - Alterar quantidade")
    escolha = input("Escolha uma opção: ")
    try:
        if escolha == '1':
            campo = "nome"
            novo_dado = input("Novo nome: ")
        elif escolha == '2':
            campo = "valor"
            novo_dado = float(input("Novo valor: "))
        elif escolha == '3':
            campo = "quantidade"
            novo_dado = int(input("Qual a nova quantidade: "))
        else:
            print("Opção inválida.")
            return
    except ValueError:
        print("Digite um valor válido.")
        return

    try:
        atualizar_produto(produtos, codigo, campo, novo_dado)
        print("Produto alterado com sucesso!")
    except ValueError as erro:
        print(erro)


def remover_produto(produtos):
    try:
        codigo = int(input("Digite o código do produto que deseja excluir: "))
    except ValueError:
        print("Digite um código inteiro válido.")
        return

    try:
        excluir_produto(produtos, codigo)
        print("Produto excluído com sucesso!")
    except ValueError as erro:
        print(erro)


def registrar_entrada(produtos):
    try:
        codigo = int(input("Digite o código do produto: "))
        quantidade = int(input("Quantidade recebida: "))
    except ValueError:
        print("Digite números inteiros válidos.")
        return

    try:
        saldo = dar_entrada(produtos, codigo, quantidade)
        print(f"Entrada registrada! Estoque atual: {saldo}")
    except ValueError as erro:
        print(erro)


def registrar_saida(produtos):
    try:
        codigo = int(input("Digite o código do produto: "))
        quantidade = int(input("Quantidade a remover: "))
    except ValueError:
        print("Digite números inteiros válidos.")
        return

    try:
        saldo = dar_saida(produtos, codigo, quantidade)
        print(f"Saída registrada! Estoque atual: {saldo}")
    except ValueError as erro:
        print(erro)


def main():
    produtos = []

    while True:
        opcao = exibir_menu()

        if opcao == '1':
            cadastrar_produto(produtos)
        elif opcao == '2':
            listar_produtos(produtos)
        elif opcao == '3':
            buscar_produto(produtos)
        elif opcao == '4':
            alterar_estoque(produtos)
        elif opcao == '5':
            remover_produto(produtos)
        elif opcao == '6':
            registrar_entrada(produtos)
        elif opcao == '7':
            registrar_saida(produtos)
        elif opcao == '0':
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
