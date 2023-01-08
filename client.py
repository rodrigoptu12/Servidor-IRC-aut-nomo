import socket

# Cria o socket do cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Obtém o endereço IP e a porta do servidor
server_address = ('localhost', 3030)
print('Conectando a {} na porta {}'.format(*server_address))
client_socket.connect(server_address)

# Envia o nome do usuário para o servidor
while True:
    username = input('Digite seu nome de usuário: ')
    client_socket.send(username.encode('utf-8'))
    response = client_socket.recv(1024).decode('utf-8')
    if response == 'ERR_NICKNAMEINUSE':
        print('O nome de usuário já está em uso')
    else:
        print('Conectado ao servidor')
        break

while True:
    # Lê o comando do usuário
    command = input('>: ')
    if command == '/QUIT':
        # Envia o comando 'QUIT' para o servidor e fecha a conexão
        client_socket.send(command.encode('utf-8'))
        client_socket.close()
        break
    elif command.startswith('/NICK'):
        # Envia o comando NICK para o servidor
        client_socket.send(command.encode('utf-8'))
        # Recebe a resposta do servidor
        response = client_socket.recv(1024).decode('utf-8')
        if response == 'ERR_NICKNAMEINUSE':
            print('O nome de usuário já está em uso')
        elif response == 'ERR_PARAMS':
            print('O comando NICK deve ser seguido de um nome de usuário')
        else:
            # Atualiza o nome de usuário
            username = command.split(' ', 1)[1]
            print('Seu nome de usuário agora eh {}'.format(username))
    elif command.startswith('/JOIN'):
        # Envia o comando JOIN para o servidor
        client_socket.send(command.encode('utf-8'))
        # Recebe a resposta do servidor
        response = client_socket.recv(1024).decode('utf-8')
        print(response)
        if response == 'ERR_PARAMS':
            print('Erro de Parametros')
        elif response == 'ERR_NOSUCHCHANNEL':
            print('Canal não existe')
        else:
            print('Entrou no canal com sucesso!')
            
    elif command.startswith('/PART'):
        # Envia o comando LIST para o servidor
        client_socket.send(command.encode('utf-8'))
        # Recebe a resposta do servidor
        response = client_socket.recv(1024).decode('utf-8')
        if (response == "ERR_PARAMS"):
            print('Falha ao sair do canal')
        else:
            print(response)
    elif command == '/LIST':
        # Envia o comando LIST para o servidor
        client_socket.send(command.encode('utf-8'))
        # Recebe a resposta do servidor
        response = client_socket.recv(1024).decode('utf-8')
        print (response)
    elif command.startswith('/WHO'):
        # Envia o comando WHO para o servidor
        client_socket.send(command.encode('utf-8'))
        # Recebe a resposta do servidor
        response = client_socket.recv(1024).decode('utf-8')
        
        print (response)
    else:   
        print('Comando inválido')
