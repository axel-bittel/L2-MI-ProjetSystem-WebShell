import json
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
    <title>Hello, world!</title>
</head>
<body>
	$(HISTORY)<br>
	$(DATA)<br>
	<form action="ajoute$(ID_SESSION)" method="get">
		<input type="text" name="saisie" placeholder="Tapez quelque chose" />
		<input type="submit" name="send" value="&#9166;">
	</form>
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
	read = os.read(fd, 100000)
	res =  str(read.decode('utf8'))
	#while (len(read) > 0) :
		#res += read.decode('utf8')
		#res = os.read(fd, 100000)
	return (res)
def get_paquet_type(msg) :
	return (msg.decode('utf8').split("\r")[0].split(' ')[0])
def get_paquet_prot(msg) :
	return (msg.decode('utf8').split('\r')[0].split(' ')[2]);
def get_paquet_data(msg) :
	return(msg.decode('utf8').split("\r")[0].split(' ')[1])
def	get_cmd() :
	id_session = ''
	msg = os.read(0, 100000)
	if (get_paquet_type(msg) != "GET" or get_paquet_prot(msg) != 'HTTP/1.1') :
		os.write(2, b"request not supported\n")
	else :
		
		#EXTRACT DATA
		data = ''
		if (len(get_paquet_data(msg).split("?")) > 1) :
			data = get_paquet_data(msg).split("?")[1].split("&")[0].split("=")[1].replace('+', ' ')
			data = escaped_latin1_to_utf8(data)
		if (len(get_paquet_data(msg).split("?")) > 1) :
			id_session = get_paquet_data(msg).split("?")[0].replace("ajoute", "").replace("/", "")
	#CREATE RETURN PAQUET
		msg = res.replace("$(DATA)", data)
		if (len(id_session) == 0) :
			id_session = str(os.getpid())
			#CREATE PROCESS SHELL
			if (os.fork() == 0) :
				#os.setsid()
				#PIPES
				os.mkfifo("/tmp/shell_vers_traitement" + (id_session))
				os.mkfifo("/tmp/traitement_vers_shell" + (id_session))	
				#READ CMD IN TRAITEMENT_VERS_SHELL
				#data_cmd = read_file(fd_read)
				#os.execvp('sh', ['sh', '-c', 'sh /tmp/traitement_vers_shell' + (id_session) + ' 11< /tmp/traitement_vers_shell' + (id_session) + ' &> /tmp/shell_vers_traitement' + (id_session) + ' 12>/tmp/traitement_vers_shell' + (id_session) + ' 13< /tmp/shell_vers_traitement' + (id_session)])
				os.write(2, bytes('sh /tmp/traitement_vers_shell' + (id_session) + ' 3<> /tmp/traitement_vers_shell' + (id_session) + ' &> /tmp/shell_vers_traitement' + (id_session) + ' 4< /tmp/shell_vers_traitement' + (id_session), 'utf8'))
				os.execvp('sh', ['sh', '-c', 'sh /tmp/traitement_vers_shell' + (id_session) + ' 3<> /tmp/traitement_vers_shell' + (id_session) + ' &> /tmp/shell_vers_traitement' + (id_session) + ' 4< /tmp/shell_vers_traitement' + (id_session)])
		msg = msg.replace("$(ID_SESSION)", id_session)
		#OPEN FILES HISTORY AND PIPE
		files_created = 0
		fd_fifo_in = -1
		fd_fifo_out = -1
		fd = os.open("/tmp/historique" + str(id_session) + ".txt", os.O_CREAT | os.O_APPEND | os.O_RDWR)
		while (not(files_created) and len(id_session) > 0) :
			try : 
				fd_fifo_out = os.open("/tmp/traitement_vers_shell" + str(id_session), os.O_WRONLY)
				fd_fifo_in = os.open("/tmp/shell_vers_traitement" + str(id_session), os.O_RDONLY)
				files_created = 1
			except :
				files_created = 0
		#Extract and write HISTORY IN SOCKET
		history = read_file(fd)
		msg = msg.replace("$(HISTORY)", history.replace("\n", "<br>"))
		os.write(1, bytes(msg, 'utf8'))
		#WRITE IN HISTORY FILE AND IN PIPE TO SHELL
		if (len(data) > 0) :
			os.write(fd, bytes(data,'utf8'))
			os.write(fd, bytes('\n', 'utf8'))
			os.write(fd_fifo_out, bytes(data, 'utf8'))
		os.close(fd)
		#WRITE RES
		if (len(data) > 0) :
			shell_res = read_file(fd_fifo_in)
			os.write(1, bytes(shell_res, 'utf8'))
		os.close (fd_fifo_in)
		os.close (fd_fifo_out)
		return (data, history)
if __name__ == "__main__" :
	get_cmd()
	sys.exit (-1)