import os


buf = os.read(0, 100000)   #on lit les 100000 premiers octets sur entree standard         
buf = buf.decode("utf8")   #on decode (on est en utf8)
buf2 = buf.split("\n")     #on a une liste dont chaque element = une ligne 

#on verfiie qu'on a bien une requete GET en HTTP/1.1
if buf2[0] == "GET / HTTP/1.1\r" :
	os.write(2, bytes("Ça marche", "utf8"))
	os.write(2, bytes(buf, "utf8"))

#on veut afficher la requête, on divise la partie entete du corps 
	entete = """
HTTP/1.1 200 
Content-Type: text/html; charset=utf-8
Connection: close
Content-Length: !!LEN!!

"""

	corps = """
<!DOCTYPE html>
<head>
    <title>Hello, world!</title>
	</head>
	<body>
		!!MESSAGE!!
	</body>
</html>
	"""

	#on veut egalement afficher le bouton 
	body = """
<form action="ajoute" method="get">
        <input type="text" name="saisie" value="Tapez quelque chose" />
        <input type="submit" name="send" value="&#9166;">
    </form>
"""

	buf = buf.replace("\n", "<br>")             #pour convertir en html
	corps = corps.replace("!!MESSAGE!!", body)  #on remplace par ce qu'on doit afficher
	l = len(corps)                              #on recupere la longueur du message
	entete = entete.replace("!!LEN!!", str(l)) 
	entete = entete.replace("\n", "\r\n")

	message = entete + corps                    #le message final à afficher
	os.write(1,bytes(message, "utf8"))          #on affiche le message


	# elif buf2[0][:20] == "GET / ajoute?saisie=" :
	#     os.write(2, bytes(buf, "utf8"))

	# else :
	#     os.write(2, b"request not supported\n")
