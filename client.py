import socket
import threading
import curses
from queue import Queue
import time

cursor_lock = threading.Lock() # Lock para evitar que o usuário escreva enquanto a mensagem está sendo exibida
stop_output_thread = False # Flag para parar a thread de output
stop_messages_queue_thread = False # Flag para parar a thread de receber mensagens

def handle_response(response: str): # Tratamento de erros
    if response == 'ERR_NICKNAMEINUSE':
        return 'O nome de usuário já está em uso'
    elif response == 'ERR_PARAMS':
        return 'Erro de Parametros'
    elif response == 'ERR_NOSUCHCHANNEL':
        return 'Canal não existe'
    elif response == 'ERR_NOSUCHNICK':
        return 'Nick não existe'
    elif response == 'ERR_NOTONCHANNEL':
        return 'Você não está no canal'
    elif response == 'ERR_NEEDMOREPARAMS':
        return 'Faltam parâmetros'
    elif response == 'ERR_CONNECTIONLOST':
        return 'Conexão perdida'
    return response

# Função para mostrar as mensagens que estão na fila na tela
def output_thread(output_win: curses.window, messages_queue: Queue):
    global cursor_lock, stop_output_thread
    while not stop_output_thread:
        if not messages_queue.empty(): # Se a fila não estiver vazia
            with cursor_lock: # trava o cursor para evitar que o usuário escreva enquanto a mensagem está sendo exibida
                response = handle_response(messages_queue.get()) # Pega a mensagem da fila
                for char in response:
                    if char in ['\r', '\n']:
                        output_win.addch('\n')
                        continue
                    output_win.addch(char)
                output_win.addch('\n')
                output_win.refresh()
            time.sleep(.1) # sleep para permitir que outra thread "pegue" o cursor
                
# Função para receber as mensagens do servidor e colocar na fila
def messages_queue_thread(client_socket: socket.socket, messages_queue: Queue):
    global stop_messages_queue_thread
    try:
        while client_socket.fileno() != -1 and not stop_messages_queue_thread: # Enquanto o socket estiver aberto
            response = client_socket.recv(2048).decode('utf-8') # Recebe a mensagem do servidor
            if not response: # Se a mensagem estiver vazia, encerra a conexão
                messages_queue.put('Conexão encerrada pelo servidor')
                break
            messages_queue.put(response) # Adiciona a mensagem na fila
    except:
        messages_queue.put('ERR_CONNECTIONLOST')

def connection_screen(stdscr: curses.window, address: tuple):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Cria o socket do cliente

    stdscr.clear() # Limpa a tela
    stdscr.addstr("CLIENTE IRC - Trabalho TR2\n")
    stdscr.addstr(f"Conectando ao servidor {address[0]}:{address[1]}") # Mostra a mensagem de conexão
    stdscr.refresh() # Atualiza a tela
    try:
        client_socket.connect(address) # Tenta conectar ao servidor
    except:
        stdscr.move(1, 0) # Move o cursor para a linha 1, coluna 0
        stdscr.clrtoeol() # Limpa a linha
        stdscr.addstr(1, 0, "Erro ao conectar") # Mostra a mensagem de erro
        stdscr.refresh()
        stdscr.getch() # Aguarda o usuário apertar uma tecla
        exit(1) # Sai do programa
    
    return client_socket

def login_screen(stdscr: curses.window, client_socket: socket.socket):
    curses.echo() # Habilita o echo do curses -> permite que o usuário veja o que está digitando

    try:
        while True:
            stdscr.clear() # Limpa a tela
            stdscr.addstr("Digite seu nome de usuário:") # Mostra a mensagem de login
            stdscr.refresh()
            nickname = stdscr.getstr(1, 0, 144).decode() # Recebe o nome de usuário do usuário 
            if nickname == '' or nickname == '\n': # Se o nome de usuário estiver vazio
                continue
            client_socket.send(nickname.encode('utf-8')) # Envia o nome de usuário para o servidor
        
            response = client_socket.recv(1024).decode('utf-8') # Recebe a resposta do servidor
            if response == 'ERR_NICKNAMEINUSE': # Se o nome de usuário já estiver em uso
                stdscr.addstr('O nome de usuário já está em uso\n', curses.A_COLOR)
                stdscr.refresh()
                stdscr.getch()
            elif response == 'OK': # Se o nome de usuário estiver disponível
                stdscr.addstr('Conectado com sucesso\n', curses.A_COLOR)     
                stdscr.refresh()
                stdscr.getch()
                break
            else: # Se o servidor retornar um erro desconhecido
                stdscr.addstr('Erro desconhecido\n', curses.A_COLOR)
                stdscr.refresh()
                stdscr.getch()
                exit(1)
    except:
        stdscr.addstr('Erro desconhecido\n', curses.A_COLOR)
        stdscr.refresh()
        stdscr.getch()
        exit(1)

def setup_windows(stdscr: curses.window):
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE) # cores para a janela de output
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_CYAN) # cores para a janela de input

    curses.noecho() # Desabilita o echo do curses -> não permite que o usuário veja o que está digitando
    curses.cbreak() # Desabilita o buffer do teclado -> cada tecla é lida imediatamente
    curses.curs_set(1) # Mostra o cursor
    stdscr.clear() # Limpa a tela

    messages_win = curses.newwin(curses.LINES-2, curses.COLS, 0, 0) # Cria a janela de output
    messages_win.bkgd(' ', curses.color_pair(1)) # Define a cor de fundo da janela
    messages_win.refresh()

    input_win = curses.newwin(1, curses.COLS, curses.LINES-1, 0) # Cria a janela de input
    input_win.bkgd(' ', curses.color_pair(2)) # Define a cor de fundo da janela
    input_win.refresh() # Atualiza a tela
    input_win.keypad(True) # Habilita o uso de teclas especiais (setas, F1, F2, etc)
    input_win.nodelay(True) # Não espera o usuário digitar algo para continuar a execução

    return messages_win, input_win

# Função que processa a mensagem digitada pelo usuário
# Retorna True enquanto o usuário não digitar /QUIT
# Retorna False quando o usuário digitar /QUIT
def input_message(input_win: curses.window, client_socket: socket.socket):
    global cursor_lock
    input_win.clear() # Limpa a janela de input
    message = '' # Inicializa a mensagem como uma string vazia
    while True:
        try:
            with cursor_lock: # Tenta obter o lock do cursor
                char = input_win.getch() # Pega o caractere digitado pelo usuário (se houver, senão lança uma exceção)
                # verifica se o usuário pressionou ENTER
                if char == curses.KEY_ENTER or char in [10, 13]:
                    if client_socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR) == 0: # se a conexão com o servidor estiver ativa
                        client_socket.send(message.encode('utf-8')) # envia a mensagem para o servidor
                    if message == "/QUIT":
                        return False # retorna False para indicar que o usuário digitou /QUIT
                    return True # retorna True para indicar que o usuário não digitou /QUIT
                # verifica se o usuário pressionou BACKSPACE ou DELETE
                elif char == curses.KEY_BACKSPACE or char == curses.KEY_DC  and len(message) > 0:
                    message = message[:-1] # remove o último caractere da mensagem
                    input_win.clear() # limpa a janela de input
                    input_win.addstr(message) # adiciona a mensagem sem o último caractere
                    input_win.refresh() # atualiza a janela de input
                elif char > 0 and char < 256:
                    message += chr(char) # adiciona o caractere à mensagem
                    input_win.addstr(chr(char)) # adiciona o caractere à janela de input
                    input_win.refresh() # atualiza a janela de input
        except:
            # se não conseguir obter o lock do cursor, passa para a próxima iteração
            # ou se o usuario não tiver digitado nada, passa para a próxima iteração
            pass
    

def chat_screen(input_win: curses.window, client_socket: socket.socket):
    global stop_output_thread, stop_messages_queue_thread
    while True:
        # se o usuário digitar /QUIT, sai do loop
        if not input_message(input_win, client_socket):
            stop_messages_queue_thread = True
            stop_output_thread = True 
            client_socket.close() # fecha a conexão com o servidor
            break

# Função que inicia e executa o cliente
def start(stdscr: curses.window):
    client_socket = connection_screen(stdscr, ('192.168.96.5', 6667)) # Conecta ao servidor

    login_screen(stdscr, client_socket) # Tela de login

    messages_win, input_win = setup_windows(stdscr) # Inicializa as janelas

    messages_queue = Queue() # Fila de mensagens recebidas do servidor

    # Inicia as threads de input e output
    # As threads são iniciadas antes do loop principal para que elas possam ser executadas em paralelo
    # thread de mensagens -> recebe mensagens do servidor
    messages_thread = threading.Thread(target=messages_queue_thread, args=(client_socket, messages_queue))
    # thread de output -> mostra mensagens na tela quando o cursor estiver livre
    _output_thread = threading.Thread(target=output_thread, args=(messages_win, messages_queue))

    messages_thread.start() # Recebe mensagens do servidor
    _output_thread.start()  # Mostra mensagens na tela

    chat_screen(input_win, client_socket) # Loop principal do chat

    messages_thread.join() # aguarda a thread de mensagens terminar
    _output_thread.join() # aguarda a thread de output terminar

    curses.endwin() # finaliza o modo curses


if __name__ == '__main__':
    curses.wrapper(start)