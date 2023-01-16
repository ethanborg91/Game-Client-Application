import socket
import signal
import sys
from urllib.parse import urlparse

# @Author: Ethan Borg   @Date: 12/6/2022
# This is the discovery class responsible for registering and deregistering 
# rooms for the game holding the names and address of each room

# The port for the discovery class

DISCOVERYPORT = 5555

# Socket for sending messages.

discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# This list stores each room together

room_map = []

# Signal handler for graceful exiting.  Let the other classes know if exited.

def signal_handler(sig, frame):
    print('Interrupt received, shutting down ...')
    message='discovery closed'
    for room in room_map:
        discovery_socket.sendto(message.encode(),("localhost", int(room[0])))
    sys.exit(0)


# Function to register a room

def register_room(address, name):
    try:
        room = (address, name)
        for rooms in room_map:
            if (room[0] == rooms[0] or room[1] == rooms[1]):
                print("There is already a room with the same name or address")
                return False
        room_map.append(room)
        return True
    except ValueError:
        print("There was an ERROR registering the room")
        return False

# Function to deregister a room

def deregister_room(name):
    try:
        for room in room_map:
            if room[1] == name:
                room_map.remove(room)
                return True
        return False
    except ValueError:
        print("There was an ERROR deregistering the room")
        return False

# Function to lookup room address from room name

def lookup_room(name):
    try:
        for room in room_map:
            if room[1] == name:
                return room[0]
        return "ROOM DOES NOT EXIST"
    except ValueError:
        print("There was an ERROR looking up the room")
        return "ROOM DOES NOT EXIST"

# This function processes commands given from the user

def process_command(command, addr):

    word = command.split()

    # This is if the discovery has been requested to Register a room

    if word[0] == "REGISTER":
        if len(word) == 3:
            if register_room(word[1], word[2]):
                print("Room " + word[2] + " was registered successfully")
                return "OK"

        return "NOTOK could not register the room"

    # This is if the discovery has been requested to Deregister a room

    elif word[0] == "DEREGISTER":
        if len(word) == 2:
            if deregister_room(word[1]):
                print("Room " + word[1] + " was deregistered successfully")
                return "OK"
        
        return "NOTOK room does not exist"

    # This is if the discovery has been requested to Lookup an address of a room

    elif word[0] == "LOOKUP":
        if len(word) == 2:
            if lookup_room(word[1]) != "ROOM DOES NOT EXIST":
                print("Room " + word[1] + " was looked up successfully")
                return "OK " + lookup_room(word[1])
                
        return "NOTOK room does not exist"


# Our main function.

def main():

    # Register our signal handler for shutting down.

    signal.signal(signal.SIGINT, signal_handler)
    
    discovery_socket.bind(('', DISCOVERYPORT))
    print("Discovery is up and running!")

    # Loop forever waiting for messages from clients.
    while True:

        # Receive a packet from a client and process it.

        message, addr = discovery_socket.recvfrom(1024)

        # Process the message and retrieve a response.

        response = process_command(message.decode(), addr)

        # Send the response message back to the client.

        discovery_socket.sendto(response.encode(),addr)


if __name__ == '__main__':
    main()
