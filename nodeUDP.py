import socket
import threading
from time import sleep
import os

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
SERVER_HOST = ('localhost', 5555)
NODE_1 = ('localhost', 7777)
NODE_2 = ('localhost', 6666)

addrslist = [SERVER_HOST, NODE_1, NODE_2]


def main():

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    serverThread = threading.Thread(target=startServer, args=[server])
    menuThread = threading.Thread(target=menu, args=[client])

    serverThread.start()

    menuThread.start()


# Menu

def menu(client):

    while True:

        sleep(3)
        print("\n" * os.get_terminal_size().lines)

        print('Informe a opção desejada\n')
        print('1 - Adicionar arquivo')
        print('2 - Excluir arquivo')
        print('3 - Listar arquivos')
        print('4 - Sair\n')

        option = (input('Opção> '))

        try:
            if(int(option) < 1 or int(option) > 4):
                print('\n\nOpção inválida\n\n')

            if(int(option) == 1):
                sendFile(client)

            if(int(option) == 2):
                sendDeleteFile(client)

            if(int(option) == 3):
                client.sendto(str(option).encode('utf-8'), SERVER_HOST)

            if(int(option) == 4):
                print('\n\nEncerrando sistema\n\n')
                client.sendto(str(option).encode('utf-8'), SERVER_HOST)
                break

        except Exception as e:
            print(e)


# Client functions

def sendMsgToAllServer(client, msg):
    for addr in addrslist:
        client.sendto(str(msg).encode('utf-8'), addr)


def sendFile(client):
    filepath = str(input('\nCaminho do arquivo> '))

    if(os.path.isfile(filepath)):

        sendMsgToAllServer(client, 1)

        filesize = os.path.getsize(filepath)
        filename = filepath.split(os.sep)
        msg = f"{filename[-1]}{SEPARATOR}{filesize}"

        try:
            for addr in addrslist:
                sendFileToAllServers(
                    client, addr, msg, filepath)

            print('\nArquivo enviado\n')
        except:
            print('Falha ao enviar')
    else:
        print('\nArquivo não encontrado')


def sendFileToAllServers(client, addr, msg, filepath):
    client.sendto(msg.encode('utf-8'), addr)

    try:
        with open(filepath, 'rb') as file:
            while True:
                bytes_read = file.read(BUFFER_SIZE)

                if not bytes_read:
                    break
                client.sendto(bytes_read, addr)

            file.close()

    except Exception as e:
        print("Falha ao enviar arquivo", e)


def sendDeleteFile(client):
    filename = str(input('\nNome do arquivo> '))

    if(os.path.isfile(f'./arquivos/{filename}')):
        sendMsgToAllServer(client, 2)
        sendMsgToAllServer(client, filename)

        print("\nArquivo removido\n")
    else:
        print('\nArquivo não encontrado')


# Server functions

def startServer(server):
    try:
        server.bind(SERVER_HOST)
        print('Servidor online')
        print(SERVER_HOST)
    except Exception as e:
        return print('Não foi possivel iniciar o servidor', e)

    receiveCommand(server)


def listFiles():
    print('\nArquivos desta pasta\n')
    for _, _, files in os.walk('./arquivos/'):
        for file in files:
            print(file)
    print('\n\n')


def receiveCommand(server):
    while True:

        try:
            msg = server.recv(BUFFER_SIZE).decode('utf-8')
            if(msg == '1'):
                receiveFile(server)

            if(msg == '2'):
                receiveDeleteFile(server)

            if(msg == '3'):
                listFiles()

            if(msg == '4'):
                server.close()
                break

        except Exception as e:
            print("Falha ao receber comando", e)
            break


def receiveDeleteFile(server):
    filename = server.recv(BUFFER_SIZE).decode('utf-8')

    if(os.path.isfile(f'./arquivos/{filename}')):
        os.remove(f'./arquivos/{filename}')
    else:
        print("Erro: arquivo %s não encontrado\n" % filename)


def receiveFile(server):
    received = server.recv(BUFFER_SIZE).decode('utf-8')
    filename, filesize = received.split(SEPARATOR)

    try:
        with open(f'./arquivos/{filename}', 'wb') as file:
            while True:
                bytes_read = server.recv(BUFFER_SIZE)

                file.write(bytes_read)

                if (len(bytes_read) == int(filesize)):
                    break
            file.close()
    except Exception as e:
        print("Falha ao receber arquivo", e)


main()