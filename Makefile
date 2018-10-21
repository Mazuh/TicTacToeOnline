any:
	echo 'Choose between making a "server" or a "client".' && exit 1

server:
	python ./simple_game_server/server.py --tcpport 1234 --udpport 1234 --capacity 2

client:
	echo 'Not yet implemented.' && exit 1
