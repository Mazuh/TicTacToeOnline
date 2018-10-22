any:
	echo 'Choose between making a "server" or a "client" run.' && exit 1

server:
	python2 ./simple_game_server/server.py --tcpport 1234 --udpport 1234 --capacity 2

client:
	python2 ./tic_tac_toe.py
