import zmq
import json
from time import sleep
from slave_class import *

def recalc_contribution(slav_obj, window_obj):
	# Recalculate available power yield
	slav_obj.total_pmax = 0
	slav_obj.total_qmax = 0
	slav_obj.total_qmin = 0
	for index in range(slav_obj.number):
		slav_obj.pi_per[index] = 0.0
		if slav_obj.dev_status[index] == 0:
			slav_obj.total_pmax += slav_obj.dev_pmax[index]
			slav_obj.total_qmax += slav_obj.dev_qmax[index]
			slav_obj.total_qmin += slav_obj.dev_qmin[index]			

	# Calculate new contribution
	for index in range(slav_obj.number):
		if slav_obj.dev_status[index] == 0:
			if slav_obj.total_pmax != 0: slav_obj.pi_per[index] = slav_obj.dev_pmax[index]/slav_obj.total_pmax
			if slav_obj.total_qmax != 0: slav_obj.qi_per[index] = slav_obj.dev_qmax[index]/slav_obj.total_qmax
			if slav_obj.total_qmin != 0: slav_obj.qa_per[index] = slav_obj.dev_qmin[index]/slav_obj.total_qmin
	
	# Calculate total production
	slav_obj.total_pac = 0
	slav_obj.total_qac = 0
	for index in range(slav_obj.number):
		slav_obj.total_pac += slav_obj.dev_pac[index]
		slav_obj.total_qac += slav_obj.dev_qac[index]
	
	total_setpoint = round(slav_obj.master_p_in_sp * slav_obj.S_nom, 2)

	# Window title
	if slav_obj.dev_status[0] == 0: dev1_status = "ON"
	else: dev1_status = "OFF"
	if slav_obj.dev_status[1] == 0: dev2_status = "ON"
	else: dev1_status = "OFF"
	slave1_str = f'Slave 1 P={round(slav_obj.total_pac, 2)} / S={total_setpoint} / A={slav_obj.total_pmax} / I={slav_obj.S_nom}'
	dev1_str = f'dev1 ({dev1_status}) S={round(slav_obj.dev_p_sp[0]*slav_oblj.S_nom, 2)} / I={slav_obj.installed[0]}'
	dev2_str = f'dev2 ({dev2_status}) S={round(slav_obj.dev_p_sp[1]*slav_obj.S_nom, 2)} / I={slav_obj.installed[1]}'
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
		for i in range(slave_obj.number):
			dest = "Inverter_" + str(i+1)
			# Distribution for p inj, q inj and q abs
			slave_obj.dev_p_sp[i] = slave_obj.master_p_in_sp * slave_obj.pi_per[i]
			if slave_obj.master_q_in_sp < 0: slave_obj.dev_q_sp[i] = slave_obj.master_q_in_sp * slave_obj.qa_per[i]
			else: slave_obj.dev_q_sp[i] = slave_obj.master_q_in_sp * slave_obj.qi_per[i]
			# Check limits
			if slave_obj.dev_p_sp[i]*slave_obj.S_nom > slave_obj.dev_pmax[i]: slave_obj.dev_p_sp[i] = slave_obj.dev_pmax[i]/slave_obj.S_nom 
			if slave_obj.dev_q_sp[i]*slave_obj.S_nom  > slave_obj.dev_qmax[i]: slave_obj.dev_q_sp[i] = slave_obj.dev_qmax[i]/slave_obj.S_nom 
			if slave_obj.dev_q_sp[i]*slave_obj.S_nom  < slave_obj.dev_qmin[i]: slave_obj.dev_q_sp[i] = slave_obj.dev_qmin[i]/slave_obj.S_nom 
			# Send json
			message1 = { "destination": dest, "value": str(slave_obj.dev_p_sp[i]*slave_obj.S_nom), "value_name": "P_SP_slave" }
			message2 = { "destination": dest, "value": str(slave_obj.dev_q_sp[i]*slave_obj.S_nom), "value_name": "Q_SP_slave" }
			try:
				socket_tx.send_json(message1, zmq.NOBLOCK)
				socket_tx.send_json(message2, zmq.NOBLOCK)
				if printMessages: print("Success")
			except:
				if printMessages: print("Failed")
		# Send to master
		message1 = { "destination": "master", "value_name": "Total_Pmax_available", "value": str(slave_obj.total_pmax) }
		message2 = { "destination": "master", "value_name": "Total_Qmax_available", "value": str(slave_obj.total_qmax) }
		message3 = { "destination": "master", "value_name": "Total_Qmin_available", "value": str(slave_obj.total_qmin) }
		message4 = { "destination": "master", "value_name": "status_ippm", "value": str(slave_obj.status_ippm) }
		message5 = { "destination": "master", "value_name": "P_generated", "value": str(slave_obj.total_pac) }
		message6 = { "destination": "master", "value_name": "Q_generated", "value": str(slave_obj.total_qac) }
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


