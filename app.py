from flask import Flask, render_template, request, redirect, jsonify
import json
import os

app = Flask(__name__)

CAMINHO_DADOS = 'dados/estoque.json'

# Função para carregar dados
def carregar_dados():
    if os.path.exists(CAMINHO_DADOS):
        with open(CAMINHO_DADOS, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {"estoque": [], "relatorio": {}, "entrada_total": 0, "saida_total": 0}

# Função para salvar dados
def salvar_dados(dados):
    with open(CAMINHO_DADOS, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    dados = carregar_dados()
    return render_template(
        'index.html',
        estoque=dados['estoque'],
        relatorio=dados['relatorio'],
        entrada_total=dados.get('entrada_total', 0),
        saida_total=dados.get('saida_total', 0)
    )

@app.route('/adicionar', methods=['POST'])
def adicionar():
    nome = request.form['nome'].strip()
    quantidade = int(request.form['quantidade'])

    dados = carregar_dados()
    estoque = dados['estoque']

    for item in estoque:
        if item['nome'].lower() == nome.lower():
            item['quantidade'] += quantidade
            break
    else:
        estoque.append({'nome': nome, 'quantidade': quantidade})

    dados['entrada_total'] += quantidade

    salvar_dados(dados)
    return redirect('/')

@app.route('/saida/<nome>')
def saida(nome):
    dados = carregar_dados()
    for item in dados['estoque']:
        if item['nome'] == nome and item['quantidade'] > 0:
            item['quantidade'] -= 1
            dados['relatorio'][nome] = dados['relatorio'].get(nome, 0) + 1
            dados['saida_total'] += 1
            break

    salvar_dados(dados)
    return redirect('/')

# ✅ Corrigido para subtrair da entrada_total
@app.route('/remover/<nome>')
def remover(nome):
    dados = carregar_dados()
    estoque = dados['estoque']
    novo_estoque = []

    for item in estoque:
        if item['nome'] == nome:
            dados['entrada_total'] -= item['quantidade']
        else:
            novo_estoque.append(item)

    dados['estoque'] = novo_estoque
    salvar_dados(dados)
    return redirect('/')

@app.route('/backup')
def backup():
    dados = carregar_dados()
    return jsonify(dados)

@app.route('/limpar_relatorio')
def limpar_relatorio():
    dados = carregar_dados()
    dados['relatorio'] = {}
    dados['saida_total'] = 0
    salvar_dados(dados)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
