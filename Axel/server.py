from multiprocessing.connection import wait
import os, select, socket, sys, signal
import json, time

MAX_SIZE_MSG  = 4096
test = b"""HTTP/1.1 200 
Content-Type: text/html; charset=utf-8
Connection: close
Content-Length: 125

<!DOCTYPE html>
<head>
    <title>Hello, world!</title>
</head>
<body>
bite
</body>
</html>"""
childs = []

def sig_int(sig_num, frame) :
	for c in childs :
			os.kill(c, signal.SIGSTOP)
	try :
		while (os.waitpid(-1, 0)) : 
			continue
	except : 
		print ("Kill all process")
	exit (128 + sig_num)

def	create_server(HOST, PORT, traitement) :
	nb_client = 0
	close = False
	signal.signal(signal.SIGINT, sig_int)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	while (1) :
		try :
			sock.bind((HOST, PORT))
			break
		except :
			print("error Create socket\nWaiting can connect...")
			time.sleep (1)
	print("Server mount")
	sock.listen()
	socketlst = [sock, sys.stdin]
	while not(close) :
		(new_sock, _, _) = select.select(socketlst, [], [])
		for s in new_sock :
			if (s == sock) :
				if (nb_client < 4) :
					(new_sock, (host, port)) = sock.accept()
					socketlst.append(new_sock)
					nb_client = nb_client + 1
				else :
					os.waitpid(-1, 0)
					nb_client -= 1
			elif (s == sys.stdin) :
				msg = sys.stdin.readline()
				if (msg == "exit\n") : 
					s.close()
					close = True
					break
			else :
				pid = os.fork()
				if (pid == 0) :
					res = s.fileno()
					os.dup2(res, 0)
					os.dup2(res, 1)
					os.execvp("python3", ["python3", traitement + ".py"])
				else :
					childs.append(pid)
					socketlst.remove(s)
					s.close()
	sock.close()
	
if __name__ == "__main__" :
	create_server("127.0.0.1", 4243, "traitment5")