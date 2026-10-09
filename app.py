import uuid
# CORREÇÃO 1: Importando a classe datetime corretamente para evitar erros de conversão de data
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for

# Inicialização da aplicação Flask
app = Flask(__name__)

# Simulação de tabelas do banco de dados (Listas globais)
base_fake = []
base_recursos = []

# Dicionário global para armazenar as informações do perfil
dados_usuario = {
   'nome': 'Vitor',
   'cargo': 'Desenvolvedora de Sistemas',
   'status': 'Ativo',
   'plataforma': 'Python Flask Back-end',
   'ambiente': 'PyCharm IDE',
   'servidor': 'sem'
}


# ==========================================
# GESTÃO OPERACIONAL: PAINEL DE ATIVIDADES
# ==========================================

@app.route('/')
def login():
   return render_template('login.html')


@app.route('/atividades/criar', methods=['GET', 'POST'])
def criar_atividade():
   if request.method == 'POST':
       # CORREÇÃO 2: Alterado de 'form_nome' para 'form_nome_tarefa' para bater com o name do seu HTML
       nome_atividades = request.form.get('form_nome_tarefa')
       id_responsavel = request.form.get('form_id_responsavel')
       status_atividades = request.form.get('form_status_tarefa')
       prioridade_atividades = request.form.get('form_prioridade')

       # Captura os recursos selecionados (checkboxes do formulário)
       recursos_atividades = request.form.getlist('form_item')

       # Captura os prazos desejados vindos do formulário
       data_abertura = request.form.get('form_data_abertura')
       data_encerramento = request.form.get('form_data_encerramento')

       # Formatação das datas de AAAA-MM-DD para DD/MM/AAAA
       if data_abertura:
           try:
               data_objeto = datetime.strptime(data_abertura, '%Y-%m-%d')
               data_abertura = data_objeto.strftime('%d/%m/%Y')
           except ValueError:
               data_abertura = "Não informado"
       else:
           data_abertura = "Não informado"

       if data_encerramento:
           try:
               data_objeto = datetime.strptime(data_encerramento, '%Y-%m-%d')
               data_encerramento = data_objeto.strftime('%d/%m/%Y')
           except ValueError:
               data_encerramento = "Não informado"
       else:
           data_encerramento = "Não informado"

       dados = {
           'id': str(uuid.uuid4()),
           'nome_atividades': nome_atividades,
           'data_abertura': data_abertura,
           'data_encerramento': data_encerramento,
           'id_responsavel': id_responsavel,
           'status_atividades': status_atividades,
           'recursos_atividades': recursos_atividades,
           'prioridade_atividades': prioridade_atividades,
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
# ROTA DE PERFIL
# ==========================================

# Inicialize essa lista simulada no topo do seu arquivo app.py junto com as outras
base_pessoas = []


@app.route('/pessoa', methods=['GET', 'POST'])
def pessoa():
    if request.method == 'POST':
        # Captura os dados exatos vindos do formulário flutuante
        nova_pessoa = {
            'id': str(uuid.uuid4()),
            'nome': request.form.get('cadastro_nome'),
            'telefone': request.form.get('cadastro_telefone'),
            'email': request.form.get('cadastro_email'),
            'nascimento': request.form.get('cadastro_nascimento')
        }

        # Adiciona à lista fake do sistema
        base_pessoas.append(nova_pessoa)
        return redirect(url_for('pessoa'))

    # Retorna a página renderizando a lista atualizada
    return render_template('pessoa.html', dados_pessoas=base_pessoas)


@app.route('/pessoa/excluir/<string:pessoa_id>', methods=['POST'])
def excluir_pessoa(pessoa_id):
    global base_pessoas
    base_pessoas = [p for p in base_pessoas if p.get('id') != pessoa_id]
    return redirect(url_for('pessoa'))


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


if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5007)
