import socket
import threading

from usuario import Usuario
from canal import Canal

def handle_client(client_socket: socket.socket, client_address):
    # inicializa o nome de usuário
    while True:
        usuario = Usuario()
        # Recebe o nome de usuário do cliente
        nickname = client_socket.recv(1024).decode("utf-8")
        # Verifica se o nome de usuário já está em uso
        #instanciar Usuario
        if usuario.conectar(nickname, client_socket, client_address):
            break

    usuario.mostrar_usuarios()
    usuario.receber_mensagem("Bem vindo ao servidor de chat!" \
                                "\nDigite /NICK <apelido> para mudar seu apelido" \
                                "\nDigite /USER <username> <realname> para definir seu username e realname" \
                                "\nDigite /QUIT para sair do servidor" \
                                "\nDigite /JOIN <canal> para entrar em um canal" \
                                "\nDigite /PART <canal> para sair de um canal" \
                                "\nDigite /LIST para ver os canais disponíveis" \
                                "\nDigite /PRIVMSG <destinatario> <mensagem> para enviar uma mensagem privada" \
                                "\nDigite /WHO para ver os usuários conectados" \
                            )


    while True:
        # Recebe o comando do cliente
        message = client_socket.recv(1024).decode("utf-8")
        if not message:
            # Fecha a conexão se o comando for 'QUIT'
            # Remove o usuário da lista de usuários conectados
            Canal.remove_usuario(usuario.canal, usuario)
            usuario.sair()
            usuario.mostrar_usuarios()
            break
        elif message == "/QUIT":
            # Fecha a conexão se o comando for 'QUIT'
            # Remove o usuário da lista de usuários conectados
            Canal.remove_usuario(usuario.canal, usuario)
            usuario.sair()

            break
        elif message.startswith("/NICK"):
            # Dar um apelido ou Altera o apelido do usuário
            #verificar numero de argumentos
            if len(message.split(" ")) != 2:
                client_socket.send("ERR_PARAMS".encode("utf-8"))
                continue
            _, new_nickname = message.split(" ", 1)
            # Verifica se o apelido já está sendo usado por outro usuário
            print("comando nick: ", message)
            usuario.mudar_nickname(new_nickname)
            # mostrar lista de usuários
            usuario.mostrar_usuarios()
        elif message.startswith("/USER"):
            # Registra o nome de usuário
            # /USER <username> <hostname> <servername> :<realname>
            _, username, _, _, realname = message.split(" ", 4)
            usuario.set_usuario(username, realname)
        elif message.startswith("/JOIN"):
            # Entra em um canal  
            # /JOIN <channel> 
            #verificar numero de argumentos
            if len(message.split(" ")) != 2:
                client_socket.send("ERR_PARAMS".encode("utf-8"))
                continue
            _, canal = message.split(" ", 1)
            Canal.add_usuario(canal, usuario)
        elif message.startswith("/PART"):
            # Sai de um canal
            # /PART <channel> 
            #verificar numero de argumentos
            if len(message.split(" ")) != 2:
                client_socket.send("ERR_PARAMS".encode("utf-8"))
                continue
            _, canal = message.split(" ", 1)
            Canal.remove_usuario(canal, usuario)
        elif message.startswith("/LIST"):
            # Lista os canais existentes
            usuario.receber_mensagem(Canal.mostrar_canais())
        elif message.startswith("/PRIVMSG"):
            # Envia uma mensagem para um usuário ou canal
            # /PRIVMSG <receiver> :<message>
            #verificar numero de argumentos
            if len(message.split(" ")) != 3:
                client_socket.send("ERR_PARAMS".encode("utf-8"))
                continue
            _, receiver, message = message.split(" ", 2)

            #verifica se o destino é um canal ou usuário
            message = "(privado) " + receiver +": "+ message
            if receiver.startswith("#"):  
                Canal.enviar_mensagem(receiver, message, usuario)
            else:
                usuario.enviar_mensagem(receiver, message)
        elif message.startswith("/WHO"):
            # Lista os usuários conectados em um canal
            #verificar numero de argumentos
            if len(message.split(" ")) != 2:
                client_socket.send("ERR_PARAMS".encode("utf-8"))
                continue
            _, canal = message.split(" ", 1)
            usuario.receber_mensagem(Canal.mostrar_canal(canal))
        else:
            if (usuario.canal != None):
                Canal.enviar_mensagem(usuario.canal, message, usuario)
                mensagem = usuario.nickname + ": " + message
                usuario.receber_mensagem(mensagem)
            else:
                usuario.receber_mensagem("ERRO! ENTRE EM UM CANAL PRIMEIRO!")

def main():

    # Cria o socket do servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Obtém o endereço IP e a porta do servidor
    server_address = ("localhost", 3030)
    print("Iniciando o servidor em {} na porta {}".format(*server_address))
    server_socket.bind(server_address)

    # Começa a escutar por conexões
    server_socket.listen()

    Canal.iniciar_canais_padrao()
    
    while True:
        # Aceita uma conexão
        client_socket, client_address = server_socket.accept()
        print("Conexão de:", client_address)
        # Cria uma thread para lidar com o cliente
        client_thread = threading.Thread(target=handle_client,
                                        args=(client_socket, client_address))
        client_thread.start()
    
if __name__ == "__main__":
    main()