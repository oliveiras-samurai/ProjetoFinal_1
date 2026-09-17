# importar bibliotecas
import ...

# Base de dados endereço
engine = create_engine('mysql+pymysql://root:senaisp@localhost:3306/taskflow')

# config sessao
local_session = sessionmaker(bind=engine)

Base = declarative_base()

class Pessoa(Base):
    __tablename__ = 'pessoas'
