import socket

# Cria o socket do cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Obtém o endereço IP e a porta do servidor
server_address = ('localhost', 6669)
print('Conectando a {} na porta {}'.format(*server_address))
client_socket.connect(server_address)

# Envia o nome do usuário para o servidor
# username = input('Digite seu nome de usuário: ')
username = ''
# client_socket.send(username.encode('utf-8'))

while True:
    # Lê o comando do usuário
    command = input('Digite o comando: ')
    if command == 'QUIT':
        # Envia o comando 'QUIT' para o servidor e fecha a conexão
        client_socket.send(command.encode('utf-8'))
        client_socket.close()
    elif command.startswith('NICK'):
        # Envia o comando NICK para o servidor
        client_socket.send(command.encode('utf-8'))
        # Recebe a resposta do servidor
        response = client_socket.recv(1024).decode('utf-8')
        if response == 'ERR_NICKNAMEINUSE':
            print('O nome de usuário já está em uso')
        else:
            # Atualiza o nome de usuário
            username = command.split(' ', 1)[1]
            print('Seu nome de usuário agora eh {}'.format(username))
    else:
        print('Comando inválido')
