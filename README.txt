How to run the program for my assignment

1. First run the room.py class in the terminal. You must run it with the roomConnections, serverPort, roomName, roomDescription, and roomItems respectively.
An example code to put in the terminal could be: python3 room.py -e room://localhost:4444 5555 Foyer "Hello World" vase rug

2. You can put multiple rooms. If you want rooms to connect just make sure the direction is put logically correct and the address put after has the port of the room you would like to connect to 
An example code of another room could be: python3 room.py -w room://localhost:5555 4444 Study "This is a new room" book desk 

3. Then you must run the player.py class in a seperate terminal. You must run it with the playerName, and the serverAddress respectively. The server address have the port of the room you would like to join 
An example code to put in the terminal could be: python3 player.py Bob room://localhost:5555

4. You can now add multiple players to an open room server

5. Within any of the clients you can enter the specified commands that were in the assignment instructions.
An example of this would be "take vase" or another example could be "inventory" 