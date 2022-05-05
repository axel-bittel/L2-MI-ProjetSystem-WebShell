import os, select, socket, signal, sys

MAXBYTES = 4096
fils = []

def create_server(HOST, PORT, traitant) :

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGCHLD, signal.SIG_IGN) #TO AVOID DEFUNCT PROCESS

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((HOST, PORT))
    print("Server Mount")
    serversocket.listen(4)
    socketlist = [0,serversocket]
    fils = []

    while len(socketlist) > 0:
        (readable, _, _) = select.select(socketlist, [], [])
        for s in readable:
            if s==0 :
                data = os.read(0, MAXBYTES)
                if data != b'exit\n' : 
                    continue
                else :
                    socketlist.remove(serversocket)
                    for s in socketlist :
                        try :
                            s.shutdown(socket.SHUT_RDWR)
                            s.close()
                        except :
                            continue
                    socketlist = []
                    break
            elif s == serversocket:
                (clientsocket, (addr, port)) = s.accept()
                print("connection from:", addr, port)
                socketlist.append(clientsocket)
            else :
                pid = os.fork()
                if (pid==0) :
                    res = s.fileno()
                    os.dup2(res,0)
                    os.dup2(res, 1)
                    os.execvp("python3", ["python3", traitant + ".py"])
                else :
                    fils.append(pid)
                    s.close()
                    socketlist.remove(s)		
    serversocket.close()

def handler(signum, frame) :
    for pid in fils :
        os.kill(pid, signal.SIGKILL)
        #os.waitpid(pid,0)


if __name__ == "__main__" :
	if (len(sys.argv) == 3) :
		ip = "127.0.0.1"
		port = sys.argv[2]
		file = sys.argv[1]
		if (not(port.isnumeric())) :
			os.write (2, bytes("PORT IS NOT A NUMBER\n", "utf8"))
			exit (1)
		if (not(os.path.exists(bytes(file + ".py", "utf8")))) :
			os.write (2, bytes("FILE NOT EXIST\n", "utf8"))
			exit (1)
		create_server(ip, int(port), file)
	else :
		os.write (2, bytes("NOT ENOUGH ARUMENTS\n", "utf8"))
	#create_server("127.0.0.1", 2105, "Axel/webshell2")