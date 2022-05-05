import json
import os
import sys

res = """
HTTP/1.1 200
Content-Type: text/html; charset=utf-8
Connection: close
Content-Length: $(SIZE) 

"""
res2="""
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
	msg = os.read(0, 100000)
	if (msg.decode('utf8').split("\r")[0].split(' ')[0] != "GET" or msg.decode('utf8').split('\r')[0].split(' ')[2] != 'HTTP/1.1') :
		os.write(2, b"request not supported\n")
	else :
		inter = msg.decode('utf8')
		msg = res2.replace("$(RES)", msg.decode('utf8').replace("\n", "<br>"))
		msg = res.replace("$(SIZE)", str(len(msg))).replace('\n', '\n\r') + msg
		os.write(2, bytes(msg, 'utf8'))
		os.write(1, bytes(msg, 'utf8'))
	exit (0)
if __name__ == "__main__" :
	main()