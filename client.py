# UNIVERSIDADE FEDERAL DO RIO GRANDE DO NORTE
# DEPARTAMENTO DE ENGENHARIA DE COMPUTACAO E AUTOMACAO
# REDES DE COMPUTADORES (DCA3605)
# AUTORES: MARCOS AURÉLIO TAVARES FILHO E ANA BEATRIZ MAIA MORAIS
# INSPIRADO NO MATERIAL DE CARLOS VIEGAS
#
# --- INICIO DA LOGICA DE CODIGO ---

# Importacao das bibliotecas
from socket import *    # socket
import sys              # sys (para argumentos na linha de comando)
import threading
import time

def ler_mensagem(sockclient):
    while True:
        try:
            data = sockclient.recv(1024).decode('utf-8')
            # Verifica se o servidor fechou a conexão
            if not data:
                print("\nO servidor encerrou a conexão")
                # Fecha o socket localmente para forçar a saída da thread principal
                sockclient.close()
                break
            print(f"\n{data}")
        except Exception:
                break

def envia_mensagem(sockclient):
    while True:
        try:
            mensagem = input("")
            mensagem +="\r\n"

            if sockclient.fileno() == -1:
                break

            sockclient.send(mensagem.encode("utf-8"))

        except Exception:
            sockclient.close()
            break

# Definicao das variaveis
serverName = '10.13.123.0'    # IP do servidor 
serverPort = 54321          # porta do servidor 

# Criacao do socket TCP (SOCK_STREAM = TCP)
clientSocket = socket(AF_INET, SOCK_STREAM)  
# Permite reusar a porta caso fique "presa" por algum processo que nao foi encerrado corretamente
clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

try:
    # Conecta ao servidor
    clientSocket.connect((serverName, serverPort))
    ler = threading.Thread(target=ler_mensagem, args=(clientSocket,))
    ler.daemon = True
    ler.start()

    envia_mensagem(clientSocket)

except KeyboardInterrupt:
    print("\nCliente encerrado pelo usuario (Ctrl+C).")
except ConnectionRefusedError:
    print(f"Nao foi possivel conectar ao servidor em {serverName}:{serverPort}.")
except Exception as e:
    print(f"Erro durante a comunicacao: {e}")
finally:
    clientSocket.close()

# --- FIM DA LOGICA DE CODIGO ---