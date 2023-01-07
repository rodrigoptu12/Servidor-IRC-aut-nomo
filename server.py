import socket
import threading

# Cria o socket do servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Obtém o endereço IP e a porta do servidor
server_address = ('localhost', 6669)
print('Iniciando o servidor em {} na porta {}'.format(*server_address))
server_socket.bind(server_address)

# Começa a escutar por conexões
server_socket.listen(5)

# Dicionário de usuários conectados ao servidor
connected_users = {}


def handle_client(client_socket, client_address):
    # Recebe o nome do usuário
    #username = client_socket.recv(1024).decode('utf-8')
    username = ''
    # Adiciona o usuário ao dicionário de usuários conectados
    # connected_users[client_address] = username
    # print('{} conectado'.format(username))
    # # print connected_users
    # print('Usuários conectados: {}'.format(', '.join(
    #     connected_users.values())))
    while True:
        # Recebe o comando do cliente
        command = client_socket.recv(1024).decode('utf-8')
        if command == 'QUIT':
            # Fecha a conexão se o comando for 'QUIT'
            client_socket.close()
            # Remove o usuário do dicionário de usuários conectados
            if username in connected_users.values():
                del connected_users[client_address]
                print('{} desconectado'.format(username))
                print('Usuários conectados: {}'.format(', '.join(
                    connected_users.values())))

            break
        elif command.startswith('NICK'):
            # Dar um apelido ou Altera o apelido do usuário
            _, new_username = command.split(' ', 1)
            # Verifica se o apelido já está sendo usado por outro usuário
            if new_username in connected_users.values():
                client_socket.send('ERR_NICKNAMEINUSE'.encode('utf-8'))
            else:
                connected_users[client_address] = new_username
                print('{} alterou o apelido para {}'.format(
                    username, new_username))
                print('Usuários conectados: {}'.format(', '.join(
                    connected_users.values())))
                client_socket.send('OK'.encode('utf-8'))
                # Atualiza o nome de usuário
                username = new_username
                break;
        


while True:
    # Aceita uma conexão
    client_socket, client_address = server_socket.accept()
    print('Conexão de:', client_address)
    # Cria uma thread para lidar com o cliente
    client_thread = threading.Thread(target=handle_client,
                                     args=(client_socket, client_address))
    client_thread.start()