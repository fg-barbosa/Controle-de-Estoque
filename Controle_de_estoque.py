def exibir_menu():
    print("\n===== ESTOQUE =====")
    print("1 - Cadastrar produto")
    print("2 - Listar produtos")
    print("3 - Buscar produto")
    print("4 - Alterar estoque")
    print("5 - Remover produto")
    print("0 - Sair")

    return input("Escolha: ")


def cadastrar_produto(produtos):
    print("Entrando no cadastro de produtos... ")

    try:
        codigo = int(input("Código do produto:"))
        for produto in produtos:
            if codigo == produto['codigo']:
                print("Já existe um produto com este código!")
                return
        nome = input("Nome do produto: ").strip()
        if nome == "":
            print("O nome não pode estar vazio.")
            return
        valor = float(input("Valor do produto: "))
        if valor <= 0:
            print("O valor deve ser maior que 0.")
            return
        quantidade = int(input("Quantidade de produtos: "))
        if quantidade < 0:
            print("A quantidade minima é 0.")
            return

        produto = {
            "codigo": codigo,
            "nome": nome,
            "valor": valor,
            "quantidade": quantidade
        }

        produtos.append(produto)
        print("Produto cadastrado com sucesso!")

    except ValueError:
        print("Digite um valor válido!")


def listar_produtos(produtos):
    for produto in produtos:
        print(f"Código: {produto['codigo']}\nNome: {produto['nome']}\nValor: {produto['valor']}")


def buscar_produto(produtos):
    busca = input("Digite código, nome ou valor do produto: ")

    for produto in produtos:
        if busca == str(produto["codigo"]):
            print(f"Produto relacionado: {produto['codigo']}")

        elif busca == produto["nome"]:
            print(f"Produto relacionado: {produto['nome']}")

        elif busca == str(produto["valor"]):
            print(f"Produto relacionado: {produto['valor']}")


def alterar_estoque(produtos):
    try:
        alterar = int(input("Digite o código do produto: "))

        for produto in produtos:
            if alterar == produto["codigo"]:
                print("Escolha uma das opções: ")
                print("1 - Alterar nome: ")
                print("2 - Alterar valor: ")
                print("3 - Alterar quantidade: ")
                escolha_alteracao = input("Escolha uma opção: ")

                if escolha_alteracao == '1':
                    novo_nome = input("Novo nome: ").strip()
                    if novo_nome == "":
                        print("O nome não pode estar vazio.")
                        return
                    produto['nome'] = novo_nome

                elif escolha_alteracao == '2':
                    novo_valor = float(input("Novo valor: "))
                    if novo_valor <= 0:
                        print("O valor deve ser maior que 0.")
                        return
                    produto['valor'] = novo_valor

                elif escolha_alteracao == '3':
                    nova_quantidade = int(input("Qual a nova quantidade: "))
                    if nova_quantidade < 0:
                        print("O mínimo permitido é 0.")
                        return
                    produto['quantidade'] = nova_quantidade

    except ValueError:
        print("Digite um valor valido.")


def remover_produto(produtos):
    excluir_produto = input("Digite o código do produto que deseja excluir: ")

    for produto in produtos:
        if excluir_produto == str(produto["codigo"]):
            produtos.remove(produto)
            print("Produto excluido com sucesso!")
            break


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
        elif opcao == '0':
            break


if __name__ == "__main__":
    main()
