import socket
import threading


# Function to receive messages from the server
def receive_messages():
    while True:
        try:
            # Receive message
            message = client_socket.recv(2048).decode("utf-8")
            if message == "Connection closed by the server.":
                print(message)
                break
            print(message)
        except:
            print("Connection closed.")
            break


# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


IP = socket.gethostbyname(socket.gethostname()) # system IP address
# Connect to the server
client_socket.connect((IP, 15000))


# Receive the initial message asking for username
initial_message = client_socket.recv(2048).decode("utf-8")
print(initial_message, end=' ')
username = input()
client_socket.send(username.encode("utf-8"))


# Start a new thread to receive messages from the server
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()


while True:
    message = input(f"\n\033[91m>\033[0m ")
    # Send message to the server
    client_socket.send(message.encode("utf-8"))
    if message.upper() == "BYE":
        print("You have left the chat room.")
        break


client_socket.close()