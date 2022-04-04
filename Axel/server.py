import os, select, socket, sys
import json

MAX_SIZE_MSG  = 4096

def	create_server(HOST, PORT) :
	nb_client = 0
	close = False
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try :
		sock.bind((HOST, PORT))
	except :
		print("error Create socket")
		exit(1)
	sock.listen()
	socketlst = [sock, sys.stdin]
	while not(close) :
		(new_sock, _, _) = select.select(socketlst, [], [])
		for s in new_sock :
			if (s == sock) :
				if (nb_client < 4) :
					(new_sock, (host, port)) = sock.accept()
					socketlst.append(new_sock)
				nb_client += 1
			elif (s == sys.stdin) :
				msg = sys.stdin.readline()
				if (msg == "exit\n") : 
					s.close()
					close = True
					break
			else :
				msg = s.recv(MAX_SIZE_MSG).decode('utf8')
				print(msg)
				try :
					s.send("<html>bite</html>")
				except :
					print ("ERROR SEND")
				socketlst.pop(socketlst.index(s))
				s.close()
				nb_client -= 1
				
	sock.close()
	
if __name__ == "__main__" :
	create_server("127.0.0.1", 4242)