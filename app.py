from datetime import datetime
from functools import wraps
from os import times
from flask import Flask, render_template, request, redirect, url_for, flash, g
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from banco import tabela_ordem_servico, tabela_usuario, tabela_equipamento, tabela_recurso
from models import db_session, Usuario, Pessoa, Servico, Equipamento, Recursos
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = "chave-secreta-projeto-final-2026"

# Configuração Flask_Login
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Faça login para acessar"


# Prevenir gargalo "too many connections"
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


# Carregar informações do usuário logado
@login_manager.user_loader
def load_user(user_id):
    return db_session.get(Pessoa, int(user_id))

def roles_required(*papeis_permitidos):
    '''
    Decorator para restringir acesso
    baseado no papel do usuario logado
    '''
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.papel not in papeis_permitidos:
                flash("Acesso negado: Você não tem permissão para acessar esta página", category='error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Interface de autenticação
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()

        pessoa_sql = select(Pessoa).where(Pessoa.email == email)
        pessoa_resultado = db_session.execute(pessoa_sql).scalar()

        if not pessoa_resultado:
            flash('Falha na autenticação: E-mail não encontrado', 'error')
            return redirect(url_for('login'))

        if pessoa_resultado and pessoa_resultado.check_password(senha):
            login_user(pessoa_resultado)
            return redirect(url_for("dashboard"))
        else:
            flash('falha na autenticação: Senha incorreta', 'error')
            return redirect(url_for('login'))

    return render_template(
        "login.html",
        registro=request.args.get("registro")
    )


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route('/registro', methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()

        if not nome and not email and not senha:
            flash('Preencher todos os campos', 'error')
            return redirect(url_for('registro'))
        pessoa_sql = select(Pessoa).where(Pessoa.email == email)
        pessoa_email = db_session.execute(pessoa_sql).scalar_one_or_none()

        if pessoa_email:
            flash('E-mail já cadastrado', 'error')
            return redirect(url_for('registro'))
        try:
            nova_pessoa = Pessoa(
                nome=nome,
                email=email
            )
            nova_pessoa.set_password(senha)
            db_session.add(nova_pessoa)
            db_session.commit()
            flash('Usuário cadastrado', 'success')
            return redirect(url_for('login'))
        except SQLAlchemyError as e:
            print(f'SQLALchemyError:{e}')
            flash('Erro no banco')
            return redirect(url_for('registro'))
        except Exception as e:
            print(f'Erro ao registrar')
            flash(f'Erro ao registrar', category='error')
            return redirect(url_for('registro'))
    return render_template("login.html")


@app.route("/")

def inicio():
    return render_template('inicio.html')

@app.route("/dashboard")
@login_required
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


# --- USUÁRIOS ---
def get_usuarios():
    return db_session.execute(select(Usuario, Servico).outerjoin(Servico, Usuario.servico_id == Servico.id)).all()


@app.route('/usuarios')
@login_required
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
@login_required
def novo_usuario():
    if request.method == "POST":
        nome = request.form.get("nome")
        telefone = request.form.get("telefone")
        email = request.form.get("email")
        data_nascimento = request.form.get("data_nascimento")

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

        tabela_usuario.salvar(nome=nome, telefone=telefone, email=email, data_nascimento=data_nascimento)
        return redirect(url_for("listar_usuarios"))

    usuarios = tabela_usuario.select_todos()
    return render_template("usuarios.html", usuarios=usuarios)


@app.route("/usuarios/<id_usuario>", methods=["GET", "POST"])
@login_required
def editar_usuario(id_usuario):
    usuario = tabela_usuario.select_um(id_usuario)

    if request.method == "POST":
        nome = request.form.get("nome")
        telefone = request.form.get("telefone")
        email = request.form.get("email")
        data_nascimento = request.form.get("data_nascimento")

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

    usuarios = tabela_usuario.select_todos()
    return render_template("usuarios.html", usuarios=usuarios, editar=usuario)


@app.route("/usuarios/excluir/<usuario_id>", methods=["GET", "POST"])
@login_required
def excluir_usuario(usuario_id):
    usuario_sql = select(Usuario).where(Usuario.id == usuario_id)
    usuario = db_session.execute(usuario_sql).scalar_one_or_none()
    if usuario:
        db_session.delete(usuario)
        db_session.commit()
    return redirect(url_for('listar_usuarios'))
# --- SERVIÇOS ---
@app.route("/servicos")
@login_required
@roles_required('admin')
def listar_servicos():
    servicos = tabela_ordem_servico.select_todos()
    return render_template("servico.html", servicos=servicos)


@app.route("/servicos/novo", methods=["GET", "POST"])
@login_required
@roles_required('admin')
def novo_servico(id_responsavel=None):
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        data_abertura = request.form.get("data_abertura")
        data_encerramento = request.form.get("data_encerramento")
        id_responsavel = request.form.get("id_responsavel")
        status_servico = request.form.get("status_servico")
        equipamento = request.form.get("equipamento")
        recurso = request.form.get("recurso")
        prioridade = request.form.get("prioridade")

        if not nome:
            flash('Preencha o nome', 'error')
            return redirect(url_for('novo_servico'))

        tabela_ordem_servico.salvar(
            nome=nome,
            data_abertura=data_abertura,
            data_encerramento=data_encerramento,
            id_responsavel=id_responsavel,
            status_servico=status_servico,
            equipamento=equipamento,
            recurso=recurso,
            prioridade=prioridade
        )
        return redirect(url_for("listar_servicos"))

    servicos = tabela_ordem_servico.select_todos()
    equipamentos = db_session.execute(select(Equipamento)).scalars().all()
    recursos = db_session.execute(select(Recursos)).scalars().all()
    usuarios = db_session.execute(select(Usuario)).scalars().all()

    return render_template(
        "servico.html",
        servicos=servicos,
        lista_equipamentos=equipamentos,
        lista_recursos=recursos,
        lista_usuarios=usuarios,
    )


@app.route("/servicos/<id_servico>", methods=["GET", "POST"])
@login_required
def editar_servico(id_servico, id_responsavel=None):
    servico = tabela_ordem_servico.select_um(id_servico)

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        data_abertura = request.form.get("data_abertura")
        data_encerramento = request.form.get("data_encerramento")
        id_responsavel = request.form.get("id_responsavel")
        status_servico = request.form.get("status_servico")
        equipamento = request.form.get("equipamento")
        recurso = request.form.get("recurso")
        prioridade = request.form.get("prioridade")

        if not nome:
            flash('Preencha o nome', 'error')
            return redirect(url_for('editar_servico', id_servico=id_servico))

        servico.nome = nome
        servico.id_responsavel = id_responsavel
        servico.status_servico = status_servico
        servico.equipamento = equipamento if equipamento else "Nenhum"
        servico.recurso = recurso if recurso else "Nenhum"
        servico.prioridade = prioridade

        if data_abertura:
            servico.data_abertura = datetime.strptime(data_abertura, '%Y-%m-%dT%H:%M')
        if data_encerramento:
            servico.data_encerramento = datetime.strptime(data_encerramento, '%Y-%m-%dT%H:%M')

        db_session.commit()
        flash("Serviço alterado com sucesso", category="success")
        return redirect(url_for("listar_servicos"))

    servicos = tabela_ordem_servico.select_todos()
    equipamentos = db_session.execute(select(Equipamento)).scalars().all()
    recursos = db_session.execute(select(Recursos)).scalars().all()
    usuarios = db_session.execute(select(Usuario)).scalars().all()

    return render_template(
        "servico.html",
        servicos=servicos,
        editar=servico,
        lista_equipamentos=equipamentos,
        lista_recursos=recursos,
        lista_usuarios=usuarios,
    )


@app.route("/servicos/excluir/<servico_id>", methods=["GET", "POST"])
@login_required
def excluir_servico(servico_id):
    servico = tabela_ordem_servico.select_um(servico_id)
    if servico:
        db_session.delete(servico)
        db_session.commit()
        flash("Serviço excluído com sucesso", category="success")
    return redirect(url_for('listar_servicos'))


# --- EQUIPAMENTOS ---
@app.route("/equipamentos")
@login_required
def listar_equipamentos():
    equipamentos = tabela_equipamento.select_todos_equipamentos()
    return render_template("equipamentos.html", equipamentos=equipamentos)


@app.route("/equipamentos/novo", methods=["GET", "POST"])
@login_required
def novo_equipamento():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        tipo = request.form.get("tipo", "").strip()

        if not nome:
            flash('Preencha o nome do equipamento', 'error')
            return redirect(url_for('novo_equipamento'))

        tabela_equipamento.salvar_equipamento(nome=nome, tipo=tipo)
        return redirect(url_for("listar_equipamentos"))

    equipamentos = tabela_equipamento.select_todos_equipamentos()
    return render_template("equipamentos.html", equipamentos=equipamentos)


@app.route("/equipamentos/<id_equipamento>", methods=["GET", "POST"])
@login_required
def editar_equipamento(id_equipamento):
    equipamento = tabela_equipamento.select_um(id_equipamento)

    if request.method == "POST":
        equipamento.nome = request.form.get("nome", "").strip()
        equipamento.tipo = request.form.get("tipo", "").strip()
        db_session.commit()
        flash("Equipamento alterado com sucesso", category="success")
        return redirect(url_for("listar_equipamentos"))

    equipamentos = tabela_equipamento.select_todos_equipamentos()
    return render_template("equipamentos.html", equipamentos=equipamentos, editar=equipamento)


@app.route("/equipamentos/excluir/<equipamento_id>", methods=["GET", "POST"])
@login_required
def excluir_equipamento(equipamento_id):
    equipamento = tabela_equipamento.select_um(equipamento_id)
    if equipamento:
        db_session.delete(equipamento)
        db_session.commit()
        flash("Equipamento excluído com sucesso", category="success")
    return redirect(url_for('listar_equipamentos'))


# --- RECURSOS ---
@app.route("/recursos")
@login_required
def listar_recursos():
    recursos = db_session.execute(select(Recursos)).all()
    return render_template("recursos.html", recursos=recursos)


@app.route("/recursos/novo", methods=["GET", "POST"])
@login_required
def novo_recurso():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()

        if not nome:
            flash('Preencha o nome do recurso', 'error')
            return redirect(url_for('novo_recurso'))

        novo = Recursos(nome=nome)
        db_session.add(novo)
        db_session.commit()
        flash("Recurso cadastrado com sucesso", category="success")
        return redirect(url_for("listar_recursos"))

    recursos = db_session.execute(select(Recursos)).all()
    return render_template("recursos.html", recursos=recursos)


@app.route("/recursos/<recurso_id>", methods=["GET", "POST"])
@login_required
def editar_recurso(recurso_id):
    recurso = db_session.execute(select(Recursos).where(Recursos.id == recurso_id)).scalar_one_or_none()

    if request.method == "POST":
        recurso.nome = request.form.get("nome", "").strip()
        db_session.commit()
        flash("Recurso alterado com sucesso", category="success")
        return redirect(url_for("listar_recursos"))

    recursos = db_session.execute(select(Recursos)).all()
    return render_template("recursos.html", recursos=recursos, editar=recurso)


@app.route("/recursos/excluir/<recurso_id>", methods=["GET", "POST"])
@login_required
def excluir_recurso(recurso_id):
    recurso = db_session.execute(select(Recursos).where(Recursos.id == recurso_id)).scalar_one_or_none()
    if recurso:
        db_session.delete(recurso)
        db_session.commit()
        flash("Recurso excluído com sucesso", category="success")
    return redirect(url_for('listar_recursos'))



if __name__ == "__main__":
    app.run(debug=True)
