import sqlite3

# cria banco usuario.db SQlite
# conexao = sqlite3.connect('banco_de_dados.db')
URL_CONNEXAO = "postgres://neondb_owner:3Vzlg8qIRBoa@ep-green-bonus-a58b1qy5.us-east-2.aws.neon.tech/neondb"
conexao = psycopg.connect(URL_CONNEXAO)
# executar comandos SQL
cursor = conexao.cursor()


# Executar o comando SQL
cursor.execute(comando_sql)

### Tabela usuario

# executar comandos SQL
cursor = conexao.cursor()

# criar a tabela de usuario
comando_sql = """
CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY,
    nome TEXT,
    email TEXT,
    telefone TEXT,
    senha TEXT
)
"""
# Executar o comando SQL
cursor.execute(comando_sql)


### Tabela produto
cursor = conexao.cursor()

# criar a tabela de produto
comando_sql = """
CREATE TABLE IF NOT EXISTS produto (
    id INTEGER PRIMARY KEY,
    nome TEXT,
    codigo TEXT,
    quantidade  INTEGER,
    data_hora_saida  TIMESTAMP
)
"""
# Executar o comando SQL
cursor.execute(comando_sql)

# fechar a conexão
conexao.commit()
conexao.close()