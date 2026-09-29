# Controle de Estoque

Programa em Python para controlar produtos, com uma interface web em Flask e um menu pelo terminal.

Nesta primeira etapa da integração web, é possível cadastrar, listar e buscar produtos pelo navegador. Alteração, exclusão, entradas e saídas continuam disponíveis pelo terminal.

## O que dá para fazer

- Cadastrar produtos com código, nome, valor e quantidade.
- Listar os produtos e buscar por código, nome ou valor.
- Buscar por parte do nome, sem diferenciar maiúsculas e minúsculas.
- Alterar o nome, o valor ou a quantidade de um produto.
- Remover produtos.
- Registrar entradas e saídas do estoque.

O programa impede códigos duplicados, nomes vazios, valores inválidos e saídas maiores que a quantidade disponível.

## Como executar

É necessário ter o Python 3.9 ou superior instalado.

Baixe o repositório ou clone com o Git:

```bash
git clone https://github.com/fg-barbosa/Controle-de-Estoque.git
cd Controle-de-Estoque
```

### Interface web (Flask)

Na raiz do projeto, crie um ambiente virtual e instale as dependências:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app backend.app run
```

No Python do MSYS2, usado neste ambiente, a pasta do executável é `bin`:

```powershell
.\.venv\bin\python.exe -m pip install -r requirements.txt
.\.venv\bin\python.exe -m flask --app backend.app run
```

No Linux/macOS, use `.venv/bin/python` nos comandos acima. Não é necessário ativar o ambiente quando o caminho do executável é informado.

Abra http://127.0.0.1:5000 no navegador. Inicie o servidor na raiz do projeto; abrir os arquivos HTML diretamente não processa os templates.

| Rota | Método | Função |
| --- | --- | --- |
| `/` | GET | Página inicial e total de produtos |
| `/produtos` | GET | Listagem e busca opcional por `?busca=arroz` |
| `/cadastrar` | GET, POST | Formulário e cadastro de produto |
| `/static/style.css` | GET | Estilos da interface |

O cadastro usa as mesmas regras do terminal. Erros são exibidos no formulário, preservando os valores digitados; após salvar, a aplicação redireciona para a listagem. A busca vazia na web mostra todos os produtos. Os formulários incluem proteção CSRF.

Requisições de cadastro na mesma instância são sincronizadas: se dois navegadores tentarem cadastrar o mesmo código ao mesmo tempo, apenas um cadastro será aceito.

### Pelo terminal

O modo terminal continua usando apenas a biblioteca padrão do Python:

```bash
python backend/Controle_de_estoque.py
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

No cadastro e na alteração de preços, use vírgula ou ponto como separador decimal, por exemplo `10,50` ou `10.50`, sem separador de milhar ou notação científica. Os preços são armazenados como `Decimal`, com precisão de centavos. Valores com frações de centavo, como `0,001` ou `2,675`, são rejeitados sem arredondamento; zeros adicionais, como em `10,500`, são aceitos. A busca por preço compara o valor numérico: `10`, `10,0` e `10.00` encontram o mesmo preço.

As quantidades devem ser números inteiros; nas entradas e saídas, devem ser maiores que zero.

## Testes

Na pasta do projeto, execute:

```bash
python -m unittest discover -s backend -v
```

Use o Python do ambiente virtual para incluir os testes Flask, por exemplo: `.\.venv\bin\python.exe -m unittest discover -s backend -v` no MSYS2 ou `.\.venv\Scripts\python.exe -m unittest discover -s backend -v` no Windows convencional.

Os testes verificam as regras de estoque, o fluxo do terminal e a integração web: páginas, cadastro, busca, validações, precisão dos preços, cadastros concorrentes, redirecionamento, proteção CSRF e escape de HTML.

## Arquivos principais

- `backend/Controle_de_estoque.py`: regras do estoque e interação pelo terminal.
- `backend/app.py`: criação da aplicação Flask e rotas web.
- `backend/test_estoque.py` e `backend/test_app.py`: testes com `unittest`.
- `frontend/`: templates HTML renderizados pelo Flask.
- `design/style.css`: estilos servidos pelo Flask.
- `requirements.txt`: dependências da interface web.

## Limitações atuais

Os produtos ficam apenas na memória: ao reiniciar o servidor ou encerrar o terminal, os dados são perdidos. O terminal e a interface web têm estoques independentes. Ainda não há salvamento em arquivo ou banco de dados.

A aplicação web é uma base para desenvolvimento local, sem autenticação. Uma única instância compartilha o estoque entre os navegadores; múltiplos processos teriam listas separadas. A chave de sessão é gerada a cada inicialização, ou pode ser definida pela variável de ambiente `SECRET_KEY`. Reiniciar sem chave fixa também invalida as sessões e os formulários abertos.

Referências da implementação: [início rápido do Flask](https://flask.palletsprojects.com/en/stable/quickstart/) e [fábricas de aplicação](https://flask.palletsprojects.com/en/stable/patterns/appfactories/).
