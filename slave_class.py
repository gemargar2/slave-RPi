from numpy import zeros

printMessages = False

class Slave_class:
	def __init__(self, config):
		# Store config data locally
		self.configdata = config
		self.slave_id = int(self.configdata["device"]["ID"])
		self.P_nominal = int(self.configdata["device"]["nominal_power"])
		self.devices = self.configdata["device"]["devices"]
		self.number = len(self.devices) # number of inverters
		# Inverters
		self.installed = [] # nominal power of inverters
		self.contribution = [] # percentage of contribution to the final power output
		self.device_id = []
		# Inverter signals
		self.dev_pac = zeros(self.number) # P actual
		self.dev_qac = zeros(self.number) # Q actual
		self.dev_pmax = zeros(self.number) # Pmax available
		self.dev_qmax = zeros(self.number) # Qmax available
		self.dev_qmin = zeros(self.number) # Qmin available
		self.dev_status = zeros(self.number) # Operation status
		self.dev_connx = zeros(self.number) # Connection status
		# Setpoints
		self.dev_p_sp = zeros(self.number)
		self.dev_q_sp = zeros(self.number)
		# Summary
		self.slav_pac = 0
		self.slav_qac = 0
		self.slav_pmax = 0
		self.slav_qmax = 0
		self.slav_qmin = 0
		self.ippm_switch = 0
		self.status_ippm = 0
		# Master setpoints
		self.master_p_in_sp = 0
		self.master_q_in_sp = 0
		self.connect_to_devices()

	def connect_to_devices(self):
		p_avail = 0
		for i in self.devices:
			self.device_id.append(int(self.devices[i]["ID"]))
			self.installed.append(int(self.devices[i]["nominal_power"]))
			self.contribution.append(float(self.devices[i]["nominal_power"])/self.P_nominal)
			p_avail += int(self.devices[i]["nominal_power"])

		print(self.device_id)
		print(self.installed)
		print(self.contribution)

		if p_avail != self.P_nominal:
			print("Error! Sum of inverter's nominal power ratings does not match Slave's nominal power")
		else:
			print("P_avail ok")

	def recalc_contribution(self, window_obj):
		# Recalculate available power yield
		index = 0
		new_pmax = 0
		for i in self.devices:
			self.contribution[index] = 0.0
			if self.dev_status[index] == 0:
				new_pmax += int(self.devices[i]["nominal_power"])
			index += 1

		# Calculate new contribution
		index = 0
		for i in self.devices:
			if self.device_state[index] == 0:
				self.contribution[index] = float(self.devices[i]["nominal_power"])/new_pmax
			index += 1
		
		self.slav_pmax = new_pmax
		total_production = round(self.dev_pac[0] + self.dev_pac[1], 2)
		total_setpoint = round(self.master_p_in_sp * self.P_nominal, 2)

		if self.dev_status[0] == 0: dev1_status = "ON"
		else: dev1_status = "OFF"
		if self.dev_status[1] == 0: dev2_status = "ON"
		else: dev1_status = "OFF"

		slave1_str = f'Slave 1 P={total_production} / S={total_setpoint} / A={self.slav_pmax} / I={self.P_nominal}'
		dev1_str = f'dev1 ({dev1_status}) S={round(self.dev_p_sp[0]*self.P_nominal, 2)} / I={self.installed[0]}'
		dev2_str = f'dev2 ({dev2_status}) S={round(self.dev_p_sp[1]*self.P_nominal, 2)} / I={self.installed[1]}'
		window_obj.fig.suptitle(f'{slave1_str} \n {dev1_str} \n {dev2_str}')




