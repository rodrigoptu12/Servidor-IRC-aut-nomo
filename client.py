import socket
import threading
import curses
from queue import Queue
import time

cursor_lock = threading.Lock()

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
    stdscr.addstr(r, c, prompt_string)
    stdscr.refresh()
    input = stdscr.getstr(r + 1, c, 144).decode()
    return input  #       ^^^^  reading input at next line

def output_thread(output_win: curses.window, messages_queue: Queue):
    while True:
        while not messages_queue.empty():
            with cursor_lock:
                response = messages_queue.get()
                output_win.addstr(f"{response}\n")
                output_win.refresh()
            time.sleep(.1) # sleep for 100ms to allow other threads to run
                

def messages_queue_thread(client_socket: socket.socket, messages_queue: Queue):
    while True:
        response = client_socket.recv(1024).decode()
        messages_queue.put(response)
        

def start(stdscr: curses.window):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #client_socket.setblocking(False)
    # Obtém o endereço IP e a porta do servidor
    server_address = ('localhost', 3030)
    stdscr.addstr(0, 0, f"Conectando ao servidor {server_address[0]}:{server_address[1]}")
    err = client_socket.connect_ex(server_address)
    if err == 115:
        stdscr.addstr(1, 0, "Conectando...")
        stdscr.refresh()
        while err == 115:
            err = client_socket.connect_ex(server_address)

    if err == 0:
        stdscr.addstr(1, 0, "Conectado com sucesso")
        stdscr.refresh()
        stdscr.getch()
    else:
        stdscr.addstr(1, 0, "Erro ao conectar")
        stdscr.refresh()
        stdscr.getch()
        exit(1)

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE) # color pair 1
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_CYAN) # color pair 2
    curses.echo() 

    while True:
        stdscr.clear()
        nickname = my_raw_input(stdscr, 0, 0, 'Digite seu nome de usuário:')
        client_socket.send(nickname.encode('utf-8'))
    
        response = client_socket.recv(1024).decode('utf-8')
        if response == 'ERR_NICKNAMEINUSE':
            stdscr.addstr('O nome de usuário já está em uso\n')
            stdscr.refresh()
            stdscr.getch()
        elif response == 'OK':
            stdscr.addstr('Conectado com sucesso\n', curses.A_COLOR)     
            stdscr.refresh()
            stdscr.getch()
            break
        else:
            stdscr.addstr('Erro desconhecido\n')
            stdscr.refresh()
            stdscr.getch()
            exit(1)

    curses.noecho()
    curses.cbreak() 
    stdscr.clear()

    messages_win = curses.newwin(curses.LINES-2, curses.COLS, 0, 0)
    messages_win.scrollok(True)
    messages_win.bkgd(' ', curses.color_pair(1))
    messages_win.refresh()

    input_win = curses.newwin(1, curses.COLS, curses.LINES-1, 0)
    input_win.bkgd(' ', curses.color_pair(2))
    input_win.refresh()
    input_win.keypad(True)
    input_win.nodelay(True) # Não espera o usuário digitar algo
    curses.curs_set(1)

    messages_queue = Queue() # Fila de mensagens

    # Inicia as threads de input e output
    messages_thread = threading.Thread(target=messages_queue_thread, args=(client_socket, messages_queue))
    _output_thread = threading.Thread(target=output_thread, args=(messages_win, messages_queue))

    messages_thread.start() # Recebe mensagens do servidor
    _output_thread.start()  # Mostra mensagens na tela

    exit_client = False # Flag para sair do loop principal
    while not exit_client:
        input_win.clear()
        message = ""
        while True:
            try:
                with cursor_lock:
                    char = input_win.getch()
                    # verifica se o usuário pressionou ENTER
                    if char == curses.KEY_ENTER or char in [10, 13]:
                        if message == "/QUIT":
                            client_socket.close()
                            exit_client = True
                        elif len(message) > 0:
                            client_socket.send(message.encode())
                        break
                    # verifica se o usuário pressionou BACKSPACE
                    elif char == curses.KEY_BACKSPACE or char == curses.KEY_DC  and len(message) > 0:
                        message = message[:-1]
                        input_win.clear()
                        input_win.addstr(message)
                        input_win.refresh()
                    # verifica se o usuário pressionou UP
                    elif char == curses.KEY_UP:
                        messages_win.scroll(-1)
                        messages_win.refresh()
                    # verifica se o usuário pressionou DOWN
                    elif char == curses.KEY_DOWN:
                        messages_win.scroll(1)
                        messages_win.refresh()
                    # se não for nenhum dos casos acima, adiciona o caractere à mensagem
                    else:
                        message += chr(char)
                        input_win.addstr(chr(char))
                        input_win.refresh()
            except:
                pass

    curses.endwin()


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