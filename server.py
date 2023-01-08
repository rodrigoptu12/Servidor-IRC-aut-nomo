import socket
import threading

from usuario import Usuario
from canal import Canal

# Cria o socket do servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Obtém o endereço IP e a porta do servidor
server_address = ("localhost", 3030)
print("Iniciando o servidor em {} na porta {}".format(*server_address))
server_socket.bind(server_address)

# Começa a escutar por conexões
server_socket.listen()

# Dicionário de usuários conectados ao servidor

# Dicionário de canais existentes


def handle_client(client_socket: socket.socket, client_address):
    # inicializa o nome de usuário
    while True:
        usuario = Usuario()
        # Recebe o nome de usuário do cliente
        username = client_socket.recv(1024).decode("utf-8")
        # Verifica se o nome de usuário já está em uso
        #instanciar Usuario
        if usuario.conectar(username, client_socket, client_address) == False:
            client_socket.send("ERR_NICKNAMEINUSE".encode("utf-8"))
        else:
            client_socket.send("OK".encode("utf-8"))
            break
        client_socket.close()
        return
    else:
        client_socket.send("OK".encode("utf-8"))

    usuario.mostrar_usuarios()

    while True:
        # Recebe o comando do cliente
        command = client_socket.recv(1024).decode("utf-8")
        if command == "/QUIT":
            # Fecha a conexão se o comando for 'QUIT'
            # Remove o usuário da lista de usuários conectados
            usuario.sair()
            usuario.mostrar_usuarios()
            break
        elif command.startswith("/NICK"):
            # Dar um apelido ou Altera o apelido do usuário
            #verificar numero de argumentos
            if len(command.split(" ")) != 2:
                client_socket.send("ERR_PARAMS".encode("utf-8"))
                continue
            _, new_username = command.split(" ", 1)
            # Verifica se o apelido já está sendo usado por outro usuário
            usuario.mudar_nick(new_username)
            # mostrar lista de usuários
            usuario.mostrar_usuarios()
            client_socket.send("OK".encode("utf-8"))
            # Atualiza o nome de usuário
            username = new_username
        elif command.startswith("/USER"):
            # Registra o nome de usuário
            # /USER <username> <hostname> <servername> :<realname>
            _, username, _, _, realname = command.split(" ", 4)
            usuario.set_usuario(username, realname)
            # Verifica se o nome de usuário já está sendo usado por outro usuário
        elif command.startswith("/JOIN"):
            # Entra em um canal  
            # /JOIN <channel> 
            #verificar numero de argumentos
            if len(command.split(" ")) != 2:
                client_socket.send("ERR_PARAMS".encode("utf-8"))
                continue
            _, canal = command.split(" ", 1)
            usuario.enviar_mensagem(Canal.add_usuario(canal, usuario))
        elif command.startswith("/PART"):
            # Sai de um canal
            # /PART <channel> 
            #verificar numero de argumentos
            if len(command.split(" ")) != 2:
                client_socket.send("ERR_PARAMS".encode("utf-8"))
                continue
            _, canal = command.split(" ", 1)
            usuario.enviar_mensagem(Canal.remove_usuario(canal, usuario))
        elif command.startswith("/LIST"):
            # Lista os canais existentes
            usuario.enviar_mensagem(Canal.mostrar_canais())
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
                Canal.enviar_mensagem(receiver, usuario, message)
            else:
                usuario.enviar_mensagem(receiver, usuario, message)
        elif command.startswith("/WHO"):
            # Lista os usuários conectados em um canal
            #verificar numero de argumentos
            if len(command.split(" ")) != 2:
                client_socket.send("ERR_PARAMS".encode("utf-8"))
                continue
            _, canal = command.split(" ", 1)
            usuario.enviar_mensagem(Canal.mostrar_canal(canal))
def main():
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