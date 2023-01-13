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

    while True:
        # Recebe o comando do cliente
        command = client_socket.recv(1024).decode("utf-8")
        if command == "/QUIT":
            # Fecha a conexão se o comando for 'QUIT'
            # Remove o usuário da lista de usuários conectados
            Canal.remove_usuario(usuario.canal, usuario)
            usuario.sair()

            break
        elif command.startswith("/NICK"):
            # Dar um apelido ou Altera o apelido do usuário
            #verificar numero de argumentos
            if len(command.split(" ")) != 2:
                client_socket.send("ERR_PARAMS".encode("utf-8"))
                continue
            _, new_nickname = command.split(" ", 1)
            # Verifica se o apelido já está sendo usado por outro usuário
            print("comando nick: ", command)
            usuario.mudar_nickname(new_nickname)
            # mostrar lista de usuários
            usuario.mostrar_usuarios()
        elif command.startswith("/USER"):
            # Registra o nome de usuário
            # /USER <username> <hostname> <servername> :<realname>
            _, username, _, _, realname = command.split(" ", 4)
            usuario.set_usuario(username, realname)
        elif command.startswith("/JOIN"):
            # Entra em um canal  
            # /JOIN <channel> 
            #verificar numero de argumentos
            if len(command.split(" ")) != 2:
                client_socket.send("ERR_PARAMS".encode("utf-8"))
                continue
            _, canal = command.split(" ", 1)
            usuario.receber_mensagem(Canal.add_usuario(canal, usuario))
        elif command.startswith("/PART"):
            # Sai de um canal
            # /PART <channel> 
            #verificar numero de argumentos
            if len(command.split(" ")) != 2:
                client_socket.send("ERR_PARAMS".encode("utf-8"))
                continue
            _, canal = command.split(" ", 1)
            usuario.receber_mensagem(Canal.remove_usuario(canal, usuario))
        elif command.startswith("/LIST"):
            # Lista os canais existentes
            usuario.receber_mensagem(Canal.mostrar_canais())
        elif command.startswith("/PRIVMSG"):
            # Envia uma mensagem para um usuário ou canal
            # /PRIVMSG <receiver> :<message>
            #verificar numero de argumentos
            if len(command.split(" ")) != 3:
                client_socket.send("ERR_PARAMS".encode("utf-8"))
                continue
            _, receiver, message = command.split(" ", 2)

            #verifica se o destino é um canal ou usuário
            if receiver.startswith("#"):  
                Canal.enviar_mensagem(receiver, message, usuario)
            else:
                usuario.enviar_mensagem(receiver, message)
        elif command.startswith("/WHO"):
            # Lista os usuários conectados em um canal
            #verificar numero de argumentos
            if len(command.split(" ")) != 2:
                client_socket.send("ERR_PARAMS".encode("utf-8"))
                continue
            _, canal = command.split(" ", 1)
            usuario.receber_mensagem(Canal.mostrar_canal(canal))

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