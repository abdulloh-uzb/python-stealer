import socket

HOST = "0.0.0.0" 
PORT = 1337  

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Server listening on {HOST}:{PORT}")

conn, addr = server_socket.accept()
print(f"Connection from {addr}")


def receive(filename, conn):
        with open(filename, 'wb') as f:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                f.write(data)
        print(f"{filename} transfer complete.")


receive("test.zip",conn)  # Receive the first file

print("File transfer complete.")
conn.close()
server_socket.close()
