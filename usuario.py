import socket


class Usuario:
    # todos os usuários
    usuarios = {}

    def __init__(self):
        pass

    def conectar(self, nick: str, _socket: socket, endereco):
        # cria um novo usuário
        self.nick = nick
        self.socket = _socket
        self.endereco = endereco
        self.username = None
        self.realname = None
        self.canal = None
        # adiciona o usuário à lista de usuários se ele não existir
        if self.nick not in self.usuarios.keys():
            self.usuarios[self.nick] = self
            return True
        else:
            _socket.send("ERR_NICKNAMEINUSE".encode("utf-8"))
            return False

    def sair(self):
        # remove o usuário da lista de usuários
        del self.usuarios[self.nick]
        # fecha o socket do cliente
        self.socket.close()

    def mudar_nick(self, novo_nick: str):
        # verifica se o novo nick já existe
        if novo_nick not in self.usuarios.keys():
            self.usuarios[novo_nick] = self.usuarios[self.nick]
            del self.usuarios[self.nick]
            self.nick = novo_nick
            self.socket.send("OK".encode("utf-8"))
        else:
            self.socket.send("ERR_NICKNAMEINUSE".encode("utf-8"))

    def set_usuario(self, username: str = None, realname: str = None):
        self.username = username
        self.realname = realname

    def set_canal(self, canal: str = None):
        self.canal = canal

    def informacoes(self):
        info = f"\nNick: {self.nick} \
                  \nSocket: {self.socket} \
                  \nEndereço: {self.endereco} \
                  \nUsername: {self.username} \
                  \nRealname: {self.realname}"

        return info

    def enviar_mensagem(self, mensagem: str):
        self.socket.send(mensagem.encode("utf-8"))

    @staticmethod
    def mostrar_usuarios():
        for usuario in Usuario.usuarios:
            print(usuario)

    def __str__(self):
        return self.nick
