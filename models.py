from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session

engine = create_engine('mysql+pymysql://root:senaisp@localhost:3306/projeto_final')
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

class Servico(Base):
    __tablename__ = 'servicos'
    id = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)
    data_abertura = Column(DateTime, nullable=False)
    data_encerramento = Column(DateTime, nullable=False)
    id_responsavel = Column(String(100), nullable=False)
    status_servico = Column(String(50), nullable=False)
    equipamento = Column(String(255), nullable=False)
    recurso = Column(String(255), nullable=False)
    prioridade = Column(String(50), nullable=False)

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)
    telefone = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    data_nascimento = Column(Date, nullable=False)
    servico_id = Column(Integer, ForeignKey('servicos.id'), nullable=True)

class Equipamento(Base):
    __tablename__ = 'equipamentos'
    id = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)
    tipo = Column(String(50), nullable=False)
    servico_id = Column(Integer, ForeignKey('servicos.id'), nullable=True)

class Recursos(Base):
    __tablename__ = 'recursos'
    id = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)
    servico_id = Column(Integer, ForeignKey('servicos.id'), nullable=True)

class Movimentacao(Base):
    __tablename__ = 'movimentacoes'
    id = Column(Integer, primary_key=True)
    tipo = Column(String(30), nullable=False)
    item_nome = Column(String(100), nullable=False)
    quantidade = Column(Integer, nullable=False, default=1)
    responsavel = Column(String(100), nullable=False)
    data_movimentacao = Column(DateTime, nullable=False)
    observacao = Column(String(255), nullable=True)
