import json
from select import select
from signal import SIGKILL, SIGUSR1
import time 
import os
import sys

res = """
HTTP/1.1 200
Content-Type: text/html; charset=utf-8
Connection: close
Content-Length: $(SIZE) 

"""
res2 = """
<!DOCTYPE html>
<html>
<head>
    <title>WEB SHELL 3</title>
</head>
<body style="background-color:black;color:#00FA16">
	<h1 style="text-align:center"><strong><u>WEB SHELL</u></strong></h1><br>
	<h3><u>HISTORY</u></h3> 
	$(HISTORY)<br>
	<h3><u>LAST CMD :</u> $(DATA)</h3><br>
	<form style="background-color:black;color:#00FA16" action="ajoute$(ID_SESSION)$(IS_STDIN)" method="get">
		<input id="textbox" type="text"  style="border:3px solid #46C786;border-radius:10px;width:200px;box-shadow:1px 1px 2px #C0C0C0 inset;" name="saisie" placeholder="$(TEXT_BOX)" />
		<input type="submit" name="send" value="&#9166;">
	</form>
	<h3><u>RES CMD :</u></h3> 
	$(RES)
</body>
<script language="javascript">
	var box_input = document.getElementById('textbox');
	box_input.focus();
	box_input.select();
</script> 	
</html>
""" 
is_stdin = 0
def escaped_utf8_to_utf8(s):
    res = b'' ; i = 0
    while i < len(s):
        if s[i] == '%':
            res += int(s[i+1:i+3], base=16).to_bytes(1, byteorder='big')
            i += 3
        else :
            res += bytes(s[i], "utf8")
            i += 1
    return res.decode('utf-8')

def read_file (fd, change_stdin = 0) :
	is_error = False
	reading = True
	is_none = 0 
	global is_stdin
	read = bytes('', "utf8")
	while (reading) :
		try :
			inter = os.read(fd, 4096) 
			read += inter 
			if (inter[-1] == 10 and inter[0] != 10) :
				reading = False
			elif (is_none > 1) :
				reading = False
			elif (inter == b'\10'):
				is_none += 1 
				time.sleep(1)
		except :
			if (is_error) :
				if (change_stdin == 1) :
					is_stdin = 1
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
	for i in msg.decode('utf8').split('\r') :
		if i.split(' ')[0].replace("\n", "") == "Accept:" :
			return (i.split(' ')[1].split(',')[0])
	return ('')
def	get_cmd() :
	global is_stdin
	id_session = ''
	msg = os.read(0, 100000) #READ PAQUET
	if (get_paquet_type(msg) != "GET" or get_paquet_prot(msg) != 'HTTP/1.1') : #IS GOOD PAQUET
		os.write(2, b"request not supported\n")
	elif (get_acceptHTML(msg) != 'text/html'):
		os.write(2, b"NOT HTML/TEXT SUPPORT\n")
		os.close (0)
		sys.exit (0)
	else :
		#EXTRACT DATA
		data = ''
		if (len(get_paquet_data(msg).split("?")) > 1) :
			data = get_paquet_data(msg).split("?")[1].split("&")[0].split("=")[1].replace('+', ' ')
			data = escaped_utf8_to_utf8(data)
		if (len(get_paquet_data(msg).split("?")) > 1) :
			id_session = get_paquet_data(msg).split("?")[0].replace("ajoute", "").replace("/", "")[:-1]
			is_stdin = int(get_paquet_data(msg).split("?")[0].replace("ajoute", "").replace("/", "")[-1])
		#CHECK IF CMD IS EXIT
		if (data.split(' ')[0].lower() == 'exit') :
			os.kill(int(id_session), SIGKILL)
			id_session = ''
			data = ''
	#CREATE RETURN PAQUET
		msg = res2.replace("$(DATA)", data)
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
			os.write(fd_history, bytes("<font color='orange'>" + time.strftime("%d/%m/%Y %H:%M:%S") + "$</font> " + data + '\n','utf8'))
			os.write(fd_fifo_out, bytes(data + "\n", 'utf8'))
			if (is_stdin == 1) :
				os.write(fd_fifo_out, b"\04")
			time.sleep(0.1) #LET THE TIME TO WRITE AND PROCESS 
		#WRITE RES CMD
		if (len(data) > 0) :
			shell_res = ''
			if (is_stdin == 0) :
				shell_res = read_file(fd_fifo_in, 1)
			else :
				shell_res = read_file(fd_fifo_in, 0)
				is_stdin = 0
			msg = msg.replace("$(RES)" ,shell_res.replace("\n", "<br>"))
			msg = msg.replace("$(IS_STDIN)", str(is_stdin))
			if (is_stdin == 0) :
				msg = msg.replace("$(TEXT_BOX)", "Tapez une commande")
			else :
				msg = msg.replace("$(TEXT_BOX)", "Entree Standard")
			os.write(fd_history, bytes(shell_res, 'utf8'))
			os.close (fd_fifo_in)
			os.close (fd_fifo_out)
		else : #KEEP PROCESS ALIVE AND WAIT END SH
			msg = msg.replace("$(IS_STDIN)", "0")
			msg = msg.replace("$(TEXT_BOX)", "Tapez une commande")
			msg = res.replace("$(SIZE)", str(len(msg))).replace('\n', '\r\n') + msg
			os.write(1, bytes(msg.replace("$(RES)", ""), 'utf8')) #WRITE PAQUET
			time.sleep(0.1) #LET THE TIME TO WRITE
			os.close(0)
			os.close(1) #CLOSE IN/OUT SOCKET 
			os.kill(os.getppid(), SIGUSR1) #SIG TO SAY THE END OF THIS PROCESS TO SERVER 
			try :
				os.waitpid(pid, 0) #STAY ALIVE FOR THE SH PROCESS
			except :
				sys.exit(0)
		msg = res.replace("$(SIZE)", str(len(msg))).replace('\n', '\r\n') + msg
		os.write(1, bytes(msg, 'utf8')) #WRITE PAQUET
		os.close(0)
	
if __name__ == "__main__" :
	get_cmd()
	sys.exit (0)