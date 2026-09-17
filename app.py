from datetime import datetime
from os import times

from flask import Flask, render_template, request, redirect, url_for, flash, g
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from banco import tabela_ordem_servico, tabela_usuario, tabela_equipamento, tabela_recurso
from models import *

app = Flask(__name__)
app.secret_key = "chave-secreta-projeto-final-2026"


@app.route("/")
def dashboard():
    servicos = tabela_ordem_servico.select_quantidade_total()
    usuarios = tabela_usuario.select_quantidade_total()
    equipamentos = tabela_equipamento.select_quantidade_total()
    recursos = tabela_recurso.select_quantidade_total()

    return render_template(
        "dashboard.html",
        total_usuarios=usuarios,
        total_servicos=servicos,
        total_equipamentos=equipamentos,
        total_recursos=recursos,
    )


@app.route('/usuarios')
def listar_usuarios():
    db_session.commit()
    query = select(Usuario, Servico).outerjoin(Servico, Usuario.servico_id == Servico.id)
    usuarios_do_banco = db_session.execute(query).all()
    todos_servicos = db_session.execute(select(Servico)).scalars().all()
    return render_template(
        'usuarios.html',
        usuarios=usuarios_do_banco,
        servicos=todos_servicos
    )


@app.route('/usuarios/novo', methods=['GET', 'POST'])
def novo_usuario():
    if request.method == "POST":
        nome = request.form.get("nome")
        telefone = request.form.get("telefone")
        email = request.form.get("email")
        data_nascimento = request.form.get("data_nascimento")

        # Verifica se foi digitado
        if not nome:
            flash('Preencha o nome do jogador', 'error')
            return render_template('usuarios.html')
        if not telefone:
            flash('Preencha o número de telefone', 'error')
            return render_template('usuarios.html')
        if not email:
            flash('Preencha o email', 'error')
            return render_template('usuarios.html')
        if not data_nascimento:
            flash('Preencha a data', 'error')
            return render_template('usuarios.html')

        # SALVAR NO BANCO DE DADOS:
        tabela_usuario.salvar(nome=nome, telefone=telefone, email=email, data_nascimento=data_nascimento)

        return redirect(url_for("listar_usuarios"))

    usuarios = tabela_usuario.select_todos()
    print(usuarios)
    return render_template("usuarios.html", usuarios=usuarios)


@app.route("/usuarios/<id_usuario>", methods=["GET", "POST"])
def editar_usuario(id_usuario):
    # Buscar o jogador no banco
    usuario = tabela_usuario.select_um(id_usuario)

    if request.method == "POST":
        nome = request.form.get("nome")
        telefone = request.form.get("telefone")
        email = request.form.get("email")
        data_nascimento = request.form.get("data_nascimento")

        # Verifica se foi digitado
        if not nome:
            flash('Preencha o nome do jogador', 'error')
        elif not telefone:
            flash('Preencha o número de telefone', 'error')
        elif not email:
            flash('Preencha o email', 'error')
        elif not data_nascimento:
            flash('Preencha a data', 'error')
        else:
            usuario.nome = nome
            usuario.telefone = telefone
            usuario.email = email
            usuario.data_nascimento = data_nascimento
            db_session.commit()

            flash("Usuário alterado com sucesso", category="success")

        return redirect(url_for("listar_usuarios"))

    # Carregar as informações
    usuarios = tabela_usuario.select_todos()
    return render_template("usuarios.html", usuarios=usuarios, editar=usuario)

@app.route("/usuarios/excluir/<usuario_id>", methods=["GET", "POST"])
def excluir_usuario(usuario_id):
    usuario_sql = select(Usuario).where(Usuario.id == usuario_id)
    usuario = db_session.execute(usuario_sql).scalar_one_or_none()
    if usuario:
        db_session.delete(usuario)
        db_session.commit()
    return redirect(url_for('listar_usuarios'))


@app.route("/servicos")
def listar_servicos():
    servicos = tabela_ordem_servico.select_todos()
    return render_template("servico.html", servicos=servicos)


@app.route("/servicos/novo", methods=["GET", "POST"])
def novo_servico(usuarios_ids=None):
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        data_abertura = request.form.get("data_abertura")
        data_encerramento = request.form.get("data_encerramento")
        id_responsavel = request.form.get("id_responsavel")
        status_servico = request.form.get("status_servico")
        equipamento = request.form.getlist("equipamentos_selecionados")
        recurso = request.form.get("recurso")
        prioridade = request.form.get("prioridade")

        if not nome:
            flash('Preencha o nome', 'error')
            return redirect(url_for('novo_servico'))
        if not data_abertura:
            flash('Preencha a data de abertura', 'error')
            return redirect(url_for('novo_servico'))
        if not data_encerramento:
            flash('Preencha a data de encerramento', 'error')
            return redirect(url_for('novo_servico'))
        if not id_responsavel:
            flash('Preencha o responsável', 'error')
            return redirect(url_for('novo_servico'))
        if not status_servico:
            flash('Preencha o status', 'error')
            return redirect(url_for('novo_servico'))
        if not equipamento:
            flash('Preencha o equipamento', 'error')
            return redirect(url_for('novo_servico'))
        if not recurso:
            flash('Preencha o recurso', 'error')
            return redirect(url_for('novo_servico'))
        if not prioridade:
            flash('Preencha o prioridade', 'error')
            return redirect(url_for('novo_servico'))

        servico = tabela_ordem_servico.salvar(
            nome=nome,
            data_abertura=data_abertura,
            data_encerramento=data_encerramento,
            id_responsavel=id_responsavel,
            status_servico=status_servico,
            equipamento=equipamento,
            recurso=recurso,
            prioridade=prioridade
        )

        if usuarios_ids and servico:
            for usuario_id in usuarios_ids:
                usuario = tabela_usuario.select_um(usuario_id)
                if usuario:
                    usuario.servico_id = servico.id
                    db_session.add(usuario)
            db_session.commit()

        return redirect(url_for('listar_servicos'))

    servicos = tabela_ordem_servico.select_todos()
    usuarios = tabela_usuario.select_todos()
    lista_equipamento = tabela_equipamento.select_todos_equipamentos()
    lista_recurso = tabela_recurso.select_todos_recursos()

    return render_template(
        "servico.html",
        servicos=servicos,
        usuarios=usuarios,
        lista_equipamentos=lista_equipamento,
        lista_recursos=lista_recurso,
    )

@app.route("/servicos/<id_servico>", methods=["GET", "POST"])
def editar_servico(id_servico):
    # Buscar o jogador no banco
    servico = tabela_ordem_servico.select_um(id_servico)

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        data_abertura = request.form.get("data_abertura")
        data_encerramento = request.form.get("data_encerramento")
        id_responsavel = request.form.get("id_responsavel")
        status_servico = request.form.get("status_servico")
        equipamento = request.form.getlist("equipamentos_selecionados")
        recurso = request.form.get("recurso")
        prioridade = request.form.get("prioridade")

        if not nome:
            flash('Preencha o nome', 'error')
        elif not data_abertura:
            flash('Preencha a data de abertura', 'error')
        elif not data_encerramento:
            flash('Preencha a data de encerramento', 'error')
        elif not id_responsavel:
            flash('Preencha o responsável', 'error')
        elif not status_servico:
            flash('Preencha o status', 'error')
        elif not equipamento:
            flash('Preencha o equipamento', 'error')
        elif not recurso:
            flash('Preencha o recurso', 'error')
        elif not prioridade:
            flash('Preencha a prioridade', 'error')
        else:
            servico.nome = nome
            servico.data_abertura = data_abertura
            servico.data_encerramento = data_encerramento
            servico.id_responsavel = id_responsavel
            servico.status_servico = status_servico
            servico.equipamento = equipamento
            servico.recurso = recurso
            servico.prioridade = prioridade
            db_session.commit()

            flash("Serviço alterado com sucesso", category="success")

        return redirect(url_for("listar_servicos"))

    # Carregar as informações
    servicos = tabela_ordem_servico.select_todos()
    return render_template("servico.html", servicos=servicos, editar=servico)


@app.route("/servico/<id_servico>")
def detalhes_servico(id_servico):
    servicos = tabela_ordem_servico.select_um(int(id_servico))
    return render_template("time_detalhes.html", servicos=servicos)


@app.route("/servicos/excluir/<servico_id>", methods=["GET", "POST"])
def excluir_servico(servico_id):
    servico_sql = select(Servico).where(Servico.id == servico_id)
    servico = db_session.execute(servico_sql).scalar_one_or_none()
    if servico:
        db_session.delete(servico)
        db_session.commit()
    return redirect(url_for('listar_servicos'))


@app.route('/equipamentos')
def listar_equipamentos():
    lista_equipamentos = tabela_equipamento.select_todos_equipamentos()
    return render_template('equipamentos.html', equipamentos=lista_equipamentos)


@app.route("/equipamentos/novo", methods=["GET", "POST"])
def novo_equipamento():
    if request.method == "POST":
        nome = request.form.get("nome")
        tipo = request.form.get("tipo")

        if not nome:
            flash('Preencha o nome do equipamento', 'error')
            return redirect(url_for('novo_equipamento'))
        if not tipo:
            flash('Preencha o tipo do equipamento', 'error')
            return redirect(url_for('novo_equipamento'))

        tabela_equipamento.salvar_equipamento(nome=nome, tipo=tipo)
        return redirect(url_for('listar_equipamentos'))

    equipamentos = tabela_equipamento.select_todos_equipamentos()
    servicos = tabela_ordem_servico.select_todos()
    return render_template("equipamentos.html", equipamentos=equipamentos, servicos=servicos)

@app.route("/equipamentos/<id_equipamento>", methods=["GET", "POST"])
def editar_equipamento(id_equipamento):
    # Buscar o jogador no banco
    equipamento = tabela_equipamento.select_um(id_equipamento)

    if request.method == "POST":
        nome = request.form.get("nome")
        tipo = request.form.get("tipo")

        if not nome:
            flash('Preencha o nome do equipamento', 'error')
        elif not tipo:
            flash('Preencha o tipo do equipamento', 'error')
        else:
            equipamento.nome = nome
            equipamento.tipo = tipo
            db_session.commit()

            flash("Equipamento alterado com sucesso", category="success")

        return redirect(url_for("listar_equipamentos"))

        # Carregar as informações
    equipamentos = tabela_equipamento.select_todos()
    return render_template("equipamentos.html", equipamentos=equipamentos, editar=equipamento)


@app.route("/equipamentos/excluir/<equipamento_id>", methods=["GET", "POST"])
def excluir_equipamento(equipamento_id):
    equipamento_sql = select(Equipamento).where(Equipamento.id == equipamento_id)
    equipamento = db_session.execute(equipamento_sql).scalar_one_or_none()
    if equipamento:
        db_session.delete(equipamento)
        db_session.commit()
    return redirect(url_for('listar_equipamentos'))


@app.route('/recursos')
def listar_recursos():
    lista_recursos = tabela_recurso.select_todos_recursos()
    return render_template('recursos.html', recursos=lista_recursos)


@app.route("/recursos/novo", methods=["GET", "POST"])
def novo_recurso(servicos=None):
    if request.method == "POST":
        nome = request.form.get("nome")

        if not nome:
            flash('Preencha o nome do recurso', 'error')
            return redirect(url_for('novo_recurso'))

        tabela_recurso.salvar_recurso(nome=nome)
        return redirect(url_for('listar_recursos'))

    recursos = tabela_recurso.select_todos_recursos()
    servicos = tabela_ordem_servico.select_todos()
    return render_template("recursos.html", recursos=recursos, servicos=servicos)

@app.route('/excluir_recurso/<int:recurso_id>')
def excluir_recurso(recurso_id):
    recurso_sql = select(Recursos).where(Recursos.id == recurso_id)
    recurso = db_session.execute(recurso_sql).scalar_one_or_none()
    if recurso:
        db_session.delete(recurso)
        db_session.commit()
    return redirect(url_for('listar_recursos'))


if __name__ == "__main__":
    app.run(debug=True)
