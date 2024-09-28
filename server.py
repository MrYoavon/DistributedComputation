import logging
import socket
import threading
import json

# Set up logging
logging.basicConfig(level=logging.INFO)

# Global variables
current_range_start = 0
block_size = 1_000_000
hash_to_find = "ec9c0f7edcc18a98b1f31853b1813301".lower()
range_lock = threading.Lock()
found_flag = threading.Event()  # Flag to indicate the number is found
found_number = None


# Send JSON data to the client
def send_json(client_socket, data):
    message = json.dumps(data)
    client_socket.send(message.encode())


# Receive JSON data from the client
def recv_json(client_socket):
    data = client_socket.recv(1024).decode()
    return json.loads(data)


# Client handler function
def handle_client(client_socket, address):
    global current_range_start, found_number

    logging.info(f"New connection from {address}")
    try:
        # Send the MD5 hash to the client
        send_json(client_socket, {"type": "task", "hash": hash_to_find, "range_start": 0, "range_end": 0})

        # Negotiate system information (cores available)
        client_info = recv_json(client_socket)
        cores = 1
        if client_info["type"] == "info":
            cores = client_info["cores"]
            logging.info(f"Client {address} has {cores} cores")

        while not found_flag.is_set():
            # Adjust the block size based on the number of cores
            client_block_size = block_size * cores

            # Use the lock to safely update and assign the range
            with range_lock:
                range_start = current_range_start
                current_range_start += client_block_size

            # Send task with the current range
            if found_flag.is_set():  # If found by another client, stop
                break
            task_data = {
                "type": "task",
                "hash": hash_to_find,
                "range_start": range_start,
                "range_end": range_start + client_block_size
            }
            send_json(client_socket, task_data)
            logging.info(f"Sent task {range_start}-{range_start + client_block_size} to client {address}")

            # Receive response from the client
            response = recv_json(client_socket)
            if response["type"] == "result":
                if response["status"] == "FOUND":
                    found_flag.set()
                    found_number = response["number"]
                    logging.info(f"Client {address} found the number: {found_number}")
                    send_json(client_socket, {"type": "ack", "message_id": "result", "status": "result_received"})
                    break
                else:
                    logging.info(f"Client {address} did not find the number in range {range_start}-{range_start + client_block_size}")

    except Exception as e:
        logging.error(f"Error handling client {address}: {e}")
    finally:
        # Send stop message if another client found the number
        if found_flag.is_set() and found_number:
            stop_message = {
                "type": "stop",
                "reason": "number_found",
                "found_number": found_number
            }
            send_json(client_socket, stop_message)
        client_socket.close()
        logging.info(f"Connection with {address} closed.")


# Start the server
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 9999))
    server.listen(5)

    logging.info("Server is running...")

    try:
        while True:
            client_socket, address = server.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, address))
            client_handler.start()
    except KeyboardInterrupt:
        logging.info("Server is shutting down.")
        # Send shutdown message to all clients if needed
    finally:
        server.close()


if __name__ == "__main__":
    start_server()
