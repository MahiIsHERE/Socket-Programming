import socket
import threading


# Dictionary to store clients and their usernames
clients = {}


# Function to handle client connections
def handle_client(client_socket, username):

    said_hello = False

    while True:

        try:
            # Receive initial message to determine its length
            header = client_socket.recv(2048).decode("utf-8")
            if not header:
                continue

            # Handle 'BYE' message
            if header.upper() == "BYE":
                broadcast(f"{username} has left the chat.")
                print(f"{username} has left the chat.")
                break

            # Ensure the user says 'hello' first
            if not said_hello:
                # client_socket.send(b"Say 'hello' to start!")
                if header.lower() == "hello":
                    said_hello = True
                    broadcast(f"\033[94m{username} has joined the chat.\033[0m\n")
                    client_socket.send(b"You can now send public or private messages.\n")
                else:
                    client_socket.send(b"You must start by saying 'hello'!\n")
                continue

            # Parse the message
            if header.startswith("Public message, length="):
                content = handle_public_message(header, username)
                if content:
                    broadcast(content)
                else:
                    client_socket.send(b"Your message is not correct. Please use the format: Public message, length=<msg_length_in_Byte>: <message>.\n")
            elif header.startswith("Private message, "):
                success = handle_private_message(header, username)
                if not success:
                    client_socket.send(b"Your message is not correct. Please use the format: Private message, <receiver_username>, <message_content>.\n")
            elif header == "attends":
                # Send the list of connected users
                user_list = "Connected users: " + ", ".join(clients.values())
                client_socket.send(user_list.encode("utf-8"))
            else:
                client_socket.send(b"Your message is not correct. Please use the correct format for public or private messages.\n")

        except Exception as e:
            broadcast(f"{username} has left the chat")
            break

    try:
        client_socket.send("Connection closed by the server.".encode("utf-8"))

    except Exception as e:
        print("--- connection closed ---")

    finally:
        client_socket.close()
        del clients[client_socket]


# Function to handle public messages
def handle_public_message(header, sender_username):
    try:
        # Public message, length=2: 
        parts = header.split(": ") # "Private message, length=2: hi
        message = parts[1]
        length_part = parts[0].split("=")  
        content_length = int(length_part[1])
        if len(message) == content_length:
            print(f"Public message, length={content_length}: {message}")
            return f"\033[94m\n+ {sender_username}: {message}\033[0m"
        else:
            return None
    except:
        return None


# Function to handle private messages
def handle_private_message(header, sender_username):
    try:
        parts = header.split(", ", 2) # Private message, user, hi
        if len(parts) != 3:
            return False
        # 
        receiver_username = parts[1].strip()
        message = parts[2].strip()
        content_length = len(message)

        if receiver_username in clients.values():
            formatted_msg = f"Private message, {receiver_username}, length={content_length}: {message}"
            print(f"{sender_username} -> {receiver_username}: {message}")
            send_private_message(f"\033[92m\n- {sender_username}: {message}\033[0m", receiver_username)
            return True
        else:
            return False
    except Exception as e:
        print(f"Error handling private message: {e}")
        return False


# Function to broadcast messages to all clients
def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode("utf-8"))
        except:
            client.close()


# Function to send private message to a specific user
def send_private_message(message, receiver_username):
    for client, username in clients.items():
        if username == receiver_username:
            try:
                client.send(message.encode("utf-8"))
                break
            except:
                client.close()
                

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# Bind the socket to a specific IP and port
IP = socket.gethostbyname(socket.gethostname())
server_socket.bind((IP, 15000))


# Listen for incoming connections
server_socket.listen(5)
print("Server is listening for connections...")


while True:
    # Accept a new connection
    client_socket, address = server_socket.accept()

    # Ask for username
    client_socket.send(b"\nEnter your username: ")
    username = client_socket.recv(2048).decode("utf-8").strip()

    clients[client_socket] = username

    # Start a new thread to handle the connection
    client_thread = threading.Thread(target=handle_client, args=(client_socket, username))
  
    greeting = f"\n+ Hi {username}! Welcome to the chat room.\n"
    client_socket.send(greeting.encode("utf-8"))

    # Start sending messages to the server
    client_socket.send(b"\n+ Say 'hello' to start!\n")
    
    client_thread.start()