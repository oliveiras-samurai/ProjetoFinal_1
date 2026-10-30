from flask import flash
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from models import db_session, Servico, Recursos


def select_todos():
    # Retorna todos os Serviços e a quantidade de equipamentos vinculados a cada um
    recursos_sql = (
        select(Servico, func.count(Recursos.id).label('total_recursos'))
        .outerjoin(Recursos, Recursos.servico_id == Servico.id)
        .group_by(Servico.id)
    )

    return db_session.execute(recursos_sql).all()


def select_quantidade_total():
    # Conta o total absoluto de equipamentos no banco
    recursos_sql = select(func.count(Recursos.id))
    return db_session.execute(recursos_sql).scalar()


# 🛅 FUNÇÃO COMPLETA PARA SALVAR A OS (SERVIÇO)
def salvar_servico(nome, data_abertura, data_encerramento, id_responsavel, status_servico):
    try:
        novo_servico = Servico(
            nome=nome,
            data_abertura=data_abertura,
            data_encerramento=data_encerramento,
            id_responsavel=id_responsavel,
            status_servico=status_servico
        )

        db_session.add(novo_servico)
        db_session.commit()

        flash("Serviço criado com sucesso", category='success')
        return novo_servico

    except SQLAlchemyError as e:
        db_session.rollback()
        print(f'Erro ao salvar Serviço no banco: {e}')
        flash('Erro ao salvar no banco. Verifique os dados.', category='error')
    except Exception as e:
        db_session.rollback()
        print(f'Erro inesperado no Serviço: {e}')
        flash('Erro, tente novamente', category='error')


# ⚙️ NOVA FUNÇÃO PARA SALVAR APENAS EQUIPAMENTO (Se você tiver um formulário para isso)
def salvar_recurso(nome):
    try:
        # Ajuste os campos (ex: nome, tipo) de acordo com as colunas do seu modelo Equipamento
        novo_recurso = Recursos(
            nome=nome
        )

        db_session.add(novo_recurso)
        db_session.commit()

        flash("Recurso cadastrado com sucesso", category='success')
        return novo_recurso

    except SQLAlchemyError as e:
        db_session.rollback()
        print(f'Erro ao salvar recurso no banco: {e}')
        flash('Erro ao salvar recurso.', category='error')


def select_um_recurso(id_recurso):
    # Busca um equipamento específico pelo "ID"
    recursos_sql = select(Recursos).where(Recursos.id == id_recurso)
    return db_session.execute(recursos_sql).scalar_one_or_none()


def select_todos_recursos():
    # Busca todos os equipamentos e faz um JOIN com Serviço para trazer o nome
    recursos_sql = (
        select(Recursos, Servico.nome.label('nome_servico'))
        .outerjoin(Servico, Recursos.servico_id == Servico.id)
    )
    return db_session.execute(recursos_sql).all()




