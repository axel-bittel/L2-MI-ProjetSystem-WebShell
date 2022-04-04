import json
import os
import sys

res = """
HTTP/1.1 200 
Content-Type: text/html; charset=utf-8
Connection: close
Content-Length: 100000

<!DOCTYPE html>
<html>
<head>
    <title>Hello, world!</title>
</head>
<body>
$(RES)
</body>
</html>
""" 

def	main() :
	#fd = os.open("test.txt", os.O_CREAT | os.O_WRONLY)
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