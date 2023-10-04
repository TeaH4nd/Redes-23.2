import socket
import threading

# define a localizacao do servidor
HOST = 'localhost' # vazio indica que podera receber requisicoes a partir de qq interface de rede da maquina
PORT = 10001 # porta de acesso

class Servidor:
    def __init__(self):
        '''Cria um socket de servidor e o coloca em modo de espera por conexoes.''' 

        #armazena historico de conexoes 
        self.conexoes = {}
        # cria o socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Internet( IPv4 + TCP)

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # vincula a localizacao do servidor
        self.sock.bind((HOST, PORT))

        # coloca-se em modo de espera por conexoes
        self.sock.listen(5)


    def aceitaConexao(self):
        """Aceita o pedido de conexao de um cliente
        Saida: o novo socket da conexao e o endereco do cliente"""

        # estabelece conexao com o proximo cliente
        clisock, endr = self.sock.accept()

        # registra a nova conexao
        self.conexoes[clisock] = endr

        return clisock, endr

    def atendeRequisicoes(self, clisock, endr):
        """Recebe mensagens e as envia de volta para o cliente (ate o cliente finalizar)
        Entrada: socket da conexao e endereco do cliente
        Saida:"""

        try:
            # recebe dados do cliente
            data = clisock.recv(1024).decode()
            if not data:  # dados vazios: cliente encerrou
                print(str(endr) + "-> encerrou")
                clisock.close()  # encerra a conexao com o cliente
                return

            method = data.split()[0]
            filename = data.split()[1]
            print(f"{method} ->{filename}")

            if (method == 'GET'):
                if (filename == '/' or filename == '/index.html'):
                    filename = '/index.html'
                    with open(filename[1:], 'rb') as f:
                        outputData = f.read()
                    response = bytes(f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(outputData)}\r\n\r\n",encoding="utf-8",) + outputData

                    clisock.send(response)  # envia a resposta para o cliente
                    clisock.close()  # encerra a conexao com o cliente
                if (filename == '/logout.html'):
                    with open(filename[1:], 'rb') as f:
                        outputData = f.read()
                    response = bytes(f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(outputData)}\r\n\r\n",encoding="utf-8",) + outputData

                    clisock.send(response)
                if ('css' in filename):
                    with open(filename[1:], 'rb') as f:
                        outputData = f.read()
                    response = bytes(f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(outputData)}\r\n\r\n",encoding="utf-8",) + outputData

                    clisock.send(response)  # envia a resposta para o cliente
                    clisock.close()  # encerra a conexao com o cliente
            
            if (method == 'POST'):
                loginData = data.split('\r\n')[-1]
                loginData = loginData.split('&')
                user = loginData[0].split('=')[1]
                password = loginData[1].split('=')[1]
                print(f"User: {user} Password: {password}")
                if (user == 'admin' and password == 'admin'):
                    with open('login.html', 'rb') as f:
                        outputData = f.read()
                    response = bytes(f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(outputData)}\r\n\r\n",encoding="utf-8",) + outputData

                    clisock.send(response)
                    clisock.close()
                else:
                    with open('404.html', 'rb') as f:
                        outputData = f.read()
                    response = bytes(f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\nContent-Length: {len(outputData)}\r\n\r\n",encoding="utf-8",) + outputData

                    clisock.send(response)
                    clisock.close()
        except IOError:
            response = bytes("HTTP/1.1 400 Bad Request\r\n\r\n",encoding="utf-8",)
            clisock.send(response)
            clisock.close()


    def executa(self):
        """Inicializa e implementa o loop principal (infinito) do servidor"""
        clientes = []  # armazena as threads criadas para fazer join
        print('Esperando conexões...')
        # print('Digite REM[chave] para remover uma chave do dicionario.')
        while True:
            clisock, endr = self.aceitaConexao()
            cliente = threading.Thread(target=self.atendeRequisicoes, args=(clisock, endr))
            cliente.start()
            clientes.append(cliente)  # armazena a referencia da thread para usar com join()

if __name__ == "__main__":
    servidor = Servidor()
    servidor.executa()
