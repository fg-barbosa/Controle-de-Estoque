produtos = []

while True:

    print("\n===== ESTOQUE =====")
    print("1 - Cadastrar produto")
    print("2 - Listar produtos")
    print("3 - Buscar produto")
    print("4 - Alterar estoque")
    print("5 - Remover produto")
    print("0 - Sair")

    opcao = input("Escolha: ")

    if opcao == '1':
        print("Entrando no cadastro de produtos... ")

        try:
            codigo = int(input("Código do produto:"))
            nome = (input("Nome do produto: "))
            valor = float(input("Valor do produto: "))

            produto = {
                "codigo": codigo,
                "nome": nome,
                "valor": valor
            }

            produtos.append(produto)

            print("Produto cadastrado com sucesso!")

        except ValueError:
            print("Digite um valor válido!")

    elif opcao == '2':
        for produto in produtos:
            print(f"Código: {produto['codigo']}\nNome: {produto['nome']}\nValor: {produto['valor']}")

    elif opcao == '3':
        busca = input("Digite código, nome ou valor do produto: ")
        for produto in produtos:
            if busca == str(produto["codigo"]):
                print(f"Produto relacionado: {produto['codigo']}")

            elif busca == produto["nome"]:
                print(f"Produto relacionado: {produto['nome']}")

            elif busca == str(produto["valor"]):
                print(f"Produto relacionado: {produto['valor']}")
