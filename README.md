# Controle de Estoque

Programa em Python para controlar produtos, com uma interface web em Flask e um menu pelo terminal.

Nesta primeira etapa da integração web, é possível cadastrar, listar e buscar produtos pelo navegador. Alteração, exclusão, entradas e saídas continuam disponíveis pelo terminal.

O módulo `backend/connmysql.py` permite testar a conexão e inserir produtos permanentemente no MySQL. A integração desse módulo com as telas e o menu ainda está pendente: os cadastros feitos por essas interfaces continuam em memória.

## O que dá para fazer

| Funcionalidade | Navegador | Terminal |
| --- | --- | --- |
| Cadastrar produtos com código, nome, valor e quantidade | Sim | Sim |
| Listar produtos e buscar por código, nome ou valor | Sim | Sim |
| Buscar por parte do nome, sem diferenciar maiúsculas e minúsculas | Sim | Sim |
| Alterar nome, valor ou quantidade | Ainda não | Sim |
| Remover produtos | Ainda não | Sim |
| Registrar entradas e saídas do estoque | Ainda não | Sim |

A interface web possui páginas de início, listagem e cadastro, com estilos adaptados para telas pequenas e rolagem horizontal da tabela quando necessário.

O programa impede códigos duplicados, nomes vazios, valores inválidos e saídas maiores que a quantidade disponível.

## Como executar

É necessário ter o Python 3.10 ou superior instalado. Para usar o módulo de banco, também é necessário um servidor MySQL; a configuração local foi verificada no MySQL 8.0.46.

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

No Linux/macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m flask --app backend.app run
```

Não é necessário ativar o ambiente quando o caminho do executável é informado.

Abra http://127.0.0.1:5000 no navegador. Inicie o servidor na raiz do projeto; abrir os arquivos HTML diretamente não processa os templates.

Para experimentar, acesse **Cadastrar**, informe código `1`, nome `Arroz`, valor `10,50` e quantidade `5`, e salve. O produto aparecerá em **Produtos**, onde você poderá buscar por `Arroz`, `1` ou `10,50`.

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

### Conexão com o MySQL local

Instale as dependências do `requirements.txt` no ambiente virtual, conforme as instruções acima. Elas incluem Flask, MySQL Connector/Python e python-dotenv, que carrega a configuração do arquivo `.env`.

Para um banco novo, execute no MySQL Workbench com um usuário administrador:

```sql
CREATE DATABASE controle_estoque
    CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

USE controle_estoque;

CREATE TABLE produtos (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    codigo INT NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    quantidade INT NOT NULL,
    CONSTRAINT chk_produtos_valor CHECK (valor > 0),
    CONSTRAINT chk_produtos_quantidade CHECK (quantidade >= 0),
    CONSTRAINT chk_produtos_nome CHECK (CHAR_LENGTH(TRIM(nome)) > 0)
) ENGINE=InnoDB;
```

Os `CHECK` exigem MySQL 8.0.16 ou superior. Se o banco e a tabela já existem, confira a estrutura com `SHOW CREATE TABLE controle_estoque.produtos;` em vez de repetir sua criação.

Crie um usuário exclusivo para a aplicação. Substitua a senha abaixo antes de executar; se esse usuário já foi criado, pule esta etapa:

```sql
CREATE USER 'estoque_app'@'localhost'
    IDENTIFIED BY 'SUBSTITUA_POR_UMA_SENHA';

GRANT SELECT, INSERT, UPDATE, DELETE
    ON controle_estoque.* TO 'estoque_app'@'localhost';

SHOW GRANTS FOR 'estoque_app'@'localhost';
```

Na raiz do projeto, copie `.env.example` para `.env` **somente se ainda não houver um `.env` local**:

```powershell
Copy-Item .env.example .env
```

Edite o `.env` e preencha `MYSQL_PASSWORD` com a senha desse usuário. Use aspas simples ao redor da senha. Confira também `MYSQL_USER=estoque_app`, o host, a porta e o nome do banco. O `.env` contém suas credenciais locais e é ignorado pelo Git; apenas `.env.example`, sem senha, deve ser publicado. O arquivo não criptografa a senha.

A configuração é lida da raiz do projeto, independentemente da pasta de execução. Variáveis de ambiente já definidas têm prioridade sobre o `.env`.

Teste a conexão, na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe -m backend.connmysql
```

No MSYS2 ou Linux/macOS, ajuste o executável para `.venv/bin/python`. A mensagem esperada é `Conexao e tabela produtos verificadas com sucesso!`. Esse comando consulta a estrutura da tabela e não cadastra produtos.

A função `inserir_produto(codigo, nome, valor, quantidade)` executa um `INSERT` parametrizado e confirma a transação com `commit()`. Em erro do MySQL, faz `rollback()`; o cursor e a conexão são fechados ao terminar. Ela ainda não aplica as validações das interfaces, que serão incorporadas na integração.

Próximas etapas: ligar o cadastro ao MySQL; consultar listagem, busca e total pelo banco; tratar erros na interface; testar os dados após reiniciar a aplicação; integrar alterações e movimentações do estoque.

### Como parar o programa

- **Servidor web:** pressione `Ctrl+C` no terminal em que o Flask está rodando. Fechar a aba do navegador não encerra o servidor.
- **Menu no terminal:** escolha `0 - Sair`.

Ao encerrar a interface web ou o menu, seus produtos são perdidos, pois essas interfaces ainda usam memória. Produtos inseridos pelo módulo MySQL e confirmados com `commit()` permanecem no banco.

## Testes

Na pasta do projeto, execute:

```bash
python -m unittest discover -s backend -v
```

Use o Python do ambiente virtual para incluir os testes Flask, por exemplo: `.\.venv\bin\python.exe -m unittest discover -s backend -v` no MSYS2 ou `.\.venv\Scripts\python.exe -m unittest discover -s backend -v` no Windows convencional.

Os testes verificam as regras de estoque, o fluxo do terminal e a integração web: páginas, cadastro, busca, validações, precisão dos preços, cadastros concorrentes, redirecionamento, proteção CSRF e escape de HTML.

Essa suíte não precisa de MySQL e ainda não cobre a integração com o banco. Para verificar a conexão real, use `python -m backend.connmysql` no ambiente configurado.

## Arquivos principais

- `backend/Controle_de_estoque.py`: regras do estoque e interação pelo terminal.
- `backend/app.py`: criação da aplicação Flask e rotas web.
- `backend/connmysql.py`: configuração, teste de conexão e inserção no MySQL.
- `backend/test_estoque.py` e `backend/test_app.py`: testes com `unittest`.
- `frontend/`: templates HTML renderizados pelo Flask.
- `design/style.css`: estilos servidos pelo Flask.
- `requirements.txt`: dependências da interface web e da conexão MySQL.
- `.env.example`: modelo de configuração sem credenciais reais.

## Limitações atuais

O terminal e a interface web têm estoques independentes em memória. O módulo MySQL já permite inserções permanentes, mas ainda não é chamado por essas interfaces.

A aplicação web é uma base para desenvolvimento local, sem autenticação. Uma única instância compartilha o estoque entre os navegadores; múltiplos processos teriam listas separadas. A chave de sessão é gerada a cada inicialização, ou pode ser definida pela variável de ambiente `SECRET_KEY`. Reiniciar sem chave fixa também invalida as sessões e os formulários abertos.

Referências da implementação: [início rápido do Flask](https://flask.palletsprojects.com/en/stable/quickstart/) e [fábricas de aplicação](https://flask.palletsprojects.com/en/stable/patterns/appfactories/).
