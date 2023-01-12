import socket
import select
import threading
import curses
# Tratamento de erros
erros = ['ERR_NICKNAMEINUSE', 'ERR_PARAMS', 'ERR_NOSUCHCHANNEL', 'ERR_NOSUCHNICK', 'ERR_NOTONCHANNEL', 'ERR_NEEDMOREPARAMS']
def handle_response(response):
    if response in erros:
        if response == 'ERR_NICKNAMEINUSE':
            print('O nome de usuário já está em uso')
        elif response == 'ERR_PARAMS':
            print('Erro de Parametros')
        elif response == 'ERR_NOSUCHCHANNEL':
            print('Canal não existe')
        elif response == 'ERR_NOSUCHNICK':
            print('Nick não existe')
        elif response == 'ERR_NOTONCHANNEL':
            print('Você não está no canal')
        elif response == 'ERR_NEEDMOREPARAMS':
            print('Faltam parâmetros')
    else:
        print(response)

def my_raw_input(stdscr: curses.window, r, c, prompt_string):
    curses.echo() 
    stdscr.addstr(r, c, prompt_string)
    stdscr.refresh()
    input = stdscr.getstr(r + 1, c, 144).decode()
    return input  #       ^^^^  reading input at next line

def input_thread(client_socket: socket.socket, stdscr: curses.window):
    while True:
        stdscr.move(curses.LINES-1, curses.COLS-1)
        message = my_raw_input(stdscr, 2, 3, "cool or hot?").lower()
        client_socket.send(f"{message.decode()}\n".encode())
        stdscr.move(curses.LINES-1, 0)
        # stdscr.addstr(">: ")
        # stdscr.clrtoeol()
        # message = stdscr.getstr(curses.LINES-1, 4).decode()
        # stdscr.addstr(">: " + message + '\n')
        # # Lê a mensagem do usuário
        # # message = input()   
        # # Envia a mensagem para o servidor
        # client_socket.send(message.encode('utf-8'))
        # stdscr.refresh()


def output_thread(client_socket: socket.socket, stdscr: curses.window):
    while True:
        message = f"{client_socket.recv(1024).decode()}"[:curses.COLS-1]
        stdscr.addstr(message + '\n')
        stdscr.refresh()
        stdscr.move(curses.LINES-1, 0)
        # Recebe a mensagem do servidor
        # response = client_socket.recv(1024).decode('utf-8')
        # stdscr.move(curses.LINES-2, 0)
        # stdscr.insstr(response + '\n')
        # stdscr.move(curses.LINES-1, 4)
        # stdscr.refresh()
        # Trata a mensagem recebida
       # handle_response(f"{response}")



def start(stdscr: curses.window):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Obtém o endereço IP e a porta do servidor
    server_address = ('localhost', 3033)
    print('Conectando a {} na porta {}'.format(*server_address))
    client_socket.connect(server_address)

    # stdscr.clear()
    # # mostra a mensagem "Enter your name:" na tela
    # nickname = my_raw_input(stdscr, 0, 0, "Enter your nickname: ")
    # stdscr.addstr(1, 0, nickname)
    # # Envia o nome do usuário para o servidor
    # client_socket.send(nickname.encode('utf-8'))
    # response = client_socket.recv(1024).decode('utf-8')
    # # Envia o nome do usuário para o servidor
    while True:
        stdscr.clear()
        nickname = my_raw_input(stdscr, 2, 3, "Enter your nickname: ")
        client_socket.send(nickname.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        if response == 'ERR_NICKNAMEINUSE':
            stdscr.addstr('O nome de usuário já está em uso\n')
            stdscr.refresh()
            stdscr.getch()
        else:
            stdscr.addstr('Conectado com sucesso\n', curses.A_COLOR)     
            stdscr.refresh()
            stdscr.getch()
            break
        
    #array de comandos
    comandos = ["/NICK", "/USER", "/PART", "/LIST", "/PRIVMSG", "/WHO", "/JOIN", "/QUIT"]
    while True:

        # Lê o comando do usuário
        command = input('>: ')
        # verifica se o comando é válido se 
        if command.startswith('/') and command.split(' ', 1)[0] not in comandos:
            stdscr.addstr('Comando Invalido\n', curses.A_COLOR)     
            stdscr.refresh()
            stdscr.getch()
            continue
            # Envia o comando para o servidor
        client_socket.send(command.encode('utf-8'))
        # primeira palavra da string command ate o espaço
        if command.startswith("/QUIT"):
            client_socket.close()
            break
        else:
            # Recebe a resposta do servidor
            response = client_socket.recv(1024).decode('utf-8')
            handle_response(response)
            
    # Cria as threads de entrada e saída
    _input_thread = threading.Thread(target=input_thread, args=(client_socket, stdscr))
    _output_thread = threading.Thread(target=output_thread, args=(client_socket, stdscr))
    # Inicia as threads
    _input_thread.start()
    _output_thread.start()

    curses.endwin()  # finaliza o curses




def main():
    # Cria o socket do cliente
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Obtém o endereço IP e a porta do servidor
    server_address = ('localhost', 3033)
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
    #array de comandos
    comandos = ["/NICK", "/USER", "/PART", "/LIST", "/PRIVMSG", "/WHO", "/JOIN", "/QUIT"]
    while True:

        # Lê o comando do usuário
        command = input('>: ')
        # verifica se o comando é válido se 
        if command.startswith('/') and command.split(' ', 1)[0] not in comandos:
            print('Comando inválido')
            continue
            # Envia o comando para o servidor
        client_socket.send(command.encode('utf-8'))
        # primeira palavra da string command ate o espaço
        if command.startswith("/QUIT"):
            client_socket.close()
            break
        else:
            # Recebe a resposta do servidor
            response = client_socket.recv(1024).decode('utf-8')
            handle_response(response)
            

if __name__ == '__main__':
   #main()
    curses.wrapper(start)