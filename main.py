from flask import Flask
from flask import render_template, send_from_directory, request, redirect, url_for, jsonify, session, flash
from flask_cors import CORS
import json
import psycopg

URL_CONNEXAO = "postgres://neondb_owner:3Vzlg8qIRBoa@ep-green-bonus-a58b1qy5.us-east-2.aws.neon.tech/neondb"

app = Flask(__name__)
CORS(app)


# Adiciona o icone nas páginas
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('./static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/")
def hello_world():
    return render_template("home.html")

@app.route("/cadastro_usuario")
def cadastro_usuario():
    return render_template("cadastro_usuario.html")


@app.route("/cadastro_produto")
def cadastro_produto():
    return render_template("cadastro_produto.html")


@app.route("/cadastro_nota")
def cadastrar_nota():
    if not session.get('nome'):
       return redirect(url_for('cadastro_usuario')) 
    return render_template("cadastro_nota.html") 

@app.route("/consulta_balanco")
def consulta_balanco():
    if not session.get('nome'):
        return redirect(url_for('cadastro_usuario'))
    return render_template("consulta_balanco.html")

@app.route("/saida_produto")
def saida_produto():
    return render_template("saida_produto.html")

@app.route("/solicitar_relatorio")
def solicitar_relatorio():
    dados = []
    with psycopg.connect(URL_CONNEXAO) as conn:
        with conn.cursor() as cur:
            cur.execute(""" SELECT * 
                FROM nota_fiscal 
                """, {"ativo": ativo , "passivo": passivo, "nome_cliente": f"%{nome_cliente}%" })
            dados = cur.fetchall()
    
    dados_formatados = []
    for nota_fiscal in dados:
        nota_formatada = list(nota_fiscal)
        nota_formatada[3] = nota_fiscal[3].strftime("%d-%m-%Y")
        dados_formatados.append(nota_formatada)

    return jsonify(dados_formatados)

@app.route("/executa_consulta_balanco", methods=["POST"])
def executa_consulta_balanco():
    json_request = request.json
    print(json_request)
    ativo = bool(json_request["ativo"]) # Se for TRUE, queremos notas com valor_entrada > 0
    passivo = bool(json_request["passivo"])  # Se for TRUE, queremos notas com valor_saida > 0
    nome_cliente = json_request["nome_cliente"] or ""  # Busca pelo nome do cliente. Se nome for vazio, esse parametro é ignorado

    dados = []
    with psycopg.connect(URL_CONNEXAO) as conn:
        with conn.cursor() as cur:
            cur.execute(""" SELECT nome_cliente, 
                                   valor_entrada, 
                                   valor_saida, 
                                   data_emissao 
                            FROM nota_fiscal 
                            where (%(ativo)s IS TRUE OR valor_saida > 0)
                            AND (%(passivo)s IS TRUE OR valor_entrada > 0)
                            AND (LENGTH(%(nome_cliente)s) = 0 OR nome_cliente ilike %(nome_cliente)s)
                            ORDER BY nome_cliente
                            """, {"ativo": ativo , "passivo": passivo, "nome_cliente": f"%{nome_cliente}%" })
            dados = cur.fetchall()

    dados_formatados = []
    for nota_fiscal in dados:
        dados_formatados.append(
            [
                nota_fiscal[0],
                nota_fiscal[1],
                nota_fiscal[2],
                nota_fiscal[3].strftime("%d-%m-%Y"),
            ]
        )

    return jsonify(dados_formatados)

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/consulta_produto")
def consulta_produto():
    return render_template("consulta_produto.html")

@app.route("/criar_nota", methods=["POST"])
def criar_nota():
    nome_cliente = request.form["nome_tomador_de_servicos"]
    cpf_cnpj = request.form["numero_tomador_cpf_cnpj"]
    valor_entrada = request.form["valor_entrada"]
    valor_saida = request.form["valor_saida"]
    data_emissao = request.form["data_emissao"]
    with psycopg.connect(URL_CONNEXAO) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO nota_fiscal (nome_cliente, cpf_cnpj, data_emissao, valor_entrada, valor_saida) VALUES (%s, %s, %s, %s, %s)", 
                        (nome_cliente, cpf_cnpj, data_emissao, valor_entrada, valor_saida))
            conn.commit()
    return render_template("nota_cadastrada.html")


@app.route('/submit_usuario', methods=['POST'])
def submit_usuario():
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']
    with psycopg.connect(URL_CONNEXAO) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)", 
                        (nome, email, senha))
            conn.commit()
    return redirect(url_for('login'))

@app.route('/submit_produto', methods=['POST'])
def submit_produto():
    nome = request.form['nome']
    quantidade_existente = request.form['quantidade_existente']
    codigo = request.form['codigo_produto']
    with psycopg.connect(URL_CONNEXAO) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO produto ( nome,codigo, quantidade) VALUES (%s, %s, %s)",
                            (nome, codigo, quantidade_existente))
            conn.commit()
   # return redirect(url_for('home.html'))
    return render_template("home.html")

@app.route('/retorna_produtos', methods=['POST'])
def retorna_produtos():
    data = request.get_json()
    nome = data.get('nome', '')
    codigo = data.get('codigo_produto', '')

    dados = []
    with psycopg.connect(URL_CONNEXAO) as conn:
        with conn.cursor() as cur:
            cur.execute("""select nome,
                                  codigo,
                                  quantidade,
                                  data_hora_saida
                           from produto
                           where nome like '%{}%'
                           and codigo like '%{}%'""".format(nome, codigo))
            dados = cur.fetchall()

    dados_formatados = []

    for produtos in dados:
        data_hora = None
        if produtos[3]:
            data_hora = produtos[3].isoformat()

        dados_formatados.append(
            {
                'nome': produtos[0],
                'codigo': produtos[1],
                'quantidade': produtos[2],
                'data_hora_saida': produtos[3]
            }
        )

    return jsonify(dados_formatados)

    # return render_template("home.html")




@app.route("/submit_login", methods=['POST'])
def submit_login():
    email = request.form['email']
    senha = request.form['senha']

    with psycopg.connect(URL_CONNEXAO) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM usuarios where email = %s and senha = %s", (email, senha))
            usuario = cur.fetchone()

    if len(usuario) > 0:
        session['nome'] = usuario[1]
        session['email'] = email
        session['id_usuario'] = usuario[0]
        session['secret_key'] = 'chave_acesso'
        return redirect(url_for('cadastrar_nota'))
    else:
        return redirect(url_for('cadastro_usuario'))

@app.route('/saida_produto', methods=['POST'])
def vender_produto():
    nome = request.form['nome']
    codigo = request.form['codigo_produto']
    quantidade_vendida = int(request.form['quantidade_vendida'])

    with psycopg.connect(URL_CONNEXAO) as conn:
        with conn.cursor() as cur:
            # Verifica quantidade atual
            cur.execute("""
                SELECT quantidade FROM produto
                WHERE nome = %s AND codigo = %s
            """, (nome, codigo))
            resultado = cur.fetchone()

            if not resultado:
                flash("Produto não encontrado.")
                return redirect(url_for('saida_produto'))

            quantidade_atual = resultado[0]

            if quantidade_vendida > quantidade_atual:
                flash("Quantidade vendida excede o estoque atual.")
                return redirect(url_for('saida_produto'))

            # Atualiza a quantidade
            nova_quantidade = quantidade_atual - quantidade_vendida
            cur.execute("""
                UPDATE produto SET quantidade = %s, data_hora_saida = now()
                WHERE nome = %s AND codigo = %s
            """, (nova_quantidade, nome, codigo))
            conn.commit()

    flash("Saida registrada com sucesso.")
    return redirect(url_for('saida_produto'))

if __name__=="__main__":
    app.secret_key = 'chave_acesso'
    app.run(host="0.0.0.0",port=9000, debug=True)
