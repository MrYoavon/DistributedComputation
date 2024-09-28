import os
import socket
import hashlib
import threading
import logging
import json
import sys
import argparse

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Log to console
    ]
)

# MD5 calculation function
def calculate_md5(input_string):
    return hashlib.md5(input_string.encode()).hexdigest().lower()

# Function to send JSON data to the server
def send_json(client_socket, data):
    message = json.dumps(data)
    client_socket.send(message.encode())

# Function to receive JSON data from the server
def recv_json(client_socket):
    data = client_socket.recv(1024).decode()
    return json.loads(data)

# Worker thread function to check a range of numbers
def check_range(start, end, md5_to_find, found_flag, lock):
    for i in range(start, end):
        number_str = str(i).zfill(10)
        hash = calculate_md5(number_str)
        with lock:
            if found_flag[0]:
                return
        if hash == md5_to_find:
            logging.info(f"Found: {number_str}")
            with lock:
                found_flag[0] = True
                found_flag[1] = number_str
            return

def main(ip, port):
    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((ip, port))
    except socket.error as e:
        logging.error(f"Could not connect to server: {e}")
        return

    # Send system information (number of cores)
    core_count = os.cpu_count()
    send_json(client_socket, {"type": "info", "cores": core_count})

    try:
        while True:
            # Receive the task (hash and range)
            task = recv_json(client_socket)

            if task["type"] == "task":
                logging.info(f"Received task: {task}")
                range_start, range_end = task["range_start"], task["range_end"]
                md5_to_find = task["hash"]

                # Shared variable and lock for the found flag
                found_flag = [False, None]
                lock = threading.Lock()

                # Divide the work into threads based on available cores
                threads = []
                chunk_size = (range_end - range_start) // core_count

                for i in range(4):
                    start = range_start + i * chunk_size
                    end = start + chunk_size if i < 3 else range_end
                    thread = threading.Thread(target=check_range, args=(start, end, md5_to_find, found_flag, lock))
                    threads.append(thread)
                    thread.start()

                # Wait for all threads to finish
                for thread in threads:
                    thread.join()

                # Send the result to the server
                if found_flag[0]:
                    send_json(client_socket, {"type": "result", "status": "FOUND", "number": found_flag[1]})
                else:
                    send_json(client_socket, {"type": "result", "status": "NOT FOUND"})

            elif task["type"] == "stop":
                logging.info(f"Stop received: {task['reason']}")
                break  # Exit on stop message

    except KeyboardInterrupt:
        logging.info("Stopping the client...")
    finally:
        client_socket.close()
        logging.info("Client socket closed.")
        sys.exit(0)  # Exit the program


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Client script to connect to a server.")
    parser.add_argument('--ip', type=str, default="127.0.0.1", help="Server IP address")
    parser.add_argument('--port', type=int, default=9999, help="Server port number")

    # Parse arguments
    args = parser.parse_args()

    # Call main with the provided ip and port
    main(args.ip, args.port)

