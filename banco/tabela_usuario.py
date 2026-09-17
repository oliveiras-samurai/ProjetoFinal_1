from datetime import time

from flask import flash
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from models import Usuario, db_session, Servico


def select_todos():
    # Buscar todos os times no banco
    # 1 - Montar o select
    # join(Tabela que eu quero juntar, condição = chave estrangeira igual chave primária)
    usuarios_sql = select(Usuario, Servico).join(Servico, Usuario.servico_id == Servico.id)
    # 2 - Executar o select
    # usar scalars quando tiver somente uma tabela
    usuarios = db_session.execute(usuarios_sql).all()

    return usuarios

def select_quantidade_total():
    usuarios_sql = select(func.count(Usuario.id))
    qtd_total = db_session.execute(usuarios_sql).scalar()
    return qtd_total

print(select_quantidade_total())

def salvar(nome, telefone, email, data_nascimento):
    try:
        # cria uma nova pessoa e adiciona na base de dados
        novos_servicos = Usuario(nome=nome, telefone=telefone, email=email, data_nascimento=data_nascimento)
        # Inicializa a sessão do banco de dados
        db_session.add(novos_servicos)
        db_session.commit()
        flash("Usuário criado com sucesso", category='success')
        print(f'{novos_servicos}')
    except SQLAlchemyError as e:
        db_session.rollback()  # Reverte a transação em caso de erro
        print(f'Erro ao salvar usuario no banco: {e}')
        flash('Erro ao salvar usuario no banco', category='error')
    except Exception as e:
        db_session.rollback()
        print(f'Erro inesperado', e)
        flash('Erro, tente novamente', category='error')

def select_um(id_usuario):
    usuario_sql = select(Usuario).where(Usuario.id == id_usuario)
    usuario = db_session.execute(usuario_sql).scalar_one_or_none()
    return usuario


def select_por_servico(id_servico):
    # trazer jogadores de um time
    usuarios_sql = select(Usuario).where(Usuario.servico_id == int(id_servico))
    usuarios = db_session.execute(usuarios_sql).scalars().all()
    return usuarios

print(select_por_servico(1))

