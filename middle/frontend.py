import Pyro4

#where scripts are running. Change these if running on different machine.
client_address = "localhost"
server1_address = "localhost"
server2_address = "localhost"
server3_address = "localhost"

#Telling Pyro to use pickle as the serializer
Pyro4.config.SERIALIZER = "pickle"
Pyro4.config.SERIALIZERS_ACCEPTED = ["json", "marshal", "serpent", "pickle"]
#handles bytes directly and is fastest. Not secure but thats beyond scope of assignment.

"""
Gets list of Servers that are running
Input: 3 objects which expected to be servers
Output: A list of Servers currently running
"""
def getAvailableServers(obj1, obj2, obj3):
    available = [] #initializing empty list
    #for each object, ping and see if available. If not, do nothing.
    #if available, append to the list
    try: #server1
        obj1.ping() #ping() method defined in server script
        available.append(obj1)
    except (Pyro4.errors.CommunicationError, Pyro4.errors.NamingError) as e:
        pass

    try: #server2
        obj2.ping()
        available.append(obj2)
    except (Pyro4.errors.CommunicationError, Pyro4.errors.NamingError) as e:
        pass

    try: #server3
        obj3.ping()
        available.append(obj3)
    except (Pyro4.errors.CommunicationError, Pyro4.errors.NamingError) as e:
        pass
    #return lists of available servers
    return available

"""
Determines whether no servers are running
Input: list of Available servers
Output: Boolean describing whether at least 1 Server is running.
"""
def checkAvailability(AvailableServers):
    if len(AvailableServers) == 0: #empty list, so no servers running
        print("No servers running! At least one server should be running.") #whoever oversees frontend can debug error
        Client.print_something("\nConnection issue, please try again later.\n") #informs client of some issue
        Client.set_state("disconnected") #disconnect client
        return False #False: no servers running
    else:
        return True #True: at least 1 server running. System operational

"""
Checks presence of file in a series of servers
Inputs: list of Available servers, name of file you wish to check for
Output: List of 1s and 0s, where 1 denotes server containing file
and 0 denotes server not containing file
"""
def checkFilePresence(AvailableServers, NameOfFile):
    filecontainingservers = [] #initializng empty list
    for i in AvailableServers: #iterate through Server List
        filecontainingservers.append(i.file_exists(NameOfFile))
        #appending 1 or 0 depending on containment.
        #file_exists defined in server script.
    return filecontainingservers #return list of 1s and 0s


while True: #First loop: no Client script running
    print("Waiting for client")
    while True: #get Proxy Objects for client and servers.
        Client = Pyro4.Proxy("PYRO:client@"+client_address+":10000")
        Server1 = Pyro4.Proxy("PYRO:server1@"+server1_address+":9999")
        Server2 = Pyro4.Proxy("PYRO:server2@"+server2_address+":8888")
        Server3 = Pyro4.Proxy("PYRO:server3@"+server3_address+":7777")
        wait = False #Waiting for client script? (To break from loop)
        while True:
            try: #Try in case registration was unsuccesful (see except)
                if Client.get_state() == "disconnected": #client is initialized in this state
                    print("Client Available")
                    val_cmds = ["CONN", "QUIT"] #Valid commands for a disconnected client

                    try: #ask client for command
                        command = Client.get_command()
                    except Pyro4.errors.ConnectionClosedError as e:
                        print("client quit process") #catches client crash (ctrl c for example)
                        wait = True #breaks out of all loops except for "Waiting for client loop"
                        break #breaks from inner loop

                    if (command in val_cmds) == False: #handles invalid command
                        print("Client entered invalid command")
                        Client.print_something("\nInvalid Command, please try again\n")

                    elif command == "QUIT": #command for quitting script
                        print("client quit process") #(since they havent even connected)
                        Client.print_something("\nQuitting client.py script.")
                        Client.quit() #client closes their script entirely
                        Client._pyroRelease() #releasing pyro daemon connection (somewhat arbitrary)
                        wait = True
                        break

                    else: #I.e. client has entered CONN, to connect
                        Client.print_something("\nAttempting to connect...\n")
                        Available = getAvailableServers(Server1, Server2, Server3)
                        if checkAvailability(Available) == False:
                            break #if no servers running, break
                        else: #otherwise, connect
                            Client.set_state("connected") #defined in client script
                            print("Client Connected")


                elif Client.get_state() == "connected":
                    print("Waiting for command from client")
                    val_cmds = ["QUIT", "UPLD", "UPLD+", "LIST", "DWLD", "DELF"]
                    #Different commands when the client is connected^^
                    try: #ask client for command
                        command = Client.get_command()
                    except Pyro4.errors.ConnectionClosedError as e:
                        print("client disconnected") #catches client crash (ctrl c for example)
                        wait = True #breaks out of all loops except for "Waiting for client loop"
                        break #breaks from inner loop

                    Available = getAvailableServers(Server1, Server2, Server3)
                    if checkAvailability(Available) == False:
                        break #checking if any servers are running

                    if (command in val_cmds) == False: #handles invalid command
                        print("Client entered invalid command")
                        Client.print_something("\nInvalid Command, please try again\n")

                    elif command == "QUIT": #command for disconnecting
                        print("client ended connection")
                        Client.quit() #ends connection.
                        #quit() knows whether client is connected or disconnected


                    elif command == "UPLD": #command for unreliable uploading
                        print("upload command received, attempting upload")
                        filename, data = Client.read_file_return()
                        #gets filename and file (in bytes) from client
                        if filename != "": #Enter lets client cancel download
                            Available = getAvailableServers(Server1, Server2, Server3)
                            if checkAvailability(Available) == False:
                                break #checking if any servers are running
                            #vv initializing empty list of directory sizes vv
                            directorysizes = []
                            for i in Available:
                            #Append length of each Available server directory to list
                                directorysizes.append(len(i.get_directory()))
                                #get_directory defined in server script
                            #determine directory with fewest files
                            minimumsize = min(directorysizes)
                            #Choose Server corresponding to that directory
                            Server = Available[directorysizes.index(minimumsize)]
                            #Write file to that server
                            Server.write_file(filename, data) #write_file in server script
                            print("upload completed")
                            Client.print_something("\nUpload completed\n")
                        else: #if filename == "", i.e. client canceled
                            print("upload canceled by client")


                    elif command == "UPLD+": #Command for reliable upload
                    #Same as UPLD, just write to all available servers rather just smallest directory
                        print("reliable upload command received, attempting reliable upload")
                        filename, data = Client.read_file_return()
                        #gets filename and file (in bytes) from client
                        if filename != "": #enter to cancel
                            Available = getAvailableServers(Server1, Server2, Server3)
                            if checkAvailability(Available) == False:
                                break #checking if at least one server is running
                            #Write file to each Server running.
                            for i in Available:
                                i.write_file(filename, data)
                                print("uploading to server")
                            Client.print_something("\nUpload completed\n")
                            print("Upload completed")
                        else: #pressed enter
                            print("upload canceled by client")


                    elif command == "DWLD": #command for download
                        print("download command received, attempting download")
                        while True: #While loop in case client mispells filename
                            try: #Exception raise if file not found. Also vv
                            #will need to raise exception rather than break when no Servers
                            #running since already in a while loop.
                                filename = Client.get_filename("download")
                                if filename != "": #Enter lets client cancel download
                                #checking if at least one server is running
                                    Available = getAvailableServers(Server1, Server2, Server3)
                                    if checkAvailability(Available) == False:
                                        raise Exception("Servers all offline")
                                    #gets list of 1s and 0s denoting filepresence in each server
                                    containingservers = checkFilePresence(Available, filename)
                                    #chooses any server that contains the file
                                    Server = Available[containingservers.index(1)]
                                    #Reads the file data from the server
                                    data = Server.read_file_return(filename) #read_file_return defined in server script.
                                    #Writing file to client directory
                                    Client.write_file(filename, data)
                                    Client.print_something("\nDownload completed succesfully\n")
                                    print("Download completed")
                                else:
                                    print("download canceled by client")
                                    Client.print_something("\nDownload canceled\n")
                            except ValueError as e: #Raised if there are no 1s in containingservers
                                #i.e. when none of the servers contain the requested file
                                Client.print_something("\nFile not found. (Ensure to include the extension!)")
                                continue #Allows user to try again.
                            except Exception as err:
                                break #breaks when all servers offline

                            break #breaks once try is succesful


                    elif command == "DELF": #command for deletion
                        print("delete command received, attempting deletion")
                        try: #Try necessary for non running servers because of While loop below
                            #While true to let client mispell filename or no filename on server
                            while True:
                                #asks client for filename
                                filename = Client.get_filename("delete")
                                #checking if at least one server is running
                                Available = getAvailableServers(Server1, Server2, Server3)
                                if checkAvailability(Available) == False:
                                    raise Exception("Servers all offline")
                                #gets list of 1s and 0s denoting filepresence in each server
                                containingservers = checkFilePresence(Available, filename)
                                #if at least one server contains the file
                                if (1 in containingservers):
                                    #ask for deletion confirmation
                                    yesno = Client.get_confirm() #defined in client script
                                    if yesno == "Yes": #Yes, i confirm you may delete
                                        #checking whether all servers have crashed in meantime
                                        Available = getAvailableServers(Server1, Server2, Server3)
                                        if checkAvailability(Available) == False:
                                            raise Exception("Servers all offline")
                                        #regets list of 1s and 0s denoting filepresence in each server
                                        containingservers = checkFilePresence(Available, filename)
                                        #Delete file in each server
                                        for i in range(len(containingservers)):
                                            if containingservers[i] == 1: #if the server contains the file
                                                Server = Available[i]
                                                Server.delete_file(filename) #defined in server script
                                                print("file deleted")
                                        Client.print_something("\nFile deleted\n")
                                        break
                                    else: #I.e. client enters No
                                        print("delete canceled by client")
                                        break
                                else: #None of the servers contain the file (all 0s)
                                    Client.print_something("\nFile not found. (Ensure to include the extension!)")
                        #breaks when all servers offline
                        except Exception as e:
                            break


                    elif command == "LIST": #command for listing
                        print("list command received, attempting directory listing")

                        #checking if at least one server is running
                        Available = getAvailableServers(Server1, Server2, Server3)
                        if checkAvailability(Available) == False:
                            break

                        #Creat list of each running server's directory
                        listofdirectories = []
                        for i in Available:
                            listofdirectories.append(i.get_directory())

                        #Merge directories, removing duplicate files
                        directory = list(set().union(*listofdirectories))

                        #Send directory contents to client
                        Client.print_something("\nHere are the files/directories present in the server:")
                        for i in directory:
                            Client.print_something(i)
                        Client.print_something("")
                        print("directory listed")

            except (Pyro4.errors.CommunicationError, Pyro4.errors.NamingError) as e:
                break #I.e.try again until the client runs their script

        if wait == True:
            break #Return to "Waiting for client state"
