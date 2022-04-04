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
	$(RES)
	<form action="ajoute" method="get">
		<input type="text" name="saisie" value="Tapez quelque chose" />
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
		msg = res.replace("$(RES)", msg.decode('utf8'))
		os.write(2, bytes(msg, 'utf8'))
		print(msg, file = sys.stdout)
	exit (0)
if __name__ == "__main__" :
	main()