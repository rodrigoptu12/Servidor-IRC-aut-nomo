from usuario import Usuario

nomes_canais = ["#geral", "#jogos", "#filmes", "#musicas", "#programacao"]


class Canal:
    # todos os canais
    canais: dict[str, "Canal"] = {}  # nome: canal

    def __init__(self, nome: str):
        self.nome = nome  # nome do canal
        self.usuarios: list[Usuario] = []  # usuários que estão no canal

    def __str__(self):
        return self.nome

    @staticmethod
    def add_usuario(nome_canal, usuario: Usuario):
        # o usuário não pode estar em mais de um canal
        if nome_canal not in Canal.canais.keys():
            return "ERR_NOSUCHCHANNEL"
        if usuario.canal is not None:
            Canal.remove_usuario(usuario.canal, usuario)  # sair do canal atual

        Canal.canais[nome_canal].usuarios.append(usuario)  # entrar
        usuario.set_canal(nome_canal)  # atualizar canal do usuário
        Canal.enviar_mensagem(nome_canal, f"Usuário {usuario.nickname} entrou do canal", usuario)
        usuario.receber_mensagem("Bem vindo ao canal " + nome_canal + "\n")
        #return f"Usuário {usuario.nickname} entrou no canal {nome_canal}"

    @staticmethod
    def remove_usuario(nome_canal, usuario: Usuario):
        if usuario.canal != nome_canal:
            usuario.receber_mensagem("ERR_NOTONCHANNEL")
            return
        if nome_canal not in Canal.canais.keys():
            usuario.receber_mensagem("ERR_NOSUCHCHANNEL")
            return

        canal = Canal.canais[nome_canal]  # canal que o usuário quer sair
        canal.usuarios.remove(usuario)
        usuario.set_canal(None)  # atualizar canal do usuário
        Canal.enviar_mensagem(nome_canal, f"Usuário {usuario.nickname} saiu do canal", usuario)
        usuario.receber_mensagem("Você saiu do canal " + nome_canal + "\n")
        
    @staticmethod
    def mostrar_canal(nome_canal: str):
        if nome_canal not in Canal.canais.keys():
            return "Este canal não existe"
        canal = Canal.canais[nome_canal]
        frase = f"Usuarios do canal :{nome_canal}\n"
        for usuario in canal.usuarios:
            frase += f"Usuario: {usuario.nickname}\n"
        return frase

    @staticmethod
    def mostrar_canais():
        frase = "Canais:\n"
        for nome in nomes_canais:
            canal = Canal.canais[nome]
            frase += f"Canal: {canal.nome} Número de Usuários: ({len(canal.usuarios)})\n"
        return frase

    @staticmethod
    def enviar_mensagem(nome_canal: str, mensagem: str, remetente: Usuario = None):
        canal = Canal.canais[nome_canal]
        # se o remetente estiver no canal, não precisa enviar a mensagem para ele
        message = remetente.nickname + ": " + mensagem 
        for usuario in canal.usuarios:
            if usuario.nickname != remetente.nickname:
                usuario.receber_mensagem(message)

    @staticmethod
    def iniciar_canais_padrao():
        for nome in nomes_canais:
            Canal.canais[nome] = Canal(nome)
