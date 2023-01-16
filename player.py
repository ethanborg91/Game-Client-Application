import socket
import signal
import sys
import argparse
from urllib.parse import urlparse
import selectors

# @Author: Ethan Borg   @Date: 12/6/2022
# This player class is responsible for holding the player information
# and getting command from the player and communicating with the room

# Selector for helping us select incoming data from the server and messages typed in by the user.

sel = selectors.DefaultSelector()

# Socket for sending messages.

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

DISCOVERYSERVER = ("localhost", 5555)

# Room name.

room_name = ''

# User name for tagging sent messages.

name = ''

# Inventory of items.

inventory = []

# Directions that are possible.

connections = { 
    "north" : "",
    "south" : "",
    "east" : "",
    "west" : "",
    "up" : "",
    "down" : ""
    }

# Timeout constant

TIMEOUT = 5

# This function sends the name to the discovery to get the address

def lookup_address(name):
    room_info = "LOOKUP " + name 
    client_socket.settimeout(TIMEOUT)

    # Sends the name of the room requested to the discovery

    client_socket.sendto(room_info.encode(), DISCOVERYSERVER)
    try:
        response, addr = client_socket.recvfrom(1024)
    except OSError as msg:
            print('No response from server. Now exiting...')
            sys.exit()
    word = response.decode()
    return word

# Signal handler for graceful exiting.  Let the server know when we're gone.

def signal_handler(sig, frame):
    word = lookup_address(room_name).split()
    if word[0] == "OK":
        print('Interrupt received, shutting down ...')
        message='exit'
        client_socket.sendto(message.encode(),("localhost",word[1]))
        for item in inventory:
            message = f'drop {item}'
            client_socket.sendto(message.encode(),("localhost", word[1]))
        sys.exit(0)
    else:
        print('There was an ERROR exiting the room')
        sys.exit(0)

# Simple function for setting up a prompt for the user.

def do_prompt(skip_line=False):
    if (skip_line):
        print("")
    print("> ", end='', flush=True)

# Function to join a room.

def join_room():
    word = lookup_address(room_name)
    response = word.split()
    if response[0] == "OK":
        message = f'join {name}'
        client_socket.settimeout(TIMEOUT)
        client_socket.sendto(message.encode(), ("localhost", int(response[1])))
        try:
            response, addr = client_socket.recvfrom(1024)
            print(response.decode())
        except OSError as msg:
            print('No response from server. Now exiting...')
            sys.exit()
    else:
        print(word)
        sys.exit(0)

# Function to handle commands from the user, checking them over and sending to the server as needed.

def process_command(command):

    global room_name

    # Parse command.

    words = command.split()

    # Check if we are dropping something.  Only let server know if it is in our inventory.

    if (words[0] == 'drop'):
        if (len(words) != 2):
            print("Invalid command")
            return
        elif (words[1] not in inventory):
            print(f'You are not holding {words[1]}')
            return

    # Send command to server, if it isn't a local only one.

    if (command != 'inventory'):
        message = f'{command}'
        addy = int(lookup_address(room_name).split()[1])
        client_socket.settimeout(TIMEOUT)
        client_socket.sendto(message.encode(), ("localhost", addy))

    # Check for particular commands of interest from the user.

    # If we exit, we have to drop everything in our inventory into the room.

    if (command == 'exit'):
        for item in inventory:
            message = f'drop {item}'
            addy = int(lookup_address(room_name).split()[1])
            client_socket.sendto(message.encode(), ("localhost", addy))
        sys.exit(0)

    # If we look, we will be getting the room description to display.

    elif (command == 'look'):
        try:
            response, addr = client_socket.recvfrom(1024)
        except OSError as msg:
            print('No response from server. Now exiting...')
            sys.exit()
        print(response.decode())

    # If we inventory, we never really reached out to the room, so we just display what we have.

    elif (command == 'inventory'):
        print("You are holding:")
        if (len(inventory) == 0):
            print('  No items')
        else:
            for item in inventory:
                print(f'  {item}')

    # If we take an item, we let the server know and put it in our inventory, assuming we could take it.

    elif (words[0] == 'take'):
        try:
            response, addr = client_socket.recvfrom(1024)
        except OSError as msg:
            print('No response from server. Now exiting...')
            sys.exit()
        print(response.decode())
        words = response.decode().split()
        if ((len(words) == 2) and (words[1] == 'taken')):
            inventory.append(words[0])

    # If we drop an item, we remove it from our inventory and give it back to the room.

    elif (words[0] == 'drop'):
        try:
            response, addr = client_socket.recvfrom(1024)
        except OSError as msg:
            print('No response from server. Now exiting...')
            sys.exit()
        print(response.decode())
        inventory.remove(words[1])

    # If we're wanting to go in a direction, we check with the room and it will tell us if it's a valid
    # direction.  We can then join the new room as we know we've been dropped already from the other one.

    elif (words[0] in connections):
        try:
            response, addr = client_socket.recvfrom(1024)
        except OSError as msg:
            print('No response from server. Now exiting...')
            sys.exit()
        word = response.decode()
        if lookup_address(word).split()[0] == "OK":
            room_name = response.decode()  
            join_room()
        else:
            print(response.decode())      


    # The player wants to say something ... print the response.

    elif (words[0] == 'say'):
        try:
            response, addr = client_socket.recvfrom(1024)
        except OSError as msg:
            print('No response from server. Now exiting...')
            sys.exit()
        print(response.decode())
        
    # Otherwise, it's an invalid command so we report it.

    else:
        try:
            response, addr = client_socket.recvfrom(1024)
        except OSError as msg:
            print('No response from server. Now exiting...')
            sys.exit()
        print(response.decode())

# Function to handle incoming messages from room.  Also look for disconnect messages to shutdown.

def handle_message_from_server(sock, mask):
    response, addr = client_socket.recvfrom(1024)
    words=response.decode().split(' ')
    print()
    if len(words) == 1 and words[0] == 'disconnect':
        print('Disconnected from server ... exiting!')
        sys.exit(0)
    else:
        print(response.decode())
        do_prompt()

# Function to handle incoming messages from user.

def handle_keyboard_input(file, mask):
    line=sys.stdin.readline()[:-1]
    process_command(line)
    do_prompt()

# Our main function.

def main():

    global name
    global client_socket
    global room_name

    # Register our signal handler for shutting down.

    signal.signal(signal.SIGINT, signal_handler)

    # Check command line arguments to retrieve a URL.

    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="name for the player in the game")
    parser.add_argument("room_name", help="name for the room the player starts in")
    args = parser.parse_args()

    name = args.name
    room_name = args.room_name

    # Send message to enter the room.
    join_room()

    client_socket.settimeout(TIMEOUT)

    # Set up our selector.

    #client_socket.setblocking(False)
    sel.register(client_socket, selectors.EVENT_READ, handle_message_from_server)
    sel.register(sys.stdin, selectors.EVENT_READ, handle_keyboard_input)
    
    # Prompt the user before beginning.

    do_prompt()

    # Now do the selection.

    while(True):
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)    


if __name__ == '__main__':
    main()
