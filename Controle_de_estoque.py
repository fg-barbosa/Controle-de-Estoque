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
            quantidade = int(input("Quantidade de produtos: "))

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

    elif opcao == '4':
        try:
            alterar = int(input("Digite o código do produto: "))
            
            for produto in produtos:
                if alterar == (produto["codigo"]):
                    print("Escolha uma das opções: ")
                    print("1 - Alterar nome: ")
                    print("2 - Alterar valor: ")
                    print("3 - Alterar quantidade: ")
                    escolha_alteracao = input("Escolha uma opção: ")
                
                    if escolha_alteracao == '1':
                        produto['nome'] = input("Novo nome: ")
                
                    elif escolha_alteracao == '2':
                        produto['valor'] = float(input("Novo valor: "))

                    elif escolha_alteracao == '3':
                        produto['quantidade'] = int(input("Qual a nova quantidade: "))

        except ValueError:
            print("Digite um valor valido.")

    elif opcao == '5':
            excluir_produto = input("Digite o código do produto que deseja excluir: ")
            
            for produto in produtos:
                if excluir_produto == str(produto["codigo"]):
                    produtos.remove(produto)
                    print("Produto excluido com sucesso!")

            break

    elif opcao == '0':
        break