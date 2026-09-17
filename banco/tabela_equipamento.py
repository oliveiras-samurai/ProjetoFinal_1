from datetime import time

from flask import flash
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from models import Equipamento, db_session, Servico


def select_todos_equipamentos():
    # Buscar todos os times no banco
    # 1 - Montar o select
    # join(Tabela que eu quero juntar, condição = chave estrangeira igual chave primária)
    equipamentos_sql = select(Equipamento, Servico).join(Servico, Equipamento.servico_id == Servico.id)
    # 2 - Executar o select
    # usar scalars quando tiver somente uma tabela
    equipamentos = db_session.execute(equipamentos_sql).all()

    return equipamentos

def select_quantidade_total():
    equipamentos_sql = select(func.count(Equipamento.id))
    qtd_total = db_session.execute(equipamentos_sql).scalar()
    return qtd_total

print(select_quantidade_total())

def salvar_equipamento(nome, tipo):
    try:
        # cria uma nova pessoa e adiciona na base de dados
        novos_servicos = Equipamento(nome=nome, tipo=tipo)
        # Inicializa a sessão do banco de dados
        db_session.add(novos_servicos)
        db_session.commit()
        flash("Equipamento criado com sucesso", category='success')
        print(f'{novos_servicos}')
    except SQLAlchemyError as e:
        db_session.rollback()  # Reverte a transação em caso de erro
        print(f'Erro ao salvar equipamento no banco: {e}')
        flash('Erro ao salvar equipamento no banco', category='error')
    except Exception as e:
        db_session.rollback()
        print(f'Erro inesperado', e)
        flash('Erro, tente novamente', category='error')

def select_um(id_equipamento):
    equipamento_sql = select(Equipamento).where(Equipamento.id == id_usuario)
    equipamento = db_session.execute(equipamento_sql).scalar_one_or_none()
    return equipamento


def select_por_servico(id_servico):
    # trazer jogadores de um time
    equipamentos_sql = select(Equipamento).where(Equipamento.servico_id == int(id_servico))
    equipamentos = db_session.execute(equipamentos_sql).scalars().all()
    return equipamentos

print(select_por_servico(1))

