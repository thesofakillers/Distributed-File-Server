# Distributed File-Server System

Originally made for Durham University's Department of Computer Science's course _Networks and Systems_ under the sub-module _Distributed Systems_, as part of the coursework in 2017/2018.

This repository contains an implementation of a distributed file server system written in Python

This assignment is a follow-up to [this other assignment](https://github.com/thesofakillers/ClientServer-FTP) from the same module.

Please ensure [Pyro4](https://pythonhosted.org/Pyro4/) is installed.

## Repository Structure

```bash
├── local
│   ├── client.py
│   └── Resources
│       ├── LargeFile.mp4
│       ├── MediumFile.pdf
│       └── SmallFile.txt
├── middle
│   └── frontend.py
├── README.md
└── remote
    ├── server1
    │   ├── Resources
    │   └── server1.py
    ├── server2
    │   ├── Resources
    │   └── server2.py
    └── server3
        ├── Resources
        └── server3.py
```

The repository consists in five [Python 3.6](https://www.python.org/downloads/release/python-360/) scripts: `client.py`, `frontend.py`, `server1.py`, `server2.py`, `server3.py`. The 3 servers are copies of the same script placed in different directories to simulate running on different machines (actually running them on different machines can be achieved aswell.)

Files stored in Client and Servers are placed in respective "Resources" Folder.

## Instructions

Run each script in separate terminal (servers can be sent to background).
The general process is:
	1. Run `frontend.py`
	2. Run at least one of 3 server scripts. (steps 1&2: arbitrary order)
	3. Run `client.py`. Provides user with instructions along the way.

-   System handles 2 server crashes (i.e. only 1 server running).
-   Frontend running for system to be operational.

To run a script on a different machine from `frontend.py`, simply determine the machine's IP address and replace "localhost" with the IP address in respective constants across the scripts.

Example: run server3.py on different machine:
	1. Move "server3" directory to different machine
	2. Determine machine IP address.
	3. In `server3.py` and `frontend.py`, change constant `server3_address` from "localhost" to the ip address you determined (string).
	4. Proceed with general process defined above

Designed in Ubuntu. Tested on Windows/Linux Python3.6.

## In the Future
I realize that having 3 copies of the same script is very silly. In principle, I would change this so that there is a single script whose instances can be run from different terminals. This would be relatively simple to implement. Perhaps even utilizing git!
