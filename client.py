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

estacao = None
ciclos = 0
dados = {"temp": None, "hum": None, "press": None}

def trata_mensagem(mensagem):
    global ciclos
    # Remover os espacos vazios das mensagens
    mensagem = mensagem.strip() 
    param = mensagem.split(';')

    if "BEGIN" in mensagem:
        # Extraindo o ciclos com a resposta do servidor                
        ciclos = param[2]


        # Fazendo com uma variavel auxiliar
        # ciclos += 1

    if "END" in mensagem:
        print("-"*36)
        print(f"ESTACAO {estacao} - CENTRO")
        print("-"*36)

        print(f"Ciclo: {ciclos}\n")                
        print(f"Temperatura  : {dados['temp']} C")
        print(f"Umidade      : {dados['hum']} %")
        print(f"Pressao      : {dados['press']} hPA")
        print("-"*36)
        print("Aguardando novas medições...\n")


    if "TEMP" in mensagem:
        dados["temp"] = float(param[1])
        
    if "HUM" in mensagem:
        dados["hum"] = float(param[1])
    
    if "PRESS" in mensagem:
        dados["press"] = float(param[1])    


def ler_mensagem(sockclient):
    mensagem = ""
    while True:
        try:
            data = sockclient.recv(1024).decode('utf-8')
            # Verifica se o servidor fechou a conexão
            if not data:
                print("\nO servidor encerrou a conexão")
                # Fecha o socket localmente para forçar a saída da thread principal
                sockclient.close()
                break

            # Acumula as informacoes para utilizar nos registros
            for i in data:
                mensagem += i

            divisao = mensagem.split('\r\n')
            # Supondo que as linhas vem juntas
            if len(divisao) > 1:
                for linha in divisao:
                    # Existem dois ; por linha
                    if linha.count(";")==2: 
                        trata_mensagem(linha)

                        if linha == divisao[-1]:
                            mensagem = ""
                    
                    # Linha incompleta
                    else: 
                        mensagem = linha
        except Exception:
                break

def envia_mensagem(sockclient):
    global estacao
    try:
        # Utilizado na etapa 1, 2 e 3
        # listar = "LIST\r\n".encode("utf-8")
        # sockclient.sendall(listar)
        # time.sleep(0.5)

        print("Estacoes disponiveis: 001, 002, 003")

        while estacao not in ["001", "002", "003"]:
            estacao = input("Selecione uma estacao: ")

        print(f"\nIniciando monitoramento...")

        sockclient.send(f"STREAM;{estacao}\r\n".encode("utf-8"))

        while True:
            mensagem = input("")

            if sockclient.fileno() == -1:
                break

            mensagem += "\r\n"
            sockclient.send(mensagem.encode("utf-8"))

    except Exception:
        sockclient.close()

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
    print(f"Conectado ao servidor TCP.\n")

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