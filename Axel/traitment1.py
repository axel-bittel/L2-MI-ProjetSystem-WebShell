import json
import os

def	main() :
	#fd = os.open("test.txt", os.O_CREAT | os.O_WRONLY)
	msg = os.read(0, 100000)
	inter = msg.decode('utf8').split('\r')[0].split(' ')[2]
	if (msg.decode('utf8').split("\r")[0].split(' ')[0] != "GET" or msg.decode('utf8').split('\r')[0].split(' ')[2] != 'HTTP/1.1') :
		os.write(2, b"request not supported\n")
	else :
		os.write(2, msg)
	exit (1)
if __name__ == "__main__" :
	main()