"""Conexao MySQL e cadastro de produtos. Execute para testar a conexao."""

import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv


def conectar():
    """Le a configuracao local e abre uma conexao com o MySQL."""
    load_dotenv(Path(__file__).resolve().parent.parent / ".env", interpolate=False)
    obrigatorias = ("MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE")
    ausentes = [nome for nome in obrigatorias if not os.environ.get(nome)]
    if ausentes:
        raise ValueError("Configure no .env: " + ", ".join(ausentes))
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "localhost"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"],
        connection_timeout=5,
    )


def inserir_produto(codigo, nome, valor, quantidade):
    """Salva um produto e fecha os recursos mesmo se a insercao falhar."""
    conexao = conectar()
    try:
        cursor = conexao.cursor()
        try:
            sql = """
                INSERT INTO produtos (codigo, nome, valor, quantidade)
                VALUES (%s, %s, %s, %s)
            """
            dados = (codigo, nome, valor, quantidade)
            cursor.execute(sql, dados)
            conexao.commit()
        except mysql.connector.Error:
            conexao.rollback()
            raise
        finally:
            cursor.close()
    finally:
        conexao.close()


def testar_conexao():
    """Confere a conexao e as colunas usadas pelo cadastro, sem inserir dados."""
    conexao = conectar()
    try:
        cursor = conexao.cursor()
        try:
            cursor.execute("SELECT codigo, nome, valor, quantidade FROM produtos LIMIT 0")
            cursor.fetchall()
        finally:
            cursor.close()
    finally:
        conexao.close()


if __name__ == "__main__":
    try:
        testar_conexao()
    except ValueError as erro:
        print(f"Erro de configuracao: {erro}")
        raise SystemExit(1)
    except mysql.connector.Error as erro:
        print(f"Erro MySQL ({erro.errno}): {erro.msg}")
        raise SystemExit(1)
    print("Conexao e tabela produtos verificadas com sucesso!")
