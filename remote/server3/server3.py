import Pyro4
import os

server3_address = "localhost"

#Telling Pyro to use pickle as the serializer
Pyro4.config.SERIALIZER = "pickle"
Pyro4.config.SERIALIZERS_ACCEPTED = ["json", "marshal", "serpent", "pickle"]
#handles bytes directly and is fastest. Not secure but thats beyond scope of assignment.

@Pyro4.expose #Exposing Server class and its contents to Pyro
class Server():
    def __init__(self):
        pass #server does not need to be initialized with any attributes

    """
    Calling this function on an inactive Server throws a Pyro exception,
    which can be used to signal an inactive server.
    """
    def ping(self):
        return(True)

    """
    Lists the contents of the Server directory
    """
    def get_directory(self):
        #Have separate "Resources" folder for files to prevent showing "serverx.py" to client
        directorylist = os.listdir("Resources") #gets directory contents
        return directorylist

    """
    Checks whether a file exists in a server, given a passed file name (string).
    Returns a 1 if it does and a 0 if it doesnt.
    """
    def file_exists(self, filename):
        path = os.path.join("Resources", filename) #handle different OS paths
        try:
            if os.path.isfile(path): #checks if requested file is a file
                return 1
        except FileNotFoundError: #if not a file, or doesnt exist, this error will be raised
            return 0

    """
    Reads the contents of a requested file and returns them in bytes
    Input: String name of file
    Output: File contents, in bytes
    """
    def read_file_return(self, filename):
        path = os.path.join("Resources", filename) #handle different OS paths
        f = open(path, "rb") #opens file in binary mode
        data = f.read() #reads bytes directly
        f.close() #clean up
        return data #returns read bytes

    """
    Writes passed bytes to a file with passed filename.
    """
    def write_file(self, filename, data):
        path = os.path.join("Resources", filename) #handle different OS paths
        f = open(path, "wb") #opens file in binary mode
        f.write(data) #writes bytes directly
        f.close() #clean up

    """
    Deletes file with passed filename
    """
    def delete_file(self, filename):
        path = os.path.join("Resources", filename) #handle different OS paths
        os.remove(path) #removes requested file


if __name__=="__main__":
    server = Server() #initializing server
    #start pyro daemon with specific uri structure
    with Pyro4.Daemon(host = server3_address, port = 7777) as daemon:
        server_uri = daemon.register(server, "server3") #register server3
        print("server running")
        daemon.requestLoop()
