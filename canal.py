from usuario import Usuario

nomes_canais = ["#geral", "#jogos", "#filmes", "#musicas", "#programacao"]


class Canal:
    # todos os canais
    canais = {}

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
        return f"Usuário {usuario.nick} entrou no canal {nome_canal}"

    @staticmethod
    def remove_usuario(nome_canal, usuario: Usuario):
        if usuario.canal != nome_canal:
            return "Usuário não está no canal informado"
        if nome_canal not in Canal.canais.keys():
            return "Canal não existe"

        canal = Canal.canais[nome_canal]  # canal que o usuário quer sair
        canal.usuarios.remove(usuario)
        usuario.set_canal(None)  # atualizar canal do usuário
        return f"Usuário {usuario.nick} saiu do canal {canal.nome}"

    @staticmethod
    def mostrar_canal(nome_canal: str):
        if nome_canal not in Canal.canais.keys():
            return "Este canal não existe"
        canal = Canal.canais[nome_canal]
        frase = f"Usuarios do canal :{nome_canal}\n"
        for usuario in canal.usuarios:
            frase += f"Usuario: {usuario.nick}\n"
        return frase

    @staticmethod
    def mostrar_canais():
        frase = "Canais:\n"
        for nome in nomes_canais:
            canal = Canal.canais[nome]
            frase += f"Canal: {canal.nome} Número de Usuários: ({len(canal.usuarios)})\n"

        return frase

    @staticmethod
    def enviar_mensagem(nome_canal: str, mensagem: str, usuario: Usuario):
        canal = Canal.canais[nome_canal]
        for usuario in canal.usuarios:
            usuario.enviar_mensagem(mensagem)

    @staticmethod
    def iniciar_canais_padrao():
        for nome in nomes_canais:
            Canal.canais[nome] = Canal(nome)