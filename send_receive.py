import zmq
import json
from time import sleep
from slave_class import *

def recalc_contribution(slav_obj, window_obj):
	# Recalculate available power yield
	slav_obj.slav_pmax = 0
	for index in range(2):
		slav_obj.contribution[index] = 0.0
		if slav_obj.dev_status[index] == 0:
			slav_obj.slav_pmax += slav_obj.dev_pmax[index]

	# Calculate new contribution
	for index in range(2):
		if slav_obj.dev_status[index] == 0:
			if slav_obj.slav_pmax != 0:
				slav_obj.contribution[index] = float(slav_obj.dev_pmax[index]/slav_obj.slav_pmax)
	
	total_production = round(slav_obj.dev_pac[0] + slav_obj.dev_pac[1], 2)
	total_setpoint = round(slav_obj.master_p_in_sp * slav_obj.P_nominal, 2)
	if slav_obj.dev_status[0] == 0: dev1_status = "ON"
	else: dev1_status = "OFF"
	if slav_obj.dev_status[1] == 0: dev2_status = "ON"
	else: dev1_status = "OFF"
	slave1_str = f'Slave 1 P={total_production} / S={total_setpoint} / A={slav_obj.slav_pmax} / I={slav_obj.P_nominal}'
	dev1_str = f'dev1 ({dev1_status}) S={round(slav_obj.dev_p_sp[0]*slav_obj.P_nominal, 2)} / I={slav_obj.installed[0]}'
	dev2_str = f'dev2 ({dev2_status}) S={round(slav_obj.dev_p_sp[1]*slav_obj.P_nominal, 2)} / I={slav_obj.installed[1]}'
	window_obj.fig.suptitle(f'{slave1_str} \n {dev1_str} \n {dev2_str}')

def signals_rx(slave_obj, window_obj):
	# Zero MQ is the messaging protocol used to communicate with the slave devices.
	context_rx = zmq.Context()
	socket_rx = context_rx.socket(zmq.PULL)
	socket_rx.connect("ipc:///tmp/zmqpub")
	sleep(5)

	while True:
		message = socket_rx.recv_json()
		# print(message)
		if message["origin"] == "master":
			# print(message)
			if message['value_name'] == 'P_SP_master': slave_obj.master_p_in_sp = float(message['value'])
			elif message['value_name'] == 'Q_SP_master': slave_obj.master_q_in_sp = float(message['value'])
		elif message["origin"] == "Inverter_1":
			if message['value_name'] == "Total_P_ac": slave_obj.dev_pac[0] = float(message['value'])
			elif message['value_name'] == "Total_Q_ac": slave_obj.dev_qac[0] = float(message['value'])
			elif message['value_name'] == "Total_Pmax_available": slave_obj.dev_pmax[0] = float(message['value'])
			elif message['value_name'] == "Total_Qmax_available": slave_obj.dev_qmax[0] = float(message['value'])
			elif message['value_name'] == "Total_Qmin_available": slave_obj.dev_qmin[0] = float(message['value'])
			elif message['value_name'] == "Operation_Status": slave_obj.dev_status[0] = float(message['value'])
			elif message['value_name'] == "Inverter_connected": slave_obj.dev_connx[0] = float(message['value'])
		elif message["origin"] == "Inverter_2":
			if message['value_name'] == "Total_P_ac": slave_obj.dev_pac[1] = float(message['value'])
			elif message['value_name'] == "Total_Q_ac": slave_obj.dev_qac[1] = float(message['value'])
			elif message['value_name'] == "Total_Pmax_available": slave_obj.dev_pmax[1] = float(message['value'])
			elif message['value_name'] == "Total_Qmax_available": slave_obj.dev_qmax[1] = float(message['value'])
			elif message['value_name'] == "Total_Qmin_available": slave_obj.dev_qmin[1] = float(message['value'])
			elif message['value_name'] == "Operation_Status": slave_obj.dev_status[1] = float(message['value'])
			elif message['value_name'] == "Inverter_connected": slave_obj.dev_connx[1] = float(message['value'])
		# Change title
		recalc_contribution(slave_obj, window_obj)
		# Upon receiving a new value re-calculate
		# emulator_obj.hv_meter()

def signals_tx(slave_obj):
	# Zero MQ is the messaging protocol used to communicate with the slave devices.
	context_tx = zmq.Context()
	socket_tx = context_tx.socket(zmq.PUSH)
	socket_tx.bind("ipc:///tmp/zmqsub")
	sleep(5)
    
	while True:
		# Tick
		sleep(0.1)
		for i in range(2):
			dest = "Inverter_" + str(i+1)
			# Distribution
			slave_obj.dev_p_sp[i] = slave_obj.master_p_in_sp * slave_obj.contribution[i]
			if slave_obj.dev_p_sp[i] * slave_obj.P_nominal >= slave_obj.installed[i]:
				slave_obj.dev_p_sp[i] = slave_obj.installed[i]/slave_obj.P_nominal
			slave_obj.dev_q_sp[i] = slave_obj.master_q_in_sp * slave_obj.contribution[i]
			# Send json
			message1 = { "destination": dest, "value": str(slave_obj.dev_p_sp[i]*slave_obj.P_nominal), "value_name": "P_SP_slave" }
			message2 = { "destination": dest, "value": str(slave_obj.dev_q_sp[i]*slave_obj.P_nominal), "value_name": "Q_SP_slave" }
			try:
				socket_tx.send_json(message1, zmq.NOBLOCK)
				socket_tx.send_json(message2, zmq.NOBLOCK)
				if printMessages: print("Inverter messages transmitted successfully")
			except:
				if printMessages: print("Inverter messages transmission failed")
		# Send to master
		message1 = { "destination": "master", "value_name": "Total_Pmax_available", "value": str(slave_obj.slav_pmax) }
		message2 = { "destination": "master", "value_name": "Total_Qmax_available", "value": str(slave_obj.slav_qmax) }
		message3 = { "destination": "master", "value_name": "Total_Qmin_available", "value": str(slave_obj.slav_qmin) }
		message4 = { "destination": "master", "value_name": "status_ippm", "value": str(slave_obj.status_ippm) }
		message5 = { "destination": "master", "value_name": "P_generated", "value": str(slave_obj.slav_pac) }
		message6 = { "destination": "master", "value_name": "Q_generated", "value": str(slave_obj.slav_qac) }
		message7 = { "destination": "master", "value_name": "ippm_switch", "value": str(slave_obj.ippm_switch) }
		try:
			socket_tx.send_json(message1, zmq.NOBLOCK)
			socket_tx.send_json(message2, zmq.NOBLOCK)
			socket_tx.send_json(message3, zmq.NOBLOCK)
			socket_tx.send_json(message4, zmq.NOBLOCK)
			socket_tx.send_json(message5, zmq.NOBLOCK)
			socket_tx.send_json(message6, zmq.NOBLOCK)
			socket_tx.send_json(message7, zmq.NOBLOCK)
			if printMessages: print("Master messages transmitted successfully")
		except:
			if printMessages: print("Master messages transmission failed")
