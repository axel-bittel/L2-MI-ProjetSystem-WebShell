import os
import sys
import signal
import socket

L_pids=[]
nb_conn_act = 0                                                # nombre de connexions actuelles

def traitement(t,process_traitant):
	global nb_conn_act
	pid = os.fork()
                
	if pid == 0: #child
		fd = t.fileno()
		os.dup2(fd,0)
		os.dup2(fd,1)
		os.execvp("python3", ["python3", process_traitant])
            
	if pid != 0: #father
		L_pids.append(pid)    
		nb_conn_act += 1

def handler(numsig,frame):
    for p in L_pids :
        try :
            os.kill(p,signal.SIGINT)
        except :
            continue
    sys.exit(0)

def server():
    
    global nb_conn_act
    #process_traitant = sys.argv[1]
    process_traitant = "test.py"
    taille_max = 4
    port = 4003

    signal.signal(signal.SIGINT, handler)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)       # creation socket serveur
    s.bind(("", port))                                             # associe le socket à une adresse locale (port sur lequel il doit ecouter)
    s.listen(taille_max)                                           # ecoute les connexions entrantes (avec taille max de liste d'attente)
    
    while True :
        (t, add) = s.accept()                                      # accepte connexion, retourne nouveau socket et une adresse client

        if add[0] == "127.0.0.1" :
            
            if nb_conn_act < 4:
                traitement(t,process_traitant)

            else :
                os.waitpid(-1,0)
                nb_conn_act -= 1
                
                traitement(t,process_traitant)

        else :
            t.close()

server()