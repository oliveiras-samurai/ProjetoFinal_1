from datetime import datetime
from flask import flash
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from models import Usuario, db_session, Servico


def select_todos():
    servicos_sql = select(Servico)
    return db_session.execute(servicos_sql).scalars().all()


def select_quantidade_total():
    servicos_sql = select(func.count(Servico.id))
    qtd_total = db_session.execute(servicos_sql).scalar()
    return qtd_total



def salvar(nome, data_abertura, data_encerramento, id_responsavel, status_servico, equipamento, recurso, prioridade):
    try:
        resp_final = int(id_responsavel) if str(id_responsavel).isdigit() else id_responsavel
        status_final = int(status_servico) if str(status_servico).isdigit() else status_servico

        # Tratamento seguro caso as datas já venham como objetos datetime do Flask
        if isinstance(data_abertura, str):
            data_ab_formatada = datetime.strptime(data_abertura, '%Y-%m-%dT%H:%M') if data_abertura else None
        else:
            data_ab_formatada = data_abertura

        if isinstance(data_encerramento, str):
            data_en_formatada = datetime.strptime(data_encerramento, '%Y-%m-%dT%H:%M') if data_encerramento else None
        else:
            data_en_formatada = data_encerramento

        # CORREÇÃO DO EQUIPAMENTO: Trata listas vindas de checkboxes ou strings com separadores em branco
        if isinstance(equipamento, list):
            # Filtra itens vazios ou com vírgulas perdidas e junta por string
            lista_limpa = [str(x).strip() for x in equipamento if str(x).strip() and str(x).strip() != ',']
            equipamento_final = ", ".join(lista_limpa) if lista_limpa else "Nenhum"
        else:
            equipamento_str = str(equipamento).strip() if equipamento else ""
            equipamento_final = equipamento_str if (equipamento_str and equipamento_str != ',') else "Nenhum"

        recurso_final = str(recurso).strip() if recurso else "Nenhum"

        # Criando o objeto com mapeamento direto dos campos fundamentais
        novos_servicos = Servico(
            nome=nome,
            data_abertura=data_ab_formatada,
            data_encerramento=data_en_formatada
        )

        # Inserção dinâmica associando diretamente os valores tratados às colunas válidas
        if hasattr(novos_servicos, 'id_responsavel'):
            novos_servicos.id_responsavel = resp_final
        elif hasattr(novos_servicos, 'responsavel_id'):
            novos_servicos.responsavel_id = resp_final

        if hasattr(novos_servicos, 'status_servico'):
            novos_servicos.status_servico = status_final
        elif hasattr(novos_servicos, 'status'):
            novos_servicos.status = status_final

        # Vinculando os valores finais corrigidos aos atributos existentes na tabela
        if hasattr(novos_servicos, 'equipamento'):
            novos_servicos.equipamento = equipamento_final

        if hasattr(novos_servicos, 'recurso'):
            novos_servicos.recurso = recurso_final

        if hasattr(novos_servicos, 'prioridade'):
            novos_servicos.prioridade = str(prioridade) if prioridade else None

        db_session.add(novos_servicos)
        db_session.commit()

        flash("Serviço criado com sucesso", category='success')
        return novos_servicos

    except SQLAlchemyError as e:
        db_session.rollback()

        print("\n" + "!" * 60)
        print("[ERRO SECRETO DO MYSQL - VEJA ABAIXO]")
        print(e)
        print("!" * 60 + "\n")

        flash('Erro ao salvar serviço no banco', category='error')
    except Exception as e:
        db_session.rollback()
        print(f'Erro inesperado: {e}')
        flash('Erro, tente novamente', category='error')


def select_um(id_servico):
    servico_sql = select(Servico).where(Servico.id == id_servico)
    servico = db_session.execute(servico_sql).scalar_one_or_none()
    return servico
