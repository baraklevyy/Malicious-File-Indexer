#!/usr/bin/env python3

import socket
import struct
import datetime
import lz4.frame
import sys

LENGTH_FORMAT = '!H'

"""
Implementing the protocol which means:
Received data : [Length of data][Actual data]
"""


def recv_exact(dest_socket, length):
    data = b''
    remaining_length = length
    while remaining_length:
        current_data = dest_socket.recv(remaining_length)
        if not current_data:
            if data:
                raise Exception('Server returned corrupted data')
            else:
                return data

        data += current_data
        remaining_length -= len(current_data)

    return data


def request_extension(server_address, server_port, file_extension):
    server_socket = socket.socket()
    # tuple (address, port)
    # argv variables are string and server port is int. Conversion needed
    server_socket.connect((server_address, int(server_port),))
    server_socket.send(file_extension.encode())
    while True:
        try:
            # first two bytes are data length
            path_length_encoded = recv_exact(server_socket, 2)
        except Exception as e:
            print('ERROR: %s' % (e,))
            break
        if not path_length_encoded:
            break
        # Using struct-pack\unpack due to the nature of sending bytes
        path_length = struct.unpack(LENGTH_FORMAT, path_length_encoded)[0]

        try:
            compressed_path = recv_exact(server_socket, path_length)
        except Exception as e:
            print('ERROR: %s' % (e,))
            break
        if not path_length_encoded:
            break

        decompressed_path = lz4.frame.decompress(compressed_path).decode()

        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        peer_name = server_socket.getpeername()
        server_ip = peer_name[0]
        print('%s ,%s %s' % (server_ip, timestamp, decompressed_path,))
    server_socket.close()


def main(server_address, server_port):
    while True:
        file_extension = input('Please enter file extension: ')
        if not file_extension:
            break
        request_extension(server_address, server_port, file_extension)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
