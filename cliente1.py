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
import re

def ciclo(dados_ciclo):

    estacao = re.search(r'(ESTACAO|EST|ID)[:=]?\s*(\w+)', dados_ciclo, re.IGNORECASE)
    ciclo = re.search(r'(CICLO|SEQ)[:=]?\s*(\d+)', dados_ciclo, re.IGNORECASE)
    temp = re.search(r'(TEMP|TEMPERATURA)[:=]?\s*([\d\.]+)', dados_ciclo, re.IGNORECASE)
    umid = re.search(r'(UMID|UMIDADE)[:=]?\s*([\d\.]+)', dados_ciclo, re.IGNORECASE)
    press = re.search(r'(PRESS|PRESSAO)[:=]?\s*([\d\.]+)', dados_ciclo, re.IGNORECASE)

    id_est = estacao.group(2) if estacao else "N/A"
    num_ciclo = ciclo.group(2) if ciclo else "N/A"
    v_temp = temp.group(2) if temp else "N/A"
    v_umid = umid.group(2) if umid else "N/A"
    v_press = press.group(2) if press else "N/A"

    print(f" ESTACAO {id_est}")
    print("-----------------------------------")
    print(f" Ciclo: {num_ciclo}")
    print()
    print(f" Temperatura : {v_temp} C")
    print(f" Umidade     : {v_umid} %")
    print(f" Pressao     : {v_press} hPa")
    print()
    print("-----------------------------------")
    print(" Aguardando novas medicoes...")

def ler_mensagem(sockclient):
    buffer = ""
    bloco_ciclo = ""

    while True:
        try:
            data = sockclient.recv(1024).decode('utf-8', errors='ignore')
            # Verifica se o servidor fechou a conexão
            if not data:
                print("\nO servidor encerrou a conexao")
                # Fecha o socket localmente para forçar a saída da thread principal
                sockclient.close()
                break
            
            buffer += data

            while "\n" in buffer:
                linha, buffer = buffer.split("\n", 1)
                linha = linha.strip("\r")
                
                if "ESTACOES" in linha.upper() or "SELECIONADA" in linha.upper():
                    print(f"\n[SERVIDOR]: {linha}")
                    continue

                bloco_ciclo += linha + "\n"

                if "PRESSAO" in linha.upper() or "PRESS" in linha.upper():
                    ciclo(bloco_ciclo)
                    bloco_ciclo = "" 

        except Exception:
            break

def envia_mensagem(sockclient):
   
    try:
        sockclient.send("LIST\r\n".encode("utf-8"))
        time.sleep(0.5)

        estacao = input("\nDigite o codigo da estacao desejada (ex: 001, 002, 003): ").strip()
        sockclient.send(f"{estacao}\r\n".encode("utf-8"))
        print(f"Iniciando monitoramento...\n")

        while True:
            mensagem = input("")

            if sockclient.fileno() == -1:
                break

            mensagem += "\r\n"
            sockclient.send(mensagem.encode("utf-8"))

    except Exception:
        sockclient.close()

# Definicao das variaveis
serverName = '127.0.0.1'   #IP servidor 
serverPort = 54321         #Porta do servidor 

# Criacao do socket TCP (SOCK_STREAM = TCP)
clientSocket = socket(AF_INET, SOCK_STREAM)  
# Permite reusar a porta caso fique "presa" por algum processo que nao foi encerrado corretamente
clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

try:
    print(f"Conectando ao servidor em {serverName}:{serverPort}...")
    
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
