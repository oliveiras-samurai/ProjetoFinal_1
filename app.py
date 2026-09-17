
from flask import (Flask, render_template, request, redirect, url_for)
from datetime import datetime
import uuid

# Inicialização da aplicação Flask
app = Flask(__name__)

# Simulação de tabelas do banco de dados (Listas globais)
base_fake = []
base_recursos = []

# Dicionário global para armazenar as informações do perfil (Essencial para corrigir o erro!)
dados_usuario = {
    'nome': 'Vitor',
    'cargo': 'Desenvolvedor de Sistemas',
    'status': 'Ativo',
    'plataforma': 'Python Flask Back-end',
    'ambiente': 'PyCharm IDE',
    'servidor': 'sem'
}


# ==========================================
# GESTÃO OPERACIONAL: PAINEL DE ATIVIDADES
# ==========================================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/atividades/criar', methods=['GET', 'POST'])
def criar_atividade():
    if request.method == 'POST':
        nome_atividades = request.form.get('form_nome')
        descricao_atividades = request.form.get('form_descricao')
        tipo_atividades = request.form.get('form_tipo')

        # Captura os recursos selecionados (checkboxes do formulário)
        item_atividades = request.form.getlist('form_item')

        # 1. CAPTURA O PRAZO DESEJADO VINDO DO FORMULÁRIO (Input tipo date)
        data_original = request.form.get('form_data_atividades')

        # 2. FORMATAÇÃO DO PRAZO (De AAAA-MM-DD para DD/MM/AAAA)
        if data_original:
            try:
                data_objeto = datetime.strptime(data_original, '%Y-%m-%d')
                data_atividades = data_objeto.strftime('%d/%m/%Y')
            except ValueError:
                data_atividades = "Não informado"
        else:
            data_atividades = "Não informado"

        # 3. ATUALIZAÇÃO AUTOMÁTICA E BAIXA NO INVENTÁRIO DE RECURSOS (-1 un)
        if item_atividades:
            for recurso_selecionado in item_atividades:
                for recurso_estoque in base_recursos:
                    if recurso_estoque['nome'] == recurso_selecionado:
                        try:
                            qtd_atual = int(recurso_estoque['quantidade'])
                            if qtd_atual > 0:
                                recurso_estoque['quantidade'] = str(qtd_atual - 1)
                        except ValueError:
                            pass

        dados = {
            'id': str(uuid.uuid4()),
            'nome_atividades': nome_atividades,
            'data_atividades': data_atividades,
            'descricao_atividades': descricao_atividades,
            'tipo_atividades': tipo_atividades,
            'item_atividades': item_atividades
        }

        print(f'dados cadastrados: {dados}')
        base_fake.append(dados)
        return redirect(url_for('listar_atividades'))

    # Método GET envia a lista de recursos para popular as caixas de seleção
    return render_template('criar_atividades.html', lista_recursos=base_recursos)


@app.route('/atividades')
def listar_atividades():
    return render_template('listar_atividades.html', dados_atividades=base_fake)


@app.route('/atividades/excluir/<string:atividade_id>', methods=['POST'])
def excluir_atividade(atividade_id):
    global base_fake
    base_fake = [atv for atv in base_fake if atv.get('id') != atividade_id]
    return redirect(url_for('listar_atividades'))


# ==========================================
# ROTA DE PERFIL (CORRIGIDA COM ENVIO DE VARIÁVEL)
# ==========================================

@app.route('/pessoa', methods=['GET', 'POST'])
def pessoa():
    if request.method == 'POST':
        # Salva o que a pessoa digitar nos inputs da tela
        dados_usuario['nome'] = request.form.get('perfil_nome')
        dados_usuario['cargo'] = request.form.get('perfil_cargo')
        dados_usuario['status'] = request.form.get('perfil_status')
        dados_usuario['plataforma'] = request.form.get('perfil_plataforma')
        dados_usuario['ambiente'] = request.form.get('perfil_ambiente')
        dados_usuario['servidor'] = request.form.get('perfil_servidor')

        print(f"Perfil atualizado: {dados_usuario}")
        return redirect(url_for('pessoa'))

    # Corrigido aqui: passando 'usuario=dados_usuario' para o template conseguir ler os dados
    return render_template('pessoa.html', usuario=dados_usuario)


# ==========================================
# GESTÃO OPERACIONAL: INVENTÁRIO DE RECURSOS
# ==========================================

@app.route('/recursos/criar', methods=['GET', 'POST'])
def criar_recurso():
    if request.method == 'POST':
        nome_recurso = request.form.get('form_nome_recurso')
        tipo_recurso = request.form.get('form_tipo_recurso')
        quantidade = request.form.get('form_quantidade')

        recurso = {
            'id': str(uuid.uuid4()),
            'nome': nome_recurso,
            'tipo': tipo_recurso,
            'quantidade': quantidade
        }

        print(f'recurso cadastrado: {recurso}')
        base_recursos.append(recurso)
        return redirect(url_for('listar_recursos'))

    return render_template('criar_recurso.html')


@app.route('/recursos')
def listar_recursos():
    return render_template('listar_recursos.html', dados_recursos=base_recursos)


@app.route('/recursos/excluir/<string:recurso_id>', methods=['POST'])
def excluir_recurso(recurso_id):
    global base_recursos
    base_recursos = [rec for rec in base_recursos if rec.get('id') != recurso_id]
    return redirect(url_for('listar_recursos'))


# Inicialização do servidor web na rede local (porta 5007)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5007)
