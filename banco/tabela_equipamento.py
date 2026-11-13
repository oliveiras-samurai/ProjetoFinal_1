from flask import flash
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from models import db_session, Servico, Equipamento


def select_todos():
    # Retorna todos os Serviços e a quantidade de equipamentos vinculados a cada um
    equipamentos_sql = (
        select(Servico, func.count(Equipamento.id).label('total_equipamentos'))
        .outerjoin(Equipamento, Equipamento.servico_id == Servico.id)
        .group_by(Servico.id)
    )

    return db_session.execute(equipamentos_sql).all()


def select_quantidade_total():
    # Conta o total absoluto de equipamentos no banco
    equipamentos_sql = select(func.count(Equipamento.id))
    return db_session.execute(equipamentos_sql).scalar()


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

def salvar_equipamento(nome, tipo):
    try:
        novo_equipamento = Equipamento(
            nome=nome,
            tipo=tipo
        )

        db_session.add(novo_equipamento)
        db_session.commit()

        flash("Equipamento cadastrado com sucesso", category='success')
        return novo_equipamento

    except SQLAlchemyError as e:
        db_session.rollback()
        print(f'Erro ao salvar Equipamento no banco: {e}')
        flash('Erro ao salvar equipamento.', category='error')


def select_um(id_equipamento):
    # Busca um equipamento específico pelo ID
    equipamento_sql = select(Equipamento).where(Equipamento.id == id_equipamento)
    return db_session.execute(equipamento_sql).scalar_one_or_none()


def select_todos_equipamentos():
    equipamentos_sql = (
        select(Equipamento, Servico.nome.label('nome_servico'))
        .outerjoin(Servico, Equipamento.servico_id == Servico.id)
    )
    return db_session.execute(equipamentos_sql).all()
