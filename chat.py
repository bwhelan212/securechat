import socket
import threading
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
# fff
key = RSA.generate(2048)

public_key = key.publickey().export_key()
private_key_bytes = key.export_key()
partner_pubk = None

private_key = RSA.import_key(private_key_bytes)
cipher_rsa_decrypt = PKCS1_OAEP.new(private_key, hashAlgo=None, mgfunc=None, randfunc=None)
partner_cipher_rsa_encrypt= None

while True:
    host_or_client = input("Would you like to host (H/h) the chat or connect as the client (C/c)? ")
    low = host_or_client.lower()
    if low == 'h' or low == 'c':
        break
    else:
        print("Error, please enter valid response")

        
if host_or_client == "h":
    
    # AF_INET -> internet socket ; SOCK_STREAM -> tcp protocol
    # in python, have to send messages in bytes of string (msg.encode())
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind socket to host ip and a port to listen to on host/server machine
    ip = input("Please enter the host IP address: ")
    port = input("Please enter the port that the host will listen on: ")
    server.bind((ip, int(port)))
    server.listen()
    # communication to client
    client, address = server.accept()
    
    client.send(public_key)
    #partner_pubk = PKCS1_OAEP.new(client.recv(4096))
  
    partner_pubk_bytes = client.recv(4096)
    partner_pubk = RSA.import_key(partner_pubk_bytes)
    partner_cipher_rsa_encrypt = PKCS1_OAEP.new(partner_pubk, hashAlgo=None, mgfunc=None, randfunc=None)

elif host_or_client == "c":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # use host/server ip address + port that they are listening on to connect to server
    ip = input("Please enter the IP address of the server: ")
    port = input("Please enter the port to connect to: ")
    client.connect((ip,int(port)))
    partner_pubk_bytes = client.recv(4096)
    partner_pubk = RSA.import_key(partner_pubk_bytes)
    partner_cipher_rsa_encrypt= PKCS1_OAEP.new(partner_pubk, hashAlgo=None, mgfunc=None, randfunc=None)
    client.send(public_key)
else:
    exit()
    

def send_msg(c):
    while True:
        message = input("")
        ciphertext = partner_cipher_rsa_encrypt.encrypt(message.encode())
        c.send(ciphertext)
        #c.send(message.encode())
        # print("You: " + message)
        
def recieve_msg(c):
    while True:
        # revieve client data, will recieve 4096 bits max
        client_ciphertext = c.recv(4096)
        client_msg = cipher_rsa_decrypt.decrypt(client_ciphertext)
        print("Partner: " + str(client_msg.decode()))
        #print("Partner: " + str(client_ciphertext.decode()))

threading.Thread(target=send_msg, args = (client,)).start()
threading.Thread(target=recieve_msg, args = (client,)).start()
