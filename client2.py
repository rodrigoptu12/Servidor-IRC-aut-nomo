import socket

# client

def receive(client_socket):
  while True:
    try:
      # Recebe a mensagem
      message = client_socket.recv(1024).decode("utf-8")
      print(message)
    except:
      pass

def main():
  print("Iniciando o cliente...")
  address = ('26.40.92.178', 4400)
  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client_socket.connect(address)

  client_socket.send("fer2".encode("utf-8"))

  # Cria uma thread para receber mensagens do servidor
  receive(client_socket)
  client_socket.close()

if __name__ == "__main__":
  main()