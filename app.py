from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import select, func
from banco import tabela_ordem_servico, tabela_usuario, tabela_equipamento, tabela_recurso
from models import db_session, Usuario, Servico, Equipamento, Recursos, Movimentacao

app = Flask(__name__)
app.secret_key = "chave-secreta-projeto-final-2026"

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

def deletar_item(modelo, item_id, rota_destino):
    obj = db_session.execute(select(modelo).where(modelo.id == item_id)).scalar_one_or_none()
    if obj:
        db_session.delete(obj)
        db_session.commit()
    return redirect(url_for(rota_destino))

@app.route("/")
def dashboard():
    return render_template(
        "dashboard.html",
        total_usuarios=tabela_usuario.select_quantidade_total(),
        total_servicos=tabela_ordem_servico.select_quantidade_total(),
        total_equipamentos=tabela_equipamento.select_quantidade_total(),
        total_recursos=tabela_recurso.select_quantidade_total(),
        total_movimentacoes=db_session.execute(select(func.count(Movimentacao.id))).scalar() or 0,
        ultimas_movimentacoes=db_session.execute(select(Movimentacao).order_by(Movimentacao.id.desc()).limit(5)).scalars().all(),
        ultimos_servicos=db_session.execute(select(Servico).order_by(Servico.id.desc()).limit(5)).scalars().all()
    )

# --- USUÁRIOS ---
def get_usuarios():
    return db_session.execute(select(Usuario, Servico).outerjoin(Servico, Usuario.servico_id == Servico.id)).all()

@app.route('/usuarios')
def listar_usuarios():
    return render_template('usuarios.html', usuarios=get_usuarios())

@app.route('/usuarios/novo', methods=['GET', 'POST'])
@app.route("/usuarios/<int:id_usuario>", methods=["GET", "POST"])
def editar_usuario(id_usuario=None):
    usuario = tabela_usuario.select_um(id_usuario) if id_usuario else None
    if request.method == "POST":
        campos = {k: request.form.get(k, "").strip() for k in ["nome", "telefone", "email", "data_nascimento"]}
        if not all(campos.values()):
            flash('Preencha todos os campos obrigatórios.', 'error')
            return redirect(request.url)
        if usuario:
            for k, v in campos.items(): setattr(usuario, k, v)
            db_session.commit()
            flash("Usuário alterado com sucesso.", "success")
        else:
            tabela_usuario.salvar(**campos)
        return redirect(url_for("listar_usuarios"))
    return render_template("usuarios.html", usuarios=get_usuarios(), editar=usuario)

app.add_url_rule('/usuarios/novo', 'novo_usuario', editar_usuario, methods=['GET', 'POST'])

@app.route("/usuarios/excluir/<int:usuario_id>")
def excluir_usuario(usuario_id):
    return deletar_item(Usuario, usuario_id, 'listar_usuarios')

# --- SERVIÇOS ---
@app.route("/servicos")
def listar_servicos():
    return render_template("servico.html", servicos=tabela_ordem_servico.select_todos())

@app.route("/servicos/novo", methods=["GET", "POST"])
@app.route("/servicos/<int:id_servico>", methods=["GET", "POST"])
def editar_servico(id_servico=None):
    servico = tabela_ordem_servico.select_um(id_servico) if id_servico else None
    if request.method == "POST":
        dados = {
            "nome": request.form.get("nome", "").strip(),
            "data_abertura": request.form.get("data_abertura"),
            "data_encerramento": request.form.get("data_encerramento"),
            "id_responsavel": request.form.get("id_responsavel", "").strip(),
            "status_servico": request.form.get("status_servico"),
            "equipamento": ", ".join(request.form.getlist("equipamentos_selecionados")),
            "recurso": ", ".join(request.form.getlist("recursos_selecionados")),
            "prioridade": request.form.get("prioridade")
        }
        if not all(dados.values()):
            flash('Preencha todos os campos obrigatórios.', 'error')
            return redirect(request.url)
        if servico:
            for k, v in dados.items(): setattr(servico, k, v)
            db_session.commit()
            flash("Serviço alterado com sucesso.", "success")
        else:
            tabela_ordem_servico.salvar(**dados)
        return redirect(url_for('listar_servicos'))

    return render_template(
        "servico.html",
        servicos=tabela_ordem_servico.select_todos(),
        lista_equipamentos=tabela_equipamento.select_todos_equipamentos(),
        lista_recursos=tabela_recurso.select_todos_recursos(),
        editar=servico
    )

app.add_url_rule('/servicos/novo', 'novo_servico', editar_servico, methods=['GET', 'POST'])

@app.route("/servicos/excluir/<int:servico_id>")
def excluir_servico(servico_id):
    return deletar_item(Servico, servico_id, 'listar_servicos')

# --- EQUIPAMENTOS ---
@app.route('/equipamentos')
def listar_equipamentos():
    return render_template('equipamentos.html', equipamentos=tabela_equipamento.select_todos_equipamentos())

@app.route("/equipamentos/novo", methods=["GET", "POST"])
@app.route("/equipamentos/<int:id_equipamento>", methods=["GET", "POST"])
def editar_equipamento(id_equipamento=None):
    equipamento = tabela_equipamento.select_um(id_equipamento) if id_equipamento else None
    if request.method == "POST":
        nome, tipo = request.form.get("nome", "").strip(), request.form.get("tipo", "").strip()
        if not nome or not tipo:
            flash('Preencha nome e tipo do equipamento.', 'error')
            return redirect(request.url)
        if equipamento:
            equipamento.nome, equipamento.tipo = nome, tipo
            db_session.commit()
            flash("Equipamento alterado com sucesso.", "success")
        else:
            tabela_equipamento.salvar_equipamento(nome=nome, tipo=tipo)
        return redirect(url_for("listar_equipamentos"))
    return render_template("equipamentos.html", equipamentos=tabela_equipamento.select_todos_equipamentos(), editar=equipamento)

app.add_url_rule('/equipamentos/novo', 'novo_equipamento', editar_equipamento, methods=['GET', 'POST'])

@app.route("/equipamentos/excluir/<int:equipamento_id>")
def excluir_equipamento(equipamento_id):
    return deletar_item(Equipamento, equipamento_id, 'listar_equipamentos')

# --- RECURSOS ---
@app.route('/recursos')
def listar_recursos():
    return render_template('recursos.html', recursos=tabela_recurso.select_todos_recursos())

@app.route("/recursos/novo", methods=["GET", "POST"])
@app.route("/editar_recurso/<int:recurso_id>", methods=["GET", "POST"])
def editar_recurso(recurso_id=None):
    recurso = tabela_recurso.select_um_recurso(recurso_id) if recurso_id else None
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        if not nome:
            flash('Preencha o nome do recurso.', 'error')
            return redirect(request.url)
        if recurso:
            recurso.nome = nome
            db_session.commit()
            flash("Recurso alterado com sucesso.", "success")
        else:
            tabela_recurso.salvar_recurso(nome=nome)
        return redirect(url_for("listar_recursos"))
    return render_template("recursos.html", recursos=tabela_recurso.select_todos_recursos(), editar=recurso)

app.add_url_rule('/recursos/novo', 'novo_recurso', editar_recurso, methods=['GET', 'POST'])

@app.route('/excluir_recurso/<int:recurso_id>')
def excluir_recurso(recurso_id):
    return deletar_item(Recursos, recurso_id, 'listar_recursos')

# --- MOVIMENTAÇÕES ---
@app.route("/movimentacoes")
def listar_movimentacoes():
    movs = db_session.execute(select(Movimentacao).order_by(Movimentacao.id.desc())).scalars().all()
    return render_template("movimentacoes.html", movimentacoes=movs)

@app.route("/movimentacoes/nova", methods=["GET", "POST"])
def nova_movimentacao():
    if request.method == "POST":
        dados = {
            "tipo": request.form.get("tipo"),
            "item_nome": request.form.get("item_nome"),
            "quantidade": int(request.form.get("quantidade", 1)),
            "responsavel": request.form.get("responsavel", "").strip(),
            "data_movimentacao": request.form.get("data_movimentacao"),
            "observacao": request.form.get("observacao", "").strip()
        }
        if not all([dados["tipo"], dados["item_nome"], dados["responsavel"], dados["data_movimentacao"]]):
            flash("Preencha todos os campos obrigatórios.", "error")
            return redirect(url_for("nova_movimentacao"))
        db_session.add(Movimentacao(**dados))
        db_session.commit()
        flash("Movimentação registrada com sucesso.", "success")
        return redirect(url_for("listar_movimentacoes"))

    movs = db_session.execute(select(Movimentacao).order_by(Movimentacao.id.desc())).scalars().all()
    return render_template("movimentacoes.html", movimentacoes=movs, equipamentos=tabela_equipamento.select_todos_equipamentos(), recursos=tabela_recurso.select_todos_recursos())

@app.route("/movimentacoes/excluir/<int:mov_id>")
def excluir_movimentacao(mov_id):
    return deletar_item(Movimentacao, mov_id, 'listar_movimentacoes')

if __name__ == "__main__":
    app.run(debug=True)
