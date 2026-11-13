from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, true, Date
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session, DeclarativeBase
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# Base de dados endereço
engine = create_engine('mysql+pymysql://root:senaisp@localhost:3306/projeto_final')

# config sessao
db_session = scoped_session( sessionmaker(bind=engine))

class Base(DeclarativeBase):
    pass

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
    recurso = Column(String(50), nullable=False)
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

class Pessoa(Base, UserMixin):
    __tablename__ = "pessoas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(50), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    criado_em = Column(DateTime, server_default=func.now())
    atualizado_em = Column(DateTime, onupdate=func.now())

    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
