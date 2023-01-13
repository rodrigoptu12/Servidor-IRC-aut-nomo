import socket
import threading
import curses
from queue import Queue
import time

cursor_lock = threading.Lock() # Lock para evitar que o usuário escreva enquanto a mensagem está sendo exibida
stop_threads = False # Variável para parar as threads

# Tratamento de erros
erros = ['ERR_NICKNAMEINUSE', 'ERR_PARAMS', 'ERR_NOSUCHCHANNEL', 'ERR_NOSUCHNICK', 'ERR_NOTONCHANNEL', 'ERR_NEEDMOREPARAMS']
def handle_response(response: str): # Tratamento de erros
    if response in erros:
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
    return response # Se não for um erro, retorna a mensagem normalmente

# Função customizada para receber input do usuário pelo curses
def my_raw_input(stdscr: curses.window, r, c, prompt_string):
    stdscr.addstr(r, c, prompt_string)
    stdscr.refresh()
    input = stdscr.getstr(r + 1, c, 144).decode()
    return input  #       ^^^^  reading input at next line

# Função para mostrar as mensagens que estão na fila na tela
def output_thread(output_win: curses.window, messages_queue: Queue):
    global stop_threads
    while True:
        if stop_threads:
            break
        while not messages_queue.empty(): # Se a fila não estiver vazia
            with cursor_lock: # trava o cursor para evitar que o usuário escreva enquanto a mensagem está sendo exibida
                response = handle_response(messages_queue.get()) # Pega a mensagem da fila
                output_win.addstr(f"{response}\n") # Exibe a mensagem na tela
                output_win.refresh() # Atualiza a tela
            time.sleep(.1) # sleep para permitir que outra thread "pegue" o cursor
                
# Função para receber as mensagens do servidor e colocar na fila
def messages_queue_thread(client_socket: socket.socket, messages_queue: Queue):
    global stop_threads
    while True:
        if client_socket.fileno() == -1 or stop_threads: # Se o socket estiver fechado ou stop_threads
            break # sai do loop
        response = client_socket.recv(1024).decode() # Recebe a mensagem do servidor
        messages_queue.put(response) # Adiciona a mensagem na fila
        
# Função que inicia e executa o cliente
def start(stdscr: curses.window):
    global stop_threads
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Cria o socket do cliente

    server_address = ('localhost', 3030) # Endereço do servidor
    stdscr.addstr("CLIENTE IRC VERSÃO 1.0 ALPHA")
    stdscr.addstr(f"Conectando ao servidor {server_address[0]}:{server_address[1]}") # Mostra a mensagem de conexão
    err = client_socket.connect_ex(server_address) # Tenta conectar ao servidor
    if err == 115: # Se o erro for 115, o servidor não está online
        stdscr.addstr(1, 0, "Conectando...")
        stdscr.refresh() # Atualiza a tela
        while err == 115: # Enquanto o erro for 115, tenta conectar novamente
            err = client_socket.connect_ex(server_address) # Tenta conectar ao servidor
 
    if err == 0: # Se o erro for 0, a conexão foi bem sucedida
        stdscr.addstr(1, 0, "Conectado com sucesso")
        stdscr.refresh()
        stdscr.getch() # Aguarda o usuário apertar uma tecla
    else:
        stdscr.addstr(1, 0, "Erro ao conectar") # Mostra a mensagem de erro
        stdscr.refresh()
        stdscr.getch() # Aguarda o usuário apertar uma tecla
        exit(1) # Sai do programa

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE) # cores para a janela de output
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_CYAN) # cores para a janela de input
    curses.echo() # Habilita o echo do curses -> permite que o usuário veja o que está digitando

    while True:
        stdscr.clear() # Limpa a tela
        nickname = my_raw_input(stdscr, 0, 0, 'Digite seu nome de usuário:') # Pega o nome de usuário do usuário
        if nickname == '' or nickname == '\n': # Se o nome de usuário estiver vazio
            continue
        client_socket.send(nickname.encode('utf-8')) # Envia o nome de usuário para o servidor
    
        response = client_socket.recv(1024).decode('utf-8') # Recebe a resposta do servidor
        if response == 'ERR_NICKNAMEINUSE': # Se o nome de usuário já estiver em uso
            stdscr.addstr('O nome de usuário já está em uso\n')
            stdscr.refresh()
            stdscr.getch()
        elif response == 'OK': # Se o nome de usuário estiver disponível
            stdscr.addstr('Conectado com sucesso\n', curses.A_COLOR)     
            stdscr.refresh()
            stdscr.getch()
            break
        else: # Se o servidor retornar um erro desconhecido
            stdscr.addstr('Erro desconhecido\n')
            stdscr.refresh()
            stdscr.getch()
            exit(1)

    curses.noecho() # Desabilita o echo do curses -> não permite que o usuário veja o que está digitando
    curses.cbreak() # Desabilita o buffer do teclado -> cada tecla é lida imediatamente
    stdscr.clear() # Limpa a tela

    messages_win = curses.newwin(curses.LINES-2, curses.COLS, 0, 0) # Cria a janela de output
    messages_win.scrollok(True) # Habilita o scroll da janela
    messages_win.bkgd(' ', curses.color_pair(1)) # Define a cor de fundo da janela
    messages_win.refresh()

    input_win = curses.newwin(1, curses.COLS, curses.LINES-1, 0) # Cria a janela de input
    input_win.bkgd(' ', curses.color_pair(2)) # Define a cor de fundo da janela
    input_win.refresh() # Atualiza a tela
    input_win.keypad(True) # Habilita o uso de teclas especiais (setas, F1, F2, etc)
    input_win.nodelay(True) # Não espera o usuário digitar algo para continuar a execução
    curses.curs_set(1) # Mostra o cursor

    messages_queue = Queue() # Fila de mensagens recebidas do servidor

    # Inicia as threads de input e output
    # As threads são iniciadas antes do loop principal para que elas possam ser executadas em paralelo
    # thread de mensagens -> recebe mensagens do servidor
    messages_thread = threading.Thread(target=messages_queue_thread, args=(client_socket, messages_queue))
    # thread de output -> mostra mensagens na tela quando o cursor estiver livre
    _output_thread = threading.Thread(target=output_thread, args=(messages_win, messages_queue))

    messages_thread.start() # Recebe mensagens do servidor
    _output_thread.start()  # Mostra mensagens na tela

    exit_client = False # Flag para sair do loop principal
    while not exit_client:
        input_win.clear()
        message = "" # Mensagem a ser enviada
        while True:
            try:
                with cursor_lock: # Tenta obter o lock do cursor
                    char = input_win.getch() # Pega o caractere digitado pelo usuário (se houver, senão lança uma exceção)
                    # verifica se o usuário pressionou ENTER
                    if char == curses.KEY_ENTER or char in [10, 13]:
                        client_socket.send(message.encode()) # envia a mensagem para o servidor
                        if message == "/QUIT":
                            # fechar as threads
                            stop_threads = True
                            client_socket.close() # fecha a conexão com o servidor
                            exit_client = True # sai do loop principal
                        break # sai do loop de input
                    # verifica se o usuário pressionou BACKSPACE ou DELETE
                    elif char == curses.KEY_BACKSPACE or char == curses.KEY_DC  and len(message) > 0:
                        message = message[:-1] # remove o último caractere da mensagem
                        input_win.clear() # limpa a janela de input
                        input_win.addstr(message) # adiciona a mensagem sem o último caractere
                        input_win.refresh() # atualiza a janela de input
                    # verifica se o usuário pressionou UP
                    elif char == curses.KEY_UP:
                        messages_win.scroll(-1) # rola a janela de mensagens para cima
                        messages_win.refresh() # atualiza a janela de mensagens
                    # verifica se o usuário pressionou DOWN
                    elif char == curses.KEY_DOWN:
                        messages_win.scroll(1) # rola a janela de mensagens para baixo
                        messages_win.refresh() # atualiza a janela de mensagens
                    # se não for nenhum dos casos acima, adiciona o caractere à mensagem
                    elif char > 0 and char < 256:
                        message += chr(char) # adiciona o caractere à mensagem
                        input_win.addstr(chr(char)) # adiciona o caractere à janela de input
                        input_win.refresh() # atualiza a janela de input
            except:
                pass

    messages_thread.join() # aguarda a thread de mensagens terminar
    _output_thread.join() # aguarda a thread de output terminar
    curses.endwin() # finaliza o modo curses


if __name__ == '__main__':
    curses.wrapper(start)