-System
	-local
		-client.py
		-Resources
	-middle
		-frontend.py
	-remote
		-server1
			-server1.py
			-Resources
		-server2
			-server2.py
			-Resources
		-server3
			-server3.py
			-Resources
	-readme.txt
		
System consists in five python3.6 scripts: client.py, frontend.py, server1.py, server2.py, server3.py. 3 servers are copies of the same script placed in different directories to simulate running on different machines (actually running them on different machines can be achieved aswell.)

Necessary Modules: Pyro4, sys, os, pickle.

Files stored in Client and Servers are placed in respective "Resources" Folder.

Run each script in separate terminal (servers can be sent to background).
The general process is:
1. Run frontend.py
2. Run at least one of 3 server scripts. (steps 1&2: arbitrary order)
3. Run client.py. Provides user with instructions along the way.

-System handles 2 server crashes (i.e. only 1 server running). 
-Frontend running for system to be operational.

To run a script on a different machine from frontend.py, simply determine the machine's ipaddress and replace "localhost" with the ipaddress in respective constants across the scripts. 

Example: run server3.py on different machine:
1. Move "server3" directory to different machine
2. Determine machine ipaddress.
3. In server3.py and frontend.py, change constant server3_address from "localhost" to the ip address you determined (string).
4. Proceed with general process defined above

Designed in Ubuntu. Tested on Windows/Linux Python3.6.
