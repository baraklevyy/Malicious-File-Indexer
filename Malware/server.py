#!/usr/bin/env python3

import socket
import os
import lz4.frame
import datetime
import struct

# Seeking the whole memory
ROOT_PATH = '/'
# Arbitrary port number
PORT = 12346
# ! indicates network 'big-endian' , H - unsigned short which means 2 bytes
LENGTH_FORMAT = '!H'
# Arbitrary buffer length - should be sufficient
BUFFER_LENGTH = 1024


def find_extensions(base_path, extension_path, dest_socket):
    for dir_name, dirs, files_names in os.walk(base_path):
        for file_name in files_names:
            if file_name.endswith(extension_path):
                # Found good file
                full_path = os.path.join(dir_name, file_name)
                compressed_path = lz4.frame.compress(full_path.encode())
                # Protocl between client and server:
                #  unsigned short (16 bit)   | [Length of compressed data]
                #  Length of compressed data |  Compressed data
                encoded_length = struct.pack(LENGTH_FORMAT, len(compressed_path))
                data_to_send = encoded_length + compressed_path
                dest_socket.send(data_to_send)


def handle_client(client_socket):
    file_extension = client_socket.recv(BUFFER_LENGTH).decode('utf-8')
    print('Server: client sent "%s"' % (file_extension,))
    find_extensions(ROOT_PATH, file_extension, client_socket)
    client_socket.close()


def main():
    a = socket.socket()
    """
    In order to enable 'SO_REUSEADDR' specify:
    socket name = a
    level = SOL_SOCKET
    Option name = SO_REUSEADDR
    Turning the option ON/OFF --> 1/0
    Two main reason to setup SO_REUSEADDR :
    1.Alloying binding two sockets to the same source port with different address(failure may occur due to the wildcard '0.0.0.0' which consider all-locals ips as same entity.
    2. Removing the time delay in 'TIME_WAIT'-socket state, when trying to binding a new socket to the same source (address+port)
    """

    a.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # '0.0.0.0' wildcard indicates 'any address' in IPv4
    a.bind(('0.0.0.0', PORT))
    a.listen(1)

    while True:
        try:
            print('Server: listening %s:%s' % ('0.0.0.0', PORT,))
            client_socket, client_address = a.accept()
            print('Server: client %s connected' % (client_address,))
            handle_client(client_socket)
        except Exception as e:
            print('Client error: %s' % (e,))
            continue

    a.close()


if __name__ == '__main__':
    main()
