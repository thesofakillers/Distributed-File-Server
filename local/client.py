import Pyro4
import sys
import os

client_address = "localhost"

#Telling Pyro to use pickle as the serializer
Pyro4.config.SERIALIZER = "pickle"
Pyro4.config.SERIALIZERS_ACCEPTED = ["json", "marshal", "serpent", "pickle"]
#handles bytes directly and is fastest. Not secure but thats beyond scope of assignment.

@Pyro4.expose #Exposing Client class and its contents to Pyro
class Client():
    """
    A client, someone who uploads and downloads files from the system
    Has state (string) and daemon attributes.
    """
    def __init__(self, daemon, state):
        self.daemon = daemon #pyro daemon
        self.state = state #string

    """
    Allows printing from frontend on client terminal
    """
    def print_something(self, something):
        print(something)

    """
    Gets client state and returns it.
    In pyro, this is slighly easier than accessing client attributes directly.
    """
    def get_state(self):
        return self.state

    """
    Sets client state.
    """
    def set_state(self, state):
        self.state = state

    """
    Asks client to input filename for a file they wish to upload.
    Returns inputted filename and data of file in bytes
    """
    def read_file_return(self):
        while True: #Asks user to enter the name of the file.
            filename = input("\nEnter the name of the file you wish to upload.\
            \nPress enter to cancel upload.\
            \nFile name: ")

            if filename == "": #If user presses enter
                data = None #to minimize transfer size
                print("\nUpload canceled\n")

            else:
                try: #try/except to handle invalid filenames
                    path = os.path.join("Resources", filename) #handle different OS paths
                    f = open(path, "rb") #opens file in binary mode
                    data = f.read() #reads the bytes directly
                    f.close() #closes file

                except FileNotFoundError as e: #handles the error
                    print("\nFile not found. (Ensure to include the extension!)")
                    continue #Allows user to try again.
            break #breaks once try is succesful

        return filename, data

    """
    Asks user for a filename that they wish to download or delete, depending
    on the mode (string) passed to the function.
    Returns the filename requested.
    """
    def get_filename(self, mode):
        if mode == "download":
            filename = input("\nEnter the name of the file you wish to %s.\
            \nPress enter to cancel download.\
            \nFile name: " % mode)
        elif mode == "delete":
            filename = input("\nEnter the name of the file you wish to %s: " % mode)
        #returns filename obtained from input
        return filename

    """
    Writes passed data (bytes) to a file of with the passed filename (string).
    No returns.
    """
    def write_file(self, filename, data):
        path = os.path.join("Resources", filename) #handle different OS paths
        f = open(path, "wb") #opens file in binary mode
        f.write(data) #writes bytes directly
        f.close() #cleanup

    """
    Asks Client to input 'Yes' or 'No' to confirm file deletion.
    Handles client entering wrong response.
    Returns client response
    """
    def get_confirm(self):
        yesno = input("\nAre you sure you want to delete the file?\
        \nType 'Yes' or 'No': ")
        while yesno != 'Yes' and yesno != "No": #to let the user retry if they mistype yes or no
            yesno = input("Invalid response, Type 'Yes' or 'No': ")
        return yesno

    """
    Asks client to input command. Uses state attribute to determine current state.
    Different state will ask for different commands.
    Returns inputted command (string)
    """
    def get_command(self):
        if self.state == "disconnected":
            command = input("You are currently not connected to the server.\
            \n-Type \"CONN\" to send a request to connect to the server.\
            \n-Type \"QUIT\" to close the program.\
            \nPlease enter your desired command: ")
            return command

        elif self.state == "connected":
            command = input("you are currently connected to the server\
            \n-Type \"QUIT\" to end your session with the server\
            \n-Type \"UPLD\" to initiate a sequence for uploading a file to the server.\
            \n-Type \"UPLD+\" to initiate a sequence for reliable upload to the server\
            \n-Type \"LIST\" to list the directory of the server\
            \n-Type \"DWLD\" to initiate a sequence for downloading a file from the server.\
            \n-Type \"DELF\" to initate a sequence for deleting a file from the server.\
            \nPlease enter your desired command: ")
            return command

    """
    Either quits script or disconnects from system, depending on state.
    No returns.
    """
    def quit(self):
        if self.state == "disconnected":
            self.daemon.shutdown() #uses daemon attribute to disconnect from Pyro
        elif self.state == "connected":
            print("\nDisconnecting...\n")
            self.state = "disconnected" #simply changing state is enough to disconnect

if __name__=="__main__": #what to do when client.py is run
    #start pyro daemon with specific uri structure
    with Pyro4.Daemon(host = client_address, port = 10000) as daemon:
        client = Client(daemon, "disconnected") #initialize client
        client_uri = daemon.register(client, "client") #register client
        daemon.requestLoop()
