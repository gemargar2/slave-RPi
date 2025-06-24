import zmq

# connect to master socket
context_rx = zmq.Context()
socket_rx = context_rx.socket(zmq.PULL)
socket_rx.connect("tcp://160.40.55.211:2000")

# connect to slave socket
context_tx = zmq.Context()
socket_tx = context_tx.socket(zmq.PUSH)
socket_tx.bind("tcp://*:2001")

print("slave waits clock tick from master")
while True:
	# master waits clock tick from master
	message = socket_rx.recv_json()
	print(str(message))
	message = { "slave says": "hello" }
	socket_tx.send_json(message)
