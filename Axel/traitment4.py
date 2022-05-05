import json
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
    <title>Hello, world!</title>
</head>
<body>
	$(HISTORY)<br>
	$(DATA)<br>
	<form action="ajoute" method="get">
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
			i += 2
		else :
			res += s[i]
		i += 1
	return res

def	main() :
	fd = os.open("/tmp/historique.txt", os.O_CREAT | os.O_APPEND | os.O_RDWR)
	msg = os.read(0, 100000)
	if (msg.decode('utf8').split("\r")[0].split(' ')[0] != "GET" or msg.decode('utf8').split('\r')[0].split(' ')[2] != 'HTTP/1.1') :
		os.write(2, b"request not supported\n")
	else :
		read = os.read(fd, 100000)
		history =  ''
		while (len(read) > 0) :
			history += read.decode('utf8')
			read = os.read(fd, 100000)
		#EXTRACT DATA
		data = ''
		if (len(msg.decode('utf8').split("\r")[0].split(' ')[1].split("?")) > 1) :
			data = msg.decode('utf8').split("\r")[0].split(' ')[1].split("?")[1].split("&")[0].split("=")[1].replace('+', ' ')
			data = escaped_latin1_to_utf8(data)
		#CREATE RETURN PAQUET
		msg = res2.replace("$(DATA)", data)
		msg = msg.replace("$(HISTORY)", history.replace("\n", "<br>"))
		msg = res.replace("$(SIZE)", str(len(msg))).replace('\n', '\n\r') + msg
		os.write(1, bytes(msg, 'utf8'))
		#WRITE IN HISTORY
		if (len(data) > 0) :
			os.write(fd, bytes(data,'utf8'))
			os.write(fd, bytes('\n', 'utf8'))
		os.close(fd)
	exit (0)
if __name__ == "__main__" :
	main()