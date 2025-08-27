import zmq
import json
import threading
from time import sleep
from slave_class import *
from window import Window_class

printMessages = False

def plotStuff(i, window_obj, slave_obj):
	x = i/10
	window_obj.plot_data(x, slave_obj)

def master_rx(slave_obj):
	# Zero MQ is the messaging protocol used to communicate with the slave devices.
	context_rx = zmq.Context()
	socket_rx = context_rx.socket(zmq.PULL)
	socket_rx.connect("ipc:///tmp/zmqpub")
	sleep(5)

	while True:
		message = socket_rx.recv_json()
		# print(message)
		if message['value_name'] == 'P_SP_master': slave_obj.p_in_sp = float(message['value'])
		elif message['value_name'] == 'Q_SP_master': slave_obj.q_in_sp = float(message['value'])
		# Upon receiving a new value re-calculate
		# emulator_obj.hv_meter()

def inverter_tx(slave_obj):
	# Zero MQ is the messaging protocol used to communicate with the slave devices.
	context_tx = zmq.Context()
	socket_tx = context_tx.socket(zmq.PUSH)
	socket_tx.bind("ipc:///tmp/zmqsub")
	sleep(5)
    
	while(True):
		# Tick
		sleep(0.1)
		message1 = { "destination": "Inverter_1", "value": "15.0", "value_name": "P_SP_slave" }
		message2 = { "destination": "Inverter_1", "value": "0.0", "value_name": "Q_SP_slave" }
		message3 = { "destination": "Inverter_2", "value": "5.0", "value_name": "P_SP_slave" }
		message4 = { "destination": "Inverter_2", "value": "0.0", "value_name": "Q_SP_slave" }
		try:
			socket_tx.send_json(message1, zmq.NOBLOCK)
			socket_tx.send_json(message2, zmq.NOBLOCK)
			socket_tx.send_json(message3, zmq.NOBLOCK)
			socket_tx.send_json(message4, zmq.NOBLOCK)
			if printMessages: print("Success")
		except:
			if printMessages: print("Failed")

def main():
	with open('config.json', 'r') as openfile:
		config = json.load(openfile)

	# Create objects
	slave_obj = Slave_class(config)
	window_obj = Window_class()

	# Start parallel processes
	master_receive = threading.Thread(target = master_rx, args=(slave_obj,))
	master_receive.start()
	inverter_send = threading.Thread(target = inverter_tx, args=(slave_obj,))
	inverter_send.start()

	# Plot data
	i = 0
	while True:
		plotStuff(i, window_obj, slave_obj)
		i += 1

if __name__ == "__main__":
	main()
