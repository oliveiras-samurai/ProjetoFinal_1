from models import Pessoa, db_session

def criar_usuario():
    administrador=Pessoa(nome="teste_adm1",email="adm1@gmail.com",papel="administrador")
    administrador.set_password("10")
    db_session.add(administrador)
    db_session.commit()
    print('Usuário criado com sucesso!')

criar_usuario()