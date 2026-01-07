import zmq
import json
from time import sleep
from slave_class import *

def recalc_contribution(slav_obj, window_obj):
	# Recalculate available power yield
	slav_obj.total_pmax = 0
	slav_obj.total_qmax = 0
	slav_obj.total_qmin = 0
	slav_obj.connection = True
	for index in range(slav_obj.number):
		if slav_obj.dev_status[index] == 1:
			slav_obj.total_pmax += slav_obj.dev_pmax[index]
			slav_obj.total_qmax += slav_obj.dev_qmax[index]
			slav_obj.total_qmin += slav_obj.dev_qmin[index]
	
	# Calculate new contribution
	for index in range(slav_obj.number):
		slav_obj.pi_per[index] = 0.0
		slav_obj.qi_per[index] = 0.0
		slav_obj.qa_per[index] = 0.0
		if slav_obj.dev_status[index] == 1:
			if slav_obj.total_pmax != 0: slav_obj.pi_per[index] = slav_obj.dev_pmax[index]/slav_obj.total_pmax
			if slav_obj.total_qmax != 0: slav_obj.qi_per[index] = slav_obj.dev_qmax[index]/slav_obj.total_qmax
			if slav_obj.total_qmin != 0: slav_obj.qa_per[index] = slav_obj.dev_qmin[index]/slav_obj.total_qmin
	
	# Calculate total production
	slav_obj.total_pac = 0
	slav_obj.total_qac = 0
	for index in range(slav_obj.number):
		slav_obj.total_pac += slav_obj.dev_pac[index]
		slav_obj.total_qac += slav_obj.dev_qac[index]

	# Window title
	if slav_obj.dev_status[0] == 0: dev1_status = "ON"
	else: dev1_status = "OFF"
	if slav_obj.dev_status[1] == 0: dev2_status = "ON"
	else: dev1_status = "OFF"
	
	slave1_r = f'Slave1({slav_obj.total_pmax}/{slav_obj.total_qmax}/{slav_obj.total_qmin})'
	dev1_r = f'dev1({slav_obj.dev_pmax[0]}/{slav_obj.dev_qmax[0]}/{slav_obj.dev_qmin[0]})'
	dev2_r = f'dev2({slav_obj.dev_pmax[1]}/{slav_obj.dev_qmax[1]}/{slav_obj.dev_qmin[1]})'
	dev1_p = f'dev1({int(slav_obj.pi_per[0]*100)}/{int(slav_obj.qi_per[0]*100)}/{int(slav_obj.qa_per[0]*100)})'
	dev2_p = f'dev2({int(slav_obj.pi_per[1]*100)}/{int(slav_obj.qi_per[1]*100)}/{int(slav_obj.qa_per[1]*100)})'
	window_obj.fig.suptitle(f'Availability (MW/MVAR): {slave1_r}, {dev1_r}, {dev2_r} \n Contribution (%): {dev1_p} {dev2_p}')

	# Populate plot vectors
	# Index
	slav_obj.x_data.append(slav_obj.x)
	# Active power
	slav_obj.master_p_sp_data.append(slav_obj.master_p_in_sp)
	slav_obj.dev1_p_sp_data.append(slav_obj.dev_p_sp[0])
	slav_obj.dev2_p_sp_data.append(slav_obj.dev_p_sp[1])
	# Reactive power
	slav_obj.master_q_sp_data.append(slav_obj.master_q_in_sp)
	slav_obj.dev1_q_sp_data.append(slav_obj.dev_q_sp[0])
	slav_obj.dev2_q_sp_data.append(slav_obj.dev_q_sp[1])

def signals_rx(slave_obj): 
	# Zero MQ is the messaging protocol used to communicate with the slave devices.
	context_rx = zmq.Context()
	socket_rx = context_rx.socket(zmq.PULL)
	socket_rx.connect("ipc:///tmp/zmqpub")
	sleep(5)

	while True:
		message = socket_rx.recv_json()
				
		origin = ''
		# Check for connection status
		if message['value_name'] == 'df925a75-00a7-40ae-8ed9-cb5008d725ce':
			if message['origin'] == 'master': origin = 'master'
			elif message['origin'] == 'localPlatform': origin = 'SCADA'
			elif message['origin'] == 'MV_Meter': origin = 'MV_Meter'
			elif message['origin'] == 'Meteo': origin = 'Meteo'
			else:
				# Iterate through slaves
				for i in range(slave_obj.number):
					label = 'Inverter_' + str(i+1)
					if message['origin'] == label: origin = label
			#if message['status'] == True: print(f"{origin} connection ok")
			#else: print(f"{origin} connection not ok")

		if message["origin"] == "master":
			if message['value_name'] == 'P_SP_master': slave_obj.master_p_in_sp = float(message['value'])
			elif message['value_name'] == 'Q_SP_master': slave_obj.master_q_in_sp = float(message['value'])
			elif message['value_name'] == 'Start': slave_obj.start = int(message['value'])
			elif message['value_name'] == 'Stop': slave_obj.stop = int(message['value'])
		elif message["origin"] == "MV_Meter":
			if message['value_name'] == "P_generated": slave_obj.total_pac = float(message['value'])
			elif message['value_name'] == "Q_generated": slave_obj.total_qac = float(message['value'])
			elif message['value_name'] == "Voltage_3_ph": pass
			elif message['value_name'] == "IAC_rms": pass
			elif message['value_name'] == "status_ippm": slave_obj.status_ippm = int(message['value'])
			elif message['value_name'] == "ippm_switch": slave_obj.ippm_switch = int(message['value'])

		for i in range(slave_obj.number):
			sender = "Inverter_" + str(i+1)
			if message["origin"] == sender:
				if message['value_name'] == "Total_P_ac": slave_obj.dev_pac[i] = float(message['value'])
				elif message['value_name'] == "Total_Q_ac": slave_obj.dev_qac[i] = float(message['value'])
				elif message['value_name'] == "Total_Pmax_available": slave_obj.dev_pmax[i] = float(message['value'])
				elif message['value_name'] == "Total_Qmax_available": slave_obj.dev_qmax[i] = float(message['value'])
				elif message['value_name'] == "Total_Qmin_available": slave_obj.dev_qmin[i] = float(message['value'])
				elif message['value_name'] == "Operation_Status": slave_obj.dev_status[i] = float(message['value'])
				elif message['value_name'] == "Inverter_Connected": slave_obj.dev_connx[i] = float(message['value'])

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
			if slave_obj.master_q_in_sp < 0:
				slave_obj.dev_q_sp[i] = slave_obj.master_q_in_sp * slave_obj.qa_per[i]
			else:
				slave_obj.dev_q_sp[i] = slave_obj.master_q_in_sp * slave_obj.qi_per[i]
			# Check limits
			if slave_obj.dev_p_sp[i] > slave_obj.dev_pmax[i]: slave_obj.dev_p_sp[i] = slave_obj.dev_pmax[i]
			if slave_obj.dev_q_sp[i]  > slave_obj.dev_qmax[i]: slave_obj.dev_q_sp[i] = slave_obj.dev_qmax[i]
			if slave_obj.dev_q_sp[i]  < slave_obj.dev_qmin[i]: slave_obj.dev_q_sp[i] = slave_obj.dev_qmin[i]
			# Send json
			message1 = { "destination": dest, "value": str(slave_obj.dev_p_sp[i]), "value_name": "P_SP_slave" }
			message2 = { "destination": dest, "value": str(slave_obj.dev_q_sp[i]), "value_name": "Q_SP_slave" }
			message3 = { "destination": dest, "value": str(slave_obj.start), "value_name": "Start_inverter" }
			message4 = { "destination": dest, "value": str(slave_obj.stop), "value_name": "Stop_inverter" }
			try:
				socket_tx.send_json(message1, zmq.NOBLOCK)
				socket_tx.send_json(message2, zmq.NOBLOCK)
				socket_tx.send_json(message3, zmq.NOBLOCK)
				socket_tx.send_json(message4, zmq.NOBLOCK)
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


