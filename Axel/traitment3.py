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
	$(RES)<br>
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
			i += 3
		else :
			res += s[i]
		i += 1
	return res

def	main() :
	msg = os.read(0, 100000)
	if (msg.decode('utf8').split("\r")[0].split(' ')[0] != "GET" or msg.decode('utf8').split('\r')[0].split(' ')[2] != 'HTTP/1.1') :
		os.write(2, b"request not supported\n")
	else :
		inter = msg.decode('utf8')
		data = ''
		if (len(msg.decode('utf8').split("\r")[0].split(' ')[1].split("?")) > 1) :
			data = msg.decode('utf8').split("\r")[0].split(' ')[1].split("?")[1].split("&")[0].split("=")[1].replace('+', ' ')
		msg = res2.replace("$(RES)", msg.decode('utf8').replace("\n", "<br>"))
		msg = msg.replace("$(DATA)", escaped_latin1_to_utf8(data))
		msg = res.replace("$(SIZE)", str(len(msg))).replace('\n', '\n\r') + msg
		os.write(2, bytes(msg, 'utf8'))
		os.write(1, bytes(msg, 'utf8'))
	exit (0)
if __name__ == "__main__" :
	main()