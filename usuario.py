import socket


class Usuario:
    # todos os usuários dicionario str: Usuario adicionar tipagem na variavel
    usuarios: dict[str, "Usuario"] = {}

    def __init__(self):
        pass

    # conecta um usuário 
    def conectar(self, nickname: str, _socket: socket.socket, endereco):
        # cria um novo usuário
        self.nickname = nickname
        self.socket = _socket
        self.endereco = endereco
        self.username = None
        self.realname = None
        self.canal = None
        # adiciona o usuário à lista de usuários se ele não existir
        if self.nickname not in self.usuarios.keys():
            self.usuarios[self.nickname] = self
            _socket.send("OK".encode("utf-8"))
            return True
        else: # se o usuário já existir, retorna um erro
            _socket.send("ERR_NICKNAMEINUSE".encode("utf-8"))
            return False

    # desconecta um usuário
    def sair(self):
        # remove o usuário da lista de usuários se ele existir
        if self.nickname in self.usuarios.keys():
            del self.usuarios[self.nickname]
        # fecha o socket do cliente
        self.socket.close()

    def mudar_nickname(self, novo_nickname: str):
        # verifica se o novo nickname já existe
        if novo_nickname not in self.usuarios.keys():
            self.usuarios[novo_nickname] = self.usuarios[self.nickname]
            del self.usuarios[self.nickname]
            self.nickname = novo_nickname
            self.socket.send("OK".encode("utf-8"))
        else:
            self.socket.send("ERR_NICKNAMEINUSE".encode("utf-8"))

    def set_usuario(self, username: str = None, realname: str = None):
        self.username = username
        self.realname = realname

    def set_canal(self, canal: str = None):
        self.canal = canal

    def informacoes(self):
        info = f"\nNickname: {self.nickname} \
                  \nSocket: {self.socket} \
                  \nEndereço: {self.endereco} \
                  \nUsername: {self.username} \
                  \nRealname: {self.realname} \
                  \nCanal atual: {self.canal}"

        return info

    def enviar_mensagem(self, destinatario: str, mensagem: str):
        if destinatario in self.usuarios.keys():
            self.usuarios[destinatario].socket.send(mensagem.encode("utf-8"))
        else:
            self.socket.send("ERR_NOSUCHNICK".encode("utf-8"))

    def receber_mensagem(self, mensagem: str):
        self.socket.send(mensagem.encode("utf-8"))

    @staticmethod
    def mostrar_usuarios():
        print("Usuários conectados:")
        for usuario in Usuario.usuarios:
            print(usuario)

    def __str__(self):
        return self.nickname
