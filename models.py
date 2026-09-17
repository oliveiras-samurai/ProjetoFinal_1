# importar bibliotecas
from sqlalchemy import create_engine, func, Column, Integer, String, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship, sessionmaker, declarative_base, scoped_session


# Base de dados endereço
engine = create_engine('mysql+pymysql://root:senaisp@localhost:3306/projeto_final')

# config sessao
db_session = scoped_session( sessionmaker(bind=engine))

Base = declarative_base()

class Usuario(Base):
    servico_id = None
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)
    telefone = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    data_nascimento = Column(DateTime, nullable=False)


class Servico(Base):
    usuario_id = None
    __tablename__ = 'servicos'
    id = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)
    data_abertura = Column(DateTime, nullable=False)
    data_encerramento = Column(DateTime, nullable=False)
    id_responsavel = Column(String(100), nullable=False)
    status_servico = Column(String(50), nullable=False)
    equipamento = Column(String(50), nullable=False)
    prioridade = Column(String(50), nullable=False)

class Equipamento(Base):
    servico_id = None
    os_id = None
    __tablename__ = 'equipamentos'
    id = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)
    tipo = Column (String(50), nullable=False)

class Recursos(Base):
    servico_id = None
    os_id = None
    __tablename__ = 'recursos'
    id = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)

